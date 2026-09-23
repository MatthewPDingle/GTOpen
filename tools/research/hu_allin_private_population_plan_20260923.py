"""Size the complete private-card population; no policies, outcomes or GPU work."""
import itertools
import json
import time
from pathlib import Path
import numpy as np
from reboot_research_idle_v1 import idle
from sampled_physical_deals_v1 import PhysicalDeals
from sampled_physical_root_evaluation_v1 import ROOT,sha,save,hand_class
from sampled_allin_protocol_v3 import AllinCache,canonical
from storage_strategic_common_prior_20260920 import PAIRS,MASKS,CLASSES

OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='allin-private-population-plan-v1'
STORE=Path('S:/GTOpen-research')/PREFIX


def main():
    started=time.monotonic()
    def guard():assert time.monotonic()-started<180 and idle()
    guard();assert not STORE.exists()
    context=OUT/'bb-context-candidate.json';review=OUT/'sampled-physical-allin-training-cache-v1-independent-review.json'
    prior=OUT/'sampled-physical-hybrid-allin-exact-root-mix-v1-result.json'
    paths=[Path(__file__),context,review,prior,*[ROOT/'tools/research'/n for n in (
        'sampled_physical_deals_v1.py','sampled_allin_protocol_v3.py',
        'storage_strategic_common_prior_20260920.py','reboot_research_idle_v1.py')]]
    reg=dict(inputs={str(p):sha(p) for p in paths},maximum_seconds=180,
        scope='Complete compatible-private-pair support and suit-orbit sizes for cost planning. No action policies, new exact-board enumeration, candidate inspection or strength claim.',production_modified=False)
    registration=OUT/f'{PREFIX}-registration.json';save(registration,reg);STORE.mkdir()
    base=PhysicalDeals(context.read_text(),mode='full_deck',seed=0)
    cache=AllinCache.from_review(review)
    compatible=(MASKS[:,None]&MASKS[None,:])==0
    positive=compatible&(base.weights[0,:,None]>0)&(base.weights[1,None,:]>0)
    ii,jj=np.nonzero(positive)
    mass=base.weights[0,ii]*base.weights[1,jj];mass/=mass.sum()
    keys=np.empty(len(ii),dtype=np.uint32)
    perms=list(itertools.permutations(range(4)))
    for start in range(0,len(ii),65536):
        guard();end=min(start+65536,len(ii))
        cards=np.concatenate((PAIRS[ii[start:end]],PAIRS[jj[start:end]]),axis=1).astype(np.uint32)
        best=np.full(len(cards),2**24-1,dtype=np.uint32)
        for perm in perms:
            mapped=4*(cards//4)+np.asarray(perm,dtype=np.uint32)[cards%4]
            a=np.minimum(mapped[:,0],mapped[:,1]);b=np.maximum(mapped[:,0],mapped[:,1])
            c=np.minimum(mapped[:,2],mapped[:,3]);d=np.maximum(mapped[:,2],mapped[:,3])
            best=np.minimum(best,(a<<18)|(b<<12)|(c<<6)|d)
        keys[start:end]=best
    unique,inverse,counts=np.unique(keys,return_inverse=True,return_counts=True)
    grouped=np.bincount(inverse,weights=mass,minlength=len(unique))
    cards=np.array([[(int(key)>>shift)&63 for shift in (18,12,6,0)] for key in unique])
    assert all(len(set(map(int,row)))==4 for row in cards)
    selected=np.linspace(0,len(unique)-1,min(1024,len(unique)),dtype=int)
    for index in selected:assert canonical(list(map(int,cards[index])))==tuple(map(int,cards[index]))
    # Check original physical pairs against the independent scalar routine,
    # not merely that the computed representative happens to be canonical.
    physical_selected=np.linspace(0,len(ii)-1,min(1024,len(ii)),dtype=int)
    for index in physical_selected:
        expected=canonical(list(map(int,PAIRS[ii[index]]))+list(map(int,PAIRS[jj[index]])))
        actual=tuple((int(keys[index])>>shift)&63 for shift in (18,12,6,0))
        assert actual==expected
    direct=np.bincount(CLASSES[ii]*169+CLASSES[jj],weights=mass,minlength=169*169).reshape(169,169)
    byclass=np.zeros((169,169))
    for row,weight in zip(cards,grouped):byclass[hand_class(list(map(int,row[:2]))),hand_class(list(map(int,row[2:])))]+=weight
    class_error=float(np.max(abs(direct-byclass)));assert class_error<1e-12
    original=json.loads(prior.read_text());prior_error=float(np.max(abs(direct.sum(1)-np.asarray(original['class_probabilities']))));assert prior_error<1e-12
    records=[dict(private_cards=list(map(int,row)),probability=float(weight),physical_pairs=int(count),cached=tuple(map(int,row)) in cache.rows) for row,weight,count in zip(cards,grouped,counts)]
    assert abs(sum(r['probability'] for r in records)-1)<1e-12
    document=dict(context_sha256=sha(context),player_roles_fixed=True,physical_pairs=len(ii),rows=records)
    artifact=STORE/'private-population.json';save(artifact,document)
    covered=sum(r['cached'] for r in records);new=len(records)-covered
    for p,h in reg['inputs'].items():assert sha(p)==h,p
    result=dict(passed=True,registration_sha256=sha(registration),artifact=str(artifact),artifact_sha256=sha(artifact),
        physical_pairs=len(ii),canonical_private_pairs=len(records),cached_pairs=covered,new_exact_keys_needed=new,
        cached_probability_mass=sum(r['probability'] for r in records if r['cached']),
        maximum_class_pair_mass_error=class_error,maximum_prior_class_mass_error=prior_error,
        scalar_representative_checks=len(selected),scalar_physical_pair_checks=len(physical_selected),
        seconds=time.monotonic()-started,gpu_used=False,production_modified=False,
        accuracy_qualified=False,scope=reg['scope'])
    save(OUT/f'{PREFIX}-result.json',result);print(json.dumps(result))


if __name__=='__main__':main()
