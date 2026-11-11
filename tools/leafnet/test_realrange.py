"""Tests for realrange.py (pack, publish, compare) and prepare.py's --extra / --files-from / --side.

    python tools/leafnet/test_realrange.py

No GPU or torch. The snapshot tests price fabricated examples with solve-cli
(`cargo build --release -p solver --bin solve-cli`) and are skipped without it.
"""
import contextlib
import gc
import gzip
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import types
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import harness  # noqa: E402
import leafnet_io  # noqa: E402
import realrange  # noqa: E402
from gonogo import split_of  # noqa: E402
from prepare import REAL_GENERATOR  # noqa: E402
from validate import default_cli  # noqa: E402

NC = 169
LEAF_BASE = 900_000_000_000      # datagen_cli.rs LEAF_JOB_BASE: every game's leaves are numbered from here
BOARDS = ["2c7d9h", "AsKd4c", "8h8d3s", "QcJc5c", "Td9s2h", "6s5s4d"]
POT_TYPES = ["limped", "srp", "3bet", "4bet"]


def example(rng, job, index):
    """A solved example with made-up numbers in the format of `solve-cli datagen solve`."""
    r = np.round(rng.uniform(0, 1, (2, NC)) * (rng.uniform(0, 1, (2, NC)) < 0.6), 3)
    r[:, 0] = 1.0
    value = np.round(rng.uniform(0.1, 0.9, (2, NC)), 5).tolist()
    for p in range(2):
        for k in np.nonzero(r[p] == 0)[0][:5]:
            value[p][int(k)] = None                  # classes a board removes come back as null
    pot = round(float(rng.uniform(4, 40)), 2)
    return {"type": "example", "job": job, "index": index, "board": BOARDS[int(rng.integers(len(BOARDS)))],
            "pot_type": POT_TYPES[job % 4], "pot_bb": pot, "stack_bb": round(float(rng.uniform(20, 150)), 2),
            "rake_pct": 0.05, "rake_cap_bb": 3.0, "range": r.tolist(), "attempt": 0,
            "reach": np.round(r * rng.uniform(4, 12, (2, NC)), 3).tolist(),
            "eq": np.round(rng.uniform(0.2, 0.8, (2, NC)), 5).tolist(), "value": value,
            "iterations": 300, "exploit_pct_pot": round(float(rng.uniform(0.1, 0.4)), 3), "seconds": 1.0}


def write_game(folder, rng, leaves, boards=2, solved=None):
    """A `datagen leaves` + `datagen solve` folder with `leaves` leaves; only the first `solved` examples solved."""
    os.makedirs(folder)
    recs = [example(rng, LEAF_BASE + rank, b) for rank in range(leaves) for b in range(boards)]
    with open(os.path.join(folder, "inputs.jsonl"), "w") as f:
        f.write("".join(json.dumps({k: v for k, v in r.items() if k not in ("type", "reach", "eq", "value")}) + "\n"
                        for r in recs))
    with open(os.path.join(folder, "solved.jsonl"), "w") as f:
        f.write("".join(json.dumps(r) + "\n" for r in recs[:solved]))
    with open(os.path.join(folder, "leaves.json"), "w") as f:
        json.dump({"game": os.path.join("X:", "private", "saves", os.path.basename(folder) + ".bin"),
                   "realization": "leafnet", "iteration": 2000, "positions": ["BTN", "SB", "BB"],
                   "leaves_in_game": 40, "exported": leaves, "boards_per_leaf": boards, "chip_share_covered": 0.9,
                   "leaves": [{"job": LEAF_BASE + k, "path": [k], "raises": k % 4} for k in range(leaves)]}, f)
    return recs


def config(stack, realization="leafnet"):
    cfg = {"positions": ["BTN", "SB", "BB"], "stack": stack, "open_raises": [2.5], "realization": realization}
    return dict(cfg, leaf_net="snap/ens3") if realization == "leafnet" else cfg


def pilot(root, rng, held=("h1",)):
    """Four games: g1 solved under two realizations, g2 half solved, h1 held out."""
    games = [("g1", config(100)), ("g1-bal", config(100, "balanced")), ("g2", config(60)), ("h1", config(150))]
    for gid, _ in games:
        write_game(os.path.join(root, gid), rng, leaves=6, solved=7 if gid == "g2" else None)
    with open(os.path.join(root, "manifest.json"), "w") as f:
        json.dump({"games": [{"id": gid, "folder": gid, "held_out": gid in held, "source": cfg["realization"],
                              "config": cfg} for gid, cfg in games]}, f)


def pack(root, out, **kw):
    args = types.SimpleNamespace(root=root, out=out, manifest=None, held_name=kw.get("held_name", "realrange-heldout"))
    with contextlib.redirect_stdout(io.StringIO()):
        return realrange.cmd_pack(args)


def publish(root, out, contributor="Tester", set_name="round1"):
    args = types.SimpleNamespace(root=root, out=out, manifest=None, contributor=contributor, set=set_name,
                                 target=0.5, max_iters=1000)
    with contextlib.redirect_stdout(io.StringIO()):
        realrange.cmd_publish(args)
    return os.path.join(out, "real", contributor, set_name)


def read_job_file(path):
    with gzip.open(path, "rt", encoding="utf-8") as f:
        rows = [json.loads(l) for l in f]
    return rows[0], rows[1:]


def job_files(folder):
    return sorted(os.path.join(d, n) for d, _, names in os.walk(folder) for n in names if n.startswith("job-"))


class PackTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = os.path.join(self.tmp, "pilot")
        os.makedirs(self.root)
        pilot(self.root, np.random.default_rng(5))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_training_leaves_become_one_training_job_each(self):
        out = os.path.join(self.tmp, "pack")
        info = pack(self.root, out)
        files = job_files(os.path.join(out, "train"))
        self.assertEqual(len(files), 6 + 6 + 4)                    # g2: 7 examples solved = 4 leaves, the last with one board
        self.assertEqual(info["train"], {"games": 3, "leaves": 16, "examples": 12 + 12 + 7})
        jobs = set()
        for path in files:
            header, recs = read_job_file(path)
            self.assertEqual(header["type"], "header")
            self.assertEqual(header["generator_version"], REAL_GENERATOR)
            self.assertEqual(os.path.basename(path), f"job-{header['job']}.jsonl.gz")
            self.assertEqual(os.path.basename(os.path.dirname(path)), header["game"])
            self.assertEqual(split_of(header["job"]), "train")
            self.assertTrue(recs and all(r["job"] == header["job"] and r["type"] == "example" for r in recs))
            self.assertEqual([r["index"] for r in recs], list(range(len(recs))))
            self.assertNotIn(header["job"], jobs)                  # the games' own numbers all started at LEAF_BASE
            jobs.add(header["job"])
        self.assertTrue(all(realrange.TRAIN_BASE <= j < realrange.HELD_BASE for j in jobs))

    def test_the_solved_values_are_copied_unchanged(self):
        out = os.path.join(self.tmp, "pack")
        pack(self.root, out)
        with open(os.path.join(self.root, "g1", "solved.jsonl")) as f:
            first = json.loads(f.readline())
        header, recs = read_job_file(job_files(os.path.join(out, "train", "g1"))[0])
        self.assertEqual(header["leaf_job"], first["job"])
        self.assertEqual({k: v for k, v in recs[0].items() if k != "job"}, {k: v for k, v in first.items() if k != "job"})

    def test_held_out_games_become_one_check_set(self):
        out = os.path.join(self.tmp, "pack")
        info = pack(self.root, out)
        self.assertEqual(info["held_out"], {"games": 1, "leaves": 6, "examples": 12})
        self.assertFalse(os.path.exists(os.path.join(out, "train", "h1")))
        with open(os.path.join(out, "realrange-heldout", "solved.jsonl")) as f:
            recs = [json.loads(l) for l in f]
        self.assertEqual(len(recs), 12)
        self.assertEqual(len({r["job"] for r in recs}), 6)
        self.assertTrue(all(r["job"] >= realrange.HELD_BASE for r in recs))
        with open(os.path.join(out, "realrange-heldout", "leaves.json")) as f:
            leaves = json.load(f)
        self.assertEqual(leaves["games"], ["h1"])
        self.assertEqual({l["job"] for l in leaves["leaves"]}, {r["job"] for r in recs})
        self.assertTrue(all(l["game"] == "h1" and "path" in l for l in leaves["leaves"]))

    def test_packing_again_gives_the_same_bytes(self):
        a, b = os.path.join(self.tmp, "a"), os.path.join(self.tmp, "b")
        pack(self.root, a)
        pack(self.root, b)
        def sha(path):
            with open(path, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()
        self.assertEqual([sha(p) for p in job_files(a)], [sha(p) for p in job_files(b)])

    def test_a_held_out_game_solved_twice_cannot_be_trained_on(self):
        root = os.path.join(self.tmp, "twin")
        os.makedirs(root)
        pilot(root, np.random.default_rng(6), held=("g1",))          # g1-bal is the same game under "balanced"
        with self.assertRaises(SystemExit) as e, contextlib.redirect_stdout(io.StringIO()):
            pack(root, os.path.join(self.tmp, "pack"))
        self.assertIn("g1-bal", str(e.exception))

    def test_a_pack_is_written_once(self):
        out = os.path.join(self.tmp, "pack")
        pack(self.root, out)
        with self.assertRaises(SystemExit):
            pack(self.root, out)


class PublishTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = os.path.join(self.tmp, "pilot")
        os.makedirs(self.root)
        pilot(self.root, np.random.default_rng(5))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def rows(self, path):
        with open(path, encoding="utf-8") as f:
            return [json.loads(l) for l in f]

    def test_every_game_becomes_one_file_with_its_solves(self):
        out = publish(self.root, os.path.join(self.tmp, "pub"))
        self.assertEqual(sorted(os.listdir(out)), ["g1-bal.jsonl", "g1.jsonl", "g2.jsonl", "h1.jsonl"])
        with open(os.path.join(self.root, "g2", "solved.jsonl")) as f:
            solved = [json.loads(l) for l in f]
        rows = self.rows(os.path.join(out, "g2.jsonl"))
        head = rows[0]
        self.assertEqual({k: head[k] for k in ("type", "format", "format_version", "menu", "contributor", "set", "game")},
                         {"type": "header", "format": "gtopen-real-range", "format_version": 1, "menu": realrange.MENU,
                          "contributor": "Tester", "set": "round1", "game": "g2"})
        self.assertEqual((head["examples"], head["asked"]), (7, 12))      # half solved: published as it is
        self.assertEqual((head["target_pct"], head["max_iterations"]), (0.5, 1000))
        self.assertEqual(rows[1:-1], solved)                               # the examples, unchanged
        self.assertEqual(rows[-1], {"type": "done", "examples": 7})
        self.assertEqual([l["job"] for l in head["leaves"]], sorted({r["job"] for r in solved}))  # solved leaves only
        self.assertEqual(head["config"], config(60))
        self.assertEqual(head["preflop"]["iteration"], 2000)
        self.assertTrue(self.rows(os.path.join(out, "h1.jsonl"))[0]["held_out"])
        self.assertEqual(self.rows(os.path.join(out, "g1-bal.jsonl"))[0]["source"], "balanced")

    def test_the_local_path_of_the_save_is_not_published(self):
        out = publish(self.root, os.path.join(self.tmp, "pub"))
        for name in os.listdir(out):
            with open(os.path.join(out, name), encoding="utf-8") as f:
                self.assertNotIn("private", f.read())

    def test_the_menu_name_is_the_solvers(self):
        with open(os.path.join(realrange.ROOT, "crates", "solver", "src", "datagen.rs"), encoding="utf-8") as f:
            src = f.read()
        self.assertIn(f'pub const MENU: &str = "{realrange.MENU}";', src)
        self.assertIn(f'pub const REAL_FORMAT: &str = "{realrange.REAL_FORMAT}";', src)
        self.assertIn(f"pub const REAL_FORMAT_VERSION: u32 = {realrange.REAL_FORMAT_VERSION};", src)

    def bytes_of(self, folder):
        out = {}
        for name in os.listdir(folder):
            with open(os.path.join(folder, name), "rb") as f:
                out[name] = f.read()
        return out

    def test_publishing_again_changes_nothing(self):
        out = publish(self.root, os.path.join(self.tmp, "pub"))
        before = self.bytes_of(out)
        publish(self.root, os.path.join(self.tmp, "pub"))
        self.assertEqual(before, self.bytes_of(out))

    def test_an_uploaded_file_is_never_rewritten(self):
        out = publish(self.root, os.path.join(self.tmp, "pub"))
        with open(os.path.join(out, "g2.jsonl.uploaded"), "w") as f:
            f.write("https://example.invalid/pr/1\n")
        rng = np.random.default_rng(9)                                      # one more example gets solved
        with open(os.path.join(self.root, "g2", "solved.jsonl"), "a") as f:
            f.write(json.dumps(example(rng, LEAF_BASE + 3, 1)) + "\n")
        with self.assertRaises(SystemExit) as e, contextlib.redirect_stdout(io.StringIO()):
            publish(self.root, os.path.join(self.tmp, "pub"))
        self.assertIn("never changed", str(e.exception))
        os.remove(os.path.join(out, "g2.jsonl.uploaded"))                   # not uploaded yet: rewritten
        publish(self.root, os.path.join(self.tmp, "pub"))
        self.assertEqual(self.rows(os.path.join(out, "g2.jsonl"))[0]["examples"], 8)

    def test_only_leaves_of_a_solved_game_are_published(self):
        with open(os.path.join(self.root, "g1", "leaves.json"), "w") as f:
            json.dump({"leaves": []}, f)                                    # not from `datagen leaves`
        with self.assertRaises(SystemExit) as e, contextlib.redirect_stdout(io.StringIO()):
            publish(self.root, os.path.join(self.tmp, "pub"))
        self.assertIn("never ranges from anywhere else", str(e.exception))

    def test_names_must_be_plain(self):
        for kw in ({"contributor": "a/b"}, {"set_name": ".."}, {"set_name": "round 1"}):
            with self.assertRaises(SystemExit), contextlib.redirect_stdout(io.StringIO()):
                publish(self.root, os.path.join(self.tmp, "pub"), **kw)
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "pub")))

    def test_a_pack_from_the_published_files_is_the_pack_from_the_folders(self):
        out = publish(self.root, os.path.join(self.tmp, "pub"))
        for name in ("g1.jsonl", "h1.jsonl"):                               # as downloaded from the dataset
            with open(os.path.join(out, name), "rb") as src, gzip.open(os.path.join(out, name + ".gz"), "wb") as dst:
                dst.write(src.read())
            os.remove(os.path.join(out, name))
        a, b = os.path.join(self.tmp, "a"), os.path.join(self.tmp, "b")
        info_a = pack(self.root, a)
        info_b = pack(os.path.join(self.tmp, "pub"), b)                     # no manifest there: the headers are read
        self.assertEqual(info_a["train"], info_b["train"])
        self.assertEqual(info_a["held_out"], info_b["held_out"])
        # the manifest lists g1, g1-bal, g2, h1 and the files sort the same way, so the numbering is the same
        names = lambda d: [os.path.relpath(p, d) for p in job_files(d)]
        self.assertEqual(names(a), names(b))
        for pa, pb in zip(job_files(a), job_files(b)):
            with open(pa, "rb") as fa, open(pb, "rb") as fb:
                self.assertEqual(fa.read(), fb.read())
        with open(os.path.join(a, "realrange-heldout", "solved.jsonl"), "rb") as fa, \
                open(os.path.join(b, "realrange-heldout", "solved.jsonl"), "rb") as fb:
            self.assertEqual(fa.read(), fb.read())

    def test_a_published_twin_of_a_held_out_game_is_still_refused(self):
        root = os.path.join(self.tmp, "twin")
        os.makedirs(root)
        pilot(root, np.random.default_rng(6), held=("g1",))
        publish(root, os.path.join(self.tmp, "pub2"))
        with self.assertRaises(SystemExit) as e, contextlib.redirect_stdout(io.StringIO()):
            pack(os.path.join(self.tmp, "pub2"), os.path.join(self.tmp, "pack"))
        self.assertIn("g1-bal", str(e.exception))


@unittest.skipUnless(os.path.exists(default_cli()), "needs solve-cli (cargo build --release -p solver --bin solve-cli)")
class SnapshotTests(unittest.TestCase):
    """prepare.py on a made-up pool, then the same pool plus a pack, then compare on it."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.work = os.path.join(cls.tmp, "work")
        rng = np.random.default_rng(11)
        cls.pool = os.path.join(cls.tmp, "pool")
        for job in range(1, 31):                                    # 30 pool jobs of 4 examples: every split has some
            path = os.path.join(cls.pool, "someone", f"job-{job}.jsonl.gz")
            realrange.write_job_file(path, {"type": "header", "generator_version": 3, "job": job},
                                     [example(rng, job, i) for i in range(4)])
        root = os.path.join(cls.tmp, "pilot")
        os.makedirs(root)
        pilot(root, rng)
        cls.pack = os.path.join(cls.tmp, "pack")
        pack(root, cls.pack)
        cls.prepare("--data", cls.pool, "--name", "base")
        cls.prepare("--files-from", "base", "--extra", os.path.join(cls.pack, "train"),
                "--leafcheck", os.path.join(cls.pack, "realrange-heldout"), "--name", "real", "--side")

    @classmethod
    def tearDownClass(cls):
        gc.collect()                                                # memory-mapped arrays: Windows keeps the files locked
        shutil.rmtree(cls.tmp, ignore_errors=True)

    @classmethod
    def prepare(cls, *args, ok=True):
        proc = subprocess.run([sys.executable, os.path.join(HERE, "prepare.py"), "--work", cls.work, *args],
                              capture_output=True, text=True)
        if ok and proc.returncode != 0:
            raise AssertionError(f"prepare.py {' '.join(args)} failed:\n{proc.stdout[-2000:]}\n{proc.stderr[-2000:]}")
        return proc

    def load(self, snap, name):
        return np.load(os.path.join(self.work, "snapshots", snap, name + ".npy"))

    def manifest(self, snap):
        with open(os.path.join(self.work, "snapshots", snap, "manifest.json")) as f:
            return json.load(f)

    def test_the_pool_rows_are_the_base_snapshots(self):
        n = len(self.load("base", "jobs"))
        self.assertEqual(n, 120)
        for name in ("x", "y", "mask", "w", "jobs", "split", "generator", "base_balanced"):
            np.testing.assert_array_equal(self.load("real", name)[:n], self.load("base", name), err_msg=name)
        self.assertEqual({int(s) for s in self.load("base", "split")}, {0, 1, 2})
        with open(os.path.join(self.work, "snapshots", "base", "inputs_val.jsonl")) as a, \
                open(os.path.join(self.work, "snapshots", "real", "inputs_val.jsonl")) as b:
            self.assertEqual(a.read(), b.read())

    def test_the_extra_rows_are_real_range_training_rows(self):
        n = len(self.load("base", "jobs"))
        gen, split = self.load("real", "generator"), self.load("real", "split")
        self.assertEqual(len(gen), n + 31)
        self.assertTrue((gen[n:] == REAL_GENERATOR).all() and (gen[:n] == 3).all())
        self.assertTrue((split[n:] == harness.SPLITS["train"]).all())
        m = self.manifest("real")
        self.assertEqual(m["files_from"], "base")
        self.assertEqual(m["extra_examples_by_split"], {"train": 31, "val": 0, "test": 0})
        self.assertEqual(m["examples_by_split"]["val"], self.manifest("base")["examples_by_split"]["val"])
        self.assertEqual(m["generator_versions"], {"3": 30, str(REAL_GENERATOR): 16})

    def test_every_listed_file_is_found_from_the_manifest(self):
        """What flops.load_side does: join each file to "source", read it, and expect the snapshot's row order."""
        m, jobs, row = self.manifest("real"), self.load("real", "jobs"), 0
        self.assertEqual(sum(1 for fm in m["files_manifest"] if fm.get("extra")), 16)
        for fm in m["files_manifest"]:
            with gzip.open(os.path.join(m["source"], fm["file"]), "rt", encoding="utf-8") as f:
                got = [json.loads(l)["job"] for l in f if '"type":"example"' in l.replace(" ", "")]
            self.assertEqual(got, jobs[row:row + fm["examples"]].tolist())
            row += fm["examples"]
        self.assertEqual(row, len(jobs))

    def test_a_side_snapshot_does_not_become_the_current_one(self):
        self.assertEqual(harness.current_snapshot(self.work), "base")

    def test_a_changed_pool_file_is_refused(self):
        pool = os.path.join(self.tmp, "pool-changed")
        shutil.copytree(self.pool, pool)
        path = os.path.join(pool, "someone", "job-7.jsonl.gz")
        realrange.write_job_file(path, {"type": "header", "generator_version": 3, "job": 7},
                                 [example(np.random.default_rng(1), 7, i) for i in range(4)])
        proc = self.prepare("--files-from", "base", "--data", pool, "--name", "changed", "--side", ok=False)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("differ from the ones base froze", proc.stderr)
        self.assertFalse(os.path.exists(os.path.join(self.work, "snapshots", "changed")))

    def test_extra_files_outside_the_training_split_are_refused(self):
        job = next(j for j in range(realrange.TRAIN_BASE, realrange.TRAIN_BASE + 100) if split_of(j) == "val")
        extra = os.path.join(self.tmp, "extra-val")
        realrange.write_job_file(os.path.join(extra, f"job-{job}.jsonl.gz"),
                                 {"type": "header", "generator_version": REAL_GENERATOR, "job": job},
                                 [example(np.random.default_rng(2), job, 0)])
        proc = self.prepare("--files-from", "base", "--extra", extra, "--name", "stray", "--side", ok=False)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("validation or test split", proc.stderr)
        self.assertFalse(os.path.exists(os.path.join(self.work, "snapshots", "stray")))

    def net(self, name, bias):
        """A net whose residual is `bias` for every class: its predictions are the balanced model's plus bias."""
        path = os.path.join(self.tmp, name + ".bin")
        leafnet_io.write(path, [np.zeros((686, 4), np.float32), np.zeros((4, 2 * NC), np.float32)],
                         [np.zeros(4, np.float32), np.full(2 * NC, bias, np.float32)], np.zeros(686, np.float32),
                         np.ones(686, np.float32))
        return path

    def test_compare_reports_the_shortfall_of_each_arm(self):
        arms = {"zero": [self.net("zero", 0.0)], "plus": [self.net("plus", 0.01)], "both": [self.net("zero", 0.0), self.net("plus", 0.01)]}
        rep = realrange.compare(self.work, "real", arms, reps=200)
        self.assertEqual(set(rep), {"val", "leaf:realrange-heldout"})
        for name, e in rep.items():
            a = e["arms"]
            self.assertEqual(list(a), ["balanced", "zero", "plus", "both"])
            # a zero net is the balanced model; +0.01 for every class of both players is +2% of the pot in total
            for k in ("class_error", "range_error", "total_pct"):
                self.assertAlmostEqual(a["zero"][k], a["balanced"][k], places=9, msg=name)
            self.assertAlmostEqual(a["plus"]["total_pct"] - a["zero"]["total_pct"], 2.0, places=3)
            self.assertAlmostEqual(a["plus"]["vs_first"]["total_pct"], 2.0, places=3)
            lo, hi = a["plus"]["vs_first"]["total_pct_ci"]
            self.assertTrue(1.99 < lo <= hi < 2.01)                  # the same shift on every resample
            self.assertAlmostEqual(a["both"]["total_pct"] - a["zero"]["total_pct"], 1.0, places=3)
            self.assertAlmostEqual(a["both"]["class_error"], (a["zero"]["class_error"] + a["plus"]["class_error"]) / 2, places=9)
            self.assertNotIn("vs_first", a["zero"])
            by = a["zero"]["total_pct_by_type"]
            self.assertEqual(list(by), POT_TYPES)
            lo, hi = a["zero"]["total_pct_ci"]
            self.assertTrue(lo <= a["zero"]["total_pct"] <= hi)
        held = rep["leaf:realrange-heldout"]
        self.assertEqual((held["examples"], held["jobs"]), (12, 6))
        self.assertEqual(list(held["games"]), ["h1"])
        self.assertEqual(held["games"]["h1"]["plus"]["leaves"], 6)
        self.assertAlmostEqual(held["games"]["h1"]["plus"]["total_pct"], held["arms"]["plus"]["total_pct"], places=9)
        self.assertEqual(rep["val"]["games"], {})
        text = realrange.markdown("real", arms, rep, False)
        self.assertIn("## leaf:realrange-heldout (12 examples, 6 leaves)", text)
        self.assertIn("plus minus zero: class error", text)
        self.assertIn("| h1 | 6 |", text)

    def test_an_ensemble_arm_is_scored_as_its_mean_output(self):
        arms = {"zero": [self.net("zero", 0.0)], "both": [self.net("zero", 0.0), self.net("plus", 0.01)],
                "half": [self.net("half", 0.005)]}
        rep = realrange.compare(self.work, "real", arms, ensemble=True, reps=50)
        for e in rep.values():
            for k in ("class_error", "range_error", "total_pct"):
                self.assertAlmostEqual(e["arms"]["both"][k], e["arms"]["half"][k], places=7)

    def test_a_net_is_found_by_run_id_folder_or_file(self):
        rdir = os.path.join(self.work, "runs", "base", "20261111-000000-s0")
        os.makedirs(rdir, exist_ok=True)
        shutil.copy(self.net("zero", 0.0), os.path.join(rdir, "leaf_net.bin"))
        want = os.path.join(rdir, "leaf_net.bin")
        self.assertEqual(realrange.resolve_net(self.work, "20261111-000000-s0"), want)
        self.assertEqual(realrange.resolve_net(self.work, rdir), want)
        self.assertEqual(realrange.resolve_net(self.work, want), want)
        with self.assertRaises(SystemExit):
            realrange.resolve_net(self.work, "no-such-run")


if __name__ == "__main__":
    unittest.main()
