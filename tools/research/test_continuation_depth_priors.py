import unittest
import numpy as np
import continuation_depth_priors as model


class DepthPriorChecks(unittest.TestCase):
    def test_interpolation_knots_clamping_and_midpoints(self):
        for i,s in enumerate(model.KNOTS):
            lo,hi,f=model.interpolation(s)
            self.assertAlmostEqual(model.KNOTS[lo]**(1-f)*model.KNOTS[hi]**f,s,places=12)
        self.assertEqual(model.interpolation(0),model.interpolation(1))
        self.assertEqual(model.interpolation(100),model.interpolation(20))
        self.assertEqual(model.interpolation(np.sqrt(8*16))[:2],(3,4))
        self.assertAlmostEqual(model.interpolation(np.sqrt(8*16))[2],.5,places=12)

    def test_zero_slope_matches_original_priors_and_depth_tables_complement(self):
        counts,eq=model.study.pilot.matrices();rng=np.random.default_rng(19)
        m=dict(knots=model.KNOTS.tolist(),base_priors=model.prior.priors().tolist(),
            intercept=rng.normal(0,.3,169).tolist(),slope=np.zeros(169).tolist())
        q=np.array(m['base_priors'])*np.exp(m['intercept'])
        for spr in [0,1,3,8,12,20]:
            case=dict(weights=rng.uniform(.001,1,(2,169)).tolist(),pot=20.,stack=spr*20)
            c=model.study.pilot.context(case,counts,eq);c['case']=case
            np.testing.assert_allclose(model.predict(c,m,counts,eq),model.prior.predict(c,dict(class_base=q.tolist()),counts,eq),atol=1e-14,rtol=0)
        m['slope']=rng.normal(0,.2,169).tolist();tables=model.tables(m,eq)
        np.testing.assert_allclose(tables[:,0]+tables[:,1].transpose(0,2,1),1,atol=1e-14,rtol=0)
        c['case']['stack']=240
        self.assertAlmostEqual(float((model.predict(c,m,counts,eq)*c['mass']).sum()),1,places=12)


if __name__=='__main__':unittest.main()
