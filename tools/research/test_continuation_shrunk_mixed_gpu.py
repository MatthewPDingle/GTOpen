import copy
import unittest
from unittest.mock import patch
import numpy as np
import continuation_shrunk_mixed_gpu as mixed


class MixedChecks(unittest.TestCase):
    def test_lower_precision_preserves_predictions_and_pot_accounting(self):
        model=mixed.study.read(mixed.double.shrunk.OUT/'candidate.json');before=copy.deepcopy(model)
        counts,eq=mixed.study.pilot.matrices();rng=np.random.default_rng(20260916)
        for alpha in [.02,.1,1.,10.]:
            for spr in [1.,8.,20.]:
                weights=rng.dirichlet(np.full(169,alpha),size=2)
                case=dict(weights=weights.tolist(),pot=20.,stack=spr*20.)
                c=mixed.study.pilot.context(case,counts,eq)
                c.update(case=case,base_x=c['x'].copy(),base_names=list(c['names']))
                actual=mixed.simulated(c,model);expected=mixed.double.shrunk.network.predict(c,model)
                np.testing.assert_allclose(actual,expected,atol=1e-6,rtol=0)
                self.assertLess(abs(float((actual*c['mass']).sum()-1)),1e-10)
        self.assertEqual(model,before)

    def test_float_literals_roundtrip_all_neural_parameters(self):
        model=mixed.study.read(mixed.double.shrunk.OUT/'candidate.json')
        values=[v for net in model['networks'] for key in ['weight','bias','output'] for v in np.array(net[key]).reshape(-1)]
        for value in values:
            literal=mixed.float_literal(value)
            self.assertTrue(literal.endswith('f'))
            self.assertEqual(np.float32(float(literal[:-1])),np.float32(value))

    def test_existing_double_oracle_cannot_override_failed_fresh_accuracy(self):
        with patch.object(mixed.double,'qualified',side_effect=AssertionError('fresh accuracy failed')):
            with self.assertRaisesRegex(AssertionError,'fresh accuracy'):mixed.command([],None)


if __name__=='__main__':unittest.main()
