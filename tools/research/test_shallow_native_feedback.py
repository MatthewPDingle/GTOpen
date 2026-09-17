"""Analytical controls for the new range-feedback evaluator."""
import unittest
import numpy as np
import evaluate_shallow_native_feedback as evaluate


class FeedbackControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tree=evaluate.study.read(evaluate.study.OUT/'shallow/tree.json')
        cls.values,cls.info,_=evaluate.native.tree_values(cls.tree)

    def test_exact_leaf_substitution_recovers_native_actions(self):
        leaves={}
        for path in evaluate.native.previous.old.PATHS:
            node=next(n for n in self.tree['nodes'] if n['path']==path)
            g=self.info[node['id']]['gross']
            leaves[node['id']]=dict(direct=g,corrected=g,direct_boot=np.tile(g,(20,1)),
                                   corrected_boot=np.tile(g,(20,1)),gain=np.zeros(169))
        result=evaluate.actions(self.tree,leaves,np.ones((20,1)))
        self.assertLess(result['max_independent_reconstruction_error_bb'],1e-10)
        for kind in ['call_vs_fold','call_vs_raise']:
            for error in result[kind]['pair_weighted_mae_bb']['shallow'].values():
                self.assertLess(error,1e-10)

    def test_call_leaf_shift_is_not_mistaken_for_raise_improvement(self):
        leaves={}
        for path in evaluate.native.previous.old.PATHS:
            node=next(n for n in self.tree['nodes'] if n['path']==path)
            g=self.info[node['id']]['gross']+(1. if path==[2,1] else 0.)
            leaves[node['id']]=dict(direct=g,corrected=g,direct_boot=np.tile(g,(20,1)),
                                   corrected_boot=np.tile(g,(20,1)),gain=np.zeros(169))
        result=evaluate.actions(self.tree,leaves,np.ones((20,1)))
        for row in result['records']:
            self.assertAlmostEqual(row['corrected_delta_bb'],row['shallow_delta_bb']-1.,places=8)

    def test_unsettled_references_cannot_pass_action_quality(self):
        leaves={}
        for path in evaluate.native.previous.old.PATHS:
            node=next(n for n in self.tree['nodes'] if n['path']==path)
            g=self.info[node['id']]['gross']
            leaves[node['id']]=dict(direct=g,corrected=g,direct_boot=np.tile(g,(20,1)),
                                   corrected_boot=np.tile(g,(20,1)),gain=np.full(169,100.))
        result=evaluate.actions(self.tree,leaves,np.ones((20,1)))
        for kind in ['call_vs_fold','call_vs_raise']:
            self.assertEqual(result[kind]['qualified_hand_classes'],0)
            self.assertIsNone(result[kind]['pair_weighted_mae_bb']['shallow']['corrected'])

    def test_equity_adjustment_recovers_known_payoffs_despite_board_shocks(self):
        case=evaluate.study.read(evaluate.study.OUT/'manifest.json')['cases'][2]
        context=evaluate.native.fit.context(case)
        expected=evaluate.native.hybrid(context)
        boards=[dict(stratum='paired' if i<2 else 'unpaired') for i in range(4)]
        m=dict(cases=[case],boards=boards,bootstrap_seed=13,bootstrap_replicates=100)
        rows=[]
        for b in range(4):
            hands=[]
            for side in [0,1]:
                shock=(.001 if b%2 else -.001)*(1 if side==0 else -1)
                hands.append([dict(hand=h,pair_mass=float(context['mass'][side,k]),
                    equity=float(context['raw'][side,k]+shock),
                    ev_bb=float(case['pot']*(expected[side,k]+shock)),
                    br_ev_bb=float(case['pot']*(expected[side,k]+shock)))
                    for k,h in enumerate(evaluate.pilot.LABELS)])
            rows.append(dict(job=dict(iso_weight=b+1,inclusion_probability=.5),hands=hands))
        estimates,reports=evaluate.leaf_estimates(m,{case['id']:rows},evaluate.bootstrap(m))
        self.assertLess(reports[case['id']]['mae_bb']['shallow']['corrected'],1e-10)
        np.testing.assert_allclose(estimates[case['node']]['corrected_boot'],
            np.broadcast_to(case['pot']*expected[0],(100,169)),atol=1e-10)


if __name__=='__main__':unittest.main()
