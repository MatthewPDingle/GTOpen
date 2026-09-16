import unittest
import numpy as np
import continuation_pairwise_values as pair


class PairwiseTests(unittest.TestCase):
    def fixture(self, own=None):
        rng = np.random.default_rng(123)
        counts = rng.uniform(.1, 1, (169, 169))
        counts = counts+counts.T
        weights = rng.uniform(.1, 1, (2, 169))
        if own is not None:
            weights[0] = own
        joint = counts*weights[0, :, None]*weights[1, None, :]
        mass = np.array([joint.sum(axis=1), joint.sum(axis=0)])/joint.sum()
        return dict(case=dict(id='fixture', weights=weights.tolist(), pot=20., stack=200.),
                    raw=np.ones((2, 169))*.5, mass=mass), counts

    def test_direct_pair_matrix(self):
        c, counts = self.fixture()
        x = pair.design(c, counts)
        self.assertEqual(x.shape, (2, 169, 363))
        coef = np.random.default_rng(456).normal(0, .01, 363)
        model = dict(coef=coef.tolist(), scale=[1.]*363)
        result = pair.predict(c, x, model)
        f = pair.hand_features()
        matrices = np.array([f@b@f.T for b in coef.reshape(3, 11, 11)])
        payoff = .5 + np.einsum('b,bij->ij', pair.bases(10), matrices)
        w = np.array(c['case']['weights'])
        oop = counts*w[1, None, :]
        ip = counts*w[0, None, :]
        direct = np.array([(oop*payoff).sum(axis=1)/oop.sum(axis=1),
                           (ip*(1-payoff.T)).sum(axis=1)/ip.sum(axis=1)])
        np.testing.assert_allclose(result, direct, atol=1e-12, rtol=0)
        self.assertAlmostEqual(float((result*c['mass']).sum()), 1, places=12)

    def test_no_own_range_dependence(self):
        a, counts = self.fixture()
        b, same_counts = self.fixture(own=np.linspace(.05, 1, 169))
        np.testing.assert_array_equal(counts, same_counts)
        np.testing.assert_allclose(pair.design(a, counts)[0], pair.design(b, counts)[0], atol=1e-12, rtol=0)

    def test_joint_gate_does_not_hide_bad_family(self):
        self.assertTrue(pair.gate({'a': 5., 'b': 5.}, {'a': 6., 'b': 6.}, {'a': 5., 'b': 5.}))
        self.assertFalse(pair.gate({'a': 4., 'b': 5.3}, {'a': 6., 'b': 6.}, {'a': 5., 'b': 5.}))


if __name__ == '__main__':
    unittest.main()
