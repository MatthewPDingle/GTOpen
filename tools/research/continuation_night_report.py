"""Readable evidence checkpoint; never promotes a model or completes the goal."""
import continuation_bridge_run as bridge

study=bridge.study
BASE=bridge.OUT.parent
OUT=BASE/'night-shift-20260916'


def read(relative):
    path=BASE/relative
    return study.read(path) if path.exists() else None


def report():
    now=study.night.now()
    lines=['# Preflop accuracy and runtime: night-shift checkpoint','',f'Updated {now}.', '',
        'The scheduled research window ends at **20:49:02 UTC on 16 September** '
        '(06:19 Adelaide on 17 September). This document is a checkpoint, not a completion or deployment claim.', '',
        '## Decision so far','',
        'Accuracy and speed are separate requirements. A candidate that improves the average but materially '
        'worsens one family is rejected. A speed improvement to a rejected predictor does not qualify that '
        'predictor for use. No research runner in this study deploys to the app on port 56708.', '',
        '## New reference data','',
        '| Partition | Saved references / planned | Purpose |','|---|---:|---|']
    for folder,partition,purpose in [('range-bridges-20260916','training','New training range and stack examples'),
            ('range-bridges-20260916','evaluation','N03 fixed-model accuracy test'),
            ('expanded-validation-20260916','prospective','Fresh evaluation of any eligible N06b/N08 models')]:
        m=read(f'{folder}/{partition}/manifest.json')
        if not m:continue
        count=sum((BASE/folder/partition/'jobs'/f"{j['id']}.json").exists() for j in m['jobs'])
        lines.append(f'| {folder.split("-2026")[0]} / {partition} | {count} / {len(m["jobs"])} | {purpose} |')
    lines+=['','Counts indicate saved files; the study audit separately validates their numerical quality. '
        'N03 adds 36 synthetic contexts, not 36 independent real-player populations. '
        'Original plus development plus new contexts total 62 training cases.', '',
        '## Prospective accuracy: targeted blind-call data (N01)','',
        'This completed experiment failed its fixed accuracy screen. It improved on the previous learned '
        'predictor at both tested cases, but one case became worse than ordinary Balanced.', '',
        '| Case | Balanced error | Previous predictor | N01 predictor | Change vs Balanced |',
        '|---|---:|---:|---:|---:|']
    n01=read('policy-refinement-20260916/evaluation-comparison.json')
    assert n01 and not n01['all_screen_pass']
    for c in n01['cases']:
        e=c['mae_pct_pot']
        lines.append(f"| {c['case']} | {e['balanced']:.3f} | {e['previous']:.3f} | {e['candidate']:.3f} | {100*c['improvement_vs_balanced']:+.1f}% |")
    lines+=['','Errors are mean absolute hand-value errors as a percentage of the starting pot. '
        'Positive change means lower error. [Full N01 result and uncertainty](../policy-refinement-20260916/RESULTS.md).', '',
        '## Training-family screens','',
        'These scores select models for later evaluation; they are not independent evidence of poker-strategy '
        'accuracy. Each validation family is excluded from fitting. Fixed candidate sets are retained, including failures.', '',
        '| Experiment | Best attempted error (% pot) | Mean gain | Worst family error ratio | Eligible |',
        '|---|---:|---:|---:|---|']
    specs=[('N02 curvature','night-shift-20260916/curvature-final-selection.json',lambda r:r['kind'] not in ['shape','base']),
        ('N02 hand offsets','night-shift-20260916/hand-offset-final-selection.json',lambda r:True),
        ('N05 projected fitting','projected-fit-20260916/training-screen.json',lambda r:r['kind']!='ordinary'),
        ('N06 nonlinear','nonlinear-residual-20260916/training-screen.json',lambda r:r['width']>0),
        ('N06b nonlinear + new data','nonlinear-expanded-20260916/training-screen.json',lambda r:r['width']>0),
        ('N08 precision weighting','precision-weighted-20260916/training-screen.json',lambda r:r['power']>0)]
    for label,path,keep in specs:
        result=read(path)
        if not result:
            lines.append(f'| {label} | Pending | — | — | Pending |');continue
        best=min((r for r in result['scores'] if keep(r)),key=lambda r:r['mean'])
        comparisons=best.get('comparisons')
        if comparisons:
            gain=' / '.join(f"{100*v['improvement']:+.2f}%" for v in comparisons.values())
            worst=' / '.join(f"{v['worst_family_ratio']:.6f}" for v in comparisons.values())
        else:
            gain=f"{100*best['improvement']:+.2f}%";worst=f"{best['worst_family_ratio']:.6f}"
        eligible=any(r['eligible'] for r in result['scores'] if keep(r))
        lines.append(f"| {label} | {best['mean']:.3f} | {gain} | {worst} | {'Yes; evaluation still required' if eligible else 'No'} |")
    n03=read('range-bridges-20260916/training-screen.json')
    if n03:
        lines.append(f"| N03 range diversity | {sum(n03['family_means'].values())/len(n03['family_means']):.3f} | {100*n03['improvement']:+.2f}% | {n03['worst_family_ratio']:.6f} | {'Yes; evaluation still required' if n03['eligible'] else 'No'} |")
    else:lines.append('| N03 range diversity | Pending | — | — | Pending |')
    lines+=['','N03 uses the original 24 validation cases. Other rows use the original 26 including the '
        'two development cases, so do not rank N03 against them using raw error. N06b/N08 gains and ratios '
        'list the expanded-data and original-data controls respectively; both must pass. '
        'Eligibility requires at least 5% lower mean error and no family more than 5% worse. '
        'Printed values never determine the gate: full-precision values do.', '',
        'The label-precision diagnostic found appreciable variation between 20-flop subsets and the '
        '100-flop training estimates. Exact rank-event controls reduced that variation by 6–21%, '
        'but failed the fixed all-family 20% requirement. The original labels were retained. '
        'This diagnostic is not an estimate of error against exact poker values.', '']
    later=[]
    n03_evaluation=read('range-bridges-20260916/evaluation.json')
    if n03_evaluation:later.append(dict(n03_evaluation,model='N03'))
    expanded=read('expanded-validation-20260916/evaluation.json')
    if expanded:later.extend(expanded['models'])
    lines+=['## Later prospective accuracy checks','']
    if not later:lines+=['Pending eligibility and fresh reference generation. No later evaluation gain is claimed.','']
    for result in later:
        lines += [f"### {result['model']}: {'passed' if result['accuracy_screen_passed'] else 'failed'} the fixed accuracy screen",'',
            '| Held-out family | Balanced error | Previous predictor | Candidate | Improvement vs Balanced, 90% interval |',
            '|---|---:|---:|---:|---:|']
        for family in result['families']:
            e=family['mae_pct_pot'];lo,hi=family['paired_90_improvement_ci']['balanced']
            lines.append(f"| {family['family']} | {e['balanced']:.3f} | {e['previous']:.3f} | {e['candidate']:.3f} | {100*lo:+.1f}% to {100*hi:+.1f}% |")
        lines+=['',f"Candidate SHA-256: `{result['candidate_sha256']}`.",'',
            'The gate also checks every individual case against the previous predictor. '
            'Passing this value-error screen alone does not authorize deployment.','']
    lines+=['## Speed and unchanged-result checks (N04)','']
    parity=read('interface-work-reuse-20260916/parity.json');assert parity and parity['passed']
    regressions=read('interface-work-reuse-20260916/regressions.json')
    assert regressions['cpu_suite']=='passed' and regressions['gpu_suite']['failed']==regressions['preflop_gpu_suite']['failed']==0
    lines+=['Removing overwritten terminal work passed the independent 12-case action-value oracle, '
        'the ordinary CPU test suite and 21 GPU regression tests. The repeated benchmark additionally '
        'requires equality of every saved regret and accumulated strategy value.', '']
    timing=read('interface-work-reuse-20260916/timing.json')
    if timing:
        for repeat in range(3):
            saved=read(f'interface-work-reuse-20260916/repeat-{repeat}/full-state-parity.json')
            assert saved and saved['all_numeric_entries_equal']
        lines+=['| Path | Median seconds / iteration |','|---|---:|']
        for arm,value in timing['median_seconds_per_iteration'].items():lines.append(f'| {arm} | {value:.4f} |')
        lines+=['',f"Speedup versus the identical unoptimized predictor: **{timing['speedup_vs_identical_predictor']:.3f}×**. "
            f"Overhead versus ordinary Balanced: **{100*timing['overhead_vs_original']:+.1f}%**. "
            'The operational speed target is no more than 10% overhead.', '']
    else:lines+=['**Timing is pending. No speed gain is claimed yet.**','']
    lines+=['This benchmark retains the old predictor, which failed an accuracy screen. '
        'Any newly qualified predictor still needs its own implementation, timing and changed-policy checks.', '',
        '## Remaining limitations','',
        '- Fixed zero-rake, heads-up postflop references use a restricted bet menu. They are not complete preflop game solves.',
        '- Small average solve gaps do not guarantee every rare-hand training value is accurate.',
        '- Fresh-board evaluation reuses historical case identities from held-out source families; it is not untouched-context validation.',
        '- The larger preflop interface still approximates multiway card removal and ignores folded-card bunching.',
        '- Bootstrap intervals condition on fitted models and cached equities. Value accuracy and frozen-value best-response gaps do not certify full-game exploitability.', '',
        'See the [plan and invariants](README.md), [experiment ledger](ledger.json) and individual study artifacts for hashes, protocols and detailed results.','']
    hand_quality=read('range-bridges-20260916/partial-hand-quality.json')
    if hand_quality:
        lines+=['## Hand-level reference diagnostic','',
            f"Snapshot at {hand_quality['checked_at']}, covering {hand_quality['references']} / {hand_quality['planned']} planned training references. "
            f"Hands with more than 1% pot remaining best-response gain account for **{100*hand_quality['mean_tail_mass_by_threshold']['1.0']:.4f}%** "
            'of hand mass when averaging completed references and players equally. '
            f"The largest observed individual gain is {hand_quality['worst_hand_values'][0]['br_gain_pct_pot']:.3f}% of pot. "
            'This diagnoses remaining solve error, not model prediction error or a rigorous per-hand value-error bound. '
            'A partial snapshot is not a final all-flop estimate.', '',
            '[Hand-level audit details](../range-bridges-20260916/partial-hand-quality.json).','']
    (OUT/'RESULTS.md').write_text('\n'.join(lines),encoding='utf-8',newline='\n')
    print('Updated checkpoint:',OUT/'RESULTS.md',flush=True)


if __name__=='__main__':report()
