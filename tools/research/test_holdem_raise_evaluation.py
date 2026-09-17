"""Analytical checks for branch probabilities, investments and evidence gates."""
import unittest
import numpy as np
import evaluate_holdem_raise_audit as audit


class RaiseChecks(unittest.TestCase):
    def test_common_board_shock_cancels_in_paired_action_interval(self):
        # Real saved branch probabilities, but analytic fake reference payoffs:
        # each board adds the same shock to call and raise. Their difference
        # must have zero sampling width even though each action is noisy.
        m = audit.run.read(audit.run.OUT/'manifest.json')
        m['bootstrap_replicates'] = 100
        tree = audit.run.read(audit.run.OUT/'tree.json')
        values, info, _ = audit.run.tree_values(tree)
        terms, parent, denominator = audit.terminal_coefficients(tree, info)
        rows = {}
        for case in m['cases']:
            coefficient = terms[case['node']]['coefficient']
            data = []
            for b, board in enumerate(m['boards']):
                shock = .1 if b % 2 else -.1
                gross = info[case['node']]['gross'].copy()
                if case['id'] != 'fourbet-call': gross += shock/coefficient
                hands = [dict(hand=h,pair_mass=1.,ev_bb=float(gross[k]),equity=.5,
                              br_ev_bb=float(gross[k])) for k,h in enumerate(audit.run.prior.pilot.LABELS)]
                data.append(dict(job=dict(board=board['board'],stratum=board['stratum'],iso_weight=1.,inclusion_probability=1.),hands=[hands]))
            rows[case['id']] = data
        result = audit.evaluate(m, rows, tree)
        expected = (values[parent['children'][2]]-values[parent['children'][1]])/denominator
        for k,row in enumerate(result['records']):
            self.assertAlmostEqual(row['direct_delta_bb'], expected[k], places=8)
            self.assertLess(row['direct_95_interval'][1]-row['direct_95_interval'][0], 1e-8)

    def test_opponent_responses_and_own_future_choices(self):
        nodes = [dict(path=[2], kind=0, actor=1, children=[1, 2, 3]),
                 dict(kind=1), dict(kind=2),
                 dict(kind=0, actor=0, children=[4, 5, 6], sigma=np.tile([.5, .3, .2], (169, 1)).T.ravel().tolist()),
                 dict(kind=1), dict(kind=2),
                 dict(kind=0, actor=1, children=[7, 8], sigma=np.tile([.25, .75], (169, 1)).T.ravel().tolist()),
                 dict(kind=1), dict(kind=2)]
        for n in nodes[1:]: n['path'] = []
        info = {i:dict(factor=np.full(169, f)) for i, f in [(1,.4),(2,.4),(4,.2),(5,.12),(7,.08),(8,.08)]}
        terms, _, _ = audit.terminal_coefficients(dict(nodes=nodes), info)
        expected = {2:1., 4:.5, 5:.3, 7:.05, 8:.15}
        for i, w in expected.items(): np.testing.assert_allclose(terms[i]['coefficient'], w)
        # Gross payouts and total investment: convert to advantage over a -1bb fold.
        money = {2:(2.8,2.5), 4:(10.,7.5), 5:(6.,7.5), 7:(0.,7.5), 8:(23.,22.5)}
        action = {}
        for i, term in terms.items():
            gross, invested = money[i]
            action.setdefault(term['action'], np.zeros(169))
            action[term['action']] += term['coefficient']*(gross-invested+1.)
        np.testing.assert_allclose(action[1], 1.3)
        np.testing.assert_allclose(action[2], 1.5)
        np.testing.assert_allclose(action[2]-action[1], .2)

    def test_paired_interval_and_quality_gates(self):
        c = audit.classify
        self.assertEqual(c(.2, [-.4,-.1], [-.3,-.08], .5,.5,.01,.01), 'clear_model_raise_reference_call')
        self.assertEqual(c(-.2, [.1,.4], [.08,.3], .5,.5,.01,.01), 'clear_model_call_reference_raise')
        self.assertEqual(c(.2, [-.4,-.1], [-.3,.08], .5,.5,.01,.01), 'uncertain_or_no_clear_sign_disagreement')
        self.assertEqual(c(.2, [-.4,-.1], [-.3,-.08], 1e-8,.5,.01,.01), 'sparse_action_support')
        self.assertEqual(c(.2, [-.4,-.1], [-.3,-.08], .5,.5,.01,.1), 'postflop_hand_unsettled')

    def test_postflop_weighting_keeps_pot_units(self):
        label = audit.run.prior.pilot.LABELS[0]
        rows = []
        for pot_ev, mass, iso in [(9., 1., 2), (21., 3., 4)]:
            hands = [dict(hand=h, pair_mass=mass, ev_bb=pot_ev, equity=.4, br_ev_bb=pot_ev+.02) for h in audit.run.prior.pilot.LABELS]
            rows.append(dict(job=dict(iso_weight=iso, inclusion_probability=.5), hands=[hands]))
        w, v, residual, br = audit.board_arrays(rows, 15.)
        np.testing.assert_allclose(v.sum(axis=0)/w.sum(axis=0), (4*9+24*21)/28)
        np.testing.assert_allclose(residual.sum(axis=0)/w.sum(axis=0), (4*9+24*21)/28-6.)
        np.testing.assert_allclose(br.sum(axis=0)/w.sum(axis=0), .02)


if __name__ == '__main__': unittest.main()
