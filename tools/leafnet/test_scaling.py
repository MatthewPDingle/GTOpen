"""Tests for the scaling-law fit and data subsets (no GPU or torch needed).

    python tools/leafnet/test_scaling.py
"""
import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scaling  # noqa: E402


class ScalingTests(unittest.TestCase):
    def test_fit_recovers_a_known_law(self):
        true = {"E": 0.1376, "A": 0.5, "a": 0.45, "B": 2.0, "b": 0.6}
        N = np.array([1.3e5, 3.3e5, 7.9e5, 1.3e6, 2.6e6] * 5, float)
        D = np.repeat([3_600, 7_300, 14_600, 29_000, 58_500], 5).astype(float)
        err = scaling.predict_law(true, N, D) + np.random.default_rng(0).normal(0, 2e-6, len(N))
        f = scaling.fit_law(N, D, err)
        self.assertAlmostEqual(f["E"], true["E"], delta=3e-4)
        self.assertAlmostEqual(f["a"], true["a"], delta=0.05)
        self.assertAlmostEqual(f["b"], true["b"], delta=0.05)
        self.assertLess(f["rmse"], 1e-5)
        # extrapolating in data stays close to the true law
        self.assertAlmostEqual(float(scaling.predict_law(f, 1.3e6, 240_000)),
                               float(scaling.predict_law(true, 1.3e6, 240_000)), delta=2e-4)

    def test_coefficients_stay_nonnegative(self):
        N = np.array([1e5, 1e6] * 3, float)
        D = np.repeat([1e4, 2e4, 4e4], 2).astype(float)
        err = np.full(len(N), 0.14)          # flat: nothing helps
        f = scaling.fit_law(N, D, err)
        self.assertGreaterEqual(min(f["A"], f["B"], f["E"]), 0)
        self.assertAlmostEqual(f["E"], 0.14, places=6)

    def test_an_unidentified_exponent_is_flagged(self):
        # error falls with data far faster than any exponent in the search range allows
        N = np.array([1e5, 1e6] * 4, float)
        D = np.repeat([1e4, 1.4e4, 2e4, 4e4], 2).astype(float)
        err = 0.138 + 1e30 * D ** -8.0 + 1e-3 * (N / 1e5) ** -0.5
        f = scaling.fit_law(N, D, err)
        self.assertIn("b", f["at_edge"])
        md = scaling.markdown("snap", {"val_class": {
            "fit": f, "min_fraction": 0.25, "full_data": [],
            "points": [{"params": 1, "train_examples": 1, "error": 0.1, "seeds": 1, "fitted": True}] * 6,
            "predictions": []}}, 1_572_864)
        self.assertIn("Warning", md)

    def test_subsets_are_nested_whole_jobs(self):
        jobs = np.repeat(np.arange(1000, 1200), 100)
        masks = {fr: scaling.subset_mask(jobs, fr) for fr in (0.0625, 0.25, 0.5, 1.0)}
        self.assertTrue(masks[1.0].all())
        for small, big in [(0.0625, 0.25), (0.25, 0.5), (0.5, 1.0)]:
            self.assertTrue((masks[small] <= masks[big]).all())
        self.assertEqual(masks[0.25].sum(), 50 * 100)
        for fr, m in masks.items():   # every job is all in or all out
            for j in np.unique(jobs):
                sel = m[jobs == j]
                self.assertTrue(sel.all() or not sel.any())

    def test_report_holds_out_the_full_data(self):
        true = {"E": 0.1376, "A": 0.5, "a": 0.45, "B": 2.0, "b": 0.6}
        rows = []
        for n in (1.3e5, 7.9e5, 2.6e6):
            for d in (3_600, 7_300, 14_600, 20_500, 29_000, 41_000, 58_500):
                for seed in range(2):
                    rows.append({"params": int(n), "train_examples": d, "seed": seed,
                                 "val_class": float(scaling.predict_law(true, n, d)),
                                 "leaf_class:x": float(scaling.predict_law(true, n, d)) + 0.014})
        manifest = {"examples": 73_000, "examples_by_split": {"train": 58_500}}
        rep = scaling.fit_report(rows, manifest, 1_572_864)
        self.assertEqual(set(rep), {"val_class", "leaf_class:x"})
        v = rep["val_class"]
        self.assertLess(v["holdout_full_data"]["max_abs_error"], 5e-4)
        # the two smallest fractions are listed but left out of the fit
        self.assertEqual(sum(p["fitted"] for p in v["points"]), 3 * 5)
        self.assertEqual(len(v["full_data"]), 3)
        self.assertLess(max(abs(p["miss"]) for p in v["full_data"]), 1e-5)
        self.assertEqual(v["fit"]["at_edge"], [])
        self.assertEqual([p["examples"] for p in rep["val_class"]["predictions"]],
                         [73_000, 100_000, 150_000, 300_000, 1_000_000])
        md = scaling.markdown("snap", rep, 1_572_864)
        self.assertIn("| 300,000", md)


if __name__ == "__main__":
    unittest.main()
