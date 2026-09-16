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
    n13=read('equity-moments-20260916/training-screen.json')
    if n13:
        lines.append(f"| N13 matchup-distribution moments | {n13['mean']:.3f} | {100*n13['improvement']:+.2f}% | {n13['worst_family_ratio']:.6f} | {'Yes; evaluation still required' if n13['eligible'] else 'No'} |")
    else:lines.append('| N13 matchup-distribution moments | Not fitted | — | — | Pending |')
    lines+=['','N03 uses the original 24 validation cases. Other rows use the original 26 including the '
        'two development cases, so do not rank N03 against them using raw error. N06b/N08 gains and ratios '
        'list the expanded-data and original-data controls respectively; both must pass. '
        'Eligibility requires at least 5% lower mean error and no family more than 5% worse. '
        'Printed values never determine the gate: full-precision values do.', '',
        'The label-precision diagnostic found appreciable variation between 20-flop subsets and the '
        '100-flop training estimates. Exact rank-event controls reduced that variation by 6–21%, '
        'but failed the fixed all-family 20% requirement. The original labels were retained. '
        'This diagnostic is not an estimate of error against exact poker values.', '']
    n09=read('recalibrated-priors-20260916/training-screen.json')
    if n09:
        lines+=['## Cheap pairwise-prior recalibration (N09)','',
            f"The fixed training screen {'passed' if n09['eligible'] else 'failed'}. Mean error was "
            f"**{n09['means']['candidate']:.3f}% of pot**, versus {n09['means']['balanced']:.3f}% for Balanced "
            f"({100*n09['comparisons']['balanced']['improvement']:.1f}% lower). The worst family ratio was "
            f"{n09['comparisons']['balanced']['worst_family_ratio']:.6f}. "
            'It also had to improve at least 5% on unchanged priors under the same compatible-pair calculation, '
            'with no family more than 5% worse against either baseline.', '',
            'The conditional predictor remains more accurate on training-family checks. N09 is considered '
            'because its pairwise matrices can be cached. GPU correctness and performance require the separate checks below. '
            'Its frozen candidate was registered before N03 evaluation outcomes existed, permitting shared '
            'future reference computation under a separate prospective protocol. '
            '[Full N09 result](../recalibrated-priors-20260916/RESULTS.md).','']
    n10=read('pair-value-adjustments-20260916/training-screen.json')
    if n10:
        lines+=['## Cached additive pair values (N10)','',
            f"The fixed training screen {'passed' if n10['eligible'] else 'failed'}. Mean error was "
            f"**{n10['means']['candidate']:.3f}% of pot**, compared with {n10['means']['n09']:.3f}% for N09. "
            f"The worst family ratio versus N09 was {n10['comparisons']['n09']['worst_family_ratio']:.6f}. "
            'This tests a different cheap pair-table model that can represent value from future bets. '
            'Its independent algebra, accounting and synthetic recovery checks passed, but those checks '
            'do not establish accuracy on real reference values. '
            '[Full N10 result](../pair-value-adjustments-20260916/RESULTS.md).','']
    n11=read('corrected-pair-priors-20260916/training-screen.json')
    if n11:
        lines+=['## Fixed correction to cached priors (N11)','',
            f"The fixed two-stage screen {'passed' if n11['eligible'] else 'failed'}. Mean error was "
            f"**{n11['means']['candidate']:.3f}% of pot**, versus {n11['means']['n09']:.3f}% for N09. "
            f"The worst family ratio versus N09 was {n11['comparisons']['n09']['worst_family_ratio']:.6f}. "
            'Both fitting stages excluded the validation family, and all 26 N09 control errors reproduced. '
            '[Full N11 result](../corrected-pair-priors-20260916/RESULTS.md).','']
    for label,folder in [('N12','depth-pair-priors-20260916'),('N12b','depth-priors-expanded-20260916')]:
        depth=read(f'{folder}/training-screen.json')
        lines+=[f'## Depth-dependent cached priors ({label})','']
        if depth:
            control='n09' if label=='N12' else 'n09_original'
            lines+=[f"The fixed training screen {'passed' if depth['eligible'] else 'failed'}. Mean error was "
                f"**{depth['means']['candidate']:.3f}% of pot**; improvement over the original-data N09 control was "
                f"{100*depth['comparisons'][control]['improvement']:.2f}%. "
                'The complete controls and family checks determine eligibility, without rounded thresholds. '
                f'[Protocol and evidence](../{folder}/README.md).','']
        else:lines+=['The unchanged model will be checked after the new training references complete. No result is claimed.','']
    later=[]
    n03_evaluation=read('range-bridges-20260916/evaluation.json')
    if n03_evaluation:later.append(dict(n03_evaluation,model='N03'))
    n09_evaluation=read('recalibrated-priors-20260916/evaluation.json')
    if n09_evaluation:later.append(dict(n09_evaluation,model='N09'))
    depth_evaluation=read('depth-priors-expanded-20260916/evaluation.json')
    if depth_evaluation:later.append(dict(depth_evaluation,model='N12b'))
    moment_evaluation=read('equity-moments-20260916/evaluation.json')
    if moment_evaluation:later.append(dict(moment_evaluation,model='N13'))
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
    lines+=['## Cached-prior GPU checks (N09)','']
    compiled=read('recalibrated-priors-gpu-20260916/compilation.json')
    if compiled:
        assert compiled['compile_exit_code']==0 and compiled['gpu_executed'] is False
        lines+=['The isolated cached-matrix source passes offline CUDA compilation. '
            'This verifies source compilation only; it does not establish execution correctness or speed.','']
    n09_oracle=read('recalibrated-priors-gpu-20260916/oracle-check.json')
    if n09_oracle:
        assert n09_oracle['passed']
        lines+=[f"The independent GPU oracle passed {len(n09_oracle['tests'])} dense/sparse cases.",'']
    n09_timing=read('recalibrated-priors-gpu-20260916/timing.json')
    if n09_timing:
        assert n09_evaluation and n09_evaluation['accuracy_screen_passed'] and n09_oracle['passed']
        frozen=read('recalibrated-priors-20260916/candidate-freeze.json')
        assert frozen['sha256']==n09_evaluation['candidate_sha256']
        for repeat in range(3):
            assert read(f'recalibrated-priors-gpu-20260916/repeat-{repeat}/original-state-parity.json')['all_numeric_entries_equal']
            if repeat:assert read(f'recalibrated-priors-gpu-20260916/repeat-{repeat}/candidate-repeat-parity.json')['all_numeric_entries_equal']
        lines+=['| Path | Median seconds / iteration |','|---|---:|']
        for arm,value in n09_timing['median_seconds_per_iteration'].items():lines.append(f'| {arm} | {value:.4f} |')
        lines+=['',f"Candidate overhead versus Balanced: **{100*n09_timing['overhead_vs_original']:+.1f}%**. "
            f"The fixed-work runtime target {'passed' if n09_timing['within_runtime_target'] else 'failed'}. "
            'These measurements do not establish convergence speed. Changed-policy validation and the '
            'remaining multiway limitations still matter.','']
    else:lines+=['Execution oracle and repeated timing remain pending; they run only after prospective accuracy passes.','']
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
    lines+=['## Parallel range summaries (N14)','',
        'A separately specified experiment distributes each serial range-summary calculation over '
        '32 GPU threads. It retains the old predictor and double precision but changes summation order. '
        '[Protocol and required tolerances](../warp-summary-20260916/README.md).','']
    warp=read('warp-summary-20260916/timing.json')
    if warp:
        lines += [f"Measured speedup versus the filtered control: **{warp['speedup_vs_filtered_control']:.3f}x**. "
            f"Overhead versus Balanced: **{100*warp['overhead_vs_original']:+.1f}%**. "
            'Full saved-state comparisons and repeated-candidate equality are required. '
            'This does not qualify the old predictor for deployment.','']
    else:lines+=['Prepared; no speed result is claimed until the independent oracle and repeated benchmark complete.','']
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
            + ('All planned training references are included.' if hand_quality['references']==hand_quality['planned']
             else 'A partial snapshot is not a final all-flop estimate.'), '',
            '[Hand-level audit details](../range-bridges-20260916/partial-hand-quality.json).','']
    (OUT/'RESULTS.md').write_text('\n'.join(lines),encoding='utf-8',newline='\n')
    print('Updated checkpoint:',OUT/'RESULTS.md',flush=True)


if __name__=='__main__':report()
