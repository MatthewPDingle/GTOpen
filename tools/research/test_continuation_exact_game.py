import unittest
import numpy as np
import continuation_exact_game as g


class ExactGameTests(unittest.TestCase):
    def test_explicit_deals_and_fold_payoff(self):
        self.assertEqual(g.LEGAL.sum(), 6)
        p = np.zeros((3, 3)); q = np.zeros((3, 3))
        self.assertAlmostEqual(float(g.payoff(p, q)), 0.)
        p[0] = 1
        self.assertAlmostEqual(float(g.payoff(p, q)), 1.)
        q[0] = 1
        self.assertAlmostEqual(float(g.payoff(p, q)), 0.)

    def test_matching_pennies_lp(self):
        x, y, value, gap = g.equilibrium(np.array([[1., -1.], [-1., 1.]]))
        np.testing.assert_allclose(x, [.5, .5], atol=1e-9)
        np.testing.assert_allclose(y, [.5, .5], atol=1e-9)
        self.assertLess(abs(value)+gap, 1e-9)

    def test_tree_values_against_independent_payoff(self):
        rng = np.random.default_rng(18)
        for _ in range(12):
            policy = rng.dirichlet([1, 1], size=(6, 3))
            v = g.CFR().walk(0, np.ones((2, 3)), policy)
            ev = float(g.payoff(*g.pack(policy)))
            self.assertAlmostEqual(v[0].sum(), ev, places=12)
            self.assertAlmostEqual(v[1].sum(), -ev, places=12)
            metrics = g.measure(policy)
            for player in [0, 1]:
                tree_br = g.CFR().walk(0, np.ones((2, 3)), policy, br=player)[player].sum()
                gain = metrics[f'gain_p{player}']
                self.assertAlmostEqual(tree_br, gain+(ev if player == 0 else -ev), places=12)

    def test_continuation_conservation_sparse_and_dense(self):
        for c in [1, 2]:
            for x, y in [(np.ones(3), np.ones(3)), (np.array([0., 1., 0.]), np.array([1., 0., 1.])),
                         (np.zeros(3), np.ones(3)), (np.array([1., 0., 0.]), np.array([1., 0., 0.]))]:
                v, policy, gap, fallback = g.exact(c, x, y)
                self.assertTrue(np.isfinite(v).all())
                self.assertLessEqual(np.max(np.abs(v)), c+2+1e-9)
                self.assertLess(gap, 1e-8)
                a, b = g.normalize(x), g.normalize(y)
                w = np.array([a*(g.LEGAL@b), b*(g.LEGAL.T@a)])
                if not fallback:
                    self.assertAlmostEqual(float(np.sum(w*v)), 0., places=10)

    def test_exact_leaf_matches_full_tree_same_policies(self):
        policy = np.ones((6, 3, 2))*.5
        policy[0, :, 1] = [.1, .7, .9]
        policy[1, :, 1] = [.4, .8, .2]
        policy[:, :, 0] = 1-policy[:, :, 1]
        full = g.complete_upper(policy)
        np.testing.assert_allclose(g.CFR(g.exact).walk(0, np.ones((2, 3)), policy),
                                   g.CFR().walk(0, np.ones((2, 3)), full), atol=1e-10)


if __name__ == '__main__':
    unittest.main()
