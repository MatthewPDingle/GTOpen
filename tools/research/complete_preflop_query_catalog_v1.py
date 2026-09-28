"""Complete supported preflop queries from a retained native holding catalog.

Scoped to the existing five-decision BB/BTN subtree. Builds own-action links;
does not generate a policy, replace a model's root catalog, or sample deals.
"""
import copy
import json
import numpy as np
from board_root_components_v1 import validate_context
from preflop_allin_matrix_v1 import AllinMatrix
from sampled_physical_preflop_table_v1 import validate_preflop
from sampled_physical_root_evaluation_v1 import hand_class


def build(native, context_source, matrix_document):
    if native.get('format')!=1 or native.get('context_source')!=context_source:
        raise ValueError('Native catalog/context mismatch')
    context=json.loads(context_source);validate_context(context)
    nodes=context['nodes'];decisions={i for i,n in enumerate(nodes) if n['kind']==0}
    if decisions!={0,3,6,9,12}:raise ValueError('Unsupported decision coverage')
    matrix=AllinMatrix(matrix_document,context_source)
    masses=(matrix.bb_mass,matrix.btn_mass)
    physical={i:set() for i in decisions};classes={};parents={}
    for node in sorted(decisions):
        for action,child in enumerate(nodes[node]['children']):
            if child in parents or child==0:raise ValueError('Context must be a rooted tree')
            parents[child]=(node,action)
    for row in native['rows']:
        node=row['node'];hand=row['hand'];obs=row['observation']
        if (type(node) is not int or node not in decisions or len(hand)!=2
                or any(type(c) is not int for c in hand) or not 0<=hand[0]<hand[1]<52):
            raise ValueError('Valid native decision/physical holding required')
        key=tuple(hand)
        if key in physical[node]:raise ValueError('Duplicate physical holding')
        physical[node].add(key);actor=nodes[node]['actor']
        validate_preflop(obs,context,actor)
        if int(obs['hi'])!=node+1 or obs['phase']!=0 or 'own_history' in obs:
            raise ValueError('Unexpected native holding observation')
        cls=hand_class(hand);lo=int(obs['lo'])
        if hand_class([lo&63,(lo>>6)&63])!=cls:raise ValueError('Native class/key disagreement')
        identity=(node,cls)
        if identity in classes and classes[identity]!=obs:raise ValueError('Class is not suit-invariant')
        classes[identity]=obs
    expected={(a,b) for a in range(52) for b in range(a+1,52)}
    if any(holdings!=expected for holdings in physical.values()):raise ValueError('Incomplete native physical catalog')
    if len(classes)!=len(decisions)*169:raise ValueError('Incomplete class catalog')
    keys=[(node,cls) for node in sorted(decisions) for cls in range(169) if masses[nodes[node]['actor']][cls]>0]
    ids={key:i for i,key in enumerate(keys)};observations=[];metadata=[]
    for node,cls in keys:
        obs=copy.deepcopy(classes[(node,cls)]);actor=obs['actor'];path=[];cursor=node
        while cursor:
            if cursor not in parents or len(path)>=len(nodes):raise ValueError('Broken/cyclic ancestry')
            parent,action=parents[cursor];path.append((parent,action));cursor=parent
        history=[]
        for parent,action in reversed(path):
            if nodes[parent]['actor']==actor:
                index=ids[(parent,cls)]
                if index>=len(observations):raise ValueError('Own ancestor must precede observation')
                history.append([index,action,len(nodes[parent]['actions'])])
        obs['own_history']=history;observations.append(obs)
        metadata.append(dict(node=node,hand_class=cls,actor=actor,index=len(observations)-1))
    return dict(format=1,context_source=context_source,
        query=dict(context_source=context_source,observations=observations),rows=metadata,
        physical_rows_checked=len(native['rows']),canonical_rows_checked=len(classes),
        supported_classes=[int(np.count_nonzero(m)) for m in masses],
        scope='Preflop query construction only; original model/catalog/inference unchanged.')
