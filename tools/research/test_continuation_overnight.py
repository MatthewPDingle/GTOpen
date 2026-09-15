"""Split integrity, range transformation and predictor accounting checks."""
import copy
import json
import os
import unittest

import numpy as np
import continuation_overnight as night
import continuation_overnight_fit as trainer
import range_value_pilot as pilot


class OvernightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m=night.checked_manifest()
        cls.cases=json.loads((night.OUT/'fixtures.json').read_text())['cases']
        cls.counts,cls.eq=pilot.matrices()

    def context(self,case):
        c=pilot.context(case,self.counts,self.eq)
        c.update(case=case,base_x=c['x'].copy(),base_names=list(c['names']),
                 residual=.1*(c['raw']-.5),observed=(c['mass']>0).astype(float))
        return c

    def test_entire_sources_and_boards_are_separate(self):
        for field in ['family','source_sha256']:
            train={c[field] for c in self.cases if c['partition']=='train'}
            test={c[field] for c in self.cases if c['partition']=='test'}
            self.assertFalse(train&test)
        train={b['board'] for b in self.m['boards'] if b['partition']=='train'}
        test={b['board'] for b in self.m['boards'] if b['partition']=='test'}
        self.assertFalse(train&test);self.assertEqual((len(train),len(test)),(100,100))
        self.assertEqual(len(self.m['jobs']),3200)
        for c in self.cases:
            jobs=[j for j in self.m['jobs'] if j['case']==c['id']]
            self.assertEqual(len(jobs),100)
            self.assertTrue(all(j['partition']==c['partition'] for j in jobs))

    def test_cleaning_budget_and_probe_support(self):
        for c in self.cases:
            w=np.array(c['weights'])
            self.assertTrue(np.isfinite(w).all())
            self.assertTrue(all(x<=.001+1e-10 for x in c['removed_mass_fraction']))
            for hand in night.PROBES:
                self.assertTrue((w[:,pilot.INDEX[hand]]>=.0001).all())
            for p,label in enumerate(['range_oop','range_ip']):
                np.testing.assert_allclose(pilot.weights(c[label]),w[p],atol=1e-12)

    def test_range_scale_does_not_change_encoder_or_features(self):
        case=copy.deepcopy(self.cases[0]);c=self.context(case)
        enc=trainer.encoder([self.context(x) for x in self.cases[:5]],'pca8')
        before=copy.deepcopy(enc)
        case['weights']=(np.array(case['weights'])*np.array([[.2],[.3]])).tolist()
        scaled=self.context(case)
        np.testing.assert_allclose(trainer.features(c,enc)['x'],trainer.features(scaled,enc)['x'],atol=1e-10)
        self.assertEqual(enc,before)

    def test_fitted_candidates_conserve_pot_on_unseen_ranges(self):
        cases=[self.context(c) for c in self.cases[:6]]
        external=self.context(self.cases[-1])
        for kind in ['shape','pca8']:
            model=trainer.fit(cases,kind,.1)
            pred=trainer.predict(external,model)
            self.assertTrue(np.isfinite(pred).all())
            self.assertAlmostEqual(float((pred*external['mass']).sum()),1,places=10)
            # The zero-sum linear equity correction is representable; this
            # checks the train/predict feature order as well as normalization.
            error=np.abs(pred-(external['raw']+external['residual']))
            self.assertLess(float((error*external['mass']).sum()/2),.035)

    def test_process_liveness_uses_a_real_handle(self):
        self.assertTrue(night.process_alive(os.getpid()))
        self.assertFalse(night.process_alive(0))


if __name__=='__main__':unittest.main()
