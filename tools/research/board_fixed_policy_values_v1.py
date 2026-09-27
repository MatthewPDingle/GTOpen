"""Counterfactual value vectors for a fixed public runout and fixed policies.

No board sampling or normalization: caller supplies nonnegative private weights.
Opponent path reach is propagated; each hero's own action is averaged at its
decision. Card compatibility is integrated by the terminal reducer.
"""
import numpy as np
from board_sorted_terminal_v2 import masses, values


def evaluate(tree, branch, policies, weights):
    hands = [np.asarray(x, dtype=np.int64) for x in tree['hands']]
    ranks = [np.asarray(x, dtype=np.int64) for x in tree['ranks']]
    weights = [np.asarray(w, dtype=np.float64) for w in weights]
    if any(w.shape != (len(h),) or not np.isfinite(w).all() or np.any(w < 0)
           for w, h in zip(weights, hands)) or len(weights) != 2:
        raise ValueError('Two finite nonnegative private reach vectors required')
    nodes = branch['nodes']
    for i, node in enumerate(nodes):
        if node['kind'] != 0: continue
        actor = node['actor']; p = np.asarray(policies[i])
        if (p.shape != (len(hands[actor]), len(node['children'])) or not np.isfinite(p).all()
                or np.any(p < 0) or np.max(abs(p.sum(1) - 1)) > 1e-12):
            raise ValueError('Legal normalized policy required at every decision')

    def walk(i, hero, opponent_reach):
        node = nodes[i]; kind = node['kind']; other = 1 - hero
        if kind >= 2:
            m = masses(hands[hero], ranks[hero], hands[other], ranks[other], opponent_reach)
            v = node['payouts']; offset = branch['offsets'][hero]
            if kind == 2:
                return (offset + v[1 if node['actor'] == hero else 0]) * m['valid']
            return values(m, offset + v[0], offset + v[1], offset + v[2])
        if kind == 1: return walk(node['children'][0], hero, opponent_reach)
        result = np.zeros(len(hands[hero])); p = policies[i]
        for a, child in enumerate(node['children']):
            if node['actor'] == hero: result += p[:, a] * walk(child, hero, opponent_reach)
            else: result += walk(child, hero, opponent_reach * p[:, a])
        return result
    return [walk(0, hero, weights[1 - hero]) for hero in (0, 1)]
