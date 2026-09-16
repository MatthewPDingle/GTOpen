import copy
import unittest
from unittest.mock import patch
import continuation_compact_residual as compact


class CompactChecks(unittest.TestCase):
    def test_shrink_only_scales_outputs_and_preserves_input(self):
        model=dict(width=4,output_penalty=.1,networks=[dict(output=[1.,-2.,3.,-4.],bias=[0.]*4) for _ in range(2)],losses=[dict(seed=1)])
        before=copy.deepcopy(model);result=compact.shrink(model)
        self.assertEqual(model,before)
        self.assertEqual(result['networks'][0]['output'],[.75,-1.5,2.25,-3.])
        self.assertEqual(result['residual_scale'],.75)
        self.assertEqual(result['kind'],'compact_shrunk_nonlinear_residual')

    def test_cost_reduction_does_not_bypass_family_accuracy_limits(self):
        linear=dict(mean=10.,family_means=dict(a=10.,b=10.))
        teacher=dict(mean=8.,family_means=dict(a=8.,b=8.))
        self.assertTrue(compact.gate(dict(a=8.,b=8.),linear,teacher)['eligible'])
        self.assertFalse(compact.gate(dict(a=7.,b=8.5),linear,teacher)['eligible'])
        self.assertFalse(compact.gate(dict(a=9.6,b=9.6),linear,teacher)['eligible'])

    def test_gpu_timing_blocks_cpu_fit(self):
        with patch.object(compact.timing,'require_no_timing',return_value=None),patch.object(compact.queue,'processes',return_value=[
            dict(Name='python.exe',CommandLine='python continuation_pair_reductions.py benchmark')]):
            with self.assertRaisesRegex(AssertionError,'timing'):compact.require_no_timing()


if __name__=='__main__':unittest.main()
