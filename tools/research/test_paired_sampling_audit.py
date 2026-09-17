import unittest
from unittest.mock import patch
import numpy as np
import paired_sampling_audit as audit


class PairedSamplingTests(unittest.TestCase):
    def test_stratified_resampling_preserves_counts_and_pairing(self):
        rows = {'call': [{'job': dict(board=str(i), stratum=str(i // 3))} for i in range(6)]}
        rows['raise'] = rows['call']
        draws = audit.panel_draws(rows, 13)
        np.testing.assert_array_equal(draws[:, :3].sum(axis=1), 3)
        np.testing.assert_array_equal(draws[:, 3:].sum(axis=1), 3)
        rows['raise'] = list(reversed(rows['call']))
        with self.assertRaises(AssertionError): audit.panel_draws(rows, 13)

    def test_shared_board_shock_cancels_in_action_difference(self):
        p = dict(base_delta=np.full(169, 2.), contexts=[], terms={}, info={})
        for i in range(2):
            p['contexts'].append(dict(case=dict(id=str(i), node=i, pot=1), raw=np.zeros((2, 169))))
            p['terms'][i] = dict(action=i + 1, coefficient=np.ones(169))
            p['info'][i] = dict(gross=np.zeros(169))
        mass = np.ones((2, 2, 169))
        shocks = np.broadcast_to(np.array([1., 9.])[:, None, None], mass.shape)
        draws = np.array([[2, 0], [0, 2], [1, 1]])
        with patch.object(audit.s.native.fit, 'arrays', return_value=(mass, shocks, shocks, mass * 0)):
            targets, parts = audit.sample_targets(p, {'0': [], '1': []}, draws)
        for key in audit.KEYS:
            np.testing.assert_allclose(targets[key], 2.)
            self.assertGreater(parts[key][0].std(), 0)
            self.assertGreater(parts[key][1].std(), 0)

    def test_ratio_uses_pair_mass_and_rejects_missing_support(self):
        p = dict(base_delta=np.zeros(169), contexts=[dict(case=dict(id='c', node=0, pot=5), raw=np.full((2, 169), .4))],
                 terms={0: dict(action=2, coefficient=np.ones(169))}, info={0: dict(gross=np.zeros(169))})
        mass = np.broadcast_to(np.array([1., 3.])[:, None, None], (2, 2, 169)).copy()
        ev = mass * np.array([.2, .6])[:, None, None]
        residual = ev - mass * .3
        with patch.object(audit.s.native.fit, 'arrays', return_value=(mass, ev, residual, mass * 0)):
            value, _ = audit.sample_targets(p, {'c': []}, np.ones((1, 2)))
            np.testing.assert_allclose(value['direct'], 2.5)
            np.testing.assert_allclose(value['corrected'], 3.)
            mass[:] = 0
            with self.assertRaises(AssertionError): audit.sample_targets(p, {'c': []}, np.ones((1, 2)))


if __name__ == '__main__': unittest.main()
