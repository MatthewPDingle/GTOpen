import copy
import unittest
import numpy as np
import paired_continuation_study as study
import paired_continuation_expansion as expansion


class PairedControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.families,_=study.training()

    def test_zero_correction_preserves_baseline(self):
        m=dict(coefficients=[0.]*18)
        for _,p in self.families:
            np.testing.assert_allclose(study.model.action_prediction(p,m),p['base_delta'],atol=1e-12)
            for c in p['contexts']:np.testing.assert_allclose(study.model.predict(c,m),c['base'],atol=1e-12)

    def test_shared_scaling_preserves_pot_and_payoff_bounds(self):
        rng=np.random.default_rng(773)
        for _,p in self.families:
            for c in p['contexts']:
                spr=c['case']['stack']/c['case']['pot']
                v=study.model.predict(c,dict(coefficients=rng.normal(size=18)*100))
                self.assertAlmostEqual(float((v*c['mass']).sum()),1.,places=8)
                self.assertGreaterEqual(v.min(),-spr-1e-8)
                self.assertLessEqual(v.max(),1+spr+1e-8)

    def test_known_residual_is_recovered_by_paired_fit(self):
        packs=[copy.deepcopy(p) for _,p in self.families]
        coef=np.random.default_rng(19).normal(size=18)*.001
        for p in packs:
            for c in p['contexts']:c['corrected']=c['base']+c['features']@coef
            p['reference_delta']['corrected']=p['base_delta']+p['action_x']@coef
        fit=study.model.fit(packs,1e-12,4)
        for p in packs:
            np.testing.assert_allclose(p['action_x']@np.array(fit['coefficients']),p['action_x']@coef,atol=1e-7)

    def test_new_fixture_reaches_follow_legal_probabilities(self):
        signatures=[]
        for family in ['linear','polar']:
            t=expansion.policy_tree(family);signatures.append(t['nodes'][0]['sigma'])
            for node in t['nodes']:
                if node['kind']!=0:continue
                s=np.array(node['sigma']).reshape(-1,169)
                np.testing.assert_allclose(s.sum(axis=0),1,atol=1e-12)
                self.assertTrue((s>0).all())
                for a,child in enumerate(node['children']):
                    expected=np.array(node['reaches']);expected[node['actor']]*=s[a]
                    np.testing.assert_allclose(t['nodes'][child]['reaches'],expected,atol=1e-12)
        self.assertFalse(np.allclose(*signatures))


if __name__=='__main__':unittest.main()
