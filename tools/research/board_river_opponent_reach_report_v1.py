"""Describe the fixed diagnostic and its explicitly post-hoc reach attribution."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
from pathlib import Path
import math
import numpy as np
from board_later_fit_holdout_run_v1 import OUT,read,sha,verify
from board_prefix_publication_v1 import atomic_json

PREFIX='board-river-opponent-reach-v1'


def main():
    sources=[OUT/(PREFIX+suffix) for suffix in ('-result.json','-independent-review.json','-attribution.json')]
    result,review,attribution=map(read,sources)
    assert all(r['passed'] and r['complete'] for r in (result,review,attribution))
    hashes={str(p):sha(p) for p in sources+[Path(__file__)]}
    rows=review['rows'];attr={(r['case_id'],r['bank']):r for r in attribution['rows']}
    assert len(rows)==160 and len(attr)==160
    bands=[]
    for band in ('under10','10to50','50to100','100to200','200plus'):
        chosen=[r for r in rows if r['pot_band']==band];assert len(chosen)==32
        gains=[r['original']['restricted_switch_gain_bb'] for r in chosen]
        bands.append(dict(band=band,bank_cases=32,mean_gain_bb=float(np.mean(gains)),median_gain_bb=float(np.median(gains)),
            initialization_only=sum(attr[r['case_id'],r['bank']]['initial_only_to_numerical_tolerance'] for r in chosen)))
    # A bounded candidate may also change raises; this distance is descriptive,
    # and is deliberately not converted into a whole-policy payoff difference.
    change=max(max(abs(r['original'][k]-r['bounded'][k]) for k in
        ('fold_probability','call_probability','other_action_probability')) for r in rows)
    analysis=dict(inputs=hashes,bands=bands,maximum_bounded_probability_component_change=change,
        query_balanced=True,population_claim=False,decision='Proceed to a separate fresh-data exact-target versus sampled-target learning probe; do not deploy.')
    target=OUT/(PREFIX+'-analysis.json');assert not target.exists();atomic_json(target,analysis)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(11,4.5),layout='constrained')
    for initial,color,label in ((False,'#1873a5','Later trained policies contribute'),(True,'#a85d31','Initialization only (numerical tolerance)')):
        chosen=[r for r in rows if attr[r['case_id'],r['bank']]['initial_only_to_numerical_tolerance']==initial]
        for ax,xkey in zip(axes,('pot','hero_own_likelihood')):
            ax.scatter([r[xkey] for r in chosen],[r['original']['restricted_switch_gain_bb'] for r in chosen],
                color=color,label=label,s=27,alpha=.7,edgecolors='none')
            ax.grid(alpha=.2);ax.set_ylabel('Local Fold/Call reallocation gain (bb)')
    axes[0].set_xlabel('Pot before calling (bb)');axes[1].set_xlabel("Hero's own prior-action probability (not joint reach)")
    axes[1].set_xscale('log');axes[0].legend(fontsize=8)
    fig.suptitle('80 selected river states, each checked against two frozen banks\nLocal costs, not losses per dealt hand',fontsize=12)
    plot=OUT/(PREFIX+'.png');assert not plot.exists();fig.savefig(plot,dpi=170);plt.close(fig)
    table='\n'.join(f"| {r['band']} | {r['bank_cases']} | {r['mean_gain_bb']:.3f} | {r['median_gain_bb']:.3f} | {r['initialization_only']} |" for r in bands)
    summary=attribution['summary'];trained=summary['later_generations_contribute'];initial=summary['initial_only']
    text=f'''# Conditional river diagnostic: findings and next decision

The fixed 80-case diagnostic completed in **{result['seconds_this_invocation']/60:.2f} minutes**, and independent CPU readback passed.
It found room to improve Fold/Call decisions against each frozen model's own opponent range. This is more useful evidence for a training experiment than the tiny, inconclusive gains from the preceding river-bounds pilot. It does not establish improved preflop ranges.

## What was calculated

For every selected visible river decision, enumerate all 990 legal opponent hands, apply the original entry range, and weight each hand by the frozen opponent's probability of taking the actual prior actions. Compute exact Call minus Fold for that conditional range, including ties and configured rake. The actor never receives hidden cards or future board cards.

Both original 78-model banks were checked, giving **160 bank/case calculations** over **258,957 exported observations**. All selected histories have positive opponent support and positive hero history probability. Positive support alone does not mean that a history is common.

Each reported gain reallocates only the strategy's existing Fold/Call probability to the better of those two actions. Raise/jam probabilities stay fixed. It is a valid local improvement against the specified fixed opponent, not a full best response where raising is legal, and not a prediction of whole-game win rate.

## Results, with the rare-path qualification

| Current pot (bb) | Bank/cases | Mean local gain (bb) | Median local gain (bb) | Initialization-only cases |
|---|---:|---:|---:|---:|
{table}

The cases were deliberately balanced across actor and pot size, selected from an old 32-deal archive before inference. This overrepresents some expensive and rare branches relative to actual play. The two bank measurements of one case are related, not independent hands. Do not report the overall mean of 10.415 bb as exploitability, bb/hand, or an expected deployment gain.

An explicitly **post-hoc** attribution check found that **{initial['cases']}/160** decisions were supported only by the initial policy, to numerical tolerance. Their median hero prior-action probability was **{initial['median_hero_history_likelihood']:.3g}**. The largest apparent errors were in this group: later trained strategies almost never take those same personal action paths. Their conditional behavior is consequently still the early uniform strategy.

This does not explain everything. In the other **{trained['cases']}** bank/cases, where later trained strategies contribute, the median local improvement was **{trained['median_local_gain_bb']:.3f} bb** and the mean was **{trained['mean_local_gain_bb']:.3f} bb**. Their median hero prior-action probability was **{trained['median_hero_history_likelihood']:.4f}**. These remain selected-state diagnostics, not population estimates. All cases are retained; no averaging weights or support thresholds were changed.

![Local decision costs and rare-path attribution]({PREFIX}.png)

## What this says about preflop modeling

The later-play policies still make avoidable decisions against their own modeled opponents. That matters because preflop calling and raising values depend on what happens after the flop. However, this diagnostic does not isolate a single cause: limited coverage, fitting error, training-target noise, policy drift, and finite training may all contribute. It does not prove that noisy targets alone caused the range discrepancies.

The conditional reference now gives us a practical way to test a more informative learning target. It is exact for this frozen opponent and restricted game, not an equilibrium oracle. The scope remains the inherited incoming ranges of the 200bb BB-versus-BTN subtree; other stacks, positions and multiway play are not validated.

## Next bounded experiment

Use a **new set of physical deals**, split by deal before selecting observations, for a small controlled target-learning comparison. Freeze the opponent. Compare training on the exact conditional Fold/Call contrast with training on sampled opponent outcomes whose expectation is that same contrast. Keep the visible inputs, selected training states, learner, normalization and fitting budget identical. Evaluate on untouched deal groups using exact contrasts, action direction and restricted decision cost. Record generation-zero support separately.

First verify that the sampled-label estimator is unbiased for the specified target and that no hidden information enters the input. This is a local supervised feasibility test, not a replacement for the current CFR advantage estimator. If it succeeds, derive and test the integration into the self-play estimator with its correct reach/importance weights. Then a separately registered full-policy comparison on fresh deals is required before claiming better preflop ranges or deploying anything.

Do not extend the small-bounds pilot solely to confirm its tiny gains, erase initialization from the frozen banks, or launch a broad retraining campaign on these 80 reused diagnostic cases.

## Verification and resources

Controls covered blockers, ties, rake, zero reach, suit relabeling, hidden-card isolation and equivalence with the existing native query exporter. Independent scalar readback reproduced entry weights, history likelihoods, equity and payoff arithmetic within **{review['maximum_scalar_error']:.3g}**; it reuses the native poker evaluator and is not a second independent poker engine. The behavioral-versus-mixture reach identity agreed within **{attribution['maximum_reach_identity_error']:.3g}**.

The run retained **{result['storage']['logical_bytes']/1e6:.2f} MB**, including the earlier controls. Peak own CUDA tensors were **{result['peak_cuda_allocated_bytes']/1e6:.1f} MB**, with **{result['peak_cuda_reserved_bytes']/1e6:.1f} MB** reserved by the allocator. It shared light desktop use under the 4 GB allocation cap and 2 GB external headroom rule. Readback used eight CPU workers; attribution used four. Their elapsed times were {review['seconds']:.2f} and {attribution['seconds']:.2f} seconds.

Nothing was deployed. Original training banks, production settings and historical archives remain unchanged. The broader research goal remains active.

Evidence: `{PREFIX}-result.json`, `{PREFIX}-independent-review.json`, `{PREFIX}-attribution.json`, `{PREFIX}-analysis.json`, and their immutable registrations.
'''
    report=OUT/'BOARD-RIVER-OPPONENT-REACH-FINDINGS.md';assert not report.exists()
    with report.open('x',encoding='utf-8',newline='\n') as f:f.write(text)
    verify(hashes)
    print(str(report))


if __name__=='__main__':main()
