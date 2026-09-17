import copy
import unittest
import numpy as np
import paired_continuation_study as study
import fit_paired_expansion as fit


class ExpandedControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packs=[p for _,p in study.training()[0]]

    def test_expanded_features_remain_centered(self):
        for p in self.packs:
            for c in p['contexts']:
                x=fit.diagnostic.design(c,'range54')
                np.testing.assert_allclose((x*c['mass'][...,None]).sum(axis=(0,1)),0,atol=1e-12)

    def test_null_model_preserves_both_action_estimators(self):
        for encoder,n in [('compact18',18),('range54',54)]:
            for p in self.packs:
                result=fit.score(p,dict(encoder=encoder,coefficients=np.zeros(n)))
                for key in ['direct','corrected']:
                    self.assertAlmostEqual(result['action_mae_bb'][key],result['baseline_action_mae_bb'][key],places=10)

    def test_expanded_paired_design_recovers_known_action_changes(self):
        packs=copy.deepcopy(self.packs)
        coef=np.random.default_rng(81).normal(size=54)*.0001
        for p in packs:
            for c in p['contexts']:c['corrected']=c['base']+fit.diagnostic.design(c,'range54')@coef
            p['reference_delta']['corrected']=p['base_delta']+fit.diagnostic.action_design(p,'range54')@coef
        found=fit.fit(packs,'range54',1e-12,4)
        for p in packs:
            x=fit.diagnostic.action_design(p,'range54')
            np.testing.assert_allclose(x@found,x@coef,atol=1e-7)

    def test_extreme_expanded_correction_respects_physical_bounds(self):
        coef=np.random.default_rng(82).normal(size=54)*100
        for p in self.packs:
            for c in p['contexts']:
                value=fit.prediction(c,dict(encoder='range54',coefficients=coef))
                self.assertAlmostEqual(float((value*c['mass']).sum()),1,places=8)


if __name__=='__main__':unittest.main()
