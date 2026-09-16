import unittest
import numpy as np
import continuation_equity_moments as model


class EquityMomentChecks(unittest.TestCase):
    def test_distinguishes_equal_mean_ranges_with_different_matchup_distributions(self):
        counts=np.ones((169,169));eq=np.ones((169,169))*.5
        eq[:,1]=.2;eq[:,2]=.8
        a=np.zeros((2,169));a[0,0]=1;a[1,1:3]=.5
        b=a.copy();b[1,:]=0;b[1,3]=1
        first=model.moments(dict(case=dict(weights=a.tolist())),counts,eq)
        second=model.moments(dict(case=dict(weights=b.tolist())),counts,eq)
        np.testing.assert_allclose(first[0,:,0],.34,atol=1e-14,rtol=0)
        np.testing.assert_allclose(second[0,:,0],.25,atol=1e-14,rtol=0)
        self.assertEqual(float((eq[0]*a[1]).sum()),float((eq[0]*b[1]).sum()))

    def test_compatible_weighted_moments_and_features_are_scale_invariant(self):
        counts,eq=model.study.pilot.matrices();rng=np.random.default_rng(77)
        w=rng.uniform(.001,1,(2,169));case=dict(weights=w.tolist(),pot=20.,stack=160.)
        c=model.study.pilot.context(case,counts,eq);c.update(case=case,base_x=c['x'].copy(),base_names=list(c['names']))
        actual=model.moments(c,counts,eq)
        for side in range(2):
            for h in [0,24,83,168]:
                weighted=counts[h]*w[1-side]
                expected=[sum(weighted[j]*eq[h,j]**k for j in range(169))/sum(weighted) for k in [2,3,4]]
                np.testing.assert_allclose(actual[side,h],expected,atol=1e-14,rtol=0)
        encoded=model.features(c,counts,eq)
        other=dict(case,weights=(w*np.array([.7,2.3])[:,None]).tolist())
        d=model.study.pilot.context(other,counts,eq);d.update(case=other,base_x=d['x'].copy(),base_names=list(d['names']))
        shifted=model.features(d,counts,eq)
        self.assertEqual(encoded['names'],shifted['names'])
        np.testing.assert_allclose(encoded['x'],shifted['x'],atol=1e-13,rtol=0)


if __name__=='__main__':unittest.main()
