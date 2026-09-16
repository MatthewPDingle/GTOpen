import unittest
import numpy as np
import continuation_range_sensitivity as diagnostic


class RangeSensitivityChecks(unittest.TestCase):
    def test_mass_shift_is_bounded_and_preserves_other_player(self):
        weights=np.ones((2,169));weights[1,::2]=.3
        original=weights.copy();mask=np.arange(169)%14==0
        shifted,tv=diagnostic.perturb(weights,0,mask,.01)
        combos=diagnostic.study.pilot.COMBOS
        expected=weights*combos;expected/=expected.sum(axis=1,keepdims=True)
        actual=shifted*combos
        np.testing.assert_allclose(actual.sum(axis=1),1)
        np.testing.assert_allclose(actual[1],expected[1])
        self.assertAlmostEqual(tv,.01*(1-expected[0,mask].sum()))
        np.testing.assert_array_equal(weights,original)

    def test_empty_target_refused(self):
        with self.assertRaises(AssertionError):diagnostic.perturb(np.ones((2,169)),0,np.zeros(169,dtype=bool),.01)


if __name__=='__main__':unittest.main()
