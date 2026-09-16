import copy
import unittest
import numpy as np
import continuation_shrunk_residual as model


class ShrunkResidualChecks(unittest.TestCase):
    def test_scales_only_the_centered_residual_and_preserves_input_model(self):
        rng=np.random.default_rng(90210);x=rng.normal(size=(2,169,104))
        mass=rng.dirichlet(np.ones(169),size=2)
        nets=[dict(weight=rng.normal(size=(104,8)).tolist(),bias=rng.normal(size=8).tolist(),output=rng.normal(size=8).tolist()) for _ in range(2)]
        original=dict(width=8,output_penalty=.1,networks=nets,base=dict(marker='unchanged'),losses=[1.,2.])
        before=copy.deepcopy(original);shrunk=model.shrink(original)
        def correction(nets):
            total=np.zeros((2,169))
            for net in nets:
                raw=np.maximum(0,x@np.array(net['weight'])+np.array(net['bias']))@np.array(net['output'])
                total+=(raw-(raw*mass).sum()/2)/len(nets)
            return total
        self.assertEqual(original,before);self.assertEqual(shrunk['base'],original['base'])
        actual=correction(shrunk['networks'])
        np.testing.assert_allclose(actual,.75*correction(original['networks']),atol=1e-13,rtol=0)
        self.assertLess(abs(float((actual*mass).sum())),1e-13)
        self.assertNotIn('losses',shrunk);self.assertEqual(shrunk['unshrunk_training_losses'],[1.,2.])


if __name__=='__main__':unittest.main()
