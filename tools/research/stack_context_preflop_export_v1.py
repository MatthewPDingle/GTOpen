"""Full averaged preflop policies plus compatible-card-conditioned node ranges."""
import copy
import json
import numpy as np
from sampled_physical_bank_v1 import histories
from sampled_physical_root_evaluation_v1 import hand_class
from storage_strategic_common_prior_20260920 import PAIRS,CLASSES,COUNTS


def queries_from_catalog(context_source,catalog):
    context=json.loads(context_source)
    if catalog['context_source']!=context_source:
        raise ValueError('Catalog belongs to a different game')
    rows=catalog['rows'];observations=[copy.deepcopy(row['observation']) for row in rows]
    indices={(row['node'],tuple(row['hand'])):index for index,row in enumerate(rows)}
    if len(indices)!=len(rows):
        raise ValueError('Duplicate native private holding')
    ancestors={};visited=set()
    def walk(node,path):
        if node in visited:
            raise ValueError('Preflop topology is cyclic or shares a child')
        visited.add(node);record=context['nodes'][node]
        if not record['children']:
            return
        ancestors[node]=path
        for action,child in enumerate(record['children']):
            walk(child,path+[(node,action)])
    walk(0,[])
    physical={tuple(hand) for hand in PAIRS}
    if (set(row['node'] for row in rows)!=set(ancestors)
            or any({tuple(row['hand']) for row in rows if row['node']==node}!=physical for node in ancestors)):
        raise ValueError('Every preflop decision requires the complete native private-hand catalog')
    for row,observation in zip(rows,observations):
        node=context['nodes'][row['node']]
        cards=[(int(observation['lo'])>>(6*j))&63 for j in range(2)]
        if (observation['actor']!=node['actor'] or observation['phase']!=0
                or observation['hi']!=str(row['node']+1) or observation['n']!=len(node['children'])
                or hand_class(cards)!=hand_class(row['hand'])):
            raise ValueError('Native catalog and decision geometry disagree')
        # These ancestors come from the actual complete native preflop tree,
        # not from an inferred or missing history in a training reservoir.
        observation['own_history']=[[indices[(ancestor,tuple(row['hand']))],action,len(context['nodes'][ancestor]['children'])]
            for ancestor,action in ancestors[row['node']] if context['nodes'][ancestor]['actor']==observation['actor']]
    histories(observations)
    return dict(context_source=context_source,observations=observations),ancestors


def export(context_source,catalog,class_mass,bank,*,guard):
    context=json.loads(context_source);queries,ancestors=queries_from_catalog(context_source,catalog)
    probability,support=bank.average(queries,guard=guard)
    probability=np.asarray(probability,dtype=np.float64);support=np.asarray(support,dtype=np.float64)
    if (probability.shape!=(len(catalog['rows']),4) or support.shape!=(len(probability),)
            or not np.isfinite(probability).all() or not np.isfinite(support).all() or np.any(probability<0)
            or np.any(support<0) or np.max(abs(probability.sum(1)-1))>1e-12):
        raise ValueError('Invalid complete averaged policy')
    policies={};own={};counts={};error=0.;reach_error=0.
    physical_classes={tuple(hand):int(cls) for hand,cls in zip(PAIRS,CLASSES)}
    for row,p,r in zip(catalog['rows'],probability,support):
        node=row['node'];cls=physical_classes[tuple(row['hand'])];arity=len(context['nodes'][node]['children'])
        if np.any(p[arity:]):
            raise ValueError('Illegal action mass')
        if node not in policies:
            policies[node]=np.zeros((169,arity));own[node]=np.zeros(169);counts[node]=np.zeros(169,dtype=int)
        if counts[node][cls]:
            error=max(error,float(np.max(abs(policies[node][cls]-p[:arity]))))
            reach_error=max(reach_error,abs(float(own[node][cls]-r)))
        else:
            policies[node][cls]=p[:arity];own[node][cls]=r
        counts[node][cls]+=1
    if (error>1e-12 or reach_error>1e-10 or set(policies)!=set(ancestors)
            or any(not np.array_equal(count,COUNTS) for count in counts.values())):
        raise ValueError('Incomplete or suit-dependent preflop policy')
    mass=np.asarray(class_mass,dtype=np.float64)
    if mass.shape!=(169,169) or not np.isfinite(mass).all() or np.any(mass<0) or abs(float(mass.sum())-1)>1e-12:
        raise ValueError('Normalized compatible-card class-pair entry mass required')
    nodes=[];leaf_mass=0.
    def walk(node,pairs):
        nonlocal leaf_mass
        guard();record=context['nodes'][node];total=float(pairs.sum())
        if not record['children']:
            leaf_mass+=total
            return
        actor=record['actor'];marginal=pairs.sum(axis=1 if actor==0 else 0)
        p=policies[node];weighted=(marginal[:,None]*p).sum(0)
        nodes.append(dict(node=node,actor=actor,actions=copy.deepcopy(record['actions']),path=ancestors[node],
            probability_of_reaching_node=total,action_probabilities_by_class=p.tolist(),
            entry_mass_by_class=marginal.tolist(),conditional_range_by_class=(marginal/total).tolist() if total>0 else None,
            conditional_action_frequencies=(weighted/total).tolist() if total>0 else None,
            own_history_weighted_model_support_by_class=own[node].tolist(),
            in_arriving_range=(marginal>0).tolist(),zero_node_reach=total==0))
        for action,child in enumerate(record['children']):
            next_mass=pairs*(p[:,action,None] if actor==0 else p[None,:,action])
            walk(child,next_mass)
    walk(0,mass)
    if abs(leaf_mass-1)>1e-10:
        raise ValueError('Preflop branch mass does not conserve the entry population')
    return dict(format=1,nodes=nodes,maximum_preflop_suit_policy_error=error,
        maximum_preflop_suit_support_error=reach_error,terminal_entry_mass=leaf_mass,
        scope='Independent full played strategies for both actors, propagated through the actual preflop tree with compatible-card entry mass',
        warning='A conditional action mix alone is not an entering range. Zero-arrival hands and nodes are explicitly marked.',
        accuracy_qualified=False)
