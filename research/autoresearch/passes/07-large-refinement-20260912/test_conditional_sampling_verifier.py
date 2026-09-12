"""Analytic two-action sampling fixture for the independent moment verifier."""
import copy
import unittest
from check_conditional_sampling import verify_result


def fixture():
    # Q=(0,1), sigma=(1/2,1/2), and symmetric noise (+1,-1)
    # or (-1,+1). Normalized regret covariance is [[1,-1],[-1,1]],
    # and the inferior action wins strictly in half of the offsets.
    mass=.25
    hands=[dict(class_index=h,hand=str(h),current_probabilities=[.5,.5],
                current_conditional_hand_mass=1/169) for h in range(169)]
    positive=[mass]*169+[0.]*169
    negative=[-mass]*169+[2*mass]*169
    row=dict(path=[],actor=0,source=dict(actions=['fold','call'],hands=hands,
             current_prefix_mass_by_seat=[1.,mass],forced=False,frozen=False),
             current_sigma_action_major=[.5]*338,gpu_prefix_mass_by_seat=[1.,mass],
             normalized_regret_denominator_f32=mass,zero_opponent_reach=False,
             cpu_reference=dict(status='evaluated',opponent_mass=mass,
                 hands=[dict(action_values_bb=[0.,1.]) for _ in range(169)]),
             full_action_values_raw_action_major=[0.]*169+[mass]*169,
             offset_action_values_raw_action_major=[positive.copy() if i%2 else negative.copy() for i in range(1024)])
    return dict(samples=64,offsets=1024,source_iteration=950,rows=[row],
                source_and_device_histories_unchanged=True,full_restore_exact=True)


class Moments(unittest.TestCase):
    def test_known_covariance_and_units(self):
        result=verify_result(fixture(),[[]])
        for h in result['rows'][0]['hands']:
            self.assertEqual(h['regret_mean'],[-.5,.5])
            self.assertEqual(h['regret_bias'],[0.,0.])
            self.assertEqual(h['regret_variance'],[1.,1.])
            self.assertEqual(h['regret_covariance'],[[1.,-1.],[-1.,1.]])
            self.assertEqual(h['raw_regret_variance'],[.0625,.0625])
            self.assertEqual(h['probability_strictly_promoting_inferior_action'],.5)
            self.assertEqual(h['best_action_reversal_probability'],.5)

    def test_rejects_bias_denominator_and_modified_histories(self):
        original=fixture()
        bad=copy.deepcopy(original)
        bad['rows'][0]['offset_action_values_raw_action_major'][0][0]+=10
        with self.assertRaisesRegex(ValueError,'Cyclic estimator mean'):
            verify_result(bad,[[]])
        bad=copy.deepcopy(original);bad['rows'][0]['normalized_regret_denominator_f32']=1.
        with self.assertRaisesRegex(ValueError,'normalization denominator'):
            verify_result(bad,[[]])
        bad=copy.deepcopy(original);bad['source_and_device_histories_unchanged']=False
        with self.assertRaisesRegex(ValueError,'preservation'):
            verify_result(bad,[[]])


if __name__=='__main__':unittest.main()
