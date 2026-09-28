"""Synthetic independent expectations for projected model-bank composition."""
import numpy as np
from board_river_bounds_bank_v1 import (cpu_probabilities,cpu_accumulate,cpu_finish,
    cuda_probabilities,cuda_accumulate,cuda_finish)


def control():
    import torch
    scores=np.array([
        [[8,-4,3,99],[2,1,0,99],[1,1,99,99],[-3,-2,-5,99],[-2,-2,-5,99],[0,0,99,99],[0,0,0,99],[1,0,99,99]],
        [[-4,8,2,99],[0,1,2,99],[0,1,99,99],[8,-4,3,99],[-4,8,3,99],[-2,-2,99,99],[1,1,0,99],[0,1,99,99]]],dtype=np.float64)
    actors=np.array([0,0,0,1,1,1,0,0]);arity=np.array([3,3,2,3,3,2,3,2]);legal=np.arange(4)[None,:]<arity[:,None]
    eligible=np.array([True,False,False,True,True,True,False,False]);public=np.tile([6.,2.,.4,100.],(8,1))
    scales=np.array([[1.,2.],[2.,4.]]);weights=np.array([[1.,3.],[2.,5.]])
    history=[[],[(0,2)],[(0,1)],[],[],[],[],[(6,0)]]
    expected=np.array([
        [[3/7,1/7,3/7,0],[2/3,1/3,0,0],[.5,.5,0,0],[0,1,0,0],[1,0,0,0],[1,0,0,0],[0,1,0,0],[1,0,0,0]],
        [[1/10,17/30,1/3,0],[0,1/3,2/3,0],[0,1,0,0],[9/28,7/28,12/28,0],[13/70,27/70,3/7,0],[1,0,0,0],[0,1,0,0],[0,1,0,0]]])
    numerator=np.zeros((8,4));denominator=np.zeros(8);policies=[]
    for g in range(2):
        p=cpu_probabilities(scores[g],actors,arity,eligible,public,scales[g],True)
        p[6]=[0,1,0,0] # A direct-table override, including its reach effect.
        assert np.max(abs(p-expected[g]))<1e-12
        cpu_accumulate(numerator,denominator,p,actors,weights[:,g],history);policies.append(p)
    cp,cr=cpu_finish(numerator,denominator,legal)
    scalar=np.zeros((8,4));mass=np.zeros(8)
    for i in range(8):
        for g in range(2):
            w=weights[actors[i],g]
            for ancestor,action in history[i]:w*=expected[g,ancestor,action]
            scalar[i]+=w*expected[g,i];mass[i]+=w
        scalar[i]=scalar[i]/mass[i] if mass[i]>0 else legal[i]/arity[i]
    assert np.max(abs(cp-scalar))<1e-12 and np.max(abs(cr-mass))<1e-12
    assert np.max(abs(cp[1]-[1/5,1/3,7/15,0]))<1e-12
    assert cr[7]==0 and np.array_equal(cp[7],[.5,.5,0,0])
    bn=np.zeros((8,4));bd=np.zeros(8)
    for g in range(2):
        p=cpu_probabilities(scores[g],actors,arity,eligible,public,scales[g],False);p[6]=[0,1,0,0]
        cpu_accumulate(bn,bd,p,actors,weights[:,g],history)
    baseline,_=cpu_finish(bn,bd,legal)
    assert not eligible[1] and np.max(abs(cp[1]-baseline[1]))>.001
    # Build the independent tensor representation of the same short histories.
    prior=np.zeros((8,1),dtype=np.int64);action=prior.copy();valid=np.zeros((8,1),dtype=bool)
    for i,h in enumerate(history):
        if h:prior[i,0],action[i,0]=h[0];valid[i,0]=True
    tensor=lambda v:torch.tensor(v,device='cuda')
    tp=cuda_probabilities(tensor(scores),tensor(actors),tensor(legal),tensor(eligible),tensor(public),tensor(scales),True)
    tp[:,6]=tensor(np.array([0.,1.,0.,0.]))
    assert np.max(abs(tp.cpu().numpy()-expected))<1e-12
    tn=torch.zeros((8,4),dtype=torch.float64,device='cuda');td=torch.zeros(8,dtype=torch.float64,device='cuda')
    cuda_accumulate(tn,td,tp,tensor(actors),tensor(weights),tensor(prior),tensor(action),tensor(valid))
    gp,gr=cuda_finish(tn,td,tensor(legal))
    assert np.max(abs(gp-scalar))<1e-12 and np.max(abs(gr-mass))<1e-12
    # No projection at all and zero-valued differences are identity operations.
    empty=np.zeros(8,dtype=bool)
    for g in range(2):
        assert np.array_equal(cpu_probabilities(scores[g],actors,arity,empty,public,scales[g],True),
                              cpu_probabilities(scores[g],actors,arity,empty,public,scales[g],False))
    uniform=np.ones((8,4))
    assert np.array_equal(cpu_probabilities(uniform,actors,arity,eligible,public,scales[0],True),
                          cpu_probabilities(uniform,actors,arity,eligible,public,scales[0],False))
    return dict(passed=True,models=2,observations=8,explicit_expected_probabilities=True,
        unequal_player_and_model_scales=True,nonuniform_model_weights=True,positive_and_negative_scores=True,
        exact_tie_first_legal_fallback=True,lower_and_upper_bounds=True,direct_table_reach=True,
        zero_reach_uniform_fallback=True,reach_only_descendant_change=True,
        maximum_cpu_policy_error=float(np.max(abs(cp-scalar))),maximum_cuda_policy_error=float(np.max(abs(gp-scalar))),
        maximum_cuda_reach_error=float(np.max(abs(gr-mass))),uniform_scores_unchanged=True)
