import unittest
import numpy as np
import continuation_own_drift_fit as fit


class OwnMeanChecks(unittest.TestCase):
    def test_tilt_preserves_support_and_opponent(self):
        w = np.ones((2, 169)); w[:, ::3] = 0
        mask = np.arange(169)%14 == 0
        shifted,tv = fit.tilt(w, 0, mask)
        self.assertTrue(np.array_equal(shifted==0, w==0))
        combos = fit.study.pilot.COMBOS
        before=w*combos; before/=before.sum(axis=1,keepdims=True)
        np.testing.assert_allclose(shifted[1]*combos,before[1])
        self.assertAlmostEqual(tv,.001*(1-before[0,mask].sum()))
        self.assertIsNone(fit.tilt(w,0,np.ones(169,dtype=bool)))

    def test_signed_mean_allows_compensating_hand_changes(self):
        z=np.zeros((2,169,104)); after=z.copy();mass=np.zeros((2,169));mass[:,:2]=.5
        after[0,0,0]=.1;after[0,1,0]=-.1;after[1,:,0]=10
        np.testing.assert_array_equal(fit.direction(z,after,mass,0,.01),np.zeros(104))
        after[0,1,0]=.1
        g=fit.direction(z,after,mass,0,.01)
        self.assertAlmostEqual(g[0],10.)
        coef=np.zeros(104);coef[0]=2
        self.assertAlmostEqual(float(coef@np.outer(g,g)@coef),400.)


if __name__=='__main__':unittest.main()
