"""Tests for the referee's low-noise score in the harness (no GPU or torch needed).

    python tools/leafnet/test_referee.py
"""
import contextlib
import hashlib
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
import leafnet_io  # noqa: E402

SNAP = "snap-test"
N, JOBS, NC = 64, 16, 169


def job_sums(level, rng, noise=0.0):
    return {j: np.array([100 * (level + noise * rng.standard_normal()), 100.0, 0.1, 10.0]) for j in range(JOBS)}


class RefereeTests(unittest.TestCase):
    def setUp(self):
        self.work = tempfile.mkdtemp()
        self.sdir = os.path.join(self.work, "snapshots", SNAP)
        os.makedirs(self.sdir)
        with open(os.path.join(self.work, "CURRENT_SNAPSHOT"), "w") as f:
            f.write(SNAP + "\n")
        rng = np.random.default_rng(3)
        self.truth = rng.uniform(0.2, 0.8, (N, 2, NC))                  # flop-averaged values
        luck = 0.05 * rng.standard_normal((N, 2, NC))                    # one flop's luck
        y = self.truth + luck
        arrays = {"x": rng.standard_normal((N, 686)).astype(np.float32), "y": y, "mask": np.ones((N, 2, NC)),
                  "reach": np.ones((N, 2, NC)), "w": np.ones((N, 2, NC)), "jobs": np.repeat(np.arange(JOBS), N // JOBS),
                  "pot_type": np.zeros(N, np.int64), "split": np.full(N, harness.SPLITS["val"])}
        for m in harness.MODELS:
            arrays[f"base_{m}"] = self.truth - 0.03
        for k, a in arrays.items():
            np.save(os.path.join(self.sdir, k + ".npy"), a)
        # a referee that takes out most of the luck
        self.y_cv = (y - 0.9 * luck).astype(np.float32)
        self.write_referee(self.y_cv)
        self.runs = os.path.join(self.work, "runs", SNAP)
        os.makedirs(self.runs)

    def tearDown(self):
        shutil.rmtree(self.work)

    def write_referee(self, y_cv):
        os.makedirs(os.path.join(self.sdir, "referee"), exist_ok=True)
        path = os.path.join(self.sdir, "referee", "val_cv.npy")
        np.save(path, y_cv)
        with open(path, "rb") as f:
            sha = hashlib.sha256(f.read()).hexdigest()
        with open(os.path.join(self.sdir, "referee", "referee.json"), "w") as f:
            json.dump({"val_cv_sha256": sha}, f)

    def val(self):
        return harness.EvalSet(self.sdir, np.load(os.path.join(self.sdir, "split.npy")) == harness.SPLITS["val"])

    def make_run(self, name, shift):
        """A run whose net adds a constant `shift` to balanced (zero weights, constant output bias)."""
        d = os.path.join(self.runs, name)
        os.makedirs(d)
        Ws = [np.zeros((686, 4), np.float32), np.zeros((4, 2 * NC), np.float32)]
        bs = [np.zeros(4, np.float32), np.full(2 * NC, shift, np.float32)]
        leafnet_io.write(os.path.join(d, "leaf_net.bin"), Ws, bs, np.zeros(686, np.float32), np.ones(686, np.float32))
        v = self.val()
        with open(os.path.join(d, "sums.json"), "w") as f:
            json.dump({"val": harness.sums_to_json(v.sums(v.base["balanced"] + shift))}, f)
        return name

    def test_val_cv_is_checked_against_its_hash(self):
        v = self.val()
        cv = harness.load_val_cv(self.sdir, v)
        self.assertTrue(np.array_equal(cv.y, self.y_cv))
        self.assertIs(cv.jobs, v.jobs)
        np.save(os.path.join(self.sdir, "referee", "val_cv.npy"), self.y_cv + 0.01)   # edited by hand
        with self.assertRaises(SystemExit):
            harness.load_val_cv(self.sdir, v)

    def test_no_referee_means_raw_validation(self):
        shutil.rmtree(os.path.join(self.sdir, "referee"))
        self.assertIsNone(harness.load_val_cv(self.sdir, self.val()))
        self.assertEqual(harness.score_key({"val": {}}, {"val": {}, "val_cv": {}}), "val")

    def test_the_low_noise_score_is_less_noisy_and_keeps_the_ranking(self):
        v = self.val()
        cv = v.with_targets(self.y_cv)
        for shift in (0.0, 0.01, 0.02):
            raw, low = harness.totals(v.sums(v.base["balanced"] + shift))[0], harness.totals(cv.sums(cv.base["balanced"] + shift))[0]
            self.assertLess(low, raw)          # most of the luck is gone
        order = lambda es: np.argsort([harness.totals(es.sums(es.base["balanced"] + s))[0] for s in (0.0, 0.01, 0.02, 0.04)])
        self.assertEqual(order(v).tolist(), order(cv).tolist())

    def test_rescore_adds_val_cv_and_its_seed_spread(self):
        noise = [self.make_run(f"noise-2026-11-10-s{s}", 0.025 + 0.001 * s) for s in range(3)]
        st = harness.State(self.work, SNAP)
        st.s = {"best": noise[0], "best_seeds": noise, "history": [noise[0]], "seed_spread": {"class": 0.0002}}
        st.save()
        args = types.SimpleNamespace(work=self.work, snapshot=None, force=False)
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            harness.cmd_rescore(args)
        st = harness.State(self.work, SNAP)
        sp = st.s["seed_spread"]
        self.assertEqual(sp["runs"], noise)
        self.assertEqual(len(sp["class_cv_errors"]), 3)
        self.assertGreater(sp["class_cv"], 0)
        self.assertIn("val_cv", st.group_sums(st.best_seeds()))
        # the scores match what the harness computes from the net
        cv = self.val().with_targets(self.y_cv)
        want = harness.totals(cv.sums(cv.base["balanced"] + 0.025))[0]
        self.assertAlmostEqual(sp["class_cv_errors"][0], want, places=5)

    def test_judge_uses_val_cv_and_guards_raw_validation(self):
        rng = np.random.default_rng(0)
        best = {"val": job_sums(0.1390, rng, 0.0004), "val_cv": job_sums(0.0300, rng, 0.00002)}
        better_cv = {k: {j: v - np.array([100 * 0.0002, 0, 0, 0]) for j, v in s.items()} for k, s in best.items()}
        problems, near, stats = harness.judge(best, better_cv, 0.0001)
        self.assertEqual(problems, [])
        self.assertAlmostEqual(stats["gain_class"], 0.0002, places=7)
        need, measured = harness.spread_need({"class": 0.000175, "class_cv": 0.00005}, "val_cv", 3, 3)
        self.assertAlmostEqual(need, 0.00005 / 3 ** 0.5)
        self.assertTrue(measured)
        self.assertFalse(harness.spread_need({"class": 0.000175}, "val_cv")[1])
        # better on val_cv but clearly worse on raw validation: not kept
        worse_raw = dict(better_cv, val={j: v + np.array([100 * 0.002, 0, 0, 0]) for j, v in best["val"].items()})
        problems, near, _ = harness.judge(best, worse_raw, 0.0001)
        self.assertTrue(any("raw validation" in p for p in problems), problems)
        self.assertFalse(near)


if __name__ == "__main__":
    unittest.main()
