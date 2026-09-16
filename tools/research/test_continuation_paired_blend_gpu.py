import copy
import unittest
from continuation_paired_blend_gpu import linearity

def result(values):
    return dict(iteration=1500,rows=[dict(node=7,actions=['fold','call'],hands=[dict(
        class_index=14,actor_reach=.1,action_values_counterfactual_bb=values)])])

class LinearityChecks(unittest.TestCase):
    def test_known_weighted_values(self):
        checked=linearity(result([-2.,6.]),result([2.,10.]),result([-1.,7.]))
        self.assertTrue(checked['passed'])
        self.assertEqual(checked['values'],2)
        self.assertEqual(checked['maximum_difference_bb'],0.)

    def test_wrong_weight_and_changed_reach_are_rejected(self):
        self.assertFalse(linearity(result([-2.,6.]),result([2.,10.]),result([0.,8.]))['passed'])
        changed=copy.deepcopy(result([-1.,7.]));changed['rows'][0]['hands'][0]['actor_reach']=.2
        with self.assertRaises(AssertionError):linearity(result([-2.,6.]),result([2.,10.]),changed)

if __name__=='__main__':unittest.main()
