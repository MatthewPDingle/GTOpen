"""Tests for the real-range path of upload.py and validate.py.

    python tools/datagen/test_real_uploads.py

The Hugging Face hub is replaced by a small fake, so nothing is sent anywhere.
The last test solves four tiny flop spots with solve-cli on the CPU
(`cargo build --release -p solver --bin solve-cli`) and is skipped without it.
"""
import contextlib
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


class FakeHub:
    """The parts of HfApi and hf_hub_download the two tools use, over an in-memory repo with pull requests."""

    def __init__(self):
        self.main = {}                 # path -> bytes
        self.prs = {}                  # num -> {"title", "files": {path: bytes}, "status", "comments": []}
        self.endpoint, self.token = "https://hub.invalid", None

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
        return [types.SimpleNamespace(num=n, title=pr["title"]) for n, pr in sorted(self.prs.items())
                if pr["status"] == discussion_status]

    def get_discussion_details(self, repo, num, repo_type):
        diff = "".join(f"diff --git a/{p} b/{p}\n" + ("" if p in self.main else "new file mode 100644\n")
                       for p in self.prs[num]["files"])
        return types.SimpleNamespace(diff=diff, events=[])

    def comment_discussion(self, repo, num, body, repo_type):
        self.prs[num]["comments"].append(body)

    def change_discussion_status(self, repo, num, status, repo_type):
        self.prs[num]["status"] = status

    def merge_pull_request(self, repo, num, repo_type, comment=""):
        self.main.update(self.prs[num]["files"])
        self.prs[num]["status"] = "merged"
        self.prs[num]["comments"].append(comment)

    def upload_file(self, path_or_fileobj, path_in_repo, repo_id, repo_type, commit_message):
        self.main[path_in_repo] = path_or_fileobj

    def download(self, repo, path, repo_type, revision=None, cache_dir=None, force_download=False):
        data = self.main.get(path)
        if revision and revision.startswith("refs/pr/"):
            data = self.prs[int(revision.rsplit("/", 1)[1])]["files"].get(path, data)
        if data is None:
            raise FileNotFoundError(path)
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
        patches = [mock.patch.dict(sys.modules, {"huggingface_hub": self.hub.module()}),
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
    def open_pr(self, files, title="upload"):
        num = len(self.hub.prs) + 1
        self.hub.prs[num] = {"title": title, "files": files, "status": "open", "comments": []}
        return num

    def gz(self, path):
        with open(path, "rb") as f:
            return gzip.compress(f.read())

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

    def test_game_files_from_other_logins_are_turned_away(self):
        game = game_file(self.tmp, "Stranger", "round1", "g01")
        self.open_pr({"real/Stranger/round1/g01.jsonl.gz": self.gz(game)})
        text = self.validate()
        self.assertIn("REJECT", text)
        pr = self.hub.prs[1]
        self.assertEqual(pr["status"], "closed")
        self.assertIn("accepted from Maint only", pr["comments"][0])
        self.assertEqual(self.hub.main, {})                                # nothing merged, nothing counted

    def test_a_game_file_must_sit_where_its_header_says(self):
        game = game_file(self.tmp, "Maint", "round1", "g01")
        self.open_pr({"real/Maint/round2/g01.jsonl.gz": self.gz(game)})
        self.validate()
        self.assertEqual(self.hub.prs[1]["status"], "closed")
        self.assertIn("header set 'round1' does not match the path ('round2')", self.hub.prs[1]["comments"][0])

    def test_the_verifiers_errors_reject_the_upload(self):
        game = game_file(self.tmp, "Maint", "round1", "g01", plant_errors=["example 2: re-solve differs"])
        self.open_pr({"real/Maint/round1/g01.jsonl.gz": self.gz(game)})
        self.validate()
        self.assertEqual(self.hub.prs[1]["status"], "closed")
        self.assertIn("example 2: re-solve differs", self.hub.prs[1]["comments"][0])

    def test_a_published_game_file_cannot_be_replaced(self):
        game = game_file(self.tmp, "Maint", "round1", "g01")
        self.hub.main["real/Maint/round1/g01.jsonl.gz"] = self.gz(game)
        self.open_pr({"real/Maint/round1/g01.jsonl.gz": self.gz(game_file(self.tmp, "Maint", "round1", "g01", examples=9))})
        self.validate()
        self.assertEqual(self.hub.prs[1]["status"], "closed")
        self.assertIn("changes or deletes existing files", self.hub.prs[1]["comments"][0])

    def test_other_paths_are_still_refused(self):
        game = game_file(self.tmp, "Maint", "round1", "g01")
        for path in ("real/Maint/g01.jsonl.gz", "real/Maint/round1/sub/g01.jsonl.gz", "real/Maint/round1/manifest.json",
                     "real/Maint/round1/g 01.jsonl.gz"):
            self.hub.prs.clear()
            self.open_pr({path: self.gz(game)})
            self.validate()
            self.assertEqual(self.hub.prs[1]["status"], "closed", path)
            self.assertIn("unexpected file", self.hub.prs[1]["comments"][0])

    def test_the_memory_cap_reaches_the_verifier(self):
        seen = []
        with mock.patch.object(validate, "verify_file",
                               lambda cli, path, sample, max_vram=None: seen.append(max_vram) or fake_verify(cli, path, sample)):
            game = game_file(self.tmp, "Maint", "round1", "g01")
            self.open_pr({"real/Maint/round1/g01.jsonl.gz": self.gz(game)})
            self.validate(real_max_vram=8)
        self.assertEqual(seen, [8])


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
