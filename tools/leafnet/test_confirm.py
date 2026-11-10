"""Tests for the seed-averaged keep rule (no GPU or torch needed).

    python tools/leafnet/test_confirm.py
"""
import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
import types
import unittest

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harness  # noqa: E402

JOBS = 70
SNAP = "snap-test"


def sums(level, noise, rng):
    """Per-job sums [class err * w, w, range err, count] with class error `level` (+ per-job noise)."""
    out = {}
    for j in range(JOBS):
        w = 100.0
        out[j] = np.array([w * (level + noise * rng.standard_normal()), w, 0.01 * 10, 10.0])
    return out


class ConfirmTests(unittest.TestCase):
    def setUp(self):
        self.work = tempfile.mkdtemp()
        self.dir = os.path.join(self.work, "runs", SNAP)
        os.makedirs(self.dir)
        with open(os.path.join(self.work, "CURRENT_SNAPSHOT"), "w") as f:
            f.write(SNAP + "\n")
        # a shared per-job difficulty, so best and candidate are paired like real validation jobs
        self.rng = np.random.default_rng(5)
        self.job_level = {j: 0.138 + 0.01 * self.rng.standard_normal() for j in range(JOBS)}

    def tearDown(self):
        shutil.rmtree(self.work)

    def run_dir(self, name, offset, seed_noise):
        d = os.path.join(self.dir, name)
        os.makedirs(d)
        shift = seed_noise * self.rng.standard_normal()   # a seed moves every job a little the same way
        val = {j: np.array([100 * (self.job_level[j] + offset + shift + 2e-5 * self.rng.standard_normal()),
                            100.0, 0.1, 10.0]) for j in range(JOBS)}
        leaf = {j: np.array([100 * (0.152 + offset), 100.0, 0.1, 10.0]) for j in range(8)}
        with open(os.path.join(d, "sums.json"), "w") as f:
            json.dump({"val": harness.sums_to_json(val), "leaf:check": harness.sums_to_json(leaf)}, f)
        # a tiny valid GTOLEAF file so the confirm row can read the net's size
        header = json.dumps({"sizes": [686, 4, 338]}).encode()
        n_vals = 2 * 686 + 686 * 4 + 4 + 4 * 338 + 338
        with open(os.path.join(d, "leaf_net.bin"), "wb") as f:
            f.write(b"GTOLEAF1" + len(header).to_bytes(4, "little") + header + np.zeros(n_vals, "<f4").tobytes())
        return name

    def state(self, best, seeds, spread=0.000175):
        st = harness.State(self.work, SNAP)
        st.s = {"best": best, "best_seeds": seeds, "history": [best], "seed_spread": {"class": spread}}
        st.save()
        return st

    def confirm(self, runs, against=None):
        args = types.SimpleNamespace(work=self.work, snapshot=None, runs=runs, against=against)
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            harness.cmd_confirm(args)
        return out.getvalue().strip().splitlines()[-1], harness.State(self.work, SNAP)

    def test_need_shrinks_with_seeds(self):
        self.assertAlmostEqual(harness.seed_need(0.000175, 1, 1), 0.000175)
        self.assertAlmostEqual(harness.seed_need(0.000175, 3, 3), 0.000175 / 3 ** 0.5)
        self.assertLess(harness.seed_need(0.000175, 3, 1), 0.000175)

    def test_a_steady_small_gain_is_confirmed(self):
        best = [self.run_dir(f"best-s{s}", 0.0, 3e-5) for s in range(3)]
        cand = [self.run_dir(f"cand-s{s}", -0.00012, 3e-5) for s in range(3)]
        self.state(best[0], best)
        verdict, st = self.confirm(cand)
        self.assertEqual(verdict, "VERDICT: keep")
        self.assertIn(st.s["best"], cand)
        self.assertEqual(st.s["best_seeds"], cand)
        self.assertTrue(os.path.exists(os.path.join(self.dir, "best_leaf_net.bin")))
        with open(os.path.join(self.work, "results.tsv")) as f:
            rows = f.read().splitlines()
        self.assertEqual(len(rows), 2)
        self.assertIn("keep", rows[1])

    def test_a_gain_inside_the_noise_is_not(self):
        best = [self.run_dir(f"best-s{s}", 0.0, 3e-5) for s in range(3)]
        cand = [self.run_dir(f"cand-s{s}", -0.00003, 3e-5) for s in range(3)]
        self.state(best[0], best)
        verdict, st = self.confirm(cand)
        self.assertEqual(verdict, "VERDICT: discard")
        self.assertEqual(st.s["best"], best[0])

    def test_against_must_include_the_best(self):
        best = [self.run_dir(f"best-s{s}", 0.0, 3e-5) for s in range(2)]
        cand = [self.run_dir(f"cand-s{s}", -0.0002, 3e-5) for s in range(2)]
        self.state(best[0], best)
        with self.assertRaises(SystemExit):
            self.confirm(cand, against=[best[1]])

    def test_judge_flags_a_near_miss(self):
        rng = np.random.default_rng(1)
        base = sums(0.1387, 0.002, rng)
        better = {j: v - np.array([100 * 0.0001, 0, 0, 0]) for j, v in base.items()}
        problems, near, stats = harness.judge({"val": base}, {"val": better}, 0.000175)
        self.assertTrue(near, problems)
        self.assertAlmostEqual(stats["gain_class"], 0.0001, places=7)
        problems, near, _ = harness.judge({"val": base}, {"val": better}, 0.00005)
        self.assertEqual(problems, [])
        self.assertFalse(near)


if __name__ == "__main__":
    unittest.main()
