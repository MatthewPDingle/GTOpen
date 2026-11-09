#!/usr/bin/env python3
"""Upload finished datagen jobs to the shared Hugging Face dataset.

Each run gzips every finished job file under <out>/<login>/ that has not been
uploaded yet and opens ONE pull request on the dataset with all of them.
The maintainer's validator re-checks and merges it. A `.uploaded` marker
next to each job file records what has gone up.

    pip install huggingface_hub
    hf auth login            # once, with a write token
    python tools/datagen/upload.py --contributor YOUR_GITHUB_LOGIN
    python tools/datagen/upload.py --contributor YOUR_GITHUB_LOGIN --watch 60

See docs/contribute-compute.md.
"""

import argparse
import gzip
import json
import os
import shutil
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
MAX_FILES_PER_PR = 200


def load_config():
    with open(os.path.join(HERE, "config.json")) as f:
        return json.load(f)


def finished_jobs(out_dir, login):
    d = os.path.join(out_dir, login)
    if not os.path.isdir(d):
        return []
    jobs = []
    for name in sorted(os.listdir(d)):
        if name.startswith("job-") and name.endswith(".jsonl"):
            path = os.path.join(d, name)
            if not os.path.exists(path + ".uploaded"):
                jobs.append(path)
    return jobs


def check_header(path, login):
    with open(path) as f:
        header = json.loads(f.readline())
    if header.get("type") != "header" or header.get("contributor") != login:
        raise SystemExit(f"{path}: header contributor {header.get('contributor')!r} is not {login!r}")
    return header


def upload_once(api, repo, out_dir, login):
    from huggingface_hub import CommitOperationAdd

    jobs = finished_jobs(out_dir, login)[:MAX_FILES_PER_PR]
    if not jobs:
        print("nothing new to upload")
        return 0
    stage = tempfile.mkdtemp(prefix="gtopen-upload-")
    try:
        ops = []
        examples = 0
        for path in jobs:
            header = check_header(path, login)
            examples += int(header.get("examples", 0))
            gz = os.path.join(stage, os.path.basename(path) + ".gz")
            with open(path, "rb") as src, gzip.open(gz, "wb", compresslevel=9) as dst:
                shutil.copyfileobj(src, dst)
            ops.append(CommitOperationAdd(
                path_in_repo=f"data/{login}/{os.path.basename(gz)}", path_or_fileobj=gz))
        title = f"{login}: {len(jobs)} jobs, {examples} examples"
        info = api.create_commit(
            repo_id=repo, repo_type="dataset", operations=ops,
            commit_message=title, create_pr=True,
            commit_description="Uploaded by tools/datagen/upload.py. "
                               "The maintainer's validator re-solves a sample before merging.",
        )
        for path in jobs:
            with open(path + ".uploaded", "w") as f:
                f.write((getattr(info, "pr_url", None) or str(info)) + "\n")
        print(f"opened {getattr(info, 'pr_url', info)}  ({title})")
        return len(jobs)
    finally:
        shutil.rmtree(stage, ignore_errors=True)


def main():
    cfg = load_config()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--contributor", required=True, help="your GitHub login (the one you pass to datagen run)")
    ap.add_argument("--out", default=os.path.join(ROOT, "datagen_out"), help="datagen output folder")
    ap.add_argument("--repo", default=cfg["hf_repo"], help="Hugging Face dataset id")
    ap.add_argument("--watch", type=float, default=0, help="keep running, uploading every N minutes")
    args = ap.parse_args()
    try:
        from huggingface_hub import HfApi
    except ImportError:
        sys.exit("huggingface_hub is missing: run  pip install huggingface_hub")
    api = HfApi()
    try:
        who = api.whoami()["name"]
    except Exception:
        sys.exit("not logged in to Hugging Face: run  hf auth login  (a token with write access)")
    print(f"Hugging Face user {who}, dataset {args.repo}, contributor {args.contributor}")
    while True:
        try:
            while upload_once(api, args.repo, args.out, args.contributor) == MAX_FILES_PER_PR:
                pass
        except Exception as e:
            if args.watch <= 0:
                raise
            # a network or Hub hiccup must not end an overnight run: the
            # unsent jobs stay unmarked and go up next round
            print(f"upload failed, will retry in {args.watch:g} min: {type(e).__name__}: {e}", flush=True)
        if args.watch <= 0:
            break
        time.sleep(args.watch * 60)


if __name__ == "__main__":
    main()
