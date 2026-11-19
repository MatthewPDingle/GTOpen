"""Tests for the real-range path of upload.py and validate.py.

    python tools/datagen/test_real_uploads.py

The Hugging Face hub is replaced by a small fake, so nothing is sent anywhere.
The last test solves four tiny flop spots with solve-cli on the CPU
(`cargo build --release -p solver --bin solve-cli`) and is skipped without it.
"""
import contextlib
import datetime
import gzip
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools", "leafnet"))
import upload  # noqa: E402
import validate  # noqa: E402

REPO = "Org/dataset"


def game_file(folder, login, set_name, game, examples=3, **header):
    """A game file as realrange.py publish writes it (made-up examples: these tests never solve them)."""
    d = os.path.join(folder, "real", login, set_name)
    os.makedirs(d, exist_ok=True)
    head = dict({"type": "header", "format": "gtopen-real-range", "format_version": 1, "menu": "lean-v2",
                 "contributor": login, "set": set_name, "game": game, "examples": examples,
                 "target_pct": 0.5, "max_iterations": 1000}, **header)
    rows = [head] + [{"type": "example", "job": 900_000_000_000 + k, "index": 0} for k in range(examples)]
    rows.append({"type": "done", "examples": examples})
    path = os.path.join(d, game + ".jsonl")
    with open(path, "w", encoding="utf-8") as f:
        f.write("".join(json.dumps(r) + "\n" for r in rows))
    return path


class Missing(FileNotFoundError):
    """The Hub's answer for a file that is not in the repo."""


class FakeHub:
    """The parts of HfApi and hf_hub_download the two tools use, over an in-memory repo with pull requests."""

    def __init__(self):
        self.main = {}                 # path -> bytes
        self.prs = {}                  # num -> {"title", "files": {path: bytes}, "status", "comments": []}
        self.endpoint, self.token = "https://hub.invalid", None
        self.commits = []              # messages of the files written to main
        self.after_merge = None        # called with the number right after a merge (to stop a pass part-way)

    # --- upload.py
    def whoami(self):
        return {"name": "someone"}

    def create_commit(self, repo_id, repo_type, operations, commit_message, create_pr, commit_description=""):
        assert repo_id == REPO and repo_type == "dataset" and create_pr
        files = {}
        for op in operations:
            with open(op.path_or_fileobj, "rb") as f:
                files[op.path_in_repo] = f.read()
        num = len(self.prs) + 1
        self.prs[num] = {"title": commit_message, "files": files, "status": "open", "comments": []}
        return types.SimpleNamespace(pr_url=f"https://hub.invalid/{repo_id}/discussions/{num}")

    # --- validate.py
    def list_repo_tree(self, repo, repo_type, recursive, revision=None):
        return [types.SimpleNamespace(path=p, blob_id="x") for p in self.main]

    def get_repo_discussions(self, repo, repo_type, discussion_type, discussion_status):
        return [types.SimpleNamespace(num=n, title=pr["title"], status=pr["status"])
                for n, pr in sorted(self.prs.items(), reverse=True)  # newest first, like the Hub
                if discussion_status in ("all", pr["status"])]

    def get_discussion_details(self, repo, num, repo_type):
        pr = self.prs[num]
        if pr.get("no_diff"):
            diff = ""
        else:
            diff = "".join(f"diff --git a/{p} b/{p}\n" + ("" if p in self.main and pr["status"] == "open"
                                                          else "new file mode 100644\n") for p in pr["files"])
        when = datetime.datetime(2026, 1, 1, 12, 0, num)
        events = [types.SimpleNamespace(type="comment", content=c, author=who, created_at=when)
                  for who, c in pr["comments"]]
        if pr["status"] == "merged":
            events.append(types.SimpleNamespace(type="status-change", new_status="merged", author="maintainer",
                                                created_at=when))
        return types.SimpleNamespace(diff=diff, events=events)

    def comment_discussion(self, repo, num, body, repo_type):
        self.prs[num]["comments"].append(("maintainer", body))

    def change_discussion_status(self, repo, num, status, repo_type):
        self.prs[num]["status"] = status

    def merge_pull_request(self, repo, num, repo_type, comment=""):
        self.main.update(self.prs[num]["files"])
        self.prs[num]["status"] = "merged"
        self.prs[num]["comments"].append(("maintainer", comment))
        if self.after_merge:
            self.after_merge(num)

    def upload_file(self, path_or_fileobj, path_in_repo, repo_id, repo_type, commit_message):
        self.main[path_in_repo] = path_or_fileobj
        self.commits.append(commit_message)

    def download(self, repo, path, repo_type, revision=None, cache_dir=None, force_download=False):
        data = self.main.get(path)
        if revision and revision.startswith("refs/pr/"):
            data = self.prs[int(revision.rsplit("/", 1)[1])]["files"].get(path, data)
        if data is None:
            raise Missing(path)
        d = tempfile.mkdtemp(dir=cache_dir or self.tmp)
        out = os.path.join(d, os.path.basename(path))
        with open(out, "wb") as f:
            f.write(data)
        return out

    def module(self):
        return types.SimpleNamespace(
            HfApi=lambda: self, hf_hub_download=self.download,
            CommitOperationAdd=lambda path_in_repo, path_or_fileobj: types.SimpleNamespace(
                path_in_repo=path_in_repo, path_or_fileobj=path_or_fileobj))


def fake_verify(cli, path, sample, max_vram=None):
    """What solve-cli datagen verify answers for an acceptable file of either kind, read from its header."""
    with open(path, encoding="utf-8") as f:
        head = json.loads(f.readline())
        examples = sum(1 for line in f if '"type": "example"' in line)
    if head.get("format") == "gtopen-real-range":
        return {"ok": True, "kind": "real", "contributor": head["contributor"], "set": head["set"],
                "game": head["game"], "examples": examples, "errors": list(head.get("plant_errors", [])),
                "resolved": [{"index": 0, "mean_abs_diff": 0.0, "max_abs_diff": 0.0}], "max_vram": max_vram}
    return {"ok": True, "job": head["job"], "contributor": head["contributor"], "examples": examples,
            "errors": [], "resolved": []}


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.hub = FakeHub()
        self.hub.tmp = self.tmp
        patches = [mock.patch.dict(sys.modules, {
                       "huggingface_hub": self.hub.module(),
                       "huggingface_hub.errors": types.SimpleNamespace(RemoteEntryNotFoundError=Missing)}),
                   mock.patch.object(validate, "verify_file", fake_verify),
                   mock.patch.object(validate, "block_base", lambda cli, login, cache={}: 1000),
                   mock.patch.object(validate, "publish_graph", lambda progress: None),
                   mock.patch.object(validate, "load_config", lambda: {
                       "hf_repo": REPO, "go_no_go_examples": 10, "goal_examples": 100, "real_contributors": ["Maint"]})]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def upload(self, login):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            n = upload.upload_real_once(self.hub, REPO, self.tmp, login)
        return n, out.getvalue()

    def validate(self, **kw):
        args = types.SimpleNamespace(repo=REPO, solve_cli="solve-cli", sample=3, dry_run=False, publish_graph=False,
                                     real_max_vram=kw.get("real_max_vram", 0))
        with contextlib.redirect_stdout(io.StringIO()) as out:
            validate.run_prs(args)
        return out.getvalue()

    def progress(self):
        return json.loads(self.hub.main["progress.json"])

    def open_pr(self, files, title="upload"):
        num = len(self.hub.prs) + 1
        self.hub.prs[num] = {"title": title, "files": files, "status": "open", "comments": []}
        return num

    def gz(self, path):
        with open(path, "rb") as f:
            return gzip.compress(f.read())


class UploadTests(Base):
    def test_new_game_files_go_up_as_one_pull_request(self):
        a = game_file(self.tmp, "Maint", "round1", "g01", examples=3)
        b = game_file(self.tmp, "Maint", "round1", "g02-bal", examples=5)
        game_file(self.tmp, "Other", "round1", "g01")                     # someone else's folder: left alone
        n, text = self.upload("Maint")
        self.assertEqual(n, 2)
        pr = self.hub.prs[1]
        self.assertEqual(sorted(pr["files"]), ["real/Maint/round1/g01.jsonl.gz", "real/Maint/round1/g02-bal.jsonl.gz"])
        self.assertEqual(pr["title"], "Maint: 2 real-range games, 8 examples")
        with open(a, "rb") as f:
            self.assertEqual(gzip.decompress(pr["files"]["real/Maint/round1/g01.jsonl.gz"]), f.read())
        self.assertTrue(os.path.exists(a + ".uploaded") and os.path.exists(b + ".uploaded"))
        self.assertEqual(self.upload("Maint")[0], 0)                      # nothing new the second time
        self.assertEqual(len(self.hub.prs), 1)

    def test_a_file_in_the_wrong_place_is_not_uploaded(self):
        path = game_file(self.tmp, "Maint", "round1", "g01")
        os.rename(path, os.path.join(os.path.dirname(path), "g09.jsonl"))  # header says g01
        with self.assertRaises(SystemExit) as e:
            self.upload("Maint")
        self.assertIn("header game is 'g01'", str(e.exception))
        self.assertEqual(self.hub.prs, {})

    def test_pooled_jobs_are_not_touched(self):
        os.makedirs(os.path.join(self.tmp, "Maint"))
        with open(os.path.join(self.tmp, "Maint", "job-1.jsonl"), "w") as f:
            f.write("{}\n")
        self.assertEqual(self.upload("Maint")[0], 0)


class ValidateTests(Base):
    def test_a_maintainers_game_files_are_merged_and_counted(self):
        game_file(self.tmp, "Maint", "round1", "g01", examples=3)
        game_file(self.tmp, "Maint", "round1", "g02", examples=4)
        self.upload("Maint")
        text = self.validate()
        self.assertIn("OK, 2 jobs, 7 examples", text)
        self.assertEqual(self.hub.prs[1]["status"], "merged")
        self.assertIn("real/Maint/round1/g01.jsonl.gz", self.hub.main)
        p = self.progress()
        self.assertEqual((p["total_examples"], p["real_examples"]), (7, 7))
        self.assertEqual([(e["contributor"], e.get("kind"), e["jobs"], e["examples"]) for e in p["events"]],
                         [("Maint", "real", 2, 7)])

    def test_pooled_jobs_still_count_as_before(self):
        d = os.path.join(self.tmp, "pool")
        os.makedirs(d)
        rows = [{"type": "header", "job": 1001, "contributor": "Anyone"}, {"type": "example"}, {"type": "example"}]
        with open(os.path.join(d, "job.jsonl"), "w") as f:
            f.write("".join(json.dumps(r) + "\n" for r in rows))
        game = game_file(self.tmp, "Maint", "round1", "g01", examples=3)
        self.open_pr({"data/Anyone/job-1001.jsonl.gz": self.gz(os.path.join(d, "job.jsonl")),
                      "real/Maint/round1/g01.jsonl.gz": self.gz(game)})
        self.validate()
        self.assertEqual(self.hub.prs[1]["status"], "merged")
        p = self.progress()
        self.assertEqual((p["total_examples"], p["real_examples"]), (5, 3))
        self.assertEqual(sorted((e["contributor"], e.get("kind"), e["examples"]) for e in p["events"]),
                         [("Anyone", None, 2), ("Maint", "real", 3)])
        self.assertEqual(p["contributors"], {"Maint": 3, "Anyone": 2})

    def pool_job(self, job, generator):
        d = os.path.join(self.tmp, f"pool-{job}")
        os.makedirs(d)
        rows = [{"type": "header", "job": job, "contributor": "Anyone", "generator_version": generator},
                {"type": "example"}, {"type": "example"}]
        path = os.path.join(d, "job.jsonl")
        with open(path, "w") as f:
            f.write("".join(json.dumps(r) + "\n" for r in rows))
        return self.gz(path)

    def test_older_generator_jobs_are_merged_with_a_friendly_request_to_update(self):
        with mock.patch.object(validate, "load_config", lambda: {
                "hf_repo": REPO, "go_no_go_examples": 10, "goal_examples": 100, "real_contributors": ["Maint"],
                "current_generator": 4}):
            self.open_pr({"data/Anyone/job-1001.jsonl.gz": self.pool_job(1001, 3),
                          "data/Anyone/job-1002.jsonl.gz": self.pool_job(1002, 4)})
            self.open_pr({"data/Anyone/job-1003.jsonl.gz": self.pool_job(1003, 4)})
            text = self.validate()
        self.assertEqual([self.hub.prs[n]["status"] for n in (1, 2)], ["merged", "merged"])
        self.assertIn("asked to update", text)
        first, second = self.hub.prs[1]["comments"][-1][1], self.hub.prs[2]["comments"][-1][1]
        self.assertIn("Thank you!", first)
        self.assertIn("generator v3. They are merged and count in full", first)
        self.assertIn("Generator v4 is out now", first)
        self.assertEqual(second, "Validated 1 jobs (2 examples). Thank you!")
        self.assertEqual(self.progress()["total_examples"], 6)

    def test_the_current_generator_in_config_matches_the_solver(self):
        import re
        with open(os.path.join(ROOT, "crates", "solver", "src", "datagen.rs"), encoding="utf-8") as f:
            rust = int(re.search(r"pub const GENERATOR_VERSION: u32 = (\d+);", f.read()).group(1))
        with open(os.path.join(HERE, "config.json"), encoding="utf-8") as f:
            self.assertEqual(json.load(f)["current_generator"], rust)

    def test_game_files_from_other_logins_are_turned_away(self):
        game = game_file(self.tmp, "Stranger", "round1", "g01")
        self.open_pr({"real/Stranger/round1/g01.jsonl.gz": self.gz(game)})
        text = self.validate()
        self.assertIn("REJECT", text)
        pr = self.hub.prs[1]
        self.assertEqual(pr["status"], "closed")
        self.assertIn("accepted from Maint only", pr["comments"][0][1])
        self.assertEqual(self.hub.main, {})                                # nothing merged, nothing counted

    def test_a_game_file_must_sit_where_its_header_says(self):
        game = game_file(self.tmp, "Maint", "round1", "g01")
        self.open_pr({"real/Maint/round2/g01.jsonl.gz": self.gz(game)})
        self.validate()
        self.assertEqual(self.hub.prs[1]["status"], "closed")
        self.assertIn("header set 'round1' does not match the path ('round2')", self.hub.prs[1]["comments"][0][1])

    def test_the_verifiers_errors_reject_the_upload(self):
        game = game_file(self.tmp, "Maint", "round1", "g01", plant_errors=["example 2: re-solve differs"])
        self.open_pr({"real/Maint/round1/g01.jsonl.gz": self.gz(game)})
        self.validate()
        self.assertEqual(self.hub.prs[1]["status"], "closed")
        self.assertIn("example 2: re-solve differs", self.hub.prs[1]["comments"][0][1])

    def test_a_published_game_file_cannot_be_replaced(self):
        game = game_file(self.tmp, "Maint", "round1", "g01")
        self.hub.main["real/Maint/round1/g01.jsonl.gz"] = self.gz(game)
        self.open_pr({"real/Maint/round1/g01.jsonl.gz": self.gz(game_file(self.tmp, "Maint", "round1", "g01", examples=9))})
        self.validate()
        self.assertEqual(self.hub.prs[1]["status"], "closed")
        self.assertIn("changes or deletes existing files", self.hub.prs[1]["comments"][0][1])

    def test_other_paths_are_still_refused(self):
        game = game_file(self.tmp, "Maint", "round1", "g01")
        for path in ("real/Maint/g01.jsonl.gz", "real/Maint/round1/sub/g01.jsonl.gz", "real/Maint/round1/manifest.json",
                     "real/Maint/round1/g 01.jsonl.gz"):
            self.hub.prs.clear()
            self.open_pr({path: self.gz(game)})
            self.validate()
            self.assertEqual(self.hub.prs[1]["status"], "closed", path)
            self.assertIn("unexpected file", self.hub.prs[1]["comments"][0][1])

    def test_the_memory_cap_reaches_the_verifier(self):
        seen = []
        with mock.patch.object(validate, "verify_file",
                               lambda cli, path, sample, max_vram=None: seen.append(max_vram) or fake_verify(cli, path, sample)):
            game = game_file(self.tmp, "Maint", "round1", "g01")
            self.open_pr({"real/Maint/round1/g01.jsonl.gz": self.gz(game)})
            self.validate(real_max_vram=8)
        self.assertEqual(seen, [8])


class CountingTests(Base):
    """progress.json holds every merged pull request, however the validator was stopped."""

    def pooled_pr(self, job, login="Anyone", examples=2, title=None):
        d = os.path.join(self.tmp, f"job-{job}")
        os.makedirs(d)
        rows = [{"type": "header", "job": job, "contributor": login, "examples": examples}]
        rows += [{"type": "example"}] * examples
        with open(os.path.join(d, "job.jsonl"), "w") as f:
            f.write("".join(json.dumps(r) + "\n" for r in rows))
        return self.open_pr({f"data/{login}/job-{job}.jsonl.gz": self.gz(os.path.join(d, "job.jsonl"))},
                            title=title or f"{login}: 1 jobs, {examples} examples")

    def counted(self):
        return sorted((e["pr"], e["contributor"], e["jobs"], e["examples"]) for e in self.progress()["events"])

    def test_each_merge_is_written_before_the_next_pull_request(self):
        self.pooled_pr(1001)
        self.pooled_pr(1002)
        seen = []
        self.hub.after_merge = lambda num: seen.append(len(self.hub.commits))
        self.validate()
        self.assertEqual(seen, [0, 1])  # the first merge was in progress.json before the second happened
        self.assertEqual(self.progress()["total_examples"], 4)

    def test_a_validator_killed_part_way_loses_no_count(self):
        self.pooled_pr(1001)
        self.pooled_pr(1002)
        self.pooled_pr(1003)

        def kill(num):  # the window is closed right after the second merge, before anything is written for it
            if len([p for p in self.hub.prs.values() if p["status"] == "merged"]) == 2:
                raise KeyboardInterrupt

        self.hub.after_merge = kill
        with self.assertRaises(KeyboardInterrupt):
            self.validate()
        self.assertEqual(len(self.progress()["events"]), 1)
        self.hub.after_merge = None
        text = self.validate()  # the next start merges the one left and finds the one that was never written
        self.assertIn("merged pull requests were missing from progress.json: adding 2 examples", text)
        self.assertEqual(self.counted(), [(1, "Anyone", 1, 2), (2, "Anyone", 1, 2), (3, "Anyone", 1, 2)])
        self.assertEqual(self.progress()["contributors"], {"Anyone": 6})
        self.validate()  # and counts nothing twice
        self.assertEqual(self.progress()["total_examples"], 6)

    def lose_the_count(self):
        """Merge everything that is open, then forget it was counted."""
        self.validate()
        del self.hub.main["progress.json"]

    def test_uncounted_merges_are_credited_by_folder_with_the_merge_time(self):
        self.pooled_pr(1001, login="Newcomer", examples=3, title="Somebody-else: 9 jobs, 900 examples")
        self.lose_the_count()
        self.validate()
        (e,) = self.progress()["events"]
        self.assertEqual((e["contributor"], e["jobs"], e["examples"], e["pr"]), ("Newcomer", 1, 3, 1))
        self.assertEqual(e["time"], "2026-01-01T12:00:01+00:00")

    def test_a_contributors_own_validated_comment_is_not_believed(self):
        self.pooled_pr(1001, examples=3)
        self.lose_the_count()
        self.hub.prs[1]["comments"].append(("Anyone", "Validated 1 jobs (5000 examples). Thank you!"))
        self.validate()
        self.assertEqual(self.counted(), [(1, "Anyone", 1, 3)])

    def test_real_range_and_mixed_merges_are_recounted_from_the_files(self):
        self.pooled_pr(1001)
        game = game_file(self.tmp, "Maint", "round1", "g01", examples=3)
        self.hub.prs[1]["files"]["real/Maint/round1/g01.jsonl.gz"] = self.gz(game)
        self.lose_the_count()
        self.validate()
        p = self.progress()
        self.assertEqual(sorted((e["contributor"], e.get("kind"), e["jobs"], e["examples"]) for e in p["events"]),
                         [("Anyone", None, 1, 2), ("Maint", "real", 1, 3)])
        self.assertEqual(p["real_examples"], 3)

    def test_without_a_diff_the_title_counts_only_if_the_validator_agrees(self):
        self.pooled_pr(1001, examples=3)
        self.pooled_pr(1002, examples=3, title="Anyone: 1 jobs, 300 examples")
        self.lose_the_count()
        for pr in self.hub.prs.values():
            pr["no_diff"] = True
        with mock.patch("urllib.request.urlopen", side_effect=OSError("gone")):
            text = self.validate()
        self.assertEqual(self.counted(), [(1, "Anyone", 1, 3)])
        self.assertIn("PR #2 is merged but not counted, and could not be read", text)

    def test_a_dry_run_lists_uncounted_merges_and_writes_nothing(self):
        self.pooled_pr(1001)
        self.lose_the_count()
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertIsNone(validate.recount(self.hub, REPO, dry_run=True))
        self.assertIn("would add 2 examples", out.getvalue())
        self.assertNotIn("progress.json", self.hub.main)

    def test_a_dropped_connection_never_restarts_the_count(self):
        self.pooled_pr(1001)
        self.validate()
        self.pooled_pr(1002)
        before = self.hub.main["progress.json"]
        real = self.hub.download

        def flaky(repo, path, **kw):  # progress.json cannot be read; everything else can
            if path == "progress.json":
                raise ConnectionError("no network")
            return real(repo, path, **kw)

        with mock.patch.dict(sys.modules, {"huggingface_hub": types.SimpleNamespace(
                HfApi=lambda: self.hub, hf_hub_download=flaky)}):
            text = self.validate()
        self.assertIn("merged, but progress.json could not be written (the next pass adds it)", text)
        self.assertEqual(self.hub.main["progress.json"], before)  # not replaced by a near-empty one
        self.assertEqual(self.hub.prs[2]["status"], "merged")
        self.validate()  # the next pass counts the merge that could not be written
        self.assertEqual(self.counted(), [(1, "Anyone", 1, 2), (2, "Anyone", 1, 2)])

    def too_many(self, header=None):
        import urllib.error
        return urllib.error.HTTPError("https://hub.invalid/x", 429, "Too Many Requests", header or {}, None)

    def test_the_hubs_rate_limit_says_how_long_to_wait(self):
        self.assertEqual(validate.rate_limit_wait(self.too_many({"RateLimit": '"pages";r=0;t=42'})), 47)
        self.assertEqual(validate.rate_limit_wait(self.too_many({"Retry-After": "10"})), 15)
        self.assertEqual(validate.rate_limit_wait(self.too_many()), 65)
        self.assertEqual(validate.rate_limit_wait(self.too_many({"RateLimit": '"pages";r=0;t=9999'})), 330)
        hub_error = RuntimeError("429")  # huggingface_hub's errors carry the response
        hub_error.response = types.SimpleNamespace(status_code=429, headers={"ratelimit": '"api";r=0;t=3'})
        self.assertEqual(validate.rate_limit_wait(hub_error), 8)
        self.assertIsNone(validate.rate_limit_wait(ConnectionError("no network")))

    def test_a_rate_limit_in_the_recount_waits_and_carries_on(self):
        for job in (1001, 1002, 1003):
            self.pooled_pr(job)
        self.lose_the_count()
        real, calls, naps = validate.pr_diff, [], []

        def limited(api, repo, num):  # the Hub refuses the second diff once
            calls.append(num)
            if calls.count(2) == 1 and num == 2:
                raise self.too_many({"RateLimit": '"pages";r=0;t=30'})
            return real(api, repo, num)

        with mock.patch.object(validate, "pr_diff", limited), mock.patch.object(validate.time, "sleep", naps.append):
            text = self.validate()
        self.assertEqual(naps, [35])
        self.assertIn("Hugging Face asked for a pause", text)
        self.assertEqual(self.counted(), [(1, "Anyone", 1, 2), (2, "Anyone", 1, 2), (3, "Anyone", 1, 2)])

    def test_a_failed_pass_is_tried_again_soon(self):
        naps, passes = [], []

        def run(args):
            passes.append(1)
            if len(passes) == 1:
                raise self.too_many({"RateLimit": '"pages";r=0;t=100'})
            if len(passes) == 2:
                raise ConnectionError("no network")
            if len(passes) == 4:
                raise KeyboardInterrupt

        argv = ["validate.py", "--watch", "60", "--solve-cli", sys.executable]
        with mock.patch.object(validate, "run_prs", run), mock.patch.object(validate.time, "sleep", naps.append), \
                mock.patch.object(sys, "argv", argv), contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(KeyboardInterrupt):
                validate.real_main()
        self.assertEqual(naps, [105, 300, 3600])  # the Hub's pause, a short retry, then the usual hour

    def test_a_merge_written_twice_counts_once(self):
        self.pooled_pr(1001)
        self.pooled_pr(1002)
        self.validate()
        p = self.progress()
        p["events"].append(dict(p["events"][0]))
        self.hub.main["progress.json"] = json.dumps(p).encode()
        text = self.validate()
        self.assertIn("holds 1 merges twice: dropping the repeats", text)
        self.assertEqual(self.counted(), [(1, "Anyone", 1, 2), (2, "Anyone", 1, 2)])
        self.assertEqual(self.progress()["total_examples"], 4)

    def test_the_graph_is_drawn_at_the_end_of_a_long_pass(self):
        for job in (1001, 1002, 1003):
            self.pooled_pr(job)
        drawn = []
        args = types.SimpleNamespace(repo=REPO, solve_cli="solve-cli", sample=3, dry_run=False, publish_graph=True,
                                     real_max_vram=0)
        with mock.patch.object(validate, "publish_graph", lambda progress: drawn.append(progress["total_examples"])), \
                contextlib.redirect_stdout(io.StringIO()):
            validate.run_prs(args)
        self.assertEqual(drawn, [2, 6])  # at once after the first merge, then once more with everything


class NotesTests(Base):
    def notes(self, dry_run=False):
        args = types.SimpleNamespace(repo=REPO, dry_run=dry_run)
        with contextlib.redirect_stdout(io.StringIO()) as out:
            validate.publish_notes(args)
        return out.getvalue()

    def test_the_card_gets_one_section_however_often_it_runs(self):
        self.hub.main["README.md"] = b"---\nlicense: cc-by-4.0\n---\n# The card\n\nText.\n"
        self.notes()
        once = self.hub.main["README.md"].decode()
        self.assertTrue(once.startswith("---\nlicense: cc-by-4.0\n---\n# The card\n\nText.\n\n" + validate.NOTES_BEGIN))
        self.assertIn("real/README.md", once)
        self.assertIn("built with [Claude]", once)
        self.assertTrue(self.hub.main["real/README.md"].decode().startswith("# Real-range game files"))
        self.notes()
        self.assertEqual(self.hub.main["README.md"].decode(), once)
        self.assertEqual(once.count(validate.NOTES_BEGIN), 1)

    def test_an_older_section_is_replaced_in_place(self):
        old = f"# Card\n\n{validate.NOTES_BEGIN}\nold words\n{validate.NOTES_END}\n\n## After\n"
        new = validate.card_with_notes(old, "new words\n")
        self.assertEqual(new, f"# Card\n\n{validate.NOTES_BEGIN}\nnew words\n{validate.NOTES_END}\n\n## After\n")

    def test_a_dry_run_changes_nothing(self):
        self.hub.main["README.md"] = b"# The card\n"
        text = self.notes(dry_run=True)
        self.assertIn(validate.NOTES_BEGIN, text)
        self.assertEqual(self.hub.main, {"README.md": b"# The card\n"})


CLI = validate.default_cli()


@unittest.skipUnless(os.path.exists(CLI), "needs solve-cli (cargo build --release -p solver --bin solve-cli)")
class EndToEndTests(unittest.TestCase):
    """Four tiny flop solves on the CPU: leaves folder -> publish -> the real verifier."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        env = dict(os.environ, SOLVER_GPU="0")
        game = os.path.join(cls.tmp, "pilot", "g01")
        os.makedirs(game)
        lines = []
        for leaf in range(2):
            for board in range(2):
                out = subprocess.run([CLI, "datagen", "inputs", "777", str(leaf * 2 + board)], capture_output=True,
                                     text=True, cwd=ROOT, check=True).stdout
                ex = json.loads(out)
                ex.pop("pot_scale", None)
                ex.update(job=900_000_000_000 + leaf, index=board, pot_bb=44.0, stack_bb=12.0, pot_type="4bet",
                          rake_pct=0.05, rake_cap_bb=3.0, attempt=0)       # a shallow 4-bet pot: a tiny tree
                lines.append(json.dumps(ex))
        with open(os.path.join(game, "inputs.jsonl"), "w") as f:
            f.write("\n".join(lines) + "\n")
        with open(os.path.join(game, "leaves.json"), "w") as f:
            json.dump({"realization": "leafnet", "iteration": 2000, "positions": ["SB", "BB"], "leaves_in_game": 9,
                       "exported": 2, "boards_per_leaf": 2, "chip_share_covered": 0.9,
                       "leaves": [{"job": 900_000_000_000 + k, "path": "x", "raises": 3} for k in range(2)]}, f)
        with open(os.path.join(cls.tmp, "pilot", "manifest.json"), "w") as f:
            json.dump({"games": [{"id": "g01", "folder": "g01", "held_out": False, "source": "leafnet",
                                  "config": {"positions": ["SB", "BB"], "stack": 100.0}}]}, f)
        subprocess.run([CLI, "datagen", "solve", game], capture_output=True, text=True, cwd=ROOT, env=env, check=True)
        subprocess.run([sys.executable, os.path.join(ROOT, "tools", "leafnet", "realrange.py"), "publish",
                        os.path.join(cls.tmp, "pilot"), "--contributor", "Maint", "--set", "round1",
                        "--out", os.path.join(cls.tmp, "pub")], capture_output=True, text=True, check=True)
        cls.file = os.path.join(cls.tmp, "pub", "real", "Maint", "round1", "g01.jsonl")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def check(self, path, **kw):
        with mock.patch.dict(os.environ, {"SOLVER_GPU": "0"}):
            return validate.check_game(CLI, "Maint", "round1", "g01", path, 2, **kw)

    def altered(self, change):
        with open(self.file, encoding="utf-8") as f:
            rows = [json.loads(l) for l in f]
        change(rows)
        path = os.path.join(self.tmp, "altered.jsonl")
        with open(path, "w", encoding="utf-8") as f:
            f.write("".join(json.dumps(r) + "\n" for r in rows))
        return path

    def test_published_solves_pass_and_are_resolved(self):
        errors, summary = self.check(self.file)
        self.assertEqual(errors, [])
        self.assertEqual((summary["kind"], summary["examples"], len(summary["resolved"])), ("real", 4, 2))
        self.assertTrue(all(r["max_abs_diff"] < 0.06 for r in summary["resolved"]))

    def test_shifted_values_fail_the_resolve(self):
        def shift(rows):
            for r in rows[1:-1]:
                r["value"][0] = [None if v is None else round(v + 0.03, 5) for v in r["value"][0]]
        errors, _ = self.check(self.altered(shift))
        self.assertTrue(any("re-solve differs" in e for e in errors), errors)

    def test_implausible_inputs_fail_before_any_solve(self):
        def bad_board(rows):
            rows[1]["board"] = "AcAc5h"
        def bad_range(rows):
            rows[2]["range"][1][0] = 1.5
        def twice(rows):
            rows[2]["index"] = rows[1]["index"]
            rows[2]["job"] = rows[1]["job"]
        for change, text in ((bad_board, "is not a flop"), (bad_range, "weight outside 0..1"), (twice, "repeats")):
            errors, summary = self.check(self.altered(change))
            self.assertTrue(any(text in e for e in errors), errors)
            self.assertEqual(summary["resolved"], [])

    def test_a_file_with_no_tree_under_the_cap_is_rejected(self):
        errors, _ = self.check(self.file, max_vram=0.000001)
        self.assertTrue(any("no example was re-solved" in e for e in errors), errors)

    def test_the_local_check_walks_published_folders(self):
        args = types.SimpleNamespace(local=os.path.join(self.tmp, "pub", "real"), solve_cli=CLI, sample=2, real_max_vram=0)
        with mock.patch.dict(os.environ, {"SOLVER_GPU": "0"}), contextlib.redirect_stdout(io.StringIO()) as out:
            ok = validate.run_local(args)
        self.assertTrue(ok)
        self.assertIn("ok  real Maint/round1/g01.jsonl: 4 examples", out.getvalue())


if __name__ == "__main__":
    unittest.main()
