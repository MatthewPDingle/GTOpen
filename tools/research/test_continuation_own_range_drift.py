import unittest
import numpy as np
from continuation_own_range_drift import components


class DriftChecks(unittest.TestCase):
    def test_signed_cancellation_is_not_absolute_stability(self):
        mass = np.zeros((2, 169)); mass[:, :2] = .5
        before = np.zeros((2, 169)); after = before.copy()
        after[0, :2] = [.1, -.1]
        r = components(before, after, mass, .01)
        self.assertEqual(r['signed'], [0., 0.])
        self.assertAlmostEqual(r['absolute_per_tv'][0], 10.)

    def test_fixed_hand_values_have_zero_own_response(self):
        mass = np.full((2, 169), 1/169)
        before = np.full((2, 169), .5); after = before.copy()
        after[1] += .002
        r = components(before, after, mass, .001)
        self.assertEqual(r['absolute'][0], 0.)
        self.assertAlmostEqual(r['signed_per_tv'][1], 2.)
        with self.assertRaises(AssertionError): components(before, after, mass, 0.)


if __name__ == '__main__': unittest.main()
