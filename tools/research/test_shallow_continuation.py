"""Accounting, sample-design and boundary checks for shallow continuation research."""
import unittest
from unittest.mock import patch
import numpy as np
import shallow_continuation_audit as run
import shallow_continuation_fit as fit
import evaluate_shallow_continuation as evaluate


class ShallowChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest=run.checked()
        cls.target=cls.manifest['cases'][0]

    def test_confirmation_partition_covers_population_without_double_counting(self):
        old=run.read(run.old.OUT/'manifest.json')['boards']
        new=self.manifest['panels']['confirmation']
        self.assertFalse({b['board'] for b in old}&{b['board'] for b in new})
        pool=run.read(run.pilot.AUDIT/'fixtures.json')['canonical_flops']
        # Unit board counts, not suit multiplicities: each stratum's expansion
        # plus certainty records must exactly recover the 1,755-board frame.
        self.assertAlmostEqual(len(old)+sum(1/b['inclusion_probability'] for b in new),len(pool))
        self.assertEqual(len(new),100)
        for c in self.manifest['cases']:
            if c['partition']=='train': self.assertNotEqual(c['weights'],self.target['weights'])

    def test_exact_pair_accounting_and_payoff_bounds_under_extreme_coefficients(self):
        c=fit.context(self.target)
        for magnitude in [0.,1.,1000.,-1000.]:
            model=dict(coefficients=(np.arange(18)*magnitude).tolist())
            value=fit.predict(c,model)
            # Independently form legal deal weights, not the helper's mass.
            counts,_=run.pilot.matrices(); w=np.array(self.target['weights'])
            joint=counts*w[0,:,None]*w[1,None,:]
            total=(joint*(value[0,:,None]+value[1,None,:])).sum()/joint.sum()
            self.assertAlmostEqual(total,1.,places=10)
            spr=self.target['stack']/self.target['pot']
            self.assertGreaterEqual(value.min(),-spr-1e-9)
            self.assertLessEqual(value.max(),1+spr+1e-9)

    def test_allin_limit_and_small_stack_continuity(self):
        c=fit.context(self.target); raw=c['raw'].copy()
        model=dict(coefficients=(np.arange(18)*.1).tolist())
        c['case']=dict(c['case'],stack=0.)
        np.testing.assert_allclose(fit.predict(c,model),raw,atol=1e-14)
        c['case']['stack']=1e-8
        self.assertLess(abs(fit.predict(c,model)-raw).max(),1e-8)

    def test_certainty_rows_are_fixed_and_board_shock_cancels_in_control_variate(self):
        case=dict(pot=10.)
        labels=run.pilot.LABELS; rows=[]
        # One certainty board at 0.9 equity; two complement boards at 0.1/0.3.
        # EV tracks equity exactly plus a side-dependent fixed residual.
        for i,q in enumerate([.9,.1,.3]):
            hands=[]
            for side in range(2):
                eq=q if side==0 else 1-q; shift=.05 if side==0 else -.05
                hands.append([dict(hand=h,pair_mass=1.,equity=eq,ev_bb=10*(eq+shift),
                                   br_ev_bb=10*(eq+shift)) for h in labels])
            rows.append(dict(job=dict(iso_weight=1.,inclusion_probability=1. if i==0 else .5,stratum='s'),hands=hands))
        raw=np.full((2,169),.5)
        with patch.object(fit,'context',return_value=dict(raw=raw)):
            direct,cv=evaluate.bootstrap(case,rows,1,7,500)
        np.testing.assert_allclose(cv[:,0],.55,atol=1e-14)
        np.testing.assert_allclose(cv[:,1],.45,atol=1e-14)
        # The fixed board contributes 0.9/5 in every draw. Only complement
        # observations vary, so the exact endpoints are .31 and .47.
        self.assertAlmostEqual(direct[:,0].min(),.31)
        self.assertAlmostEqual(direct[:,0].max(),.47)


if __name__=='__main__': unittest.main()
