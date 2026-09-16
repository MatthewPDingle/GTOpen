import unittest
from unittest.mock import patch
import numpy as np
import continuation_smooth_fit as smooth


class SmoothFitChecks(unittest.TestCase):
    def test_centering_removes_weighted_feature_mean(self):
        rng=np.random.default_rng(321);z=rng.normal(size=(2,169,104));mass=rng.uniform(size=(2,169));mass/=mass.sum(axis=1,keepdims=True)
        centered=smooth.centered(z,mass)
        np.testing.assert_allclose((centered*mass[...,None]).sum(axis=(0,1)),0,atol=1e-14)
        np.testing.assert_allclose(smooth.centered(z+7,mass),centered,atol=1e-14)

    def test_accuracy_and_response_must_both_pass(self):
        old={'a':5.,'b':7.};response={'a':1.,'b':2.}
        self.assertTrue(smooth.gate(old,{'a':.7,'b':1.4},old,response,7.)['eligible'])
        self.assertFalse(smooth.gate(old,response,old,response,7.)['eligible'])
        self.assertFalse(smooth.gate({'a':5.3,'b':6.7},{'a':.7,'b':1.4},old,response,7.)['eligible'])

    def test_zero_strength_returns_independent_unchanged_base(self):
        base={'coef':[1,2]};result=smooth.linear([],base,None,0)
        self.assertEqual(result,base);result['coef'][0]=5
        self.assertEqual(base['coef'][0],1)

    def test_positive_penalty_reduces_penalized_coefficient_energy(self):
        rng=np.random.default_rng(192);z=rng.normal(size=(2,169,104));truth=rng.normal(size=104)
        c=dict(mass=np.ones((2,169))/169,observed=np.ones((2,169)),residual=z@truth)
        regularizer=np.eye(104);regularizer[0,0]=0
        with patch.object(smooth,'standardized',return_value=z):
            weak=np.array(smooth.linear([c],{},regularizer,.0001)['coef'])
            strong=np.array(smooth.linear([c],{},regularizer,1.)['coef'])
        self.assertLess(float(strong@regularizer@strong),float(weak@regularizer@weak))


if __name__=='__main__':unittest.main()
