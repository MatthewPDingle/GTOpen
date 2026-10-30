"""Synthetic candidate controls, not an accuracy experiment or fitted model."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
                  CUBLAS_WORKSPACE_CONFIG=':4096:8', PYTHONDONTWRITEBYTECODE='1')
import unittest
import numpy as np
import torch
import stack_equity_priced_model_v1 as m


def prices(n):
    stack = np.full(n, 100.)
    net = np.linspace(10., 199., n)
    cost = np.minimum(net * .3, 99.)
    return np.column_stack((stack, net, cost, np.arange(n) % 2, cost / net))


class EquityPricingControls(unittest.TestCase):
    def test_feature_contract_and_neutral_start(self):
        self.assertEqual(len(m.CARD_COLUMNS), 191)
        self.assertEqual(len(set(m.CARD_COLUMNS)), 191)
        self.assertFalse(set(m.CARD_COLUMNS) & (set(range(133, 269)) | set(range(302, 362))))
        before = torch.random.get_rng_state().clone()
        net = m.fresh(9297401, scope=m.SCOPE)
        self.assertTrue(torch.equal(before, torch.random.get_rng_state()))
        features = torch.randn(31, 387)
        self.assertTrue(torch.equal(net(features), torch.full((31,), .5)))
        self.assertTrue(all(torch.equal(v, m.fresh(9297401, scope=m.SCOPE).state_dict()[k])
                            for k, v in net.state_dict().items()))

    def test_context_cannot_leak_into_uniform_equity(self):
        net = m.fresh(17, scope=m.SCOPE, dtype=torch.float64)
        with torch.no_grad():
            net.net[-1].weight.copy_(torch.linspace(-.2, .2, 64).reshape(1, 64))
        rng = np.random.default_rng(19)
        x = rng.normal(size=(29, 387))
        altered = x.copy()
        public = sorted(set(range(387)) - set(m.CARD_COLUMNS))
        altered[:, public] = rng.normal(50, 50, (29, len(public)))
        self.assertTrue(torch.equal(net(torch.tensor(x)), net(torch.tensor(altered))))

    def test_independent_dense_readback(self):
        net = m.fresh(23, scope=m.SCOPE)
        with torch.no_grad():
            net.net[-1].weight.copy_(torch.linspace(-.7, .8, 64).reshape(1, 64))
            net.net[-1].bias.fill_(.13)
        weights = {k: v.detach().numpy().copy() for k, v in net.state_dict().items()}
        x = np.random.default_rng(29).normal(size=(257, 387))
        expected = m.numpy_equity(weights, x)
        net = net.double()
        actual = net(torch.tensor(x)).detach().numpy()
        self.assertLess(float(np.max(np.abs(expected - actual))), 2e-14)
        self.assertTrue(np.all((actual >= 0) & (actual <= 1)))

    def test_values_and_loss_match_training_objective(self):
        net = m.fresh(31, scope=m.SCOPE, dtype=torch.float64)
        x, e = torch.zeros(13, 387, dtype=torch.float64), torch.tensor(prices(13))
        values = net.normalized_values(x, e, terminal_call_confirmed=True)
        self.assertTrue(torch.equal(values[:, 0], torch.zeros(13, dtype=torch.float64)))
        np.testing.assert_allclose(values[:, 1].detach().numpy(), (.5*e[:, 1]-e[:, 2]).numpy()/100,
                                   rtol=0, atol=1e-16)
        truth = torch.linspace(.1, .9, 13, dtype=torch.float64)
        target = (truth*e[:, 1]-e[:, 2])/e[:, 0]
        loss = (values[:, 0].square() + (values[:, 1]-target).square()).mean()/2
        equivalent = ((e[:, 1]/e[:, 0]).square() * (.5-truth).square()).mean()/2
        self.assertAlmostEqual(float(loss), float(equivalent), places=14)
        loss.backward()
        self.assertTrue(torch.isfinite(net.net[-1].weight.grad).all())
        self.assertGreater(float(net.net[-1].weight.grad.abs().sum()), 0)

    def test_physical_bounds_monotonicity_and_units(self):
        q = np.linspace(0, 1, 1001)
        e = np.tile([200., 201., 100., 1., 100/201], (len(q), 1))
        original = e.copy()
        out = m.price_estimate(q, e, scope=m.SCOPE, terminal_call_confirmed=True)
        self.assertTrue(np.array_equal(e, original))
        self.assertTrue(np.all(np.diff(out['call_value_bb']) >= 0))
        self.assertEqual(out['call_value_bb'][0], -100.)
        self.assertEqual(out['call_value_bb'][-1], 101.)
        for scale in (.1, 2., 1000.):
            scaled = e.copy()
            scaled[:, :3] *= scale
            changed = m.price_estimate(q, scaled, scope=m.SCOPE, terminal_call_confirmed=True)
            np.testing.assert_allclose(changed['call_value_bb'], out['call_value_bb']*scale, rtol=1e-13, atol=1e-12)
            np.testing.assert_allclose(changed['normalized_call_value'], out['normalized_call_value'], rtol=0, atol=1e-14)
            self.assertTrue(np.array_equal(changed['call_probability'], out['call_probability']))

    def test_assumed_bound_never_hides_uncertain_rows(self):
        true_q, guessed = np.meshgrid(np.linspace(0, 1, 101), np.linspace(0, 1, 101))
        true_q, guessed = true_q.ravel(), guessed.ravel()
        e = prices(len(true_q))
        eps = np.abs(true_q - guessed)
        out = m.price_estimate(guessed, e, scope=m.SCOPE, terminal_call_confirmed=True,
                               assumed_equity_error_bound=eps)
        true_margin = true_q*e[:, 1]-e[:, 2]
        loss = np.maximum(true_margin, 0)-out['call_probability']*true_margin
        self.assertEqual(len(loss), len(true_q))
        self.assertTrue(np.all(loss <= out['assumed_greedy_loss_bound_bb'] + 1e-12))
        self.assertTrue(np.all(true_margin >= out['assumed_call_value_lower_bb'] - 1e-12))
        self.assertTrue(np.all(true_margin <= out['assumed_call_value_upper_bb'] + 1e-12))
        certain = out['stability_code'] != -1
        self.assertTrue(np.all(loss[certain] <= 1e-12))
        self.assertGreater(int((~certain).sum()), 0)

    def test_price_above_full_equity_folds_every_hand(self):
        e = np.tile([10., 2., 8., 0., 4.], (3, 1))
        out = m.price_estimate([0., .5, 1.], e, scope=m.SCOPE, terminal_call_confirmed=True)
        self.assertTrue(np.array_equal(out['call_probability'], [0., 0., 0.]))
        self.assertTrue(np.array_equal(out['call_value_bb'], [-8., -7., -6.]))

    def test_rejects_wrong_scope_and_malformed_inputs(self):
        with self.assertRaises(ValueError):
            m.fresh(3, scope='betting-conditioned-opponent')
        e = prices(2)
        for q in ([np.nan, .5], [np.inf, .5], [-.1, .5], [1.1, .5], [.5]):
            with self.assertRaises(ValueError):
                m.price_estimate(q, e, scope=m.SCOPE, terminal_call_confirmed=True)
        for col, value in ((0, 0), (1, np.inf), (2, 0), (3, 2), (4, .9)):
            broken = e.copy()
            broken[0, col] = value
            with self.assertRaises(ValueError):
                m.price_estimate([.5, .5], broken, scope=m.SCOPE, terminal_call_confirmed=True)
        with self.assertRaises(ValueError):
            m.price_estimate([.5, .5], e, scope=m.SCOPE, terminal_call_confirmed=False)
        for bound in (-.1, 1.1, np.nan):
            with self.assertRaises(ValueError):
                m.price_estimate([.5, .5], e, scope=m.SCOPE, terminal_call_confirmed=True,
                                 assumed_equity_error_bound=bound)


if __name__ == '__main__':
    torch.set_num_threads(1)
    unittest.main(verbosity=2)
