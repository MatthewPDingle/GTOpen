import unittest
import numpy as np
import continuation_pair_values as model


class PairValueChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.counts,cls.eq=model.study.pilot.matrices()

    def context(self,seed,stack=200):
        rng=np.random.default_rng(seed);w=rng.uniform(.001,1,(2,169))
        case=dict(weights=w.tolist(),pot=20.,stack=stack)
        c=model.study.pilot.context(case,self.counts,self.eq);c['case']=case
        c['observed']=np.ones((2,169))
        return c

    def candidate(self):
        rng=np.random.default_rng(24)
        return dict(hand_adjustment=rng.normal(0,.2,169).tolist(),position_adjustment=rng.normal(0,.1,169).tolist())

    def test_pair_complement_feature_equivalence_and_accounting(self):
        m=self.candidate();pair=model.pair_values(m,self.eq)
        np.testing.assert_allclose(pair[0]+pair[1].T,1,atol=1e-14,rtol=0)
        for stack in [0,20,80,200]:
            c=self.context(13,stack);actual=model.predict(c,m,self.counts,self.eq)
            expected=c['raw']+model.features(c,self.counts)@np.r_[m['hand_adjustment'],m['position_adjustment']]
            np.testing.assert_allclose(actual,expected,atol=1e-14,rtol=0)
            self.assertAlmostEqual(float((actual*c['mass']).sum()),1,places=12)
            if not stack:np.testing.assert_allclose(actual,c['raw'],atol=0,rtol=0)

    def test_fit_recovers_synthetic_pair_values_on_unseen_ranges(self):
        truth=self.candidate();cases=[self.context(i) for i in range(4)]
        for c in cases:c['residual']=model.predict(c,truth,self.counts,self.eq)-c['raw']
        fitted=model.fit(cases,self.counts,regularization=0)
        c=self.context(123,80)
        np.testing.assert_allclose(model.predict(c,fitted,self.counts,self.eq),model.predict(c,truth,self.counts,self.eq),atol=1e-11,rtol=0)
        self.assertAlmostEqual(sum(fitted['hand_adjustment']),0,places=12)

    def test_constant_hand_offset_is_irrelevant_and_values_are_not_clipped(self):
        c=self.context(5);m=self.candidate();pred=model.predict(c,m,self.counts,self.eq)
        shifted=dict(m,hand_adjustment=(np.array(m['hand_adjustment'])+5).tolist())
        np.testing.assert_allclose(model.predict(c,shifted,self.counts,self.eq),pred,atol=1e-14,rtol=0)
        extreme=dict(hand_adjustment=[0.]*169,position_adjustment=[1.]*169)
        out=model.predict(c,extreme,self.counts,self.eq)
        self.assertTrue((out[0]<0).all() and (out[1]>1).all())
        self.assertAlmostEqual(float((out*c['mass']).sum()),1,places=12)


if __name__=='__main__':unittest.main()
