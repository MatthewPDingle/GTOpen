import unittest
from unittest.mock import patch
import numpy as np
import continuation_hand_diagnostics as diagnostic


class HandGroupChecks(unittest.TestCase):
    def test_categories_cover_all_classes(self):
        labels=diagnostic.study.pilot.LABELS
        self.assertEqual(len(labels),169)
        self.assertEqual({diagnostic.group(h) for h in labels},set(diagnostic.GROUPS))
        self.assertEqual(sum(diagnostic.group(h)=='TT-AA' for h in labels),5)
        self.assertEqual(sum(diagnostic.group(h)=='22-99' for h in labels),8)

    def test_key_hands_do_not_cross_categories(self):
        self.assertEqual(diagnostic.group('KQo'),'Offsuit broadways')
        self.assertEqual(diagnostic.group('AKs'),'Suited broadways')
        self.assertEqual(diagnostic.group('A5s'),'Other suited aces')
        self.assertEqual(diagnostic.group('76s'),'Other suited hands')
        self.assertEqual(diagnostic.group('72o'),'Other offsuit hands')

    def test_position_diagnostics_normalize_separately_without_changing_inputs(self):
        mass=np.ones((2,169));mass[1]*=3
        original=mass.copy()
        predicted=np.ones((2,169))*.02;predicted[1]=-.04
        context=dict(case={'id':'synthetic'},raw=np.zeros((2,169)),
            residual=np.zeros((2,169)),mass=mass,observed=np.ones((2,169)),
            balanced=np.zeros((2,169)))
        with patch.object(diagnostic.study,'read',return_value={}), \
             patch.object(diagnostic.network,'predict',return_value=predicted), \
             patch.object(diagnostic.study.fit,'predict',return_value=predicted):
            pooled=diagnostic.summarize([context],{})
            oop=diagnostic.summarize([context],{},0)
            ip=diagnostic.summarize([context],{},1)
        self.assertAlmostEqual(pooled['cases'][0]['mae_pct_pot']['candidate'],3.5)
        self.assertAlmostEqual(oop['cases'][0]['mae_pct_pot']['candidate'],2.)
        self.assertAlmostEqual(ip['cases'][0]['mae_pct_pot']['candidate'],4.)
        for result,bias in [(oop,2.),(ip,-4.)]:
            self.assertAlmostEqual(sum(r['mass_fraction'] for r in result['groups']),1.)
            for row in result['groups']:self.assertAlmostEqual(row['candidate_bias'],bias)
        np.testing.assert_array_equal(mass,original)


if __name__=='__main__':unittest.main()
