import unittest
import numpy as np
import continuation_recalibrated_priors as model


class PriorChecks(unittest.TestCase):
    def test_pair_symmetry_and_scale_invariance(self):
        _,eq=model.study.pilot.matrices();q=model.priors()
        original=model.shares(q,eq)
        np.testing.assert_allclose(original[0]+original[1].T,1.,atol=1e-14,rtol=0)
        np.testing.assert_allclose(model.shares(q*7.3,eq),original,atol=1e-14,rtol=0)

    def test_physical_pair_weighted_accounting_and_zero_stack_equity(self):
        counts,eq=model.study.pilot.matrices();w=np.ones((2,169))*.001
        w[0,[0,40,90]]=[1,.2,.6];w[1,[0,35,168]]=[.2,1,.5]
        case=dict(weights=w.tolist(),pot=20.,stack=200.)
        c=model.study.pilot.context(case,counts,eq);c['case']=case
        q=model.priors();prob=model.opponent_probabilities(c,counts)
        expected=np.array([(prob[p]*model.shares(q,eq)[p]).sum(axis=1) for p in range(2)])
        actual=model.predict(c,dict(class_base=q.tolist()),counts,eq)
        np.testing.assert_allclose(actual,expected,atol=1e-14,rtol=0)
        self.assertAlmostEqual(float((actual*c['mass']).sum()),1.,places=12)
        c['case']['stack']=0
        np.testing.assert_allclose(model.predict(c,dict(class_base=q.tolist()),counts,eq),c['raw'],atol=1e-14,rtol=0)


if __name__=='__main__':unittest.main()
