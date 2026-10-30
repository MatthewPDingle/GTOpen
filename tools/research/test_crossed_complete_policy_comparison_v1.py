"""Synthetic orientation, transport and independent arithmetic checks."""
import math
import statistics
import unittest
import numpy as np
from crossed_complete_policy_comparison_v1 import (
    crossed_profiles, differences, CompletePolicyComparison, PROFILE_NAMES)


class ComparisonTests(unittest.TestCase):
    def test_transport_keeps_every_actors_policy_including_root(self):
        observations = [dict(hi=str(i), lo=str(i+7), actor=i % 2, n=2) for i in range(8)]
        q = dict(format=2, context_source='original context', batch_source='original batch', observations=observations)
        policies = np.zeros((4,8,4))
        for b in range(4):
            for i in range(8):
                policies[b,i,:2] = [(b*8+i+1)/40, 1-(b*8+i+1)/40]
        before = policies.copy()
        result = crossed_profiles(q, policies)
        self.assertEqual([r['name'] for r in result], list(PROFILE_NAMES))
        for profile in range(8):
            seed = profile//4
            bb, btn = divmod(profile % 4, 2)
            for i, actual in enumerate(result[profile]['policies']):
                bank = 2*seed + (bb if i % 2 == 0 else btn)
                self.assertEqual(actual['probabilities'], policies[bank,i].tolist())
                self.assertEqual({k:actual[k] for k in ('hi','lo','actor','n')}, observations[i])
        np.testing.assert_array_equal(policies, before)
        illegal = policies.copy(); illegal[0,0,2] = .01
        with self.assertRaises(ValueError): crossed_profiles(q, illegal)

    def test_sign_pairing_and_independent_scalar_intervals(self):
        # Both players have distinct values; no zero-sum sign shortcut is valid.
        values = np.empty((64,2,4,2))
        for d in range(64):
            for s in range(2):
                for p in range(4):
                    values[d,s,p] = [math.sin(d+p+s)+p*.3, math.cos(d-p+s)-p*.2]
        expected=[]
        for deal in values.tolist():
            row=[]
            for seed in deal:
                row.extend([seed[2][0]-seed[0][0],seed[3][0]-seed[1][0],
                            seed[1][1]-seed[0][1],seed[3][1]-seed[2][1]])
            expected.append(row)
        np.testing.assert_array_equal(differences(values), expected)
        comparison=CompletePolicyComparison(stack=10.,dead_money=2.,deals=64)
        comparison.add(values[:17]); comparison.add(values[17:])
        result=comparison.finish()
        for i, actual in enumerate(result['contrasts']):
            x=[r[i] for r in expected]; mean=statistics.mean(x); variance=statistics.variance(x)
            log=math.log(4*8/.05)
            radius=math.sqrt(2*variance*log/64)+7*44*log/(3*63)
            self.assertAlmostEqual(actual['mean'],mean,places=13)
            self.assertAlmostEqual(actual['sample_variance'],variance,places=13)
            self.assertAlmostEqual(actual['standard_error'],math.sqrt(variance/64),places=13)
            self.assertAlmostEqual(actual['lower'],max(-22.,mean-radius),places=12)
            self.assertAlmostEqual(actual['upper'],min(22.,mean+radius),places=12)

    def test_fixed_look_and_atomic_rejection(self):
        c=CompletePolicyComparison(stack=10.,dead_money=0.,deals=4)
        with self.assertRaises(ValueError): c.finish()
        for bad in (np.full((1,2,4,2),np.nan),np.full((1,2,4,2),11.),np.zeros((1,4,2))):
            with self.assertRaises(ValueError): c.add(bad)
            self.assertEqual([s.count for s in c.series],[0]*8)
        c.add(np.zeros((4,2,4,2)))
        with self.assertRaises(ValueError): c.add(np.zeros((1,2,4,2)))
        result=c.finish()
        self.assertTrue(all(r['mean']==0 and r['lower']<=0<=r['upper'] for r in result['contrasts']))


if __name__=='__main__': unittest.main()
