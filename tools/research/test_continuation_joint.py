"""Scientific invariants for the research-only joint continuation estimator."""
import copy
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest

import numpy as np

spec = importlib.util.spec_from_file_location("continuation_joint", Path(__file__).with_name("continuation_joint.py"))
j = importlib.util.module_from_spec(spec)
spec.loader.exec_module(j)


def row(case="case", rake=0, board="Ac7d2h", weight=1, ev=(8, 12)):
    return dict(job=dict(case=case, rake_pct=rake, board=board,
                         config=dict(tree=dict(starting_pot=20, effective_stack=80, rake_pct=rake/100, rake_cap=3))),
                weight=weight, reference_ev_bb=list(ev), reference_equity=[.4, .6],
                preflop_leaf=dict(equity=[.4, .6], raw_bb=[8, 12], static_bb=[7.7, 12.3], calibrated_bb=[6.5, 10.5]))


class JointEstimatorTests(unittest.TestCase):
    def test_mixed_binary_or_cache_corpus_is_rejected(self):
        first = dict(provenance=dict(binary_sha256="binary", source_sha256={
            "cache/realization_fit.json": "fit", "cache/preflop_eq169.bin": "equity"}))
        self.assertEqual(j.validate_provenance([first, copy.deepcopy(first)]), ("binary", "fit", "equity"))
        for field in ["binary", "fit", "equity"]:
            changed = copy.deepcopy(first)
            if field == "binary":
                changed["provenance"]["binary_sha256"] = "changed"
            else:
                path = "cache/realization_fit.json" if field == "fit" else "cache/preflop_eq169.bin"
                changed["provenance"]["source_sha256"][path] = "changed"
            with self.assertRaises(j.IntegrityError):
                j.validate_provenance([first, changed])

    def test_optimized_interpreter_retains_integrity_guards(self):
        script = f"""
import importlib.util
spec = importlib.util.spec_from_file_location('audit', {str(Path(j.__file__).resolve())!r})
j = importlib.util.module_from_spec(spec)
spec.loader.exec_module(j)
def item(binary):
    return {{'provenance': {{'binary_sha256': binary, 'source_sha256': {{'cache/realization_fit.json': 'fit', 'cache/preflop_eq169.bin': 'eq'}}}}}}
try:
    j.validate_provenance([item('first'), item('second')])
except j.IntegrityError:
    pass
else:
    raise RuntimeError('Optimized Python bypassed the integrity guard')
"""
        result = subprocess.run([sys.executable, "-O", "-c", script], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout+result.stderr)

    def test_prediction_has_no_flop_or_reference_outcome_input(self):
        model = dict(rake_multiplier=1.7, transfer_intercept=-.02, transfer_equity_slope=.04)
        before = row(rake=5)
        after = copy.deepcopy(before)
        after["job"]["board"] = "KsKhKd"
        after["reference_ev_bb"] = [-70, 88]
        after["reference_equity"] = [.01, .99]
        self.assertEqual(j.predict(before, model)[0].tolist(), j.predict(after, model)[0].tolist())
        self.assertEqual(j.predict(before, model)[1], j.predict(after, model)[1])

    def test_joint_accounting_and_physical_limits(self):
        for rate in [0, 5]:
            for q in [0, .01, .5, .99, 1]:
                for transfer in [-20, 0, 20]:
                    r = row(rake=rate)
                    r["preflop_leaf"]["equity"][0] = q
                    value, rake = j.predict(r, dict(rake_multiplier=5, transfer_intercept=transfer, transfer_equity_slope=1))
                    self.assertAlmostEqual(float(value.sum())+rake, 20)
                    self.assertGreaterEqual(min(value), -80)
                    self.assertLessEqual(max(value), 100-rake)
                    self.assertTrue((rake == 0) if rate == 0 else (1 <= rake <= 3))

    def test_case_rake_fitting_weights_preserve_relative_board_mass(self):
        rows = [row(case=case, rake=rake, weight=w) for case in ["A", "B"] for rake in [0, 5] for w in [1, 3]]
        w = j.normalized_weights(rows)
        self.assertAlmostEqual(float(w.sum()), 1)
        for i in range(0, 8, 2):
            self.assertAlmostEqual(float(w[i:i+2].sum()), .25)
            self.assertAlmostEqual(float(w[i+1]/w[i]), 3)

    def test_zero_rake_cap_means_uncapped_not_rake_free(self):
        r = row(rake=5)
        r["job"]["config"]["tree"]["rake_cap"] = 0
        value, rake = j.predict(r, dict(rake_multiplier=4, transfer_intercept=0, transfer_equity_slope=0))
        self.assertAlmostEqual(rake, 4)
        self.assertAlmostEqual(float(value.sum()), 16)

    def test_holdout_uses_pair_and_inclusion_weights_not_equal_boards(self):
        rows = [row(rake=rake, board=board, weight=w, ev=ev) for rake in [0, 5]
                for board, w, ev in [("A", 1, [0, 20]), ("B", 3, [8, 12])]]
        model = dict(rake_multiplier=1, transfer_intercept=0, transfer_equity_slope=0)
        groups = j.grouped(rows, model)
        self.assertEqual(groups[0]["reference_ev_bb"], [6, 14])
        scaled = copy.deepcopy(rows)
        for r in scaled:
            r["weight"] *= 100
        self.assertEqual(j.grouped(scaled, model), groups)

    def test_fit_recovers_reference_transfer_without_using_legacy_values(self):
        rows = []
        for case, q in [("weak", .3), ("equal", .5), ("strong", .7)]:
            for rate in [0, 5]:
                for board, weight in [("A", 1), ("B", 3)]:
                    r = row(case=case, rake=rate, board=board, weight=weight)
                    rake = 2.0 if rate else 0.0
                    oop = (20-rake)*q+20*(-.02+.03*(q-.5))
                    r["reference_ev_bb"] = [oop, 20-rake-oop]
                    r["reference_expected_rake_bb"] = rake
                    r["preflop_leaf"]["equity"] = [q, 1-q]
                    rows.append(r)
        model = j.train(rows, 0)
        self.assertAlmostEqual(model["rake_multiplier"], 2)
        self.assertAlmostEqual(model["transfer_intercept"], -.02)
        self.assertAlmostEqual(model["transfer_equity_slope"], .03)
        changed = copy.deepcopy(rows)
        for r in changed:
            r["preflop_leaf"]["calibrated_bb"] = [-1000, 2000]
        self.assertEqual(j.train(changed, 0), model)


if __name__ == "__main__":
    unittest.main()
