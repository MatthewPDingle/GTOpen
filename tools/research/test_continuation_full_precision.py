import copy
import unittest
from unittest.mock import patch
import continuation_full_precision as full
import continuation_policy_transfer_optimized as transfer


def fixture():
    return dict(iteration=150,rows=[dict(node=1,actor=0,actions=['Fold','Call'],hands=[dict(
        class_index=0,actor_reach=.1,average_probabilities=[.5,.5],action_values_counterfactual_bb=[0.,1.])])])


class FullPrecisionChecks(unittest.TestCase):
    def test_tolerance_is_not_relaxed(self):
        a=fixture();b=copy.deepcopy(a)
        b['rows'][0]['hands'][0]['action_values_counterfactual_bb'][1]+=.000003
        self.assertFalse(full.action_difference(a,b)['passed'])

    def test_changed_class_or_nan_refused(self):
        a=fixture();b=copy.deepcopy(a);b['rows'][0]['hands'][0]['class_index']=1
        with self.assertRaises(AssertionError):full.action_difference(a,b)
        b=copy.deepcopy(a);b['rows'][0]['hands'][0]['action_values_counterfactual_bb'][1]=float('nan')
        with self.assertRaises(AssertionError):full.action_difference(a,b)

    def test_no_transfer_without_full_precision_runtime_pass(self):
        def read(path):
            return {'accuracy_screen_passed':True} if path.name=='evaluation.json' else {'within_runtime_target':False}
        with patch.object(transfer.study,'read',side_effect=read):
            with self.assertRaises(AssertionError):transfer.selection('N20')


if __name__=='__main__':unittest.main()
