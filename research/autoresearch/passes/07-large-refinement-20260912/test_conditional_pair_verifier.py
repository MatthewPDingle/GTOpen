"""Analytic pair-screen gate checks, including rejected/no-improvement cases."""
import copy
import unittest
from test_conditional_sampling_verifier import fixture
from check_conditional_pair import BLINDS, compare


def inputs():
    base = fixture()
    row = base['rows'][0]
    base['rows'] = [copy.deepcopy(row), copy.deepcopy(row)]
    for row, path in zip(base['rows'], BLINDS):
        row['path'] = path
    corrected = copy.deepcopy(base)
    corrected.update(pair_control=True, pair_extra_bytes=100)
    return base, corrected


class Screen(unittest.TestCase):
    def test_exact_correction_passes_and_unchanged_noise_fails(self):
        base, corrected = inputs()
        unchanged = compare(base, corrected, BLINDS)
        self.assertFalse(unchanged['screen_passed'])
        self.assertEqual(unchanged['weighted_variance_ratio'], 1.)
        for row in corrected['rows']:
            row['offset_action_values_raw_action_major'] = [row['full_action_values_raw_action_major'].copy() for _ in range(1024)]
        exact = compare(base, corrected, BLINDS)
        self.assertTrue(exact['screen_passed'])
        self.assertEqual(exact['weighted_variance_ratio'], 0.)

    def test_changed_reference_is_rejected(self):
        base, corrected = inputs()
        corrected['rows'][0]['full_action_values_raw_action_major'][0] += 1.
        with self.assertRaisesRegex(ValueError, 'Different frozen comparison'):
            compare(base, corrected, BLINDS)


if __name__ == '__main__':
    unittest.main()
