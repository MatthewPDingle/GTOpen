#!/usr/bin/env python3
"""Maintainer tool: check pooled uploads, merge the good ones, track progress.

For every open pull request on the dataset it downloads the new job files,
checks each one with `solve-cli datagen verify` (header, regenerated inputs,
sanity, and a re-solve of a few examples), then merges the pull request or
closes it with the errors. Merged jobs are appended to progress.json in the
dataset, which the GitHub progress graph reads.

    python tools/datagen/validate.py                      # all open PRs
    python tools/datagen/validate.py --dry-run            # check, don't merge
    python tools/datagen/validate.py --local datagen_out  # check local files only
    python tools/datagen/validate.py --watch 60           # every hour

Needs a build of solve-cli (GPU build recommended) and, except with --local,
`hf auth login` with write access to the dataset.
"""

import argparse
import datetime
import gzip
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PATH_RE = re.compile(r"^data/([A-Za-z0-9_-]+)/job-(\d+)\.jsonl\.gz$")
BLOCK = 1 << 24


def load_config():
    with open(os.path.join(HERE, "config.json")) as f:
        return json.load(f)


def default_cli():
    exe = "solve-cli.exe" if os.name == "nt" else "solve-cli"
    return os.path.join(ROOT, "target", "release", exe)


def block_base(cli, login, cache={}):
    if login not in cache:
        out = subprocess.run([cli, "datagen", "block", login], capture_output=True, text=True, env=cuda_env())
        try:
            cache[login] = int(out.stdout.strip())
        except ValueError:
            raise ToolError(f"{cli} datagen block failed (exit code {out.returncode}): "
                            f"{out.stderr.strip()[-400:]}") from None
    return cache[login]


def cuda_env():
    """Environment with the pip-installed CUDA runtime compiler on the search path."""
    env = dict(os.environ)
    if os.name == "nt":
        d = os.path.join(ROOT, ".cuda-nvrtc", "nvidia", "cuda_nvrtc", "bin")
        if os.path.isdir(d):
            env["PATH"] = d + os.pathsep + env.get("PATH", "")
        cuda = env.get("CUDA_PATH")
        if cuda and os.path.isdir(os.path.join(cuda, "bin")):
            env["PATH"] = os.path.join(cuda, "bin") + os.pathsep + env["PATH"]
    else:
        for d in (os.path.expanduser("~/.local/cuda-nvrtc/nvidia/cuda_nvrtc/lib"), "/usr/local/cuda/lib64"):
            if os.path.isdir(d):
                env["LD_LIBRARY_PATH"] = d + os.pathsep + env.get("LD_LIBRARY_PATH", "")
    return env


class ToolError(RuntimeError):
    """solve-cli itself failed: a problem on this machine, not in the upload."""


def verify_file(cli, path, sample):
    """Run solve-cli datagen verify on a plain .jsonl file; returns the summary dict."""
    proc = subprocess.run([cli, "datagen", "verify", path, "--sample", str(sample)],
                          capture_output=True, text=True, env=cuda_env())
    lines = [l for l in proc.stdout.splitlines() if l.startswith("{")]
    if not lines:
        raise ToolError(
            "solve-cli crashed while verifying (exit code %s): %s\n"
            "On a GPU build, install the CUDA runtime compiler as in the README "
            "(or set SOLVER_GPU=0 to re-solve on the CPU)." % (proc.returncode, proc.stderr.strip()[-400:]))
    return json.loads(lines[-1])


def check_job(cli, login, job, local_jsonl, sample):
    errors = []
    base = block_base(cli, login)
    if not (base <= job < base + BLOCK):
        errors.append(f"job {job} is outside {login}'s block")
    summary = verify_file(cli, local_jsonl, sample)
    if summary.get("contributor") not in (None, login):
        errors.append(f"header contributor {summary.get('contributor')!r} does not match folder {login!r}")
    if summary.get("job") not in (None, job):
        errors.append(f"header job {summary.get('job')} does not match file name {job}")
    errors += summary.get("errors", [])
    return errors, summary


def run_local(args):
    total, bad = 0, 0
    for dirpath, _, files in os.walk(args.local):
        for name in sorted(files):
            m = re.match(r"^job-(\d+)\.jsonl$", name)
            if not m:
                continue
            login = os.path.basename(dirpath)
            path = os.path.join(dirpath, name)
            errors, summary = check_job(args.solve_cli, login, int(m.group(1)), path, args.sample)
            diffs = ", ".join(f"#{r['index']} mean {r['mean_abs_diff']:.4f} max {r['max_abs_diff']:.4f}"
                              for r in summary.get("resolved", []))
            status = "ok " if not errors else "BAD"
            print(f"{status} {login}/{name}: {summary.get('examples', 0)} examples  {diffs}")
            for e in errors:
                print(f"     {e}")
            total += 1
            bad += bool(errors)
    print(f"{total} job files, {bad} failed")
    return bad == 0


def load_progress(api, repo):
    from huggingface_hub import hf_hub_download
    try:
        p = hf_hub_download(repo, "progress.json", repo_type="dataset", force_download=True)
        with open(p) as f:
            return json.load(f)
    except Exception:
        return {"format": "gtopen-leaf-values-progress", "events": []}


def save_progress(api, repo, progress, message):
    cfg = load_config()
    events = progress["events"]
    progress["total_examples"] = sum(e["examples"] for e in events)
    progress["total_jobs"] = sum(e["jobs"] for e in events)
    by = {}
    for e in events:
        by[e["contributor"]] = by.get(e["contributor"], 0) + e["examples"]
    progress["contributors"] = dict(sorted(by.items(), key=lambda kv: -kv[1]))
    progress["go_no_go_examples"] = cfg["go_no_go_examples"]
    progress["goal_examples"] = cfg["goal_examples"]
    progress["updated"] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    data = json.dumps(progress, indent=1).encode()
    api.upload_file(path_or_fileobj=data, path_in_repo="progress.json", repo_id=repo,
                    repo_type="dataset", commit_message=message)


def publish_graph(progress):
    """Redraw the GitHub progress graph now and push it to the datagen-progress
    branch, as the scheduled GitHub Action does. GitHub often skips scheduled
    runs for hours, so the validator publishes right after each merge with this
    machine's git credentials. Best effort: a failure only prints a warning."""
    sys.path.insert(0, HERE)
    import progress_chart
    git = ["git", "-c", "user.name=datagen validator",
           "-c", "user.email=datagen-validator@users.noreply.github.com"]
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
    stage = tempfile.mkdtemp(prefix="gtopen-graph-")
    try:
        url = subprocess.run(["git", "remote", "get-url", "origin"], cwd=ROOT, capture_output=True,
                             text=True, check=True).stdout.strip()
        m = re.search(r"github\.com[:/]+([^/]+/[^/]+?)(?:\.git)?/?$", url)
        if not m:
            raise RuntimeError(f"origin {url!r} is not a GitHub repository")
        slug = m.group(1)
        cfg = load_config()
        def out(name):
            return open(os.path.join(stage, name), "w", encoding="utf-8", newline="\n")  # same bytes as the Action
        with out("progress.svg") as f:
            f.write(progress_chart.render_svg(progress, cfg))
        with out("contributors.md") as f:
            f.write(progress_chart.render_table(progress))
        with out("progress.json") as f:
            json.dump(progress, f, indent=1)
        with out("README.md") as f:
            f.write("# Value-net training data progress\n\n"
                    "Generated automatically from the dataset's `progress.json` (by `tools/datagen/validate.py` "
                    "after each merge, and by `.github/workflows/datagen-progress.yml`). See\n"
                    f"[docs/contribute-compute.md](https://github.com/{slug}/blob/master/docs/contribute-compute.md).\n\n"
                    "![Progress](progress.svg)\n\n[Contributors](contributors.md)\n")
        stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
        for cmd in (["init", "-q", "-b", "datagen-progress"], ["add", "-A"],
                    ["commit", "-q", "-m", f"Progress graph {stamp}"],
                    ["push", "-q", "--force", url, "datagen-progress"]):
            proc = subprocess.run(git + cmd, cwd=stage, capture_output=True, text=True, env=env, timeout=120)
            if proc.returncode:
                raise RuntimeError(f"git {cmd[0]} failed: {(proc.stderr or proc.stdout).strip()[-300:]}")
        print(f"GitHub graph updated: https://github.com/{slug}/tree/datagen-progress")
    except Exception as err:
        print(f"   could not update the GitHub graph (the scheduled Action will catch up): {err}")
    finally:
        # git marks its object files read-only, which stops rmtree on Windows
        retry = lambda fn, path, _: (os.chmod(path, 0o700), fn(path))
        shutil.rmtree(stage, **({"onexc": retry} if sys.version_info >= (3, 12) else {"onerror": retry}))


def tree_oids(api, repo, revision=None):
    """path -> blob id for every file at a revision."""
    out = {}
    for item in api.list_repo_tree(repo, repo_type="dataset", recursive=True, revision=revision):
        blob = getattr(item, "blob_id", None)
        if blob is not None:
            out[item.path] = blob
    return out


def pr_diff(api, repo, num):
    """A pull request's diff text. The Hub may leave it out of the discussion
    details and serve it separately at .../discussions/N/files.diff."""
    details = api.get_discussion_details(repo, num, repo_type="dataset")
    if details.diff:
        return details.diff
    import urllib.request
    from huggingface_hub.utils import build_hf_headers
    url = f"{api.endpoint}/datasets/{repo}/discussions/{num}/files.diff"
    req = urllib.request.Request(url, headers=build_hf_headers(token=api.token))
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8", "replace")


def pr_changes(api, repo, num):
    """(added paths, other touched paths) from a pull request's diff."""
    diff = pr_diff(api, repo, num)
    added, other, path, is_new = [], [], None, False

    def flush():
        if path is not None:
            (added if is_new else other).append(path)

    for line in diff.splitlines():
        if line.startswith("diff --git "):
            flush()
            path = line.split(" b/", 1)[1] if " b/" in line else line
            is_new = False
        elif line.startswith("new file mode"):
            is_new = True
    flush()
    return added, other


def merge_time(api, repo, num):
    """When a dataset pull request was merged (UTC ISO), from its event log."""
    details = api.get_discussion_details(repo, num, repo_type="dataset")
    when = None
    for ev in details.events:
        if getattr(ev, "type", None) == "status-change" and getattr(ev, "new_status", None) == "merged":
            when = ev.created_at
        elif when is None and getattr(ev, "type", None) == "comment" and \
                str(getattr(ev, "content", "")).startswith("Validated "):
            when = ev.created_at  # the validator's merge comment, posted as it merges
    if when is None:
        return None
    if when.tzinfo is None:
        when = when.replace(tzinfo=datetime.timezone.utc)
    return when.astimezone(datetime.timezone.utc).isoformat(timespec="seconds")


def backfill_times(api, repo, progress):
    """Give older progress entries (date only) the exact time their PR was merged."""
    cache, filled = {}, 0
    for e in progress.get("events", []):
        if e.get("time") or "pr" not in e:
            continue
        if e["pr"] not in cache:
            try:
                cache[e["pr"]] = merge_time(api, repo, e["pr"])
            except Exception as err:
                print(f"   could not read the merge time of PR #{e['pr']}: {err}")
                cache[e["pr"]] = None
        if cache[e["pr"]]:
            e["time"] = cache[e["pr"]]
            filled += 1
    return filled


def run_prs(args):
    from huggingface_hub import HfApi, hf_hub_download
    api = HfApi()
    repo = args.repo
    main_oids = tree_oids(api, repo)
    prs = [d for d in api.get_repo_discussions(repo, repo_type="dataset", discussion_type="pull_request",
                                               discussion_status="open")]
    print(f"{repo}: {len(prs)} open pull requests")
    merged_events = []
    try:
        for pr in prs:
            rev = f"refs/pr/{pr.num}"
            new, other = pr_changes(api, repo, pr.num)
            errors, jobs = [], []
            other += [p for p in new if p in main_oids]  # "new" file already in main: a duplicate
            new = [p for p in new if p not in main_oids]
            if other:
                errors.append("changes or deletes existing files: " + ", ".join(sorted(other)[:10]))
            stage = tempfile.mkdtemp(prefix="gtopen-validate-")
            try:
                if not new:
                    errors.append("no new files")
                for path in new:
                    m = PATH_RE.match(path)
                    if not m:
                        errors.append(f"unexpected file {path} (only data/<login>/job-<n>.jsonl.gz)")
                        continue
                    login, job = m.group(1), int(m.group(2))
                    gz = hf_hub_download(repo, path, repo_type="dataset", revision=rev, cache_dir=stage)
                    plain = os.path.join(stage, f"job-{job}.jsonl")
                    with gzip.open(gz, "rb") as src, open(plain, "wb") as dst:
                        shutil.copyfileobj(src, dst)
                    errs, summary = check_job(args.solve_cli, login, job, plain, args.sample)
                    errors += [f"{path}: {e}" for e in errs]
                    jobs.append((login, job, summary.get("examples", 0)))
            finally:
                shutil.rmtree(stage, ignore_errors=True)
            logins = sorted({j[0] for j in jobs})
            examples = sum(j[2] for j in jobs)
            if errors:
                print(f"PR #{pr.num} ({pr.title}): REJECT")
                for e in errors[:20]:
                    print(f"   {e}")
                if not args.dry_run:
                    body = "Thanks for contributing! The validator could not accept this upload:\n\n" + \
                           "\n".join(f"- {e}" for e in errors[:30]) + \
                           "\n\nPlease update GTOpen (git pull, rebuild) and run the generator again. " \
                           "See docs/contribute-compute.md."
                    api.comment_discussion(repo, pr.num, body, repo_type="dataset")
                    api.change_discussion_status(repo, pr.num, "closed", repo_type="dataset")
                continue
            print(f"PR #{pr.num} ({pr.title}): OK, {len(jobs)} jobs, {examples} examples")
            if args.dry_run:
                continue
            api.merge_pull_request(repo, pr.num, repo_type="dataset",
                                   comment=f"Validated {len(jobs)} jobs ({examples} examples). Thank you!")
            main_oids.update({p: "" for p in new})
            now = datetime.datetime.now(datetime.timezone.utc)
            for login in logins:
                mine = [j for j in jobs if j[0] == login]
                merged_events.append({"date": now.date().isoformat(), "time": now.isoformat(timespec="seconds"),
                                      "contributor": login, "jobs": len(mine),
                                      "examples": sum(j[2] for j in mine), "pr": pr.num})
    finally:
        # record merges even when a later pull request fails, so none go uncounted
        failed = sys.exc_info()[0] is not None
        if merged_events or (not args.dry_run and not failed):
            progress = load_progress(api, repo)
            filled = 0 if args.dry_run or failed else backfill_times(api, repo, progress)
            progress["events"] += merged_events
            n = sum(e["examples"] for e in merged_events)
            if merged_events:
                save_progress(api, repo, progress, f"progress: +{n} examples")
                print(f"progress.json updated: +{n} examples")
            elif filled:
                save_progress(api, repo, progress, f"progress: merge times for {filled} older entries")
            if filled:
                print(f"progress.json: added merge times to {filled} older entries")
            if (merged_events or filled) and args.publish_graph:
                publish_graph(progress)


def main():
    try:
        real_main()
    except ToolError as e:
        sys.exit(f"stopped, nothing was merged or rejected: {e}")


def real_main():
    cfg = load_config()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=cfg["hf_repo"])
    ap.add_argument("--solve-cli", default=default_cli())
    ap.add_argument("--sample", type=int, default=3, help="examples re-solved per job")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-graph", dest="publish_graph", action="store_false",
                    help="don't push the progress graph to GitHub after merging")
    ap.add_argument("--local", help="check job files in a local folder instead of pull requests")
    ap.add_argument("--watch", type=float, default=0, help="repeat every N minutes")
    args = ap.parse_args()
    if not os.path.exists(args.solve_cli):
        sys.exit(f"{args.solve_cli} not found: build it with  cargo build --release -p solver --features gpu --bin solve-cli")
    if args.local:
        sys.exit(0 if run_local(args) else 2)
    while True:
        try:
            run_prs(args)
        except ToolError:
            raise
        except Exception as e:
            if args.watch <= 0:
                raise
            # a network or Hub hiccup must not end an overnight run
            print(f"pass failed, will retry in {args.watch:g} min: {type(e).__name__}: {e}", flush=True)
        if args.watch <= 0:
            break
        time.sleep(args.watch * 60)


if __name__ == "__main__":
    main()
