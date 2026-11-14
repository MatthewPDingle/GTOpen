"""Tests for leaf_fix.py (corrections files for PREFLOP_LEAF_FIX).

    python tools/leafnet/test_leaf_fix.py

No GPU or torch.
"""
import json
import os
import sys
import tempfile
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import leaf_fix  # noqa: E402
import leafnet_io  # noqa: E402


class LeafFixTest(unittest.TestCase):
    def test_small_pairs_are_the_pairs_from_22_to_99(self):
        parts = [leafnet_io.class_parts(i) for i in leaf_fix.SMALL_PAIRS]
        self.assertEqual(parts, [(r, r, False) for r in range(8)])  # rank 0 is the deuce, rank 7 the nine

    def test_known_changes(self):
        entries = leaf_fix.known(pairs=-0.0045, totals={"srp": -0.004, "4bet": 0.006, "3bet": 0.0})
        doc = leaf_fix.document(entries, "a test")
        self.assertEqual(leaf_fix.check(doc), (1, ["srp", "4bet"], []))
        every = entries[0]
        self.assertEqual(every["oop"], every["ip"])
        self.assertEqual([i for i, v in enumerate(every["oop"]) if v], list(leaf_fix.SMALL_PAIRS))
        self.assertTrue(all(every["oop"][i] == -0.0045 for i in leaf_fix.SMALL_PAIRS))
        # a total moves by the change: half on each player's every class
        srp = next(e for e in entries if e.get("pot_type") == "srp")
        self.assertEqual((srp["oop"], srp["ip"]), (-0.002, -0.002))
        rng = np.random.default_rng(1)
        w_oop, w_ip, _ = leafnet_io.dealt_weights(rng.random(169), rng.random(169))
        self.assertAlmostEqual(float(w_oop.sum() * srp["oop"] + w_ip.sum() * srp["ip"]), -0.004, places=12)
        self.assertEqual(leaf_fix.known(), [])

    def test_field_is_scaled_to_the_size_asked_for(self):
        rng = np.random.default_rng(2)
        rows = [{"line": f"P0 Raise 2.5 | P{k} Call 2.5", "weight": float(rng.random()) + 0.1,
                 "oop": list(rng.normal(0, 0.004, 169)), "ip": list(rng.normal(0, 0.007, 169)),
                 "oop_range": list(rng.random(169)), "ip_range": list(rng.random(169))} for k in range(1, 6)]
        entries, factor = leaf_fix.field(rows, 0.01)
        scaled = [dict(r, oop=e["oop"], ip=e["ip"]) for r, e in zip(rows, entries)]
        self.assertAlmostEqual(leaf_fix.mean_per_hand(scaled), 0.01, places=12)
        self.assertAlmostEqual(factor, 0.01 / leaf_fix.mean_per_hand(rows), places=12)
        np.testing.assert_allclose(entries[2]["ip"], factor * np.asarray(rows[2]["ip"]))
        self.assertEqual([e["line"] for e in entries], [r["line"] for r in rows])
        self.assertEqual(leaf_fix.check(leaf_fix.document(entries))[2], sorted(r["line"] for r in rows))
        # a class nobody holds does not count: its value can be anything
        rows[0]["oop_range"][5] = 0.0
        before = leaf_fix.mean_per_hand(rows)
        rows[0]["oop"][5] = 0.3
        self.assertAlmostEqual(leaf_fix.mean_per_hand(rows), before, places=15)
        with self.assertRaises(ValueError):
            leaf_fix.field([dict(rows[0], oop=[0.0] * 169, ip=[0.0] * 169)], 0.01)
        with self.assertRaises(ValueError):
            leaf_fix.field([dict(rows[0], oop=[0.0] * 5)], 0.01)

    def test_a_file_that_could_be_a_mistake_is_refused(self):
        good = {"format": "gtopen-leaf-fix", "version": 1, "entries": [{"oop": 0.01}]}
        leaf_fix.check(good)
        for entries, says in [
            ([{"oop": 1.5}], "fractions of the pot"),  # percent, not a fraction
            ([{"oop": [0.01, 0.02]}], "169 numbers"),
            ([{"oop": "0.01"}], "169 numbers"),
            ([{"pot_type": "srp", "line": "P0 Call 1", "oop": 0.01}], "not both"),
            ([{"pot_type": "5bet", "oop": 0.01}], "pot_type"),
            ([{"pot": "srp", "oop": 0.01}], "unknown key"),
            ([{"oop": 0.01}, {"ip": 0.01}], "second entry"),
            ([{"line": "A | B", "oop": 0.01}, {"line": "A | B", "ip": 0.01}], "second entry"),
            ([{"line": " ", "oop": 0.01}], "empty line"),
        ]:
            with self.assertRaises(ValueError, msg=entries) as cm:
                leaf_fix.check(dict(good, entries=entries))
            self.assertIn(says, str(cm.exception))
        for doc in ([], dict(good, version=2), {"format": "gtopen-leaf-fix", "version": 1}, dict(good, entry=[])):
            with self.assertRaises(ValueError, msg=doc):
                leaf_fix.check(doc)

    def test_command_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "known.json")
            self.assertEqual(leaf_fix.main(["known", "--pairs", "-0.0045", "--totals", "srp=-0.004,4bet=-0.0052", "--out", out]), 0)
            with open(out, encoding="utf-8") as f:
                doc = json.load(f)
            self.assertEqual(leaf_fix.check(doc), (1, ["srp", "4bet"], []))
            self.assertEqual(leaf_fix.main(["check", out]), 0)
            self.assertEqual(leaf_fix.main(["known", "--out", out]), 1)  # nothing to write
            self.assertEqual(leaf_fix.main(["known", "--totals", "river=0.1", "--out", out]), 1)
            table = os.path.join(tmp, "diff.json")
            with open(table, "w", encoding="utf-8") as f:
                json.dump({"lines": [{"line": "SB Raise 2.5 | BB Call 2.5", "weight": 1.0, "oop": [0.002] * 169, "ip": [-0.004] * 169,
                                      "oop_range": [1.0] * 169, "ip_range": [1.0] * 169}]}, f)
            scaled = os.path.join(tmp, "field.json")
            self.assertEqual(leaf_fix.main(["field", "--table", table, "--per-hand", "0.01", "--out", scaled]), 0)
            with open(scaled, encoding="utf-8") as f:
                e = json.load(f)["entries"][0]
            self.assertAlmostEqual(e["oop"][0], 0.002 / 0.003 * 0.01, places=12)
            self.assertAlmostEqual(e["ip"][0], -0.004 / 0.003 * 0.01, places=12)
            with open(scaled, "w", encoding="utf-8") as f:
                f.write("{}")
            self.assertEqual(leaf_fix.main(["check", scaled]), 1)


if __name__ == "__main__":
    unittest.main()
