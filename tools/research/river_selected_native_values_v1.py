"""Evaluate complete native trees of sampled pairs, retaining draw multiplicity."""
import math
import numpy as np


def evaluate(doc, p, draw_cards):
    if len(draw_cards) != 64: raise ValueError('Exactly 64 posterior draws required')
    selected = {tuple(pair['cards']):pair for pair in doc['pairs']}
    if len(selected)!=len(doc['pairs']) or set(selected)!=set(map(tuple,draw_cards)):
        raise ValueError('Selected native pair set does not match draws')
    target = doc['target']; n=target['n']; sigma=p[target['query_index'],:n]
    if not np.isfinite(sigma).all() or np.any(sigma<0) or abs(float(sum(sigma))-1)>1e-12:
        raise ValueError('Invalid current policy')
    vectors={}
    for cards,pair in selected.items():
        values={}
        for index in range(pair['node_start'],pair['root']+1):
            node=doc['nodes'][index]
            if node['kind']!='decision':values[index]=node['payoff']
            else:
                probs=p[node['query_index'],:len(node['children'])]
                if not np.isfinite(probs).all() or np.any(probs<0) or abs(float(sum(probs))-1)>1e-12:
                    raise ValueError('Invalid selected future policy')
                values[index]=math.fsum(float(w)*values[c] for w,c in zip(probs,node['children']))
        vectors[cards]=[values[c] for c in doc['nodes'][pair['root']]['children']]
    q=np.array([math.fsum(vectors[tuple(cards)][a] for cards in draw_cards)/64 for a in range(n)])
    value=math.fsum(float(w*x) for w,x in zip(sigma,q))
    return dict(action_values=q,value=value,regrets=q-value,pair_values=vectors)
