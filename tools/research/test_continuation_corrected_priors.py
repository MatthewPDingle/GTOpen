import unittest
from unittest.mock import patch
import numpy as np
import continuation_corrected_priors as model


class CorrectedPriorChecks(unittest.TestCase):
    def test_composition_matches_separate_components_and_preserves_accounting(self):
        counts,eq=model.study.pilot.matrices();rng=np.random.default_rng(31)
        case=dict(weights=rng.uniform(.01,1,(2,169)).tolist(),pot=20.,stack=80.)
        c=model.study.pilot.context(case,counts,eq);c['case']=case
        m=dict(priors=dict(class_base=model.prior.priors().tolist()),correction=dict(
            hand_adjustment=rng.normal(0,.1,169).tolist(),position_adjustment=rng.normal(0,.03,169).tolist()))
        expected=model.prior.predict(c,m['priors'],counts,eq)+model.correction.predict(c,m['correction'],counts,eq)-c['raw']
        np.testing.assert_allclose(model.predict(c,m,counts,eq),expected,atol=1e-14,rtol=0)
        pair=model.pair_values(m,eq)
        np.testing.assert_allclose(pair[0]+pair[1].T,1,atol=1e-14,rtol=0)
        self.assertAlmostEqual(float((expected*c['mass']).sum()),1,places=12)

    def test_both_fitting_stages_use_only_supplied_cases(self):
        cases=[dict(case=dict(id='allowed'),raw=np.array([.2]),residual=np.array([.3]))]
        with patch.object(model.prior,'fit',return_value={'fresh':True}) as fit_prior, \
             patch.object(model.prior,'predict',return_value=np.array([.4])), \
             patch.object(model.correction,'fit',return_value={'correction':True}) as fit_correction:
            result=model.fit(cases,None,None)
        self.assertIs(fit_prior.call_args.args[0],cases)
        supplied=fit_correction.call_args.args[0]
        self.assertEqual([c['case']['id'] for c in supplied],['allowed'])
        np.testing.assert_allclose(supplied[0]['residual'],[.1])
        np.testing.assert_allclose(cases[0]['residual'],[.3])
        self.assertEqual(result['priors'],{'fresh':True})


if __name__=='__main__':unittest.main()
