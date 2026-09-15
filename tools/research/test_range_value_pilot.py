"""Accounting and source-parity tests for the research continuation model."""
import copy
import json
import unittest

import numpy as np

import range_value_pilot as p


class RangeValuePilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.counts, cls.eq = p.matrices()
        cls.case = json.loads((p.AUDIT/'fixtures.json').read_text())['cases'][0]

    def test_class_labels_and_compatible_deals(self):
        self.assertEqual(len(set(p.LABELS)),169)
        self.assertEqual(p.COMBOS.sum(),1326)
        self.assertEqual(self.counts[p.INDEX['AA'],p.INDEX['AA']],6)
        self.assertEqual(self.counts[p.INDEX['AA'],p.INDEX['KK']],36)
        np.testing.assert_allclose(self.eq+self.eq.T,1,atol=1e-12)

    def test_balanced_predictions_match_recorded_engine(self):
        c = p.context(self.case,self.counts,self.eq)
        for player in range(2):
            expected = np.array([h['value_bb'] for h in self.case['balanced']['hands'][player]])
            np.testing.assert_allclose(c['balanced'][player]*self.case['pot'],expected,atol=5e-6,rtol=1e-6)

    def test_range_weight_scale_invariance(self):
        original = p.context(self.case,self.counts,self.eq)
        scaled = copy.deepcopy(self.case)
        scaled['weights'] = (np.array(scaled['weights'])*np.array([[.2],[.7]])).tolist()
        other = p.context(scaled,self.counts,self.eq)
        for key in ['raw','balanced','mass','x']:
            np.testing.assert_allclose(original[key],other[key],atol=1e-12)

    def test_centering_conserves_pot_without_clipping_hand_values(self):
        c = p.context(self.case,self.counts,self.eq)
        n = c['x'].shape[-1]
        coef = np.zeros(n)
        coef[c['names'].index('equity')] = 10
        model = dict(mean=np.zeros(n),scale=np.ones(n),coef=coef)
        before = c['x'].copy()
        pred = p.predict(c,model)
        self.assertAlmostEqual(float((pred*c['mass']).sum()),1,places=10)
        self.assertGreater(pred.max(),1)
        np.testing.assert_array_equal(c['x'],before)

    def test_ridge_ignores_unobserved_labels(self):
        c = p.context(self.case,self.counts,self.eq)
        c['residual'] = np.zeros((2,169))
        c['observed'] = (c['mass']>0).astype(float)
        first = p.fit_ridge([c],1)
        c['residual'][c['observed'] == 0] = 1e6
        second = p.fit_ridge([c],1)
        np.testing.assert_array_equal(first['coef'],second['coef'])


if __name__ == '__main__':
    unittest.main()
