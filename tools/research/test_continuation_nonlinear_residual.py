import unittest
import numpy as np
import torch
import continuation_nonlinear_residual as run


class ResidualTests(unittest.TestCase):
    def test_initial_correction_is_zero_and_accounting_is_preserved(self):
        rng=np.random.default_rng(90210)
        x=rng.normal(size=(3,2,169,104))
        mass=rng.dirichlet(np.full(169,.05),size=(3,2))
        net=run.Residual(8,90210)
        tx=torch.tensor(x,dtype=torch.float64);tm=torch.tensor(mass,dtype=torch.float64)
        np.testing.assert_array_equal(net(tx,tm).detach().numpy(),np.zeros((3,2,169)))
        with torch.no_grad():net.output.copy_(torch.tensor(rng.normal(size=8),dtype=torch.float64))
        actual=net(tx,tm).detach().numpy()
        exported=net.export()
        raw=np.maximum(0,x@exported['weight']+np.array(exported['bias']))@np.array(exported['output'])
        expected=raw-(raw*mass).sum(axis=(1,2),keepdims=True)/2
        np.testing.assert_allclose(actual,expected,atol=1e-12,rtol=0)
        np.testing.assert_allclose((actual*mass).sum(axis=(1,2)),0,atol=1e-12,rtol=0)

    def test_deterministic_cpu_initialization(self):
        a=run.Residual(16,90210);b=run.Residual(16,90210)
        self.assertEqual(a.export(),b.export())
        self.assertTrue(all(p.device.type=='cpu' and p.dtype==torch.float64 for p in a.parameters()))


if __name__=='__main__':unittest.main()
