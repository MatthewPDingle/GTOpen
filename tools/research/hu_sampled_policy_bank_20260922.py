"""Observable-history, own-reach-weighted policy-bank control.

Small-game oracle adapter for retaining iteration models instead of fitting a
second average-policy network. The finite policy arrays here are a control;
physical-poker use requires observable neural inference, not a giant table.
"""
import numpy as np


def own_history(data):
    """For each observation, list its earlier own decisions and taken actions.

    Public tree nodes have unique histories. Own card is unchanged, and only
    already-visible public cards are used to resolve ancestor observations.
    No opponent card, opponent reach, or future board enters the weight.
    """
    keys=data['information_keys'];lookup={tuple(k):i for i,k in enumerate(keys)}
    parent={}
    for n,arity in enumerate(data['arity']):
        for a,c in enumerate(data['children'][n][:arity]):
            assert c not in parent,'This adapter requires full public-history nodes.'
            parent[c]=(n,a)
    visible={n:any(k[0]==n and k[2]>=0 for k in keys) for n in range(19)}
    result=[]
    for n,card,board in keys:
        player=data['actors'][n];history=[];cursor=n
        while cursor in parent:
            previous,action=parent[cursor]
            if data['actors'][previous]==player:
                ancestor_board=board if visible[previous] else -1
                assert not visible[previous] or board>=0,'A visible card cannot become hidden.'
                info=lookup[(previous,card,ancestor_board)]
                history.append((info,action))
            cursor=previous
        result.append(tuple(reversed(history)))
    return result


def average_bank(data, policies, weights=None):
    """Mix action probabilities using iteration weight times own prior reach."""
    policies=np.asarray(policies,dtype=np.float64)
    count=len(data['information_keys'])
    assert policies.ndim==3 and policies.shape[1:]==(count,3)
    assert np.isfinite(policies).all() and (policies>=0).all()
    if weights is None:weights=np.ones(len(policies))
    weights=np.asarray(weights,dtype=np.float64)
    assert weights.shape==(len(policies),) and np.isfinite(weights).all() and (weights>0).all()
    result=np.zeros((count,3));denominators=[]
    for i,history in enumerate(own_history(data)):
        arity=data['arity'][data['information_keys'][i][0]]
        assert np.max(np.abs(policies[:,i,:arity].sum(axis=1)-1))<1e-12
        assert not np.any(policies[:,i,arity:])
        reach=weights.copy()
        for info,action in history:reach*=policies[:,info,action]
        total=float(reach.sum());denominators.append(total)
        if total>0:result[i]=(policies[:,i]*reach[:,None]).sum(axis=0)/total
        else:result[i,:arity]=1/arity
    return result,np.asarray(denominators)


def terminal_probabilities(data, policies, deal):
    probability=np.zeros(19);probability[0]=1.
    for n,arity in enumerate(data['arity']):
        if arity:
            for a,c in enumerate(data['children'][n][:arity]):
                probability[c]=probability[n]*policies[data['deal_infos'][deal][n],a]
    return probability[np.asarray(data['arity'])==0]


def check(data):
    from hu_sampled_neural_control_20260922 import geometry,exact_average_increment,normalize_average
    _,mask,actors=geometry(data)
    rng=np.random.default_rng(40260922)
    policies=rng.random((3,len(mask),3))*mask
    policies/=policies.sum(axis=2,keepdims=True)
    weights=np.array([1.,2.,4.])
    mixed,denominator=average_bank(data,policies,weights)
    accumulated=sum((w*exact_average_increment(data,p) for w,p in zip(weights,policies)),np.zeros_like(mixed))
    expected=normalize_average(accumulated,mask)
    max_average_error=float(np.max(np.abs(mixed-expected)))
    max_trajectory_error=0.
    # Independent root model draws, one per player, held for the entire hand.
    # Enumerate their joint mixture and every complete terminal path.
    for d in range(24):
        expected_terminal=np.zeros(sum(a==0 for a in data['arity']))
        for i in range(3):
            for j in range(3):
                combined=np.where((actors==0)[:,None],policies[i],policies[j])
                expected_terminal+=(weights[i]*weights[j]/weights.sum()**2)*terminal_probabilities(data,combined,d)
        actual=terminal_probabilities(data,mixed,d)
        max_trajectory_error=max(max_trajectory_error,float(np.max(np.abs(actual-expected_terminal))))
    assert max_average_error<1e-12 and max_trajectory_error<1e-12
    # Deliberately unreachable prior action: the second model's later behavior
    # must have zero weight, even if its raw iteration weight is large.
    uniform=mask/mask.sum(axis=1,keepdims=True)
    a=uniform.copy();b=uniform.copy()
    lookup={tuple(k):i for i,k in enumerate(data['information_keys'])}
    root=lookup[(0,0,-1)];later=lookup[(3,0,1)]
    a[root]=[0,1,0];b[root]=[1,0,0]
    a[later]=[0,1,0];b[later]=[1,0,0]
    got,denom=average_bank(data,[a,b],[1,100])
    assert np.array_equal(got[later],a[later]) and denom[later]==1
    naive=(a[later]+100*b[later])/101
    assert np.max(np.abs(got[later]-naive))>.99
    a[root]=b[root]=[1,0,0]
    empty,zero=average_bank(data,[a,b])
    assert zero[later]==0 and np.array_equal(empty[later],uniform[later])
    return dict(passed=True,maximum_exact_average_error=max_average_error,
        maximum_whole_trajectory_error=max_trajectory_error,
        independent_model_pair_deals=3*3*24,
        hidden_information_used=False,zero_own_reach_model_excluded=True,
        unreachable_query_fallback='uniform legal, unsupported by bank reach',
        naive_probability_average_negative_control=True,
        physical_poker_adapter_qualified=False)
