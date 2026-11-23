"""Tests for balance.py: weights that make each game mix count as meant, whatever cards solved it.

    python -m unittest tools/leafnet/test_balance.py

No GPU, no solve-cli, no torch: the pools are simulated here the way the generator draws (a card redraws
until a tree fits its cap, and a card rule has it pass over most small trees).
"""

import os
import sys
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import balance  # noqa: E402

MIX = ("mix", 7)


def simulate(cards, n_per_card, seed=0, rules=()):
    """A pool of one mix whose tree sizes (GB) are drawn log-uniform from 0.5 to 30. cards: [(cap, share)].
    Each card draws until it takes one, as datagen_mix::choose does. Returns groups, sizes, attempts."""
    rng = np.random.default_rng(seed)
    groups, sizes, attempts = [], [], []
    for cap, share in cards:
        rule = balance.rule_for(list(rules), cap)
        for _ in range(int(n_per_card * share)):
            for a in range(1000):
                gb = float(np.exp(rng.uniform(np.log(0.5), np.log(30))))
                if cap is not None and gb > cap:
                    continue
                if rule and gb < rule["under_gb"] and rng.uniform() >= rule["keep"]:
                    continue
                break
            groups.append((MIX, cap))
            sizes.append(gb * 1e9)
            attempts.append(a)
    return groups, sizes, attempts


def share_below(sizes, w, gb):
    sizes, w = np.asarray(sizes), np.asarray(w, np.float64)
    return float((w * (sizes < gb * 1e9)).sum() / w.sum())


INTENDED_BELOW_6 = np.log(6 / 0.5) / np.log(30 / 0.5)       # the mix's own share of trees under 6 GB


class BalanceTests(unittest.TestCase):
    def test_one_card_without_a_cap_needs_no_weights(self):
        groups, sizes, attempts = simulate([(None, 1.0)], 2000)
        w, report = balance.weights(groups, sizes, attempts, lambda m: [])
        np.testing.assert_allclose(w, 1.0)
        self.assertEqual(report["mix 7"]["effective_rows"], 2000)

    def test_small_and_big_cards_together_count_as_the_mix(self):
        groups, sizes, attempts = simulate([(6.0, 0.7), (27.0, 0.3)], 20000)
        raw = share_below(sizes, np.ones(len(sizes)), 6)
        w, report = balance.weights(groups, sizes, attempts, lambda m: [])
        self.assertGreater(raw, INTENDED_BELOW_6 + 0.15)            # the pool leans towards small trees
        self.assertAlmostEqual(share_below(sizes, w, 6), INTENDED_BELOW_6, delta=0.02)
        self.assertAlmostEqual(float(np.mean(w)), 1.0, places=5)     # a mix keeps its total
        cards = {c["cap_gb"]: c for c in report["mix 7"]["cards"]}
        self.assertAlmostEqual(cards[6.0]["draws_taken"], INTENDED_BELOW_6, delta=0.02)
        self.assertAlmostEqual(cards[27.0]["share"], 0.3, places=3)
        # a big tree only the big card takes weighs more than a small one every card takes
        big, small = np.asarray(sizes) > 10e9, np.asarray(sizes) < 2e9
        self.assertGreater(w[big].mean(), 2 * w[small].mean())

    def test_a_card_rule_is_undone_too(self):
        rules = [{"cap_from_gb": 12, "under_gb": 6, "keep": 0.25}]
        groups, sizes, attempts = simulate([(8.0, 0.6), (27.0, 0.4)], 20000, rules=rules)
        w, _ = balance.weights(groups, sizes, attempts, lambda m: rules)
        self.assertAlmostEqual(share_below(sizes, w, 6), INTENDED_BELOW_6, delta=0.02)
        # without telling it the rule, the big card's small trees would be counted as if it took them all
        w_wrong, _ = balance.weights(groups, sizes, attempts, lambda m: [])
        self.assertLess(share_below(sizes, w_wrong, 6), INTENDED_BELOW_6 - 0.05)

    def test_mixes_keep_their_totals_and_rows_outside_the_pool_keep_1(self):
        g1, s1, a1 = simulate([(6.0, 1.0)], 300, seed=1)
        g2, s2, a2 = simulate([(6.0, 0.5), (27.0, 0.5)], 600, seed=2)
        g2 = [(("generator", 4), cap) for _, cap in g2]
        groups = g1 + g2 + [None] * 5
        w, report = balance.weights(groups, s1 + s2 + [0] * 5, a1 + a2 + [0] * 5, lambda m: [])
        self.assertAlmostEqual(float(w[:300].sum()), 300, places=2)
        self.assertAlmostEqual(float(w[300:900].sum()), 600, places=2)
        np.testing.assert_array_equal(w[900:], 1.0)
        self.assertEqual(sorted(report), ["generator 4", "mix 7"])
        # one card alone cannot be balanced against anything: its rows stay even
        np.testing.assert_allclose(w[:300], 1.0, rtol=1e-6)

    def test_weights_are_clipped(self):
        groups, sizes, attempts = simulate([(2.0, 0.98), (27.0, 0.02)], 5000)
        w, report = balance.weights(groups, sizes, attempts, lambda m: [], clip=4)
        self.assertLessEqual(float(w.max()), 4 * 1.0001)
        self.assertAlmostEqual(float(w.mean()), 1.0, places=5)
        self.assertGreater(report["mix 7"]["clipped"], 0)

    def test_the_rule_a_card_follows(self):
        rules = [{"cap_from_gb": 12, "under_gb": 4, "keep": 0.5}, {"cap_from_gb": 19, "under_gb": 6, "keep": 0.25}]
        self.assertIsNone(balance.rule_for(rules, 6.0))
        self.assertEqual(balance.rule_for(rules, 12.0)["under_gb"], 4)
        self.assertEqual(balance.rule_for(rules, 27.0)["under_gb"], 6)
        self.assertEqual(balance.rule_for(rules, None)["under_gb"], 6)
        np.testing.assert_array_equal(balance.accept([3e9, 5e9, 20e9], 19.0, rules[1]), [0.25, 0.25, 0.0])

    def test_which_mix_a_job_belongs_to(self):
        self.assertEqual(balance.mix_of({"generator_version": 3, "job": 12}), ("generator", 3))
        self.assertEqual(balance.mix_of({"generator_version": 5, "mix": 2, "job": 2 << 44}), ("mix", 2))
        self.assertEqual(balance.mix_of({"generator_version": 6, "job": (3 << 44) + 9}), ("mix", 3))

    def test_the_published_mixes_load(self):
        rules = balance.load_rules()
        self.assertEqual(rules[1], [])
        self.assertIn(2, rules)


if __name__ == "__main__":
    unittest.main()
