"""Cross-check compact inference against the fitted dense design matrix."""
import unittest
import numpy as np
import continuation_hand_offsets as hand
import continuation_curvature as curve


class InferenceChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.cases=hand.study.fit.load_cases('train')

    def test_shape_control_matches_frozen_predictor(self):
        model=curve.fit(self.cases,'shape',.1)
        old=hand.study.read(hand.study.night.OUT/'candidate.json')
        for c in self.cases:
            np.testing.assert_allclose(curve.predict(c,model),hand.study.fit.predict(c,old),atol=1e-12,rtol=1e-10)

    def test_table_inference_matches_dense_fitting_for_all_variants(self):
        for kind in ['hand_bias','hand_equity','hand_equity_ip']:
            model=hand.fit(self.cases,kind,.1)
            for c in self.cases:
                dense=hand.predict(c,model);compact=hand.predict_compact(c,model)
                np.testing.assert_allclose(compact,dense,atol=1e-12,rtol=1e-10)
                self.assertAlmostEqual(float((compact*c['mass']).sum()),1,places=12)

    def test_curvature_dimensions_and_accounting(self):
        model=curve.fit(self.cases,'curvature',.1)
        self.assertEqual(len(model['coef']),128)
        self.assertEqual(len(set(model['feature_names'])),128)
        for c in self.cases:
            pred=curve.predict(c,model)
            self.assertTrue(np.isfinite(pred).all())
            self.assertAlmostEqual(float((pred*c['mass']).sum()),1,places=12)


if __name__=='__main__':unittest.main()
