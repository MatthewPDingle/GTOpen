"""CPU validation of the fitter objective using native rows, synthetic targets."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
import copy
import unittest
import numpy as np
import torch
import test_stack_context_fit_rows_v1 as fixtures
from stack_context_fit_rows_v1 import prepare
from stack_context_training_fit_v1 import PreparedContextObjective,fresh_network
from sampled_physical_fit_v1 import export_network


class ContextFitterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        torch.set_num_threads(1)
        fixtures.FitRowsTests.setUpClass()
        cls.fixture=fixtures.FitRowsTests()

    def data(self,registry,actor):
        return prepare(registry,self.fixture.reservoirs[actor],player=actor,
                       context_weights=self.fixture.weights(registry))

    def test_chunked_loss_and_gradient_match_direct_full_matrix(self):
        for registry in self.fixture.registries:
            for actor in (0,1):
                g=self.data(registry,actor)
                p=PreparedContextObjective(g,'cpu',dtype=torch.float64,guard=lambda:None)
                model=fresh_network(9300201+actor,g['representation']['input_width']).double()
                expected=copy.deepcopy(model)
                raw=((expected(p.x)-p.target)**2*p.weight).sum()
                raw.backward()
                observed=p.objective(model,127,lambda:None,backward=True)
                self.assertAlmostEqual(observed,float(raw.detach()),places=12)
                for a,b in zip(model.parameters(),expected.parameters()):
                    torch.testing.assert_close(a.grad,b.grad,rtol=1e-10,atol=1e-12)

    def test_neutral_extension_rng_preservation_and_learnable_extra_inputs(self):
        state=torch.get_rng_state().clone()
        base=fresh_network(9300201,362);relative=fresh_network(9300201,387)
        self.assertTrue(torch.equal(state,torch.get_rng_state()))
        g=self.data(self.fixture.registries[1],0)
        x=torch.tensor(g['features'])
        self.assertTrue(torch.equal(base(x[:,:362].contiguous()),relative(x)))
        self.assertTrue(torch.equal(base[0].weight,relative[0].weight[:,:362]))
        relative(x).square().sum().backward()
        self.assertGreater(float(relative[0].weight.grad[:,362:].abs().max()),0.)
        self.assertGreater(float(relative[0].weight.grad[:,302:362].abs().max()),0.)

    def test_exported_network_matches_independent_numpy_forward(self):
        for registry in self.fixture.registries:
            g=self.data(registry,1);width=g['representation']['input_width']
            m=fresh_network(9300202,width)
            with torch.no_grad():
                # Include nonzero new columns, not just neutral initialization.
                m[0].weight[:,302:]=.013
            net=export_network(m);m=m.double();x=g['features'].astype(np.float64)
            w=np.asarray(net['w0']).reshape(64,width)
            y=x[:,:362]@w[:,:362].T+np.asarray(net['b0'])
            if width==387:y+=x[:,362:]@w[:,362:].T
            y=np.maximum(y,0.)
            y=np.maximum(y@np.asarray(net['w1']).reshape(64,64).T+net['b1'],0.)
            y=y@np.asarray(net['w2']).reshape(4,64).T+net['b2']
            np.testing.assert_allclose(y,m(torch.tensor(x)).detach().numpy(),rtol=0,atol=1e-12)

    def test_invalid_objective_is_rejected(self):
        g=self.data(self.fixture.registries[0],0)
        for kind in ('units','weights','target','feature'):
            bad=copy.deepcopy(g)
            if kind=='units':bad['target_units']='bb'
            elif kind=='weights':bad['weights']*=2.
            elif kind=='target':bad['targets'][0,0]=float('nan')
            else:bad['features'][0,0]=float('inf')
            with self.assertRaises(ValueError):
                PreparedContextObjective(bad,'cpu',dtype=torch.float32,guard=lambda:None)


if __name__=='__main__':unittest.main()
