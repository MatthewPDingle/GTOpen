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

Real-range game files (exact flop solves of the ranges a GTOpen preflop solve
produced, written by `tools/leafnet/realrange.py publish ... --out DIR`) go up
with

    python tools/datagen/upload.py --contributor YOUR_GITHUB_LOGIN --real DIR

as real/<login>/<set>/<game>.jsonl.gz. The validator accepts those only from
the logins listed in config.json.

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


REAL_FORMAT = "gtopen-real-range"


def finished_games(real_dir, login):
    """[(path, set, game)] of real-range game files under DIR/real/<login>/<set>/ that have not gone up yet."""
    base = os.path.join(real_dir, "real", login)
    games = []
    if not os.path.isdir(base):
        return games
    for set_name in sorted(os.listdir(base)):
        d = os.path.join(base, set_name)
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            path = os.path.join(d, name)
            if name.endswith(".jsonl") and not os.path.exists(path + ".uploaded"):
                games.append((path, set_name, name[:-len(".jsonl")]))
    return games


def check_game_header(path, login, set_name, game):
    with open(path, encoding="utf-8") as f:
        header = json.loads(f.readline())
    want = {"type": "header", "format": REAL_FORMAT, "contributor": login, "set": set_name, "game": game}
    for key, value in want.items():
        if header.get(key) != value:
            raise SystemExit(f"{path}: header {key} is {header.get(key)!r}, expected {value!r}")
    return header


def upload_real_once(api, repo, real_dir, login):
    """One pull request with every real-range game file that has not gone up yet (at most MAX_FILES_PER_PR)."""
    from huggingface_hub import CommitOperationAdd

    games = finished_games(real_dir, login)[:MAX_FILES_PER_PR]
    if not games:
        print("no new real-range game files to upload")
        return 0
    stage = tempfile.mkdtemp(prefix="gtopen-upload-")
    try:
        ops = []
        examples = 0
        for n, (path, set_name, game) in enumerate(games):
            header = check_game_header(path, login, set_name, game)
            examples += int(header.get("examples", 0))
            gz = os.path.join(stage, f"{n}.gz")
            with open(path, "rb") as src, gzip.open(gz, "wb", compresslevel=9) as dst:
                shutil.copyfileobj(src, dst)
            ops.append(CommitOperationAdd(
                path_in_repo=f"real/{login}/{set_name}/{game}.jsonl.gz", path_or_fileobj=gz))
        title = f"{login}: {len(games)} real-range games, {examples} examples"
        info = api.create_commit(
            repo_id=repo, repo_type="dataset", operations=ops,
            commit_message=title, create_pr=True,
            commit_description="Exact flop solves of the ranges GTOpen preflop solves produced. "
                               "Uploaded by tools/datagen/upload.py --real. "
                               "The maintainer's validator re-solves a sample before merging.",
        )
        for path, _, _ in games:
            with open(path + ".uploaded", "w") as f:
                f.write((getattr(info, "pr_url", None) or str(info)) + "\n")
        print(f"opened {getattr(info, 'pr_url', info)}  ({title})")
        return len(games)
    finally:
        shutil.rmtree(stage, ignore_errors=True)


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
    ap.add_argument("--real", metavar="DIR", help="upload the real-range game files under DIR/real/<login>/ "
                                                  "(from realrange.py publish) instead of pooled jobs, once")
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
    if args.real:
        while upload_real_once(api, args.repo, args.real, args.contributor) == MAX_FILES_PER_PR:
            pass
        return
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
