import unittest
import numpy as np
from complete_bank_root_stability_v1 import summarize


class StabilityTests(unittest.TestCase):
    def test_known_maximum_baseline_and_identical_candidates(self):
        p=np.zeros((4,169,4));p[0,:,0]=1;p[2,:,1]=1;p[1]=.25;p[3]=.25
        m=np.arange(1,170,dtype=float);m/=m.sum();r=summarize(p,m)
        self.assertAlmostEqual(r['comparisons']['baseline_cross_seed']['entry_weighted_total_variation'],1)
        self.assertEqual(r['comparisons']['candidate_cross_seed']['entry_weighted_total_variation'],0)
        self.assertAlmostEqual(r['candidate_minus_baseline_variation'],-1)
        self.assertAlmostEqual(r['comparisons']['first_matched_change']['entry_weighted_total_variation'],.75)
        np.testing.assert_allclose(r['aggregate_action_frequencies'],[[1,0,0,0],[.25]*4,[0,1,0,0],[.25]*4])

    def test_reject_invalid_probability_and_mass(self):
        p=np.full((4,169,4),.25);m=np.ones(169)/169
        for bad in (p[:3],p*2,np.full_like(p,np.nan)):
            with self.assertRaises(ValueError):summarize(bad,m)
        with self.assertRaises(ValueError):summarize(p,m*2)


if __name__=='__main__':unittest.main()
