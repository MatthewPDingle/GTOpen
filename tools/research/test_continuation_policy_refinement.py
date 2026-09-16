"""Scientific data-boundary and frozen-fit checks for the targeted-data study."""
import collections
import unittest

import numpy as np
import continuation_policy_refinement as study


class ProtocolChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dev = study.checked('development')
        cls.test = study.checked('evaluation')

    def test_board_and_family_separation(self):
        old = study.night.checked_manifest()
        dev = {b['board'] for b in self.dev['boards']}
        test = {b['board'] for b in self.test['boards']}
        historical = {j['board'] for j in old['jobs']}
        self.assertFalse(dev & test)
        self.assertFalse((dev | test) & historical)
        self.assertEqual(sorted(collections.Counter(b['stratum'] for b in self.dev['boards']).values()), [20]*5)
        self.assertEqual(sorted(collections.Counter(b['stratum'] for b in self.test['boards']).values()), [10]*5)
        fixtures = study.read(study.night.OUT/'fixtures.json')['cases']
        training = {c['family'] for c in fixtures if c['partition']=='train'} | {c['family'] for c in self.dev['cases']}
        self.assertFalse(training & {c['family'] for c in self.test['cases']})

    def test_reused_results_are_identical_physical_solves(self):
        self.assertEqual(len(self.dev['jobs']),160)
        self.assertEqual(len(self.dev['reused']),40)
        self.assertEqual(len(self.test['jobs']),100)
        for source in self.dev['reused']:
            path = study.ROOT/source['source']
            self.assertEqual(study.pilot.sha(path),source['sha256'])
            old = study.read(path)
            self.assertTrue(old['target_met'])
            self.assertTrue(study.same_job(old['job']['config'],source['job']['config']))
            self.assertAlmostEqual(source['job']['inclusion_probability'],5*old['job']['inclusion_probability'])

    def test_original_training_pipeline_reproduces_frozen_model(self):
        original = study.fit.load_cases('train')
        fitted = study.fit.fit(original,'shape',.1)
        frozen = study.read(study.night.OUT/'candidate.json')
        self.assertEqual(fitted['feature_names'],frozen['feature_names'])
        for field in ['mean','scale','coef']:
            np.testing.assert_allclose(fitted[field],frozen[field],rtol=1e-10,atol=1e-12)
        for c in original:
            pred = study.fit.predict(c,fitted)
            self.assertTrue(np.isfinite(pred).all())
            self.assertAlmostEqual(float((pred*c['mass']).sum()),1,places=12)


if __name__=='__main__':
    unittest.main()
