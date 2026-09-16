"""Compact matched-solve evidence. Does not read or modify the live session."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import json,sys
import numpy as np
import learned_interface as study
import range_value_pilot as pilot

def analyze():
    checkpoints=[];latest={};normalized=0
    for arm in ['original','balanced','candidate']:
        for file in sorted((study.OUT/arm).glob('iteration-*.json'),key=lambda p:int(p.stem.split('-')[1])):
            d=json.loads(file.read_text());latest[arm]=d
            for row in d['views']:
                v=row['view'];sigma=np.array(v['strategy']).reshape(-1,169)
                assert np.isfinite(sigma).all() and sigma.min()>=-1e-7 and sigma.max()<=1+1e-7
                assert abs(sigma.sum(axis=0)-1).max()<2e-6
                normalized+=169
            checkpoints.append(dict(arm=arm,iteration=d['iteration'],start_iteration=d['start_iteration'],
                learning_seconds=d['learning_seconds'],seconds_per_iteration=d['learning_seconds']/(d['iteration']-d['start_iteration']),
                ev_sum_bb=sum(d['evs']),evs=d['evs'],surrogate_gap_bb=sum(d['gaps']),sha256=pilot.sha(file)))
    target=min(d['iteration'] for d in latest.values());rows=[]
    latest={arm:json.loads((study.OUT/arm/f'iteration-{target}.json').read_text()) for arm in latest}
    bypath={a:{tuple(r['path']):r['view'] for r in d['views']} for a,d in latest.items()}
    for path,v in bypath['original'].items():
        row=dict(path=list(path),seat=v['actor_pos'],actions=[a['label'] for a in v['actions']])
        for arm,vs in bypath.items():
            v=vs[path];assert row['actions']==[a['label'] for a in v['actions']]
            sigma=np.array(v['strategy']).reshape(-1,169)
            row[arm]=dict(frequencies=[a['freq'] for a in v['actions']],mixed_hands=int(((sigma>.01).sum(axis=0)>1).sum()),
                probes={h:sigma[:,pilot.INDEX[h]].tolist() for h in ['AA','KK','QQ','AKs','AQs','KQo','TT','76s']})
        rows.append(row)
    previous=study.old.OUT/'balanced'/f'iteration-{target}.json'
    control=None
    if previous.exists():
        prior=json.loads(previous.read_text());assert prior['config']==latest['original']['config']
        a={tuple(r['path']):r['view']['strategy'] for r in prior['views']}
        error=max(float(abs(np.array(a[path])-np.array(v['strategy'])).max()) for path,v in bypath['original'].items())
        ev_error=float(abs(np.array(prior['evs'])-np.array(latest['original']['evs'])).max())
        assert error<1e-6 and ev_error<1e-6
        control=dict(previous_sha256=pilot.sha(previous),max_policy_error=error,max_ev_error_bb=ev_error)
    result=dict(iteration=target,normalized_hand_rows=normalized,checkpoints=checkpoints,rows=rows,previous_control=control,
        caveat='Frequencies use the UI independent-class summary convention. Conditional per-hand policies are validated. Diagnostic partial solves; range-conditioned surrogate gaps are not full-game exploitability.')
    study.write(study.OUT/'comparison.json',result)
    print(json.dumps(checkpoints,indent=2))

def report():
    d=json.loads((study.OUT/'comparison.json').read_text());o=json.loads((study.OUT/'oracle-check.json').read_text())
    reference_path=study.OUT/'references/comparison.json'
    refs=json.loads(reference_path.read_text()) if reference_path.exists() else None
    rows=d['rows'];points=d['checkpoints'];target=d['iteration']
    names={'original':'Current Balanced','balanced':'Corrected chance + Balanced','candidate':'Corrected chance + learned'}
    latest={a:next(c for c in points if c['arm']==a and c['iteration']==target) for a in names}
    ratios={a:latest[a]['seconds_per_iteration']/latest['original']['seconds_per_iteration'] for a in names}
    tests=o['tests'];maximum=max(t['max_action_error_bb'] for t in tests)
    text=['# Learned continuation: consistent chance/value interface','',
        '**Research only. Port 56708 remains unchanged.** The frozen predictor now passes the probability/accounting checks. That does not establish poker accuracy or a production-ready speed.','',
        '## What changed','',
        'Each heads-up branch now carries one consistent legal card-pair probability through folds, calls, all-ins and postflop continuation values. The same weighting applies to chips already invested by folded players. There is no extra offset added to force the total to zero. The predictor coefficients were not changed.','',
        'In a two-player game, the card-pair probabilities are exact for suit-symmetric hand classes. In the eight-player experiment, that joint distribution is reset when two live players remain. Cards belonging to previously folded players and earlier multiplayer correlations are still omitted. Cached showdown equity remains approximate.','',
        '## Independent checks','',
        f"- {len(tests)} fixed-policy cases: two, three and eight players, current and learned continuation models, dense and sparse policies including whole unreachable branches.",
        f"- {sum(t['action_values_checked'] for t in tests):,} GPU action values checked against independently enumerated physical card pairs; maximum discrepancy {maximum:.9f} bb.",
        '- Two-player root values, individual terminal chip accounting, all-ins, folds, and folded players\' sunk costs checked. Evaluation left stored strategy/regret arrays unchanged.',
        f"- {d['normalized_hand_rows']:,} inspected hand-policy rows were finite, nonnegative and summed to one.",
        '- Ordinary CPU and GPU regression-suite results, reference tolerances and source hashes are retained in [validation.json](validation.json).','',
        '## Matched preflop runs','',
        f'All three arms start fresh from the same zero-rake, SB 0.5 eight-player straddle setup and reach {target} iterations. These are diagnostic partial solves, not certified equilibrium ranges.','',
        '| Version | EV sum, bb/hand | Frozen-value gap, bb | Seconds/iteration | Time vs current |',
        '|---|---:|---:|---:|---:|']
    for a in names:
        c=latest[a];text.append(f"| {names[a]} | {c['ev_sum_bb']:.9f} | {c['surrogate_gap_bb']:.5f} | {c['seconds_per_iteration']:.3f} | {ratios[a]:.2f}x |")
    text+=['','Timing is a single sequential matched run on this machine, including graph capture in each resumed segment; it is a screening measurement, not a controlled repeated benchmark. The production-speed screen was no more than 25% overhead. No deployment is implied.','',
        'The best-response gaps freeze the range-dependent predictions and chance anchors. They are not full-game exploitability. A smaller number cannot establish convergence of this changing continuation model.','',
        '| Decision | Current call | Corrected + Balanced | Corrected + learned |','|---|---:|---:|---:|']
    chosen=[r for r in rows if r['seat']=='BB' and any(a.startswith('Call') for a in r['actions'])]
    for r in chosen:
        idx=next(i for i,a in enumerate(r['actions']) if a.startswith('Call'));label='BB vs early open' if r['path'][0]==1 else 'BB vs BTN'
        text.append('| '+label+' | '+' | '.join(f"{r[a]['frequencies'][idx]*100:.2f}%" for a in names)+' |')
    text+=['','Aggregate frequencies retain the UI\'s independent-class display convention. Per-hand probabilities are the direct solver policies. Wider calls are not automatically more accurate.','']
    if refs:
        text+=['## Fresh postflop checks','',
            'Forty fresh solves cover the learned policy\'s BB-call branches against early position and BTN: 20 previously unused, stratified flops each. All must pass both GPU and full-enumeration CPU checks at 0.1% pot. The model is unchanged. Tiny range cleanup and probe additions are recorded in the reference manifest and used identically for prediction and solving.','',
            '| Branch | Current error (% pot) | Corrected Balanced error | Learned error | Relative improvement | 90% bootstrap interval |',
            '|---|---:|---:|---:|---:|---:|']
        for r in refs['cases']:
            e=r['weighted_mae_pot'];lo,hi=r['bootstrap_90_improvement'];text.append(f"| {' vs '.join(r['positions'])} | {e['original']*100:.2f} | {e['paired']*100:.2f} | {e['candidate']*100:.2f} | {r['improvement']*100:.1f}% | {lo*100:.1f}% to {hi*100:.1f}% |")
        text+=['','Error is range-weighted absolute conditional-value error. The reference uses cached preflop equity as a control variate plus the sampled postflop residual; the equity cache itself is Monte Carlo. These small samples exclude earlier boards and do not cover the complete board distribution. Intervals are exploratory, based on 300 stratified resamples.','',
            'The prospective screen required at least 15% lower average error in each branch. Result: **'+('passed' if refs['all_screening_pass'] else 'failed')+'**. Hand-level regressions remain visible in `references/comparison.json`. The underlying scenario family also appeared in training, so these are changed-policy stress tests, not independent scenario generalization.','']
        text+=['The 0.1% convergence bound is range-weighted; it does not independently certify each rare probe hand. Probe errors are diagnostic and need tighter targeted references before being used as promotion criteria.','',
            '| Branch | Current probe error (% pot) | Learned probe error | Negative learned values |',
            '|---|---:|---:|---:|']
        for r in refs['cases']:
            p=r['uniform_probe_mae_pot'];text.append(f"| {' vs '.join(r['positions'])} | {p['original']*100:.2f} | {p['candidate']*100:.2f} | {len(r['negative_candidate_predictions'])} |")
        text+=['']
        text+=['Examples contributing to the regressions (gross value as a fraction of pot):','',
            '| Branch | Player / hand | Reference estimate | Current | Learned |','|---|---|---:|---:|---:|']
        for r in refs['cases']:
            for h in r['worst_mass_weighted_regressions'][:3]:
                text.append(f"| {' vs '.join(r['positions'])} | {h['position']} {h['hand']} | {h['reference']:.3f} | {h['original']:.3f} | {h['candidate']:.3f} |")
        text+=['','These are sampled conditional-value estimates, not per-hand confidence intervals. Missing reference hands are excluded from regression rankings.','',
            '## Decision and next steps','',
            '**Keep this offline; do not deploy the learned candidate.** The interface repair passes its independent checks, but the predictor misses the prospective accuracy screen and the prototype misses the 25% runtime-overhead target. The 500/1,000-iteration extension is withheld at these gates; the 250-iteration study is complete as a diagnostic, not as a convergence claim.','',
            '1. Expand independent board coverage for these changed-policy ranges, particularly the middle-pair and offsuit-broadway errors, to separate systematic bias from board sampling noise.',
            '2. Add targeted training ranges generated by the candidate, keeping different source families and fresh boards reserved for evaluation. The present frozen predictor has not been refitted or tuned to this screen.',
            '3. If prediction accuracy clears the gate, optimize shared compatible-mass/value calculations and redundant terminal work. Reuse the exact action-value oracle as the correctness contract; repeat timing on matched workloads before considering an opt-in app build.','']
    text+=['## Reproduction','',
        'Build the research-only example into `target/learned-interface`; export the frozen CUDA predictor, run the independent oracle, then run matched checkpoints.','',
        '```text','cargo build --release -p solver --features preflop-research --example learned_interface --target-dir target/learned-interface',
        'python tools/research/learned_interface.py export','python tools/research/learned_interface.py oracle',
        'python tools/research/learned_interface.py run 50','python tools/research/learned_interface.py run 250',
        'python tools/research/learned_interface_reference.py prepare','python tools/research/learned_interface_reference.py run',
        'python tools/research/learned_interface_reference.py analyze','python tools/research/learned_interface_analysis.py report','```','',
        'The manifest freezes the executable, predictor, generated kernel, source save and caches. Changing frozen inputs requires a new output directory. Raw trees, checkpoints and saves remain local; compact comparisons, reference results and hashes are retained. Experimental saves still carry Balanced metadata and must never be opened in the ordinary app.','',
        '![Accounting, speed and range comparison](comparison.png)','']
    (study.OUT/'REVIEW.md').write_bytes('\n'.join(text).encode())
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,3,figsize=(13,4.8));colors=['#5086b8','#6e9e61','#d48d45']
    for a,color in zip(names,colors):
        cs=[c for c in points if c['arm']==a]
        axes[0].plot([c['iteration'] for c in cs],[c['ev_sum_bb'] for c in cs],marker='o',color=color,label=names[a])
    axes[0].axhline(0,color='black',lw=.6);axes[0].set(title='Zero-rake EV sum (all pass)',xlabel='Iterations',ylabel='bb per hand',ylim=(-.0002,.0002))
    axes[1].bar(range(3),[ratios[a] for a in names],color=colors);axes[1].set_xticks(range(3),['Current','Pair +\nBalanced','Pair +\nlearned']);axes[1].axhline(1.25,color='black',linestyle='--',lw=.8);axes[1].set(title='Time per iteration',ylabel='Multiple of current solver')
    for j,(a,color) in enumerate(zip(names,colors)):
        vals=[r[a]['frequencies'][next(i for i,b in enumerate(r['actions']) if b.startswith('Call'))]*100 for r in chosen]
        axes[2].bar(np.arange(len(vals))+(j-1)*.25,vals,width=.25,color=color)
    axes[2].set_xticks(range(len(chosen)),['BB vs early' if r['path'][0]==1 else 'BB vs BTN' for r in chosen]);axes[2].set(title=f'Calls at {target} iterations',ylabel='Calling frequency (%)')
    fig.legend(*axes[0].get_legend_handles_labels(),loc='lower center',ncol=3,bbox_to_anchor=(.5,.03));fig.suptitle('Probability/accounting fix: offline diagnostic screen');fig.tight_layout(rect=[0,.13,1,.92]);fig.savefig(study.OUT/'comparison.png',dpi=160);plt.close(fig)

if __name__=='__main__':
    analyze()
    if 'report' in sys.argv:report()
