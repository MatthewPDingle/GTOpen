import copy
import json
from pathlib import Path
import unittest

import score


class ReferenceTests(unittest.TestCase):
    def setUp(self):
        self.capture = json.loads((Path(__file__).parent / "ui-captures.json").read_text())
        self.refs = score.references(self.capture)

    def candidate(self, hand="99", action="Fold"):
        ref = self.refs["nl25-utg-open"][hand]
        return {"context": self.capture["context"], "cases": [{
            "id": "nl25-utg-open", "hands": {hand: {a: float(a == action) for a in ref}}}]}

    def test_indifferent_mix_not_punished(self):
        row = score.score(self.capture, self.candidate())["rows"][0]
        self.assertEqual(row["local_regret_bb"], 0)
        self.assertGreater(row["frequency_total_variation"], .7)

    def test_costly_fold_detected(self):
        result = score.score(self.capture, self.candidate("AA"))
        self.assertAlmostEqual(result["rows"][0]["local_regret_bb"], 18.79)
        self.assertFalse(result["complete_probe_coverage"])

    def test_wrong_config_refused(self):
        c = copy.deepcopy(self.candidate())
        c["context"]["rake_pct"] = 5
        with self.assertRaisesRegex(ValueError, "Configuration"):
            score.score(self.capture, c)

    def test_wrong_actions_refused(self):
        c = self.candidate()
        c["cases"][0]["hands"]["99"]["Raise 7"] = 0
        with self.assertRaisesRegex(ValueError, "action"):
            score.score(self.capture, c)

    def test_stale_hand_refused(self):
        c = copy.deepcopy(self.capture)
        c["cases"][0]["probes"][0]["combos"][0]["combo"] = "0_KsKh"
        with self.assertRaisesRegex(ValueError, "Wrong hand"):
            score.references(c)

    def test_nan_refused(self):
        c = self.candidate()
        c["cases"][0]["hands"]["99"]["Fold"] = float("nan")
        with self.assertRaisesRegex(ValueError, "Nonfinite"):
            score.score(self.capture, c)

    def test_suit_difference_requires_finer_scoring(self):
        c = copy.deepcopy(self.capture)
        c["cases"][0]["probes"][0]["combos"][0]["actions"][0]["ev"] = "12"
        with self.assertRaisesRegex(ValueError, "Suit-specific"):
            score.references(c)


if __name__ == "__main__":
    unittest.main()
