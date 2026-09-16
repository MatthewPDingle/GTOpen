import unittest
import json
import numpy as np
import continuation_prediction_bounds as bounds


class PredictionBoundsChecks(unittest.TestCase):
    def test_negative_values_within_remaining_stack_are_allowed(self):
        c=dict(case=dict(id='synthetic',pot=10.,stack=20.),mass=np.full((2,169),1/169))
        pred=np.stack([np.full(169,-1.),np.full(169,2.)])
        result=bounds.inspect(c,pred)
        self.assertTrue(result['passed'])
        self.assertEqual(json.loads(json.dumps(result)),result)

    def test_zero_sum_impossible_values_still_fail(self):
        c=dict(case=dict(id='synthetic',pot=10.,stack=20.),mass=np.full((2,169),1/169))
        pred=np.stack([np.full(169,-2.01),np.full(169,3.01)])
        result=bounds.inspect(c,pred)
        self.assertFalse(result['passed']);self.assertEqual(result['violating_hands'],338)
        self.assertLess(result['pot_accounting_error'],1e-12)


if __name__=='__main__':unittest.main()
