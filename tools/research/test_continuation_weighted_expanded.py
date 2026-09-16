import unittest
from unittest.mock import patch
import numpy as np
import continuation_weighted_expanded as weighted


class WeightedExpandedChecks(unittest.TestCase):
    def test_only_extra_contexts_are_downweighted(self):
        cases=[{'case':{'id':x}} for x in ['base','development','synthetic']]
        np.testing.assert_array_equal(weighted.weights_for(cases,{'base','development'},.2),[1.,1.,.2])
        np.testing.assert_array_equal(weighted.weights_for(cases,{'base','development'},0.),[1.,1.,0.])

    def test_ridge_uses_effective_case_weight_without_mutating_contexts(self):
        cases=[{'mass':np.ones((2,169))/169,'names':['test']} for _ in range(2)]
        weights=np.array([1.,.2]);original=cases[1]['mass'].copy()
        with patch.object(weighted.study.fit,'features',side_effect=lambda c,e:c), \
             patch.object(weighted.study.pilot,'fit_ridge',return_value={}) as fitter:
            weighted.weighted_base(cases,weights)
        data,alpha=fitter.call_args.args
        self.assertAlmostEqual(alpha/len(cases),.1/1.2)
        self.assertAlmostEqual(data[1]['mass'].sum(),.4)
        np.testing.assert_array_equal(cases[1]['mass'],original)


if __name__=='__main__':unittest.main()
