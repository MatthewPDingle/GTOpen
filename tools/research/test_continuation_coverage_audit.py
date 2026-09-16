import unittest
import continuation_coverage_audit as audit


class CoverageTests(unittest.TestCase):
    def test_weight_concentration(self):
        self.assertAlmostEqual(audit.effective_count([1, 1, 1, 1]), 4)
        self.assertLess(audit.effective_count([100, 1, 1, 1]), 1.1)
        self.assertAlmostEqual(audit.effective_count([2, 6]), audit.effective_count([1, 3]))

    def fixture(self):
        weights = [0]*169
        weights[audit.LABELS.index('AA')] = 1
        hand = dict(hand='AA', pair_mass=1, ev_bb=5, br_ev_bb=5, equity=.5)
        case = dict(id='case', weights=[weights.copy(), weights.copy()])
        rows = [dict(target_met=True, hands=[[hand], [hand]],
                     job=dict(case='case', board='2c3d4h', stratum='rainbow', iso_weight=24, inclusion_probability=.1))]
        return case, rows

    def test_missing_positive_class_is_reported(self):
        case, rows = self.fixture()
        self.assertTrue(audit.summarize(case, rows)['all_positive_classes_observed'])
        case['weights'][0][audit.LABELS.index('KK')] = .001
        result = audit.summarize(case, rows)
        self.assertFalse(result['all_positive_classes_observed'])
        self.assertIn('KK', result['positions'][0]['missing_classes'])

    def test_duplicate_board_rejected(self):
        case, rows = self.fixture()
        with self.assertRaises(AssertionError):
            audit.summarize(case, rows*2)


if __name__ == '__main__':
    unittest.main()
