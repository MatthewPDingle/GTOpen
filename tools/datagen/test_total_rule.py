"""Tests for the total rule and the dealt weights in leafnet_io (numpy only).

    python tools/datagen/test_total_rule.py

CASES is repeated in crates/solver/src/preflop/leaf_total.rs
(the_rule_gives_the_numbers_the_python_side_gives): the rule is fitted here
and applied there, so the two must give the same numbers.
"""
import os
import sys
import tempfile
import unittest

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import leafnet_io  # noqa: E402

VALID = {"rake_frac": [0.05, 0.05], "cap_over_pot": [0.02, 2.5], "pot_bb": [2.0, 120.0], "stack_over_pot": [0.2, 100.0]}
RULES = {
    "linear": {"form": "linear", "valid": VALID, "coef": {
        "limped": [0.848247, -0.005173, 0.029683, 0.003206], "srp": [0.922959, -0.035846, -0.016072, 0.001664],
        "3bet": [0.948199, -0.197748, -0.003144, 0.001279], "4bet": [0.969515, -0.548728, 0.001756, 0.000164]}},
    "share": {"form": "share", "valid": VALID, "coef": {
        "limped": [0.360482, -0.076927, -0.00048, -0.052659], "srp": [0.541384, -0.163357, 0.007368, -0.009273],
        "3bet": [0.813041, -0.296116, 0.018916, -0.030269], "4bet": [0.275882, -0.078548, -0.046622, 0.096291]}},
}
# form, pot type, pot bb, stack bb, rake, cap bb, total (None: the rule does not cover the leaf)
CASES = [
    ("linear", 1, 6.5, 97.0, 0.05, 3.0, 0.8808287),
    ("linear", 2, 22.0, 89.0, 0.05, 3.0, 0.9133026),
    ("linear", 3, 48.0, 76.0, 0.05, 3.0, 0.9420927),
    ("linear", 0, 2.0, 99.0, 0.05, 1.0, 0.8787449),
    ("linear", 3, 59.0, 41.0, 0.05, 3.0, 1 - 3 / 59),   # the rule says more rake than the cap allows: held to the cap
    ("share", 1, 6.5, 97.0, 0.05, 3.0, 0.8755634),
    ("share", 2, 22.0, 89.0, 0.05, 3.0, 0.9112382),
    ("share", 0, 2.0, 99.0, 0.05, 1.0, 0.8847601),
    ("share", 3, 48.0, 76.0, 0.05, 3.0, 0.9423788),
    ("share", 1, 10.0, 2.0, 0.05, 3.0, 0.93),            # a short stack: at most 5% of the pot plus both stacks
    ("linear", 1, 6.5, 97.0, 0.03, 3.0, None),           # a rake the rule was not fitted on
    ("linear", 1, 150.0, 30.0, 0.05, 30.0, None),        # a pot it was not fitted on
]


def cls(a, b, suited=False):
    hi, lo = max(a, b), min(a, b)
    return hi * 13 + hi if hi == lo else hi * 13 + lo if suited else lo * 13 + hi


class TotalRule(unittest.TestCase):
    def test_exact_totals(self):
        self.assertEqual(leafnet_io.leaf_total(None, 6.5, 97.0, 0.0, 0.0, "srp"), ("exact", 1.0))
        self.assertEqual(leafnet_io.leaf_total(RULES["linear"], 6.5, 97.0, 0.0, 3.0, 1), ("exact", 1.0))
        self.assertEqual(leafnet_io.leaf_total(None, 60.0, 70.0, 0.05, 3.0, "4bet"), ("exact", 1 - 3 / 60))
        self.assertEqual(leafnet_io.leaf_total(RULES["share"], 80.0, 60.0, 0.05, 3.0, 3), ("exact", 1 - 3 / 80))
        self.assertEqual(leafnet_io.leaf_total(None, 6.5, 97.0, 0.05, 3.0, 1), (None, None))
        self.assertEqual(leafnet_io.leaf_total(RULES["linear"], 6.5, 97.0, 0.05, 0.0, 1), (None, None))

    def test_rule_cases(self):
        for form, pot_type, pot, stack, rake, cap, want in CASES:
            kind, got = leafnet_io.leaf_total(RULES[form], pot, stack, rake, cap, pot_type)
            if want is None:
                self.assertEqual((kind, got), (None, None), (form, pot_type, pot))
            else:
                self.assertEqual(kind, "rule")
                self.assertAlmostEqual(got, want, places=6, msg=str((form, pot_type, pot)))
                self.assertEqual(leafnet_io.leaf_total(RULES[form], pot, stack, rake, cap, leafnet_io.POT_TYPES[pot_type])[1], got)

    def test_a_bad_rule_is_refused_when_a_net_is_written(self):
        for rule in RULES.values():
            leafnet_io.check_total_rule(rule)
        bad = [dict(RULES["linear"], form="cubic"), dict(RULES["linear"], valid={}),
               dict(RULES["linear"], coef=dict(RULES["linear"]["coef"], srp=[1, 0, 0])),
               dict(RULES["linear"], valid=dict(VALID, pot_bb=[100, 1]))]
        for rule in bad:
            with self.assertRaises(ValueError):
                leafnet_io.check_total_rule(rule)
        r = np.random.default_rng(0)
        Ws = [r.standard_normal((686, 3)).astype(np.float32), r.standard_normal((3, 338)).astype(np.float32)]
        bs = [np.zeros(3, np.float32), np.zeros(338, np.float32)]
        mu, sd = np.zeros(686, np.float32), np.ones(686, np.float32)
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "net.bin")
            leafnet_io.write(path, Ws, bs, mu, sd, extra={"total_rule": RULES["share"]})
            self.assertEqual(leafnet_io.read(path)[0]["total_rule"], RULES["share"])
            with self.assertRaises(ValueError):
                leafnet_io.write(path, Ws, bs, mu, sd, extra={"total_rule": bad[0]})
            with self.assertRaises(ValueError):
                leafnet_io.write_ensemble(path, [(Ws, bs, mu, sd)] * 2, extra={"total_rule": bad[1]})

    def test_dealt_weights(self):
        t = leafnet_io.disjoint_share()
        aa, kk, qq, aks, ako = cls(12, 12), cls(11, 11), cls(10, 10), cls(12, 11, True), cls(12, 11)
        self.assertAlmostEqual(t[aa, aa], 1 / 6)
        self.assertEqual(t[aa, kk], 1.0)
        self.assertAlmostEqual(t[aks, aks], 12 / 16)
        self.assertAlmostEqual(t[ako, ako], 7 / 12)
        self.assertAlmostEqual(t[aa, aks], 0.5)
        combos = np.array([6 if h // 13 == h % 13 else 4 if h // 13 > h % 13 else 12 for h in range(169)])
        np.testing.assert_allclose(t @ combos, 1225.0)   # any two cards leave 1,225 combos for the other player
        # aces and queens against ace-king suited: aces count half as much as queens
        oop, ip = np.zeros(169), np.zeros(169)
        oop[aa], oop[qq], ip[aks] = 0.5, 0.5, 3.0
        w_oop, w_ip, together = leafnet_io.dealt_weights(oop, ip)
        self.assertAlmostEqual(w_oop[aa], 1 / 3)
        self.assertAlmostEqual(w_oop[qq], 2 / 3)
        self.assertAlmostEqual(w_ip[aks], 1.0)
        self.assertAlmostEqual(float(together), 0.75 * 1326 / 1225)
        # the same two ranges and numbers as the Rust test (blocking_drops_what_the_other_range_holds)
        oop = np.array([(h * 37) % 11 + 1 if h % 2 == 0 else 0 for h in range(169)], float)
        ip = np.array([(g * 53) % 7 for g in range(169)], float)
        w_oop, w_ip, together = leafnet_io.dealt_weights(oop, ip)
        for got, want in [(w_oop[168], 0.0039421507), (w_oop[0], 0.0019710754), (w_ip[1], 0.0079351133),
                          (w_ip[160], 0.0058782930), (together, 1.0004269767)]:
            self.assertAlmostEqual(float(got), want, places=9)
        # two full ranges: every class by its combos, dealt together as often as the deck says; rows in a batch
        w_oop, w_ip, together = leafnet_io.dealt_weights(np.stack([combos, combos]), np.stack([combos, combos]))
        np.testing.assert_allclose(w_oop[1], combos / 1326)
        np.testing.assert_allclose(together, 1.0)


if __name__ == "__main__":
    unittest.main()
