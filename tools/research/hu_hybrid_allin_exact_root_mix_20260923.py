"""Aggregate frozen class policies under the complete compatible-card prior.

This removes test-sample hand-composition noise from action-frequency summaries.
It does not revalue actions, train a policy, or replace the registered tests.
"""
import json
from pathlib import Path
import time
import numpy as np
import psutil
from loopback_research_validation import idle
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from sampled_physical_deals_v1 import PhysicalDeals

OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='sampled-physical-hybrid-allin-exact-root-mix-v1'


def main():
    started=time.monotonic();assert idle() and psutil.virtual_memory().available>=20_000_000_000
    source=OUT/'sampled-physical-hybrid-allin-comparison-v1-result.json'
    comparison=json.loads(source.read_text())
    assert sha(ROOT/'tools/research/hu_sampled_physical_hybrid_allin_comparison_20260923.py')==comparison['source_sha256']
    assert sha(ROOT/'tools/research/hu_sampled_physical_dense_comparison_20260922.py')==comparison['reader_sha256']
    for candidate in comparison['candidates'].values():
        for p,h in candidate['evidence'].items():assert sha(p)==h
    for p,h in comparison['btn']['evidence'].items():assert sha(p)==h
    context_path=OUT/'bb-context-candidate.json';context_source=context_path.read_text()
    context=json.loads(context_source)
    for candidate in comparison['candidates'].values():
        registrations=[Path(p) for p in candidate['evidence'] if p.endswith('-registration.json')]
        assert len(registrations)==1
        candidate_reg=json.loads(registrations[0].read_text())
        assert sha(candidate_reg['context'])==sha(context_path)
        for p,h in candidate_reg['inputs'].items():assert sha(p)==h
    pairs=np.array([(a,b) for a in range(52) for b in range(a+1,52)])
    assert len(pairs)==1326
    # Independent enumeration, without importing the sampler's pair/class tables.
    classes=[]
    for a,b in pairs:
        lo,hi=sorted((int(a)//4,int(b)//4))
        classes.append(hi*13+lo if a%4==b%4 or hi==lo else lo*13+hi)
    classes=np.array(classes);counts=np.bincount(classes,minlength=169)
    assert sorted(set(counts))==[4,6,12]
    masses=np.asarray(context['incoming_class_mass'],dtype=np.float64)
    assert masses.shape==(2,169) and np.isfinite(masses).all() and (masses>=0).all()
    weights=masses[:,classes]/counts[classes]
    weights/=weights.max(1)[:,None];weights[weights<1e-5]=0
    # Apply the same declared relative entry cutoff, then exclude every shared
    # physical card directly, rather than relying on inclusion/exclusion counts.
    compatible=((pairs[:,None,0]!=pairs[None,:,0])&(pairs[:,None,0]!=pairs[None,:,1])
        &(pairs[:,None,1]!=pairs[None,:,0])&(pairs[:,None,1]!=pairs[None,:,1]))
    joint=weights[0,:,None]*weights[1,None,:]*compatible
    total=float(joint.sum());assert total>0 and np.isfinite(total)
    marginal=joint.sum(1)/total
    class_probability=np.bincount(classes,weights=marginal,minlength=169)
    assert np.max(abs(class_probability.sum()-1))<1e-12
    sampler=PhysicalDeals(context_source,mode='full_deck',seed=0)
    assert sampler.draws==0
    sampler_error=float(np.max(abs(marginal-sampler.first[0])));assert sampler_error<1e-12
    inputs=[source,context_path,Path(__file__),ROOT/'tools/research/sampled_physical_deals_v1.py',
        ROOT/'tools/research/storage_strategic_common_prior_20260920.py']
    inputs += [Path(p) for c in comparison['candidates'].values() for p in c['evidence']]
    inputs += [Path(p) for p in comparison['btn']['evidence']]
    reg=dict(inputs={str(p):sha(p) for p in set(inputs)},physical_combos=1326,
        entry_relative_cutoff=1e-5,scope='Post-audit class-policy aggregation under the complete physical compatible-card prior. No new sampling, policy inference, action revaluation or significance claim.',production_modified=False)
    regpath=OUT/f'{PREFIX}-registration.json';save(regpath,reg)
    candidates={}
    for name,candidate in comparison['candidates'].items():
        rows=candidate['classes'];assert len(rows)==169
        assert [r['hand_class'] for r in rows]==list(range(169))
        policy=np.asarray([r['baseline_probabilities'] for r in rows])
        assert policy.shape==(169,4) and np.isfinite(policy).all() and (policy>=0).all()
        assert np.max(abs(policy.sum(1)-1))<1e-12
        exact=class_probability@policy
        counts_test=np.array([r['test_deals'] for r in rows]);assert counts_test.sum()==16384
        sample=counts_test@policy/16384
        assert np.max(abs(sample-np.asarray(candidate['baseline_action_mix'])))<1e-12
        # Direct per-physical-combo aggregation independently checks grouping.
        direct=marginal@policy[classes];assert np.max(abs(direct-exact))<1e-12
        candidates[name]=dict(complete_prior_action_mix=exact.tolist(),sampled_test_action_mix=sample.tolist(),
            sample_minus_complete_prior=(sample-exact).tolist())
    previous=np.array([r['baseline_probabilities'] for r in comparison['candidates']['allin']['classes']])
    combined=np.array([r['baseline_probabilities'] for r in comparison['candidates']['combined']['classes']])
    change=combined-previous
    details=[dict(hand=row['hand'],hand_class=i,entry_probability=float(class_probability[i]),
        allin_to_combined_action_change=change[i].tolist()) for i,row in enumerate(comparison['candidates']['combined']['classes'])]
    assert idle() and time.monotonic()-started<120
    for p,h in reg['inputs'].items():assert sha(p)==h
    result=dict(passed=True,registration_sha256=sha(regpath),source_sha256=sha(source),
        physical_combo_count=len(pairs),positive_compatible_pairs=int(np.count_nonzero(joint)),
        class_probabilities=class_probability.tolist(),sampler_marginal_maximum_error=sampler_error,
        candidates=candidates,allin_to_combined_class_weighted_total_variation=float(class_probability@(abs(change).sum(1)/2)),
        class_changes=details,seconds=time.monotonic()-started,accuracy_qualified=False,production_modified=False,
        scope=reg['scope']+' Exact aggregation of the recorded class policies, not an independent all-suit network-invariance proof. This does not compare common-opponent EVs or establish equilibrium accuracy.')
    save(OUT/f'{PREFIX}-result.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ('class_probabilities','class_changes')}),flush=True)


if __name__=='__main__':main()
