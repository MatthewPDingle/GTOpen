import copy
import unittest

import analyze
import run


class BaselineTests(unittest.TestCase):
    def test_class_order(self):
        self.assertEqual(analyze.hand_index("AA"), 168)
        self.assertEqual(analyze.hand_index("22"), 0)
        self.assertEqual(analyze.hand_index("A5s"), 159)
        self.assertEqual(analyze.hand_index("KQo"), 141)
        self.assertNotEqual(analyze.hand_index("KQs"), analyze.hand_index("KQo"))

    def test_configuration_gate(self):
        ref = analyze.read(analyze.REF / "ui-captures.json")
        cfg = run.configuration()
        analyze.audited_context(cfg, ref)
        for field, bad in (("rake_pct", 5), ("max_raises", 3), ("stack", 100), ("allin_threshold", .85)):
            changed = copy.deepcopy(cfg)
            changed[field] = bad
            with self.assertRaises(AssertionError):
                analyze.audited_context(changed, ref)
        changed = copy.deepcopy(cfg)
        changed["posts"][6] = .4
        with self.assertRaises(AssertionError):
            analyze.audited_context(changed, ref)

    def test_raise_conversion_separates_depths(self):
        cfg = run.configuration()
        threshold = cfg["stack"] * cfg["allin_threshold"]
        fourbets = [r * m for r in (18, 24, 27, 30) for m in (2.25, 2.5)]
        self.assertLess(max(fourbets), threshold)
        self.assertGreater(min(fourbets) * 2.25, threshold)

    def test_action_amounts_not_multiplier_labels(self):
        self.assertEqual(analyze.action_name({"kind": "raise", "to": 45, "label": "4-bet 2.5x"}), "Raise 45")
        self.assertEqual(analyze.action_name({"kind": "jam", "to": 200}), "Allin 200")
        self.assertEqual(analyze.action_name({"kind": "call", "to": 18}), "Call")
        with self.assertRaises(ValueError):
            analyze.action_name({"kind": "check", "to": 0})

    def test_production_write_guard(self):
        with self.assertRaisesRegex(ValueError, "Production writes"):
            run.request("spot", {}, production=True)


if __name__ == "__main__":
    unittest.main()
