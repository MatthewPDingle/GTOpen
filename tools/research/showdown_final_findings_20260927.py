"""Publish all completed showdown contrasts and root policies after verification."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'showdown-pipelined-evaluation-study-v1'
REVIEW = 'showdown-parallel-readback-v1'


def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    rp, pp = [OUT/f'{PREFIX}-{s}.json' for s in ('registration','result')]
    ap = OUT/f'{REVIEW}-independent-review.json'
    ep = OUT/f'{REVIEW}-execution-result.json'
    reg, result, audit, execution = map(read,(rp,pp,ap,ep))
    assert result['passed'] and result['complete'] and result['deals']==65536
    assert audit['passed'] and audit['deals']==65536 and execution['passed']
    assert audit['source_result_sha256']==sha(pp)
    assert result['registration_sha256']==audit['source_registration_sha256']==sha(rp)
    assert execution['independent_review_sha256']==sha(ap)
    assert execution['execution_registration_sha256']==sha(OUT/f'{REVIEW}-execution-registration.json')
    assert audit['readback_registration_sha256']==sha(OUT/f'{REVIEW}-readback-registration.json')
    for p,h in read(OUT/f'{REVIEW}-execution-registration.json')['inputs'].items():
        assert sha(Path(p))==h
    store=Path(result['store'])
    for name,key,target in [('analysis.json','analysis_sha256','showdown-final-analysis.json'),
            ('root-stability.json','root_stability_sha256','showdown-final-root-stability.json')]:
        assert sha(store/name)==result[key]
        destination=OUT/target
        assert not destination.exists()
        destination.write_bytes((store/name).read_bytes())
    analysis=read(store/'analysis.json');roots=read(store/'root-stability.json')
    assert len(analysis['contrasts'])==8
    assert all(x['count']==65536 and x['mean']<0 and x['lower']<0<x['upper'] for x in analysis['contrasts'])
    comparisons=roots['comparisons']; old=comparisons['baseline_cross_seed'];new=comparisons['candidate_cross_seed']
    rows='\n'.join(f"| {x['name']} | {x['mean']:+.4f} | {x['standard_error']:.4f} | [{x['lower']:+.4f}, {x['upper']:+.4f}] |" for x in analysis['contrasts'])
    freq='\n'.join('| '+p+' | '+' | '.join(f'{100*v:.2f}%' for v in f)+' |' for p,f in zip(roots['policy_order'],roots['aggregate_action_frequencies']))
    # Export explicit native labels alongside all probabilities, never display-grid indices.
    import sys
    sys.path.insert(0,str(ROOT/'tools/research'))
    from storage_strategic_common_prior_20260920 import PAIRS, CLASSES
    ranks='23456789TJQKA';labels={}
    for pair,c in zip(PAIRS,CLASSES):
        hi,lo=sorted((int(pair[0])//4,int(pair[1])//4),reverse=True)
        name=ranks[hi]+ranks[lo]+('' if hi==lo else 's' if int(pair[0])%4==int(pair[1])%4 else 'o')
        c=int(c)
        assert c not in labels or labels[c]==name
        labels[c]=name
    assert len(labels)==169
    classes=[dict(native_class_index=i,hand=labels[i],entry_mass=roots['entry_masses'][i],
        policies={p:dict(zip(roots['action_order'],bank[i])) for p,bank in zip(roots['policy_order'],roots['root_probabilities'])},
        total_variation={k:v['class_total_variation'][i] for k,v in comparisons.items()}) for i in range(169)]
    (OUT/'showdown-final-all-hand-classes.json').write_text(json.dumps(classes,indent=2)+'\n',encoding='utf-8')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(10,5.6),layout='constrained')
    for i,x in enumerate(analysis['contrasts']):
        ax.errorbar(x['mean'],i,xerr=[[x['mean']-x['lower']],[x['upper']-x['mean']]],fmt='o',capsize=4,color='#286e9e' if i<4 else '#b36326')
    ax.axvline(0,color='#555',linewidth=1)
    ax.set_yticks(range(8),[x['name'].replace('first:','Run 1: ').replace('replication:','Run 2: ').replace('-v-oldBB','').replace('-v-oldBTN','').replace('-against-',' vs ') for x in analysis['contrasts']])
    ax.invert_yaxis();ax.grid(axis='x',alpha=.2)
    ax.set_xlabel('Gain from replacing one player (bb per entry; positive favors correction)')
    ax.set_title('Showdown correction: all eight intervals span zero\n65,536 common deals; registered simultaneous 95% bounded intervals')
    fig.savefig(OUT/'showdown-final-gains.png',dpi=150);plt.close(fig)
    text=f'''# Showdown correction: completed study

The correction has not demonstrated better preflop play. It modestly reduces
the difference between the two training runs, but leaves substantial hand-range
instability. All eight payoff estimates are slightly negative and all registered
intervals span zero. That is an inconclusive strength result, not proof of harm,
equivalence, or general failure of variance reduction. Do not deploy this candidate.

## What was tested

The restricted BB-versus-BTN context has a 200bb stack, a 2bb open, 0.5bb dead
money, and 5% rake capped at 2bb. Four arms used two fresh matched seeds,
78 updates and 512 physical deals per update. Both treatments integrate root
and later postflop actions; the candidate additionally applies a fixed, centered
showdown correction to BB root learning targets. Evaluation uses unchanged poker
payoffs, not corrected targets.

Every full training arm passed scalar readback. Each evaluated policy averages
played generations 0–77 with weights 1–78 and own-action reach. Generation 78
was not played and is excluded. The fixed final evaluation used 65,536 fresh
common deals across eight crossed profiles. There was no outcome-based sample
extension, favorable checkpoint selection, or changed statistical rule.

## Range stability

Cross-seed root total variation decreased from **{100*old['entry_weighted_total_variation']:.2f}%
to {100*new['entry_weighted_total_variation']:.2f}%**, a **{100*(old['entry_weighted_total_variation']-new['entry_weighted_total_variation']):.2f}-percentage-point** reduction.
The most frequent action still differs in **{new['classes_with_different_most_frequent_action']} of 169 classes**, compared with
{old['classes_with_different_most_frequent_action']} for the baseline. This is a descriptive comparison of two seeds.
Total variation measures how much action probability must move to reconcile
the policies; it is not the percentage of hands played incorrectly.

| Complete bank | Fold | Call | Raise | Jam |
| --- | ---: | ---: | ---: | ---: |
{freq}

Within matched seeds, the correction changes root probability by
{100*comparisons['first_matched_change']['entry_weighted_total_variation']:.2f}% and
{100*comparisons['replication_matched_change']['entry_weighted_total_variation']:.2f}% total variation.
Aggregate frequencies hide these large per-hand changes. The
[complete 169-class table](showdown-final-all-hand-classes.json) includes native
indices, labels checked against every physical private-hand combination, all
four policies, entry masses and every per-class comparison. The
[original stability data](showdown-final-root-stability.json) is copied byte-for-byte.

## Playing-strength comparison

Positive values mean the replacement player gains against the specified fixed
opponent. Units are bb per entry into this research spot, not bb/100 dealt hands.
The intervals are the prospectively registered bounded empirical-Bernstein
intervals with Bonferroni adjustment over all eight contrasts, family error 0.05,
at one final look. Ordinary paired standard errors are also shown.

| Replacement and fixed opponent | Mean gain | Standard error | Simultaneous 95% interval |
| --- | ---: | ---: | ---: |
{rows}

![All eight gains and intervals](showdown-final-gains.png)

The negative point estimates provide no encouraging strength signal here,
but their uncertainty does not establish harm. Wider simultaneous intervals
reflect rare large-pot outcomes and the fixed coverage requirement. We do not
replace them with narrower post-hoc intervals. More evaluation alone would
not stabilize the already-trained policies. [Full analysis](showdown-final-analysis.json).

## Verification, performance and retained history

The independent reviewer checked all 2,048 batches, **{audit['observations']:,} policy
observations**, reconstructed the exact chance stream, checked the two archive
sources, all crossed policies, root summaries, payoff accounting and all eight
statistical reductions. Maximum numerical discrepancy was
{audit['maximum_statistical_error']:.3g}. This does not independently reimplement
neural inference or native poker evaluation and is not a best-response certificate.

CPU archive work had kept the GPU waiting. Parallel archival processing improved
observed sampling throughput from roughly 2.3 to 7.2 hands/sec while preserving
the original 19,776 completed hands. The remaining 45,760 hands completed in the
separate registered continuation. These are sampling-stage measurements, not
training or whole-project speedups.

The initial serial verifier was also underusing the CPU. An eight-worker control
checked 512 reused hands with exactly matching serial outputs and rejected invalid
batch metadata; it took 12.09 seconds versus 46.34 seconds including startup
(3.83x). The full parallel review checked every hand from the beginning and
finished in **{audit['seconds']/60:.2f} minutes**. It used the unchanged original decoder
and scalar checks; results were combined in original order.

After that complete proof and source-immutability checks passed, the redundant
serial reviewer was intentionally stopped. Its controller consequently exited
with an assertion, as expected; it is not represented as a completed serial
review. The sampling result remains complete, and the separately named parallel
execution/result proves full verification. Original interrupted sampling records,
partial serial logs and the retirement record remain retained.

Production port 56708 and production code were not changed. No candidate was deployed.

## Next useful step

Do not spend another full training run simply retuning this correction. Prior
diagnostics found roughly two observations per hand class per update, empty
classes in many updates, noisy call-versus-raise values, and continued policy
movement. This experiment has not resolved that larger problem.

First use the newly completed training records to quantify class coverage and
late-policy movement for all four arms with the same definitions as the prior
study. Then qualify a small class-stratified sampling pilot: ensure regular
coverage while preserving the intended physical-card distribution through
explicit conditional sampling and any required weights. Check estimator
expectations, action-target variance, fitting behavior and time per useful
observation before a new fixed-budget matched study. This is a proposed research
direction, not a claim that stratification will solve within-class runout noise
or that a particular speedup/accuracy improvement is already available.

Future substantial runs should first inspect competing workloads and benchmark
CPU worker counts, GPU batches, RAM and I/O on a representative small workload.
Use available resources to shorten completion time, preserve room for user solves,
and avoid serial evidence processing when independent batches can run concurrently.

The larger goal still requires reliable learning and validation across positions,
stack depths, sizing trees and multiway contexts. This one spot and two seeds
cannot support those broader claims.

## Evidence identities

- Sampling registration: `{sha(rp)}`
- Completed sampling result: `{sha(pp)}`
- Completed parallel independent review: `{sha(ap)}`
- Parallel execution result: `{sha(ep)}`
- Analysis: `{result['analysis_sha256']}`
- Root policies and stability: `{result['root_stability_sha256']}`

Generated from authenticated completed artifacts by
`tools/research/showdown_final_findings_20260927.py`.
'''
    (OUT/'SHOWDOWN-MATCHED-FINAL-FINDINGS.md').write_text(text,encoding='utf-8')
    print('Published complete findings, all eight contrasts, all 169 classes and graph.')


if __name__=='__main__': main()
