"""Analytic unit/sign and evidence-quality checks for the local action audit."""
import unittest
from unittest.mock import patch
import numpy as np
import evaluate_holdem_call_audit as audit


class EvaluationChecks(unittest.TestCase):
    def fixture(self, disagreement=False):
        hands = []
        for k in range(169):
            factor = .2 if k % 2 else .7
            # Same +1bb call advantage despite different compatible opponent mass.
            hands.append(dict(class_index=k,
                action_values_counterfactual_bb=[-factor, 0., factor, 0.],
                average_probabilities=[0., 1., 0., 0.]))
        hands[0]['average_probabilities'] = [1-1e-9, 1e-9, 0., 0.]
        native = {'rows': [dict(path=[2], hands=hands)]}
        context = dict(raw=np.full((2, 169), .6 if disagreement else .1),
                       mass=np.full((2, 169), 1/169))
        rows = []
        for b in range(10):
            observed = [dict(hand=h, pair_mass=1., ev_bb=.5, equity=.1,
                             br_ev_bb=.6 if k == 1 else .5) for k, h in enumerate(audit.run.pilot.LABELS)]
            rows.append(dict(job=dict(stratum=str(b//2), iso_weight=1+b%2, inclusion_probability=.1),
                             hands=[observed], gpu_gap_pct=.01, gap_pct=.01, seconds=1.))
        return native, context, rows

    def evaluate(self, disagreement=False):
        native, context, rows = self.fixture(disagreement)
        m = dict(case={}, bootstrap_replicates=100, bootstrap_seed=17)
        with patch.object(audit.run, 'read', return_value=native), \
             patch.object(audit.run.pilot, 'matrices', return_value=(None, None)), \
             patch.object(audit.run.pilot, 'context', return_value=context):
            return audit.summarize(m, rows)

    def test_call_cost_and_compatible_mass_cancel(self):
        result = self.evaluate()
        for r in result['records']:
            self.assertAlmostEqual(r['candidate_advantage_bb'], 1.)
            self.assertAlmostEqual(r['direct_advantage_bb'], -1.)
            self.assertAlmostEqual(r['corrected_advantage_bb'], -1.)
        self.assertEqual(result['records'][0]['decision'], 'sparse_call_support')
        self.assertEqual(result['records'][1]['decision'], 'postflop_hand_unsettled')
        self.assertEqual(result['counts']['clear_model_call_reference_fold'], 167)

    def test_control_variate_disagreement_prevents_clear_sign_claim(self):
        result = self.evaluate(disagreement=True)
        self.assertNotIn('clear_model_call_reference_fold', result['counts'])
        self.assertAlmostEqual(result['records'][2]['direct_advantage_bb'], -1.)
        self.assertAlmostEqual(result['records'][2]['corrected_advantage_bb'], 1.5)

    def test_board_and_compatible_hand_mass_weighting(self):
        native, context, rows = self.fixture()
        # Repeated two-board strata: effective weights 2 and 12. EV average
        # must be (2*1+12*3)/14, not the unweighted 2bb average.
        for b, row in enumerate(rows):
            row['job'].update(iso_weight=1 if b % 2 == 0 else 3,
                              inclusion_probability=.5 if b % 2 == 0 else .25)
            for hand in row['hands'][0]:
                hand.update(pair_mass=1., ev_bb=1. if b % 2 == 0 else 3.,
                            equity=.1, br_ev_bb=1. if b % 2 == 0 else 3.)
        m = dict(case={}, bootstrap_replicates=100, bootstrap_seed=17)
        with patch.object(audit.run, 'read', return_value=native), \
             patch.object(audit.run.pilot, 'matrices', return_value=(None, None)), \
             patch.object(audit.run.pilot, 'context', return_value=context):
            result = audit.summarize(m, rows)
        self.assertAlmostEqual(result['records'][2]['direct_advantage_bb'], 38/14-1.5)
        # Doubling the first board's compatible pair mass changes its weight.
        for b, row in enumerate(rows):
            if b % 2 == 0:
                for hand in row['hands'][0]: hand['pair_mass'] = 2.
        with patch.object(audit.run, 'read', return_value=native), \
             patch.object(audit.run.pilot, 'matrices', return_value=(None, None)), \
             patch.object(audit.run.pilot, 'context', return_value=context):
            result = audit.summarize(m, rows)
        self.assertAlmostEqual(result['records'][2]['direct_advantage_bb'], 40/16-1.5)


if __name__ == '__main__': unittest.main()
