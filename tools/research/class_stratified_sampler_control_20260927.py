"""Bounded distribution/restart control, not a poker-strength experiment."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
import copy
import json
import math
from pathlib import Path
import time
import numpy as np
from class_stratified_physical_deals_v1 import ClassStratifiedDeals, METHOD
from sampled_physical_deals_v1 import PhysicalDeals
from storage_strategic_common_prior_20260920 import PAIRS, MASKS, CLASSES
from later_average_support_v1 import OUT
from sampled_physical_root_evaluation_v1 import sha,save,hand_class

PREFIX='class-stratified-sampler-control-v1'


def main():
    start=time.monotonic();source_path=OUT/'bb-context-candidate.json';source=source_path.read_text()
    paths=[source_path,*Path(__file__).parent.glob('*.py'),OUT/'CLASS-STRATIFIED-SAMPLER-PLAN.md']
    inputs={str(p):sha(p) for p in paths}
    rp=OUT/f'{PREFIX}-registration.json'
    save(rp,dict(inputs=inputs,seed=9271001,batch_size=512,batches=16,maximum_seconds=180,
        new_poker_evaluations=0,training=False,production_modified=False))
    sampler=ClassStratifiedDeals(source,seed=9271001)
    baseline=PhysicalDeals(source,mode='full_deck',seed=9271001)
    # Independent direct joint enumeration from range weights and card masks,
    # not the sampler's per-class normalized probability arrays.
    compatible=(MASKS[:,None]&MASKS[None,:])==0
    joint=baseline.weights[0,:,None]*baseline.weights[1,None,:]*compatible
    joint/=joint.sum();marginal=joint.sum(1)
    masses=np.bincount(CLASSES,weights=marginal,minlength=169)
    assert np.max(np.abs(marginal-baseline.first[0]))<1e-14
    assert np.max(np.abs(masses-sampler.mass))<1e-14 and len(sampler.active)==169
    first=sampler.sample(512);allocation=np.array(first['class_counts'])
    # Construct the actual private-pair proposal from sampler components.
    proposal=np.zeros_like(joint)
    for c,ids in sampler.indices.items():
        for i,pi in zip(ids,sampler.probabilities[c]):
            opponent=baseline.live[0][1]*compatible[i]
            proposal[i]=allocation[c]/512*pi*opponent/opponent.sum()
    weights=512*sampler.mass/allocation
    recovered=proposal*weights[CLASSES,None]
    max_error=float(np.max(np.abs(recovered-joint)))
    assert max_error<1e-14 and abs(proposal.sum()-1)<1e-12
    # An omitted-weight integration must not be mistaken for the same game.
    unweighted_tv=float(np.abs(proposal-joint).sum()/2)
    assert unweighted_tv>0.05
    checkpoint=sampler.checkpoint();restored=ClassStratifiedDeals.restore(checkpoint,source)
    following=sampler.sample(512)
    assert following==restored.sample(512) and sampler.checkpoint()==restored.checkpoint()
    cases=[first,following];sample_start=time.monotonic()
    cases.extend(sampler.sample(512) for _ in range(14))
    stratified_seconds=time.monotonic()-sample_start
    base_start=time.monotonic();old=[baseline.sample(512) for _ in range(16)]
    baseline_seconds=time.monotonic()-base_start
    for case in cases:
        assert case['training_qualified'] is False and len(case['deals'])==512
        assert min(case['class_counts'])==3 and max(case['class_counts'])==4
        assert sum(n==4 for n in case['class_counts'])==5
        assert abs(math.fsum(case['deal_weights'])-512)<1e-10
        assert all(math.isfinite(w) and w>0 for w in case['deal_weights'])
        for cards,c,w in zip(case['deals'],case['hand_classes'],case['deal_weights']):
            assert len(cards)==len(set(cards))==9 and all(type(x) is int and 0<=x<52 for x in cards)
            assert cards[:2]==sorted(cards[:2]) and cards[2:4]==sorted(cards[2:4]) and cards[4:7]==sorted(cards[4:7])
            assert hand_class(cards[:2])==c
            assert abs(w-512*masses[c]/case['class_counts'][c])<1e-12
    rejected=0
    for count in (0,168,65537,True,512.0):
        before=sampler.checkpoint()
        try:sampler.sample(count)
        except ValueError:rejected+=1
        else:raise AssertionError('Invalid batch admitted')
        assert before==sampler.checkpoint()
    for field,value in [('method','wrong'),('batches',-1)]:
        bad=copy.deepcopy(checkpoint);bad[field]=value
        try:ClassStratifiedDeals.restore(bad,source)
        except ValueError:rejected+=1
        else:raise AssertionError('Invalid checkpoint admitted')
    changed=json.loads(source);changed['incoming_class_mass'][0][0]*=.9
    try:ClassStratifiedDeals.restore(checkpoint,json.dumps(changed))
    except ValueError:rejected+=1
    else:raise AssertionError('Changed context admitted')
    missing=[169-len(set(hand_class(row[:2]) for row in b['deals'])) for b in old]
    assert time.monotonic()-start<180
    for p,h in inputs.items():assert sha(p)==h
    save(OUT/f'{PREFIX}-result.json',dict(passed=True,registration_sha256=sha(rp),
        exact_private_pair_max_probability_error=max_error,unweighted_proposal_total_variation=unweighted_tv,
        sampled_hands=8192,stratified_empty_classes=0,baseline_mean_empty_classes=float(np.mean(missing)),
        minimum_importance_weight=float(min(weights)),maximum_importance_weight=float(max(weights)),
        exact_checkpoint_replay=True,negative_controls_rejected=rejected,
        stratified_14_batch_seconds=stratified_seconds,baseline_16_batch_seconds=baseline_seconds,
        seconds=time.monotonic()-start,training_qualified=False,poker_strength_claim=False,
        production_modified=False,scope='Full-deck sampling distribution and deterministic restart only; no learning integration.'))
    print(json.dumps(dict(passed=True,max_error=max_error,unweighted_tv=unweighted_tv,
        baseline_missing=float(np.mean(missing)),stratified_missing=0,
        seconds=time.monotonic()-start)),flush=True)


if __name__=='__main__':main()
