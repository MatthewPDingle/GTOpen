#!/usr/bin/env python3
"""Maintainer tool: check pooled uploads, merge the good ones, track progress.

For every open pull request on the dataset it downloads the new job files,
checks each one with `solve-cli datagen verify` (header, regenerated inputs,
sanity, and a re-solve of a few examples), then merges the pull request or
closes it with the errors. Each merge is written to progress.json in the
dataset straight away (the GitHub progress graph reads it), and every pass
first adds any merged pull request that progress.json does not hold yet, so a
validator that was closed part-way through leaves nothing uncounted.

    python tools/datagen/validate.py                      # all open PRs
    python tools/datagen/validate.py --dry-run            # check, don't merge
    python tools/datagen/validate.py --local datagen_out  # check local files only
    python tools/datagen/validate.py --watch 60           # every hour
    python tools/datagen/validate.py --recount            # only add merges missing from progress.json

Besides pooled jobs (data/<login>/job-<n>.jsonl.gz, inputs regenerated from the
job number) it accepts real-range game files (real/<login>/<set>/<game>.jsonl.gz:
exact flop solves of the ranges a GTOpen preflop solve produced, from
`tools/leafnet/realrange.py publish`). Their inputs cannot be regenerated, so
they are taken only from the logins in config.json's real_contributors, checked
for plausibility, and a sample is re-solved like any other upload
(--real-max-vram keeps the biggest trees off a shared GPU).

What pooled jobs are drawn from is a published "game mix" (tools/datagen/mixes.json
on the master branch). solve-cli reads that list itself while checking, so a new
mix needs no update or restart here. --publish-situations puts a situation list
(from `solve-cli datagen situations`) into the dataset for a mix to draw from.

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
REAL_PATH_RE = re.compile(r"^real/([A-Za-z0-9_-]+)/([A-Za-z0-9_-]+)/([A-Za-z0-9_-]+)\.jsonl\.gz$")
REAL_FORMAT = "gtopen-real-range"
BLOCK = 1 << 24
MIX_SHIFT = 44  # a job number of generator v5 on: its game mix above this bit, a number of the block below
EXIT_LATER = 3  # solve-cli datagen verify: this machine cannot check the file right now
SITUATIONS_NAME_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


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
    # where solve-cli remembers the published game mixes, wherever this script is started from
    env.setdefault("GTOPEN_MIX_DIR", os.path.join(ROOT, "datagen_out", ".mix"))
    return env


class ToolError(RuntimeError):
    """solve-cli itself failed: a problem on this machine, not in the upload."""


def verify_file(cli, path, sample, max_vram=None):
    """Run solve-cli datagen verify on a plain .jsonl file; returns the summary dict."""
    cmd = [cli, "datagen", "verify", path, "--sample", str(sample)]
    if max_vram:
        cmd += ["--max-vram", str(max_vram)]
    proc = subprocess.run(cmd, capture_output=True, text=True, env=cuda_env())
    lines = [l for l in proc.stdout.splitlines() if l.startswith("{")]
    if proc.returncode == EXIT_LATER:
        # nothing wrong with the upload: its game mix could not be read here (no network, or a mix that
        # needs a newer build). Nothing is merged or rejected, and the next pass tries again.
        raise ToolError(proc.stderr.strip()[-400:] or "solve-cli could not check the file right now")
    if not lines:
        raise ToolError(
            "solve-cli crashed while verifying (exit code %s): %s\n"
            "On a GPU build, install the CUDA runtime compiler as in the README "
            "(or set SOLVER_GPU=0 to re-solve on the CPU)." % (proc.returncode, proc.stderr.strip()[-400:]))
    return json.loads(lines[-1])


def check_job(cli, login, job, local_jsonl, sample):
    errors = []
    base = block_base(cli, login)
    if not (base <= job % (1 << MIX_SHIFT) < base + BLOCK):
        errors.append(f"job {job} is outside {login}'s block")
    summary = verify_file(cli, local_jsonl, sample)
    if summary.get("contributor") not in (None, login):
        errors.append(f"header contributor {summary.get('contributor')!r} does not match folder {login!r}")
    if summary.get("job") not in (None, job):
        errors.append(f"header job {summary.get('job')} does not match file name {job}")
    errors += summary.get("errors", [])
    return errors, summary


def generator_of(local_jsonl):
    """The generator version in a pooled job file's header line (None if unreadable)."""
    try:
        with open(local_jsonl, encoding="utf-8") as f:
            return json.loads(f.readline()).get("generator_version")
    except (OSError, ValueError, AttributeError):
        return None


def update_note(versions, current):
    """A friendly request to update, for jobs made with an older generator that is still accepted."""
    older = sorted({v for v in versions if isinstance(v, int) and current and v < current})
    if not older:
        return ""
    made = " and ".join(f"v{v}" for v in older)
    return (f"\n\nThese jobs were made with generator {made}. They are merged and count in full. "
            f"Generator v{current} is out now: from it on, your generator moves to each new mix of games "
            "by itself, so this is the last update you need to make by hand for one. When it suits "
            "you, please update GTOpen (git pull, rebuild) and restart the generator. "
            "See docs/contribute-compute.md.")


def is_game_file(path):
    """True for a real-range game file (plain .jsonl), by its header."""
    try:
        with open(path, encoding="utf-8") as f:
            head = json.loads(f.readline())
    except (OSError, ValueError):
        return False
    return isinstance(head, dict) and head.get("format") == REAL_FORMAT


def check_game(cli, login, set_name, game, local_jsonl, sample, max_vram=None, allowed=None):
    """Check one real-range game file against where it sits (real/<login>/<set>/<game>)."""
    errors = []
    if allowed is not None and login not in allowed:
        errors.append(f"real-range files are accepted from {', '.join(sorted(allowed)) or 'nobody'} only for now "
                      f"(their ranges cannot be regenerated from a job number), not from {login}")
        return errors, {}
    summary = verify_file(cli, local_jsonl, sample, max_vram)
    if summary.get("kind") != "real":
        errors.append("not a real-range game file")
    for key, want in (("contributor", login), ("set", set_name), ("game", game)):
        if summary.get(key) != want:
            errors.append(f"header {key} {summary.get(key)!r} does not match the path ({want!r})")
    errors += summary.get("errors", [])
    return errors, summary


def run_local(args):
    total, bad = 0, 0
    for dirpath, _, files in os.walk(args.local):
        for name in sorted(files):
            path = os.path.join(dirpath, name)
            if name.endswith(".jsonl") and not name.startswith("job-") and is_game_file(path):
                # real/<login>/<set>/<game>.jsonl as realrange.py publish writes it
                set_name = os.path.basename(dirpath)
                login = os.path.basename(os.path.dirname(dirpath))
                errors, summary = check_game(args.solve_cli, login, set_name, name[:-len(".jsonl")], path,
                                             args.sample, args.real_max_vram)
                diffs = ", ".join(f"#{r['index']} mean {r['mean_abs_diff']:.4f} max {r['max_abs_diff']:.4f}"
                                  for r in summary.get("resolved", []))
                print(f"{'ok ' if not errors else 'BAD'} real {login}/{set_name}/{name}: "
                      f"{summary.get('examples', 0)} examples  {diffs}")
                for e in errors:
                    print(f"     {e}")
                total += 1
                bad += bool(errors)
                continue
            m = re.match(r"^job-(\d+)\.jsonl$", name)
            if not m:
                continue
            login = os.path.basename(dirpath)
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


def rate_limit_wait(err):
    """Seconds to wait when err is the Hub answering "too many requests" (HTTP 429), else None.
    The Hub counts requests in five-minute windows and says in its RateLimit header (t=seconds)
    when the window ends."""
    resp = getattr(err, "response", None)
    if 429 not in (getattr(err, "code", None), getattr(resp, "status_code", None)):
        return None
    headers = getattr(resp, "headers", None) or getattr(err, "headers", None) or {}
    headers = {str(k).lower(): str(v) for k, v in headers.items()}
    m = re.search(r"\bt=(\d+)", headers.get("ratelimit", ""))
    after = headers.get("retry-after", "")
    wait = int(m.group(1)) if m else int(after) if after.isdigit() else 60
    return min(max(wait, 1) + 5, 330)


def patiently(fn, *args, **kwargs):
    """Call fn; when the Hub says "too many requests", wait as long as it asks and call again."""
    for attempt in range(6):
        try:
            return fn(*args, **kwargs)
        except Exception as err:
            wait = rate_limit_wait(err)
            if wait is None or attempt == 5:
                raise
            print(f"   Hugging Face asked for a pause (too many requests): carrying on in {wait} s", flush=True)
            time.sleep(wait)


def load_progress(api, repo):
    """progress.json from the dataset; an empty one only when the dataset has none yet.
    Any other failure is raised: a network blip must never start the count again from nothing."""
    from huggingface_hub import hf_hub_download
    try:
        from huggingface_hub.errors import RemoteEntryNotFoundError as Missing
    except ImportError:  # older huggingface_hub
        from huggingface_hub.utils import EntryNotFoundError as Missing
    try:
        p = hf_hub_download(repo, "progress.json", repo_type="dataset", force_download=True)
    except Missing:
        return {"format": "gtopen-leaf-values-progress", "events": []}
    with open(p) as f:
        return json.load(f)


def save_progress(api, repo, progress, message):
    cfg = load_config()
    events = progress["events"]
    progress["total_examples"] = sum(e["examples"] for e in events)
    progress["total_jobs"] = sum(e["jobs"] for e in events)
    by = {}
    for e in events:
        by[e["contributor"]] = by.get(e["contributor"], 0) + e["examples"]
    progress["contributors"] = dict(sorted(by.items(), key=lambda kv: -kv[1]))
    progress["real_examples"] = sum(e["examples"] for e in events if e.get("kind") == "real")
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


NOTES_BEGIN, NOTES_END = "<!-- real-range notes: begin -->", "<!-- real-range notes: end -->"


def card_with_notes(card, section):
    """The dataset card with the real-range section put in (or replaced, if an earlier run put one in)."""
    block = f"{NOTES_BEGIN}\n{section.strip()}\n{NOTES_END}"
    if NOTES_BEGIN in card and NOTES_END in card:
        a, b = card.index(NOTES_BEGIN), card.index(NOTES_END) + len(NOTES_END)
        return card[:a] + block + card[b:]
    return card.rstrip("\n") + "\n\n" + block + "\n"


def publish_notes(args):
    """Put the real-range notes into the dataset: real/README.md, and a section of the dataset card."""
    from huggingface_hub import HfApi, hf_hub_download
    api = HfApi()
    with open(os.path.join(HERE, "dataset_real_readme.md"), encoding="utf-8") as f:
        readme = f.read()
    with open(os.path.join(HERE, "dataset_card_section.md"), encoding="utf-8") as f:
        section = f.read()
    with open(hf_hub_download(args.repo, "README.md", repo_type="dataset", force_download=True), encoding="utf-8") as f:
        card = f.read()
    new_card = card_with_notes(card, section)
    if args.dry_run:
        print(new_card)
        print(f"--- dry run: {args.repo} was not changed (real/README.md would be {len(readme)} characters)")
        return
    api.upload_file(path_or_fileobj=readme.encode(), path_in_repo="real/README.md", repo_id=args.repo,
                    repo_type="dataset", commit_message="Describe the real-range game files")
    if new_card != card:
        api.upload_file(path_or_fileobj=new_card.encode(), path_in_repo="README.md", repo_id=args.repo,
                        repo_type="dataset", commit_message="Dataset card: real-range game files")
    print(f"{args.repo}: real/README.md written, dataset card {'updated' if new_card != card else 'already up to date'}")


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


TITLE_RE = re.compile(r"^([A-Za-z0-9_-]+): (\d+) (jobs|real-range games), (\d+) examples$")
VALIDATED_RE = re.compile(r"^Validated (\d+) jobs \((\d+) examples\)")
GRAPH_EVERY_S = 600  # during a long pass, redraw the GitHub graph at most this often
RETRY_MIN = 5        # after a failed pass in --watch mode, try again this many minutes later


def record_merges(api, repo, events, message):
    """Add merge events to progress.json now, skipping pull requests it already holds.
    Returns the progress as saved (or as read, when there was nothing to add)."""
    progress = load_progress(api, repo)
    have = {e.get("pr") for e in progress["events"]}
    new = [e for e in events if e.get("pr") not in have]
    if new:
        progress["events"] += new
        save_progress(api, repo, progress, message)
    return progress


def header_examples(api, repo, path):
    """How many examples a job or game file on main holds (from its header, else by counting)."""
    from huggingface_hub import hf_hub_download
    stage = tempfile.mkdtemp(prefix="gtopen-recount-")
    try:
        gz = hf_hub_download(repo, path, repo_type="dataset", cache_dir=stage)
        with gzip.open(gz, "rt", encoding="utf-8") as f:
            head = json.loads(f.readline())
            if isinstance(head.get("examples"), int):
                return head["examples"]
            return sum(1 for line in f if json.loads(line).get("type") == "example")
    finally:
        shutil.rmtree(stage, ignore_errors=True)


def merged_pr_events(api, repo, pr):
    """The progress events for a pull request that was merged but never counted.

    Who is credited comes from the folders of the files it added; how much
    comes from the validator's own merge comment (only a comment by the account
    that merged it counts), or else from the files' headers on main. If the
    Hub no longer serves the diff, the pull request's title is used, but only
    when the validator's comment gives the same numbers."""
    details = api.get_discussion_details(repo, pr.num, repo_type="dataset")
    merged = [ev for ev in details.events if getattr(ev, "type", None) == "status-change"
              and getattr(ev, "new_status", None) == "merged"]
    if not merged:
        raise RuntimeError("no merge event in its log")
    when, merger = merged[-1].created_at, getattr(merged[-1], "author", None)
    if when.tzinfo is None:
        when = when.replace(tzinfo=datetime.timezone.utc)
    when = when.astimezone(datetime.timezone.utc)
    said = None  # (jobs, examples) in the validator's merge comment
    for ev in details.events:
        m = VALIDATED_RE.match(str(getattr(ev, "content", ""))) if getattr(ev, "type", None) == "comment" else None
        if m and merger is not None and getattr(ev, "author", None) == merger:
            said = (int(m.group(1)), int(m.group(2)))
    groups = {}  # (login, kind) -> [paths]
    try:
        added, other = pr_changes(api, repo, pr.num)
    except Exception as err:
        if rate_limit_wait(err) is not None:
            raise  # asked to slow down: the caller waits and reads this pull request again
        added, other = [], []
    for path in added + other:  # it was merged, so the validator saw that it only adds files
        m, real = PATH_RE.match(path), REAL_PATH_RE.match(path)
        if m or real:
            groups.setdefault(((m or real).group(1), "real" if real else "pool"), []).append(path)
    counts = {}  # (login, kind) -> (jobs, examples)
    if len(groups) == 1 and said and said[0] == len(next(iter(groups.values()))):
        counts[next(iter(groups))] = said
    elif groups:
        for key, paths in groups.items():
            counts[key] = (len(paths), sum(header_examples(api, repo, p) for p in paths))
    else:
        t = TITLE_RE.match(pr.title or "")
        if not (t and said == (int(t.group(2)), int(t.group(4)))):
            raise RuntimeError("its files could not be listed and its title does not match the validator's comment")
        counts[(t.group(1), "real" if t.group(3) != "jobs" else "pool")] = said
    events = []
    for (login, kind), (jobs, examples) in sorted(counts.items()):
        event = {"date": when.date().isoformat(), "time": when.isoformat(timespec="seconds"),
                 "contributor": login, "jobs": jobs, "examples": examples, "pr": pr.num}
        if kind == "real":
            event["kind"] = "real"
        events.append(event)
    return events


def recount(api, repo, dry_run=False):
    """Add every merged pull request that progress.json does not hold (a validator
    that was closed part-way through a pass used to leave its merges uncounted).
    Also drops a merge that was written twice. Returns the progress when it changed, else None."""
    progress = load_progress(api, repo)
    seen, once = set(), []
    for e in progress["events"]:  # the same merge written twice (two validators at once) counts once
        key = (e.get("pr"), e["contributor"], e.get("kind"))
        if "pr" not in e or key not in seen:
            once.append(e)
        seen.add(key)
    repeats = len(progress["events"]) - len(once)
    if repeats:
        print(f"progress.json holds {repeats} merges twice: {'would drop' if dry_run else 'dropping'} the repeats")
        if not dry_run:
            progress["events"] = once
            save_progress(api, repo, progress, f"progress: {repeats} merges were counted twice")
    have = {e.get("pr") for e in once}
    missing = [d for d in api.get_repo_discussions(repo, repo_type="dataset", discussion_type="pull_request",
                                                    discussion_status="all")
               if getattr(d, "status", None) == "merged" and d.num not in have]
    if not missing:
        return progress if repeats and not dry_run else None
    events = []
    for pr in sorted(missing, key=lambda d: d.num):
        try:
            found = patiently(merged_pr_events, api, repo, pr)
        except Exception as err:
            print(f"   PR #{pr.num} is merged but not counted, and could not be read: {err}")
            continue
        events += found
        for e in found:
            print(f"   PR #{pr.num}: merged {e['time']} but not counted: {e['contributor']}, "
                  f"{e['jobs']} jobs, {e['examples']} examples")
    n = sum(e["examples"] for e in events)
    print(f"{len(missing)} merged pull requests were missing from progress.json: "
          f"{'would add' if dry_run else 'adding'} {n} examples")
    if dry_run or not events:
        return progress if repeats and not dry_run else None
    return record_merges(api, repo, events, f"progress: +{n} examples from earlier merges")


def run_prs(args):
    from huggingface_hub import HfApi, hf_hub_download
    api = HfApi()
    repo = args.repo
    cfg = load_config()
    drawn = [None, 0.0]  # the progress to draw next, and when the graph was last pushed

    def graph(progress=None, force=False):
        if progress is not None:
            drawn[0] = progress
        if args.publish_graph and drawn[0] is not None and (force or time.time() - drawn[1] >= GRAPH_EVERY_S):
            publish_graph(drawn[0])
            drawn[:] = [None, time.time()]

    try:
        graph(recount(api, repo, args.dry_run))
    except Exception as err:
        print(f"   could not look for uncounted merges (will try again next pass): {type(err).__name__}: {err}")
    main_oids = tree_oids(api, repo)
    prs = [d for d in api.get_repo_discussions(repo, repo_type="dataset", discussion_type="pull_request",
                                               discussion_status="open")]
    print(f"{repo}: {len(prs)} open pull requests")
    current = cfg.get("current_generator")
    try:
        for pr in prs:
            rev = f"refs/pr/{pr.num}"
            new, other = patiently(pr_changes, api, repo, pr.num)
            errors, jobs, versions = [], [], []
            other += [p for p in new if p in main_oids]  # "new" file already in main: a duplicate
            new = [p for p in new if p not in main_oids]
            if other:
                errors.append("changes or deletes existing files: " + ", ".join(sorted(other)[:10]))
            stage = tempfile.mkdtemp(prefix="gtopen-validate-")
            try:
                if not new:
                    errors.append("no new files")
                for n, path in enumerate(new):
                    m, real = PATH_RE.match(path), REAL_PATH_RE.match(path)
                    if not m and not real:
                        errors.append(f"unexpected file {path} (only data/<login>/job-<n>.jsonl.gz "
                                      "and real/<login>/<set>/<game>.jsonl.gz)")
                        continue
                    gz = patiently(hf_hub_download, repo, path, repo_type="dataset", revision=rev, cache_dir=stage)
                    plain = os.path.join(stage, f"file-{n}.jsonl")
                    with gzip.open(gz, "rb") as src, open(plain, "wb") as dst:
                        shutil.copyfileobj(src, dst)
                    if real:
                        login = real.group(1)
                        errs, summary = check_game(args.solve_cli, login, real.group(2), real.group(3), plain,
                                                   args.sample, args.real_max_vram, set(cfg.get("real_contributors", [])))
                        jobs.append((login, "real", summary.get("examples", 0)))
                    else:
                        login, job = m.group(1), int(m.group(2))
                        errs, summary = check_job(args.solve_cli, login, job, plain, args.sample)
                        jobs.append((login, "pool", summary.get("examples", 0)))
                        versions.append(generator_of(plain))
                    errors += [f"{path}: {e}" for e in errs]
            finally:
                shutil.rmtree(stage, ignore_errors=True)
            groups = sorted({(j[0], j[1]) for j in jobs})
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
            note = update_note(versions, current)
            print(f"PR #{pr.num} ({pr.title}): OK, {len(jobs)} jobs, {examples} examples"
                  + (" (older generator: asked to update)" if note else ""))
            if args.dry_run:
                continue
            api.merge_pull_request(repo, pr.num, repo_type="dataset",
                                   comment=f"Validated {len(jobs)} jobs ({examples} examples). Thank you!" + note)
            main_oids.update({p: "" for p in new})
            now = datetime.datetime.now(datetime.timezone.utc)
            events = []
            for login, kind in groups:
                mine = [j for j in jobs if (j[0], j[1]) == (login, kind)]
                event = {"date": now.date().isoformat(), "time": now.isoformat(timespec="seconds"),
                         "contributor": login, "jobs": len(mine),
                         "examples": sum(j[2] for j in mine), "pr": pr.num}
                if kind == "real":
                    event["kind"] = "real"  # jobs = game files here
                events.append(event)
            # Count it now: a validator closed part-way through a pass must not leave merges uncounted.
            try:
                graph(patiently(record_merges, api, repo, events, f"progress: +{examples} examples"))
                print(f"progress.json updated: +{examples} examples")
            except Exception as err:
                print(f"   merged, but progress.json could not be written (the next pass adds it): "
                      f"{type(err).__name__}: {err}")
    finally:
        failed = sys.exc_info()[0] is not None
        if not args.dry_run and not failed:
            try:
                progress = load_progress(api, repo)
                filled = backfill_times(api, repo, progress)
                if filled:
                    save_progress(api, repo, progress, f"progress: merge times for {filled} older entries")
                    print(f"progress.json: added merge times to {filled} older entries")
                    graph(progress)
            except Exception as err:
                print(f"   could not check older entries' merge times: {type(err).__name__}: {err}")
        graph(force=True)


def main():
    try:
        real_main()
    except ToolError as e:
        sys.exit(f"stopped, nothing was merged or rejected: {e}")


def publish_situations(args):
    """Put a situation list (from `solve-cli datagen situations`) into the dataset as situations/<list>.jsonl."""
    import hashlib
    with open(args.publish_situations, "rb") as f:
        data = f.read()
    try:
        head = json.loads(data.split(b"\n", 1)[0])
    except ValueError:
        head = {}
    name = head.get("list") if isinstance(head, dict) else None
    if head.get("format") != "gtopen-situations" or not isinstance(name, str) or not SITUATIONS_NAME_RE.match(name):
        sys.exit(f"{args.publish_situations} is not a situation list (make it with  solve-cli datagen situations)")
    sha = hashlib.sha256(data).hexdigest()
    path = f"situations/{name}.jsonl"
    part = json.dumps({"kind": "situations", "share": 0.5, "list": name, "sha256": sha})
    if args.dry_run:
        print(f"--- dry run: {args.repo} was not changed ({path} would be {len(data)} bytes, "
              f"{head.get('situations')} situations)")
    else:
        from huggingface_hub import HfApi
        api = HfApi()
        if api.file_exists(args.repo, path, repo_type="dataset"):
            # a mix names a list by its exact bytes: a changed file would stop every generator on that mix
            sys.exit(f"{args.repo} already has {path}: a published list is never changed. Give the new one another name.")
        api.upload_file(path_or_fileobj=data, path_in_repo=path, repo_id=args.repo, repo_type="dataset",
                        commit_message=f"Situation list {name} ({head.get('situations')} situations)")
        print(f"{args.repo}: {path} written")
    print("the part for a new mix in tools/datagen/mixes.json (set the share):")
    print(part)


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
    ap.add_argument("--recount", action="store_true",
                    help="add merged pull requests that progress.json does not hold yet and stop (every "
                         "pass does this first anyway); with --dry-run, only list them")
    ap.add_argument("--real-max-vram", type=float, default=0, metavar="GB",
                    help="in real-range game files, re-solve only trees estimated to fit this much GPU memory "
                         "(0 = any size); a file with no such tree is rejected")
    ap.add_argument("--publish-notes", action="store_true",
                    help="write the real-range notes into the dataset (real/README.md and a section of the "
                         "dataset card) and stop; with --dry-run, print the card instead")
    ap.add_argument("--publish-situations", metavar="FILE",
                    help="put a situation list (from `solve-cli datagen situations`) into the dataset as "
                         "situations/<list>.jsonl and stop; with --dry-run, only check it")
    args = ap.parse_args()
    if args.publish_notes:
        return publish_notes(args)
    if args.publish_situations:
        return publish_situations(args)
    if args.recount:
        from huggingface_hub import HfApi
        progress = recount(HfApi(), args.repo, args.dry_run)
        if progress is None:
            print("nothing added to progress.json")
        elif args.publish_graph:
            publish_graph(progress)
        return
    if not os.path.exists(args.solve_cli):
        sys.exit(f"{args.solve_cli} not found: build it with  cargo build --release -p solver --features gpu --bin solve-cli")
    if args.local:
        sys.exit(0 if run_local(args) else 2)
    while True:
        retry = None  # minutes until the next pass, when this one fails
        try:
            run_prs(args)
        except ToolError as e:
            if args.watch <= 0:
                raise
            # solve-cli failed on this machine (often a GPU that was full): nothing in that pull request
            # was merged or rejected, and the next pass tries again
            retry = args.watch
            print(f"pass stopped, will retry in {retry:g} min: {e}", flush=True)
        except Exception as e:
            if args.watch <= 0:
                raise
            # a network or Hub hiccup must not end an overnight run, nor leave uploads waiting a whole
            # watch interval: go again soon (after the pause the Hub asks for, when it is a rate limit)
            wait = rate_limit_wait(e)
            retry = min(args.watch, wait / 60 if wait else RETRY_MIN)
            print(f"pass failed, will retry in {retry:.2g} min: {type(e).__name__}: {e}", flush=True)
        if args.watch <= 0:
            break
        time.sleep((args.watch if retry is None else retry) * 60)


if __name__ == "__main__":
    main()
