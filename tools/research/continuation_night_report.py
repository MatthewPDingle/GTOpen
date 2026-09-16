"""Readable evidence checkpoint; never promotes a model or completes the goal."""
import statistics
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
    n15=read('shrunk-residual-20260916/training-screen.json')
    if n15:
        lines.append(f"| N15 conservative nonlinear correction | {n15['mean']:.3f} | {100*n15['improvement']:+.2f}% | {n15['worst_family_ratio']:.6f} | {'Yes; evaluation still required' if n15['eligible'] else 'No'} |")
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
    shrunk_evaluation=read('shrunk-residual-20260916/evaluation.json')
    if shrunk_evaluation:later.append(dict(shrunk_evaluation,model='N15'))
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
    lines+=['## Nonlinear predictor GPU preparation (N15)','']
    for partition in ['training','prospective']:
        bounds=read(f'shrunk-residual-20260916/{partition}-prediction-bounds.json')
        if bounds:
            lines+=[f"The physical-value sanity check {'passed' if bounds['passed'] else 'failed'} across "
                f"{len(bounds['cases'])} {partition} contexts. Predictions are checked against the pot and remaining "
                'stack, with negative future-play values allowed inside those bounds. This is not an accuracy estimate.','']
    compiled_variants=[read(f'shrunk-residual-gpu-20260916/{v}/compilation.json') for v in ['serial','warp']]
    if all(compiled_variants):
        assert all(c['compile_exit_code']==0 and c['gpu_executed'] is False for c in compiled_variants)
        lines+=['Both double-precision implementations pass offline CUDA compilation: ordinary range summaries '
            'and parallel range summaries. Four CPU checks cover the emitted neural arithmetic, standardization '
            'and execution guards. GPU execution is allowed only after N15 passes its registered accuracy screen. '
            'Compilation is not evidence of accuracy or runtime performance.','']
    n15_oracle=read('shrunk-residual-gpu-20260916/oracle-check.json')
    n15_timing=read('shrunk-residual-gpu-20260916/timing.json')
    if n15_oracle:
        assert n15_oracle['passed']
        lines+=['Both implementations passed the independent GPU oracle and their mutual action-value comparison.','']
    if n15_timing:
        assert n15_oracle and shrunk_evaluation and shrunk_evaluation['accuracy_screen_passed']
        lines+=['| Path | Median seconds / iteration |','|---|---:|']
        for arm,value in n15_timing['median_seconds_per_iteration'].items():lines.append(f'| {arm} | {value:.4f} |')
        lines+=['',f"The fixed-work runtime target {'passed' if n15_timing['within_runtime_target'] else 'failed'}. "
            'These timings do not establish convergence speed or qualify changed-policy accuracy.','']
    else:lines+=['No N15 GPU speed result is available yet.','']
    lines+=['## Lower-cost neural arithmetic (N16)','']
    mixed_compiled=[read(f'shrunk-mixed-gpu-20260916/{v}/compilation.json') for v in ['serial','warp']]
    if all(mixed_compiled):
        assert all(c['compile_exit_code']==0 and c['gpu_executed'] is False for c in mixed_compiled)
        lines+=['Three CPU checks and both offline compilations pass. The model is unchanged: only neural '
            'accumulations use float32, with feature standardization and range centering retained in double precision. '
            'No GPU execution or speed gain is implied. [Protocol](../shrunk-mixed-gpu-20260916/README.md).','']
    mixed_timing=read('shrunk-mixed-gpu-20260916/timing.json')
    if mixed_timing:
        assert read('shrunk-mixed-gpu-20260916/oracle-check.json')['passed']
        lines+=[f"Measured overhead versus Balanced: **{100*mixed_timing['overhead_vs_original']:+.1f}%**. "
            f"Runtime target {'passed' if mixed_timing['within_runtime_target'] else 'failed'}. "
            'Strict action-value checks and bounded inspected strategy changes are required; changed-policy validation remains.','']
    lines+=['## Parallel pair bookkeeping (N17)','']
    reduced=[read(f'pair-reductions-20260916/{v}/compilation.json') for v in ['double','mixed']]
    if all(reduced):
        assert all(c['compile_exit_code']==0 and c['gpu_executed'] is False for c in reduced)
        lines+=['The rank-incidence shortcut matches physical card-combination counts in CPU checks. '
            'Both source variants compile offline. N17 parallelizes pair normalization and correction centering '
            'in double precision; its optional mixed variant also incorporates N16. Compilation alone supplies '
            'no GPU execution or timing evidence. [Protocol](../pair-reductions-20260916/README.md).','']
    reduced_oracle=read('pair-reductions-20260916/oracle-check.json')
    if reduced_oracle:
        assert reduced_oracle['passed'] and len(reduced_oracle['comparisons'])==24
        lines+=['Both GPU variants passed all 12 independent action-value oracle cases each, '
            'including zero-reach hands and multiway configurations. This verifies the implementation '
            'against its specified model; it does not make the multiway approximation exact.','']
    reduced_timing=read('pair-reductions-20260916/timing.json')
    rejected_mixed=read('pair-reductions-20260916/rejection.json')
    if rejected_mixed:
        lines += [f"The mixed implementation failed its fixed consistency limit: maximum inspected strategy "
            f"difference **{rejected_mixed['max_strategy_change']:.6f}**, player EV difference "
            f"**{rejected_mixed['max_player_ev_change_bb']:.6f} bb**. Both limits were 0.001. "
            'The joint benchmark stopped after its first repeat; no completed runtime pass is claimed. '
            'Full precision is evaluated separately under N20 with the same frozen source and model.','']
    if reduced_timing:
        assert read('pair-reductions-20260916/oracle-check.json')['passed']
        lines+=['| Path | Median seconds / iteration |','|---|---:|']
        for arm,value in reduced_timing['median_seconds_per_iteration'].items():lines.append(f'| {arm} | {value:.4f} |')
        lines+=['',f"Runtime target {'passed' if reduced_timing['within_runtime_target'] else 'failed'}. "
            'This fixed-work experiment still requires changed-policy validation before any broader accuracy claim.','']
    lines+=['## Retained full-precision implementation (N20)','',
        'N20 retains the exact N17 double source after rejecting mixed arithmetic. It adds action-value '
        'comparisons on actual solved policies, then runs three fresh original/candidate timing pairs. '
        'No failed tolerance is relaxed. [Protocol](../full-precision-20260916/README.md).','']
    full=read('full-precision-20260916/timing.json')
    full_oracle=read('full-precision-20260916/oracle-check.json')
    if full_oracle:
        assert full_oracle['passed']
        comparisons=full_oracle['comparisons']
        lines += [f"The additional check on two actual solved policies passed across "
            f"**{sum(r['values'] for r in comparisons):,} action values**. Maximum difference versus "
            f"the original validated double implementation: **{max(r['max_action_difference_bb'] for r in comparisons):.9g} bb**.",'']
    if full:
        assert full_oracle['passed']
        lines += [f"Candidate median **{full['median_seconds_per_iteration']['candidate']:.4f} s/iteration**; "
            f"overhead versus original **{100*full['overhead_vs_original']:+.2f}%**. "
            f"Runtime target {'passed' if full['within_runtime_target'] else 'failed'}. Changed-policy qualification remains separate.",'']
        for repeat in range(3):
            assert read(f'full-precision-20260916/repeat-{repeat}/original-state-parity.json')['all_numeric_entries_equal']
            if repeat:assert read(f'full-precision-20260916/repeat-{repeat}/candidate-repeat-parity.json')['all_numeric_entries_equal']
        lines += ['| Path | Median setup / compilation (s) | Median whole process (s) |','|---|---:|---:|']
        for arm in ['original','candidate']:
            rows=[r for r in full['repeats'] if r['arm']==arm]
            lines += [f"| {arm} | {statistics.median(r['setup_seconds'] for r in rows):.2f} | {statistics.median(r['total_seconds'] for r in rows):.2f} |"]
        sample=read('full-precision-20260916/repeat-0/candidate/iteration-150.json');plan=sample['plan']
        interface_bytes=20*plan['contexts']+12*len(plan['node_context'])+4*plan['paired_terminals']
        lines += ['', 'Whole-process time includes setup, 50 warm-up iterations, 100 measured iterations and final evaluation/save. '
            'It is a fixed-work measurement, not time to convergence.', '',
            f"The explicit additional interface arrays total **{interface_bytes/(1024**2):.2f} MiB**, calculated from the saved "
            'plan and the six allocations in the frozen Rust implementation. The ordinary equity cache remains allocated. '
            'This excludes CUDA modules, compiler spills and allocator overhead; total device-memory peak was not measured. '
            'The raw run logs also retain the original solver memory-budget estimate.','']
    else:lines+=['Repeated runtime qualification pending.','']
    strategy=read('policy-transfer-optimized-20260916/N20/strategy-diagnostic.json')
    if strategy:
        g=strategy['gap_total_bb']
        lines += ['## Equal-work strategy warning','',
            f"At 500 iterations, the summed frozen-value gap is **{g['original']:.6f} bb** for ordinary Balanced "
            f"versus **{g['candidate']:.6f} bb** for the candidate. Thus the measured 5.93% per-iteration overhead "
            'does not establish comparable time to a settled strategy. Calling decreases in several blind/straddle '
            'contexts; wider calling itself is not an accuracy criterion. These remain unconverged, model-dependent comparisons.', '',
            '[All 17 nodes and KQo probes](../policy-transfer-optimized-20260916/N20/STRATEGY-DIAGNOSTIC.md).','']
    sensitivity=read('range-sensitivity-20260916/diagnostic.json')
    if sensitivity:
        lines += ['## Local range sensitivity','',
            'A label-free diagnostic perturbed 24 training contexts in 288 small, prescribed ways. '
            'The candidate has roughly four to five times the median value response of Balanced, '
            'with much of that response already present in its linear base. This motivates testing '
            'smoother fitting, but higher sensitivity can be legitimate and does not establish causation '
            'for the observed convergence gap. No model was changed by the diagnostic.', '',
            '[Detailed response measurements](../range-sensitivity-20260916/RESULTS.md).','']
    smooth_freeze=read('smooth-fit-20260916/implementation-freeze.json')
    if smooth_freeze:
        smooth=read('smooth-fit-20260916/training-screen.json')
        lines += ['## Less reactive fitting (N22)','',
            'A separately prespecified CPU training screen adds a sensitivity penalty to the linear fit, '
            'then refits the same small nonlinear correction. It uses only training/development families '
            'and keeps the inference architecture unchanged. It must preserve N15 accuracy within 5% '
            'in every family, improve at least 5% over the earlier linear control, and lower mean local '
            'sensitivity by at least 25%, without worsening any family sensitivity. '
            '[Protocol](../smooth-fit-20260916/README.md).','']
        if smooth:
            lines += [f"Training screen {'selected a candidate' if smooth['selected'] else 'rejected all fixed strengths'}. "
                'Fresh independent accuracy and GPU/convergence qualification remain separate.','']
            lines += ['| Penalty | Mean error (% pot) | Worst-family change vs N15 | Sensitivity reduction | Eligible |',
                '|---|---:|---:|---:|---|']
            for row in smooth['scores']:
                lines += [f"| {row['strength']:g} | {row['mean']:.3f} | {100*(row['worst_family_ratio']-1):+.2f}% | "
                    f"{100*(1-row['response_ratio']):.2f}% | {'Yes' if row['eligible'] else 'No'} |"]
            lines += ['', 'The zero-penalty control reproduced the existing N15 training validation exactly. '
                'No failed tolerance was changed and no rejected smoother was sent to the GPU.','']
        else:lines += ['Four numerical/guard tests passed; training screen is not yet complete. No smoother candidate is qualified.','']
    weighted=read('weighted-expanded-20260916/training-screen.json')
    if weighted:
        lines += ['## Lightly weighted range-diversity data (N23)','',
            'The unchanged N15 architecture was fitted with the 36 synthetic training contexts at '
            'fixed weights .05 and .2, while retaining original contexts at weight1 and excluding entire '
            'validation families. The zero-extra-data control reproduced N15 exactly. '
            '[Protocol](../weighted-expanded-20260916/README.md).','',
            '| Extra-context weight | Mean error (% pot) | Worst-family change vs N15 | Sensitivity reduction | Eligible |',
            '|---|---:|---:|---:|---|']
        for row in weighted['scores']:
            lines += [f"| {row['weight']:g} | {row['mean']:.3f} | {100*(row['worst_family_ratio']-1):+.2f}% | "
                f"{100*(1-row['response_ratio']):.2f}% | {'Yes' if row['eligible'] else 'No'} |"]
        lines += ['', 'No fixed weight passed all requirements; the extra-data variants were not promoted. '
            'Positive-mass labels were independently verified in all 62 training contexts.','']
    lines+=['## Changed-policy validation','']
    any_transfer=False
    for name in ['N16','N17','N20']:
        transfer=read(f'policy-transfer-optimized-20260916/{name}/evaluation.json')
        if not transfer:continue
        any_transfer=True
        lines += [f"### {name}: {'passed' if transfer['accuracy_screen_passed'] else 'failed'} the unchanged four-context gate",'',
            '| Context | Balanced error | Previous predictor | Candidate error |','|---|---:|---:|---:|']
        for case in transfer['cases']:
            e=case['mae_pct_pot']
            lines += [f"| {case['case']} | {e['balanced']:.3f} | {e['previous']:.3f} | {e['candidate']:.3f} |"]
        lines += ['', 'Errors are percent of pot. Every context must improve at least 15% versus Balanced and '
            'regress at most 10% versus the previous predictor. These are fresh boards on changed ranges '
            'in a familiar scenario, not untouched-scenario validation or a full-game convergence certificate.','']
        audit=read(f'policy-transfer-optimized-20260916/{name}/reference-audit.json')
        if audit:
            assert audit['audited_references']==200 and audit['all_references_after_freeze']
            lines += [f"All **{audit['audited_references']} references** passed the provenance and solve-quality audit. "
                f"Physical prediction bounds {'passed' if audit['physical_bounds_passed'] else 'FAILED'} in the changed contexts. "
                'These diagnostics do not alter the fixed accuracy gate.','']
    if not any_transfer:lines+=['No completed changed-policy result yet.','']
    diagnostic=read('shrunk-residual-20260916/hand-group-diagnostics.json')
    if diagnostic:
        lines += ['## Hand-group and position diagnostic','',
            'The pooled N15 result improves over Balanced in all seven hand groups, but this hides '
            'position-specific weaknesses. OOP suited-broadway error is 6.141% of pot versus 3.813% '
            'for Balanced; IP premium pairs still have 16.612% error and -11.234% signed bias. '
            'These descriptive groups did not participate in fitting or acceptance and do not change the gates. '
            'OOP/IP describe postflop position, not a breakdown by individual preflop seat.', '',
            '[Full pooled and position tables](../shrunk-residual-20260916/HAND-GROUPS.md).','']
    chance_freeze=read('chance-control-20260916/protocol-freeze.json')
    if chance_freeze:
        chance=read('chance-control-20260916/result.json')
        lines += ['## Isolating the card-accounting change (N24)','',
            'The N20 path changes compatible-card accounting as well as hand values. A separately '
            'frozen control keeps the same interface but disables the learned predictor, using the '
            'previous Balanced continuation values. It compares equal150/500iteration snapshots. '
            '[Protocol](../chance-control-20260916/README.md).','']
        if chance:
            lines += ['| Iteration | Path | Summed frozen-value gap (bb) |','|---|---|---:|']
            for row in chance['rows']:lines += [f"| {row['iteration']} | {row['arm']} | {row['frozen_value_gap_bb']:.6f} |"]
            lines += ['', 'These are separate approximate games and this is one diagnostic run. '
                'It isolates one possible contributor; it does not prove a particular learned feature '
                'caused the difference or establish full-game exploitability. '
                'At 500 iterations the card-accounting control has a much smaller remaining gap than '
                'the learned path; card accounting alone does not reproduce the large learned gap. '
                '[Input and snapshot audit](../chance-control-20260916/result-audit.json).','']
        else:lines += ['Prepared and checked; no control execution result yet. It must wait for the validation queue to exit.','']
    lines+=['## Practical strategy stability (N19)','']
    stability=read('policy-stability-20260916/result.json')
    if stability:
        lines += ['| Path | Stability signal met | Additional learning time, 500 to 1500 (s) |','|---|---|---:|']
        for arm,passed in stability['practical_stability'].items():
            lines += [f"| {arm} | {'Yes' if passed else 'No'} | {stability['additional_learning_seconds'][arm]:.1f} |"]
        lines += ['', 'The fixed signal requires both consecutive 500-iteration intervals to have <=1 percentage point '
            'aggregate-action and weighted per-hand change at every inspected node, with frozen-value gap <=0.005 bb. '
            'Absent arriving ranges do not count as stable. This limited diagnostic does not establish full-game convergence. '
            'If either arm misses the signal, no comparative time-to-stability claim is made.','']
        lines += ['| Path | Gap at 1000 (bb) | Gap at 1500 (bb) |','|---|---:|---:|']
        for arm, trajectory in stability['trajectory'].items():
            lines.append(f"| {arm} | {trajectory[0]['gap_total_bb']:.6f} | {trajectory[1]['gap_total_bb']:.6f} |")
        overhead=stability['additional_learning_seconds']['candidate']/stability['additional_learning_seconds']['original']-1
        lines += ['', f'The candidate took **{100*overhead:.1f}% more learning time** for these additional '
            '1000 iterations and failed the settling signal. These are single observed spans, not repeated '
            'runtime medians or time-to-convergence measurements. The short repeated benchmark therefore '
            'does not establish approximately maintained end-to-end performance. The candidate charts changed '
            'little in the final interval, but its frozen-value gap plateaued. '
            '[Snapshot and input audit](../policy-stability-20260916/result-audit.json).','']
    else:lines+=['Prepared and tested, not yet completed. It runs only after the selected implementation passes all preceding gates.','']
    menu_freeze=read('flop-menu-20260916/candidate-freeze.json')
    if menu_freeze:
        menu=read('flop-menu-20260916/evaluation.json')
        lines += ['## Wider flop-menu sensitivity (N21)','',
            'Separately frozen before its outcomes: the same model and four changed-policy contexts, '
            '20 unused matched boards, and 160 references comparing half-pot-only flop bets with '
            'a nested 33%/50%/75% menu. Turn/river menus remain fixed. No fitting or automatic deployment. '
            '[Protocol](../flop-menu-20260916/README.md).','']
        if menu:
            lines += [f"The fixed eight-context/menu accuracy gate {'passed' if menu['accuracy_screen_passed'] else 'failed'}.",'',
                '| Context / menu | Balanced error | Previous error | Candidate error |','|---|---:|---:|---:|']
            for row in menu['cases']:
                e=row['mae_pct_pot']
                lines += [f"| {row['case']} | {e['balanced']:.3f} | {e['previous']:.3f} | {e['candidate']:.3f} |"]
            lines += ['', 'Errors are percent of pot. Twenty boards provide a limited conditional estimate; '
                'this does not establish unrestricted-tree or untouched-context accuracy.','']
        else:lines += ['Reference generation has started; no completed wider-menu accuracy result. '
            'The N24 card-accounting control has scheduling priority after N19 failed the settling check.','']
    lines+=['## Half-width nonlinear model (N18)','']
    compact=read('compact-residual-20260916/training-screen.json')
    if compact:
        lines+=[f"The fixed training screen {'passed' if compact['eligible'] else 'failed'}. "
            f"Mean error was **{compact['mean']:.3f}% of pot**, "
            f"{100*compact['improvement_vs_linear']:.2f}% lower than the linear control. "
            f"Relative to N15, mean error changed by {100*(compact['ratio_vs_n15']-1):+.2f}% and "
            f"the worst family by {100*(compact['worst_n15_family_ratio']-1):+.2f}%. "
            'The fixed screen permits at most 5% regression in any family versus N15. '
            'No speed claim follows from using fewer hidden units. [Protocol](../compact-residual-20260916/README.md).','']
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
        '## Fixed pairwise values (N25)','',
        'A separately frozen training-only experiment learns hand-versus-hand payoffs, '
        'with opposite player corrections that conserve the pot. This removes own-range '
        'dependence from each hand value but is less expressive than full postflop play. '
        'It must retain accuracy before any GPU work. '
        '[Protocol](../pairwise-values-20260916/README.md).','']
    pairwise=read('pairwise-values-20260916/training-screen.json')
    if pairwise:
        lines += [f"Training eligibility: **{pairwise['eligible']}**. "
            'Training eligibility alone does not qualify a model for deployment.','',
            '| Ridge strength | Mean family error (% pot) | Eligible |',
            '|---|---:|---|']
        for score in pairwise['scores']:
            lines.append(f"| {score['strength']} | {score['mean']:.3f} | {score['eligible']} |")
        lines += ['', 'All three numerical checks passed. A NumPy boolean prevented the initial result from '
            'being written; a separate output-only adapter reran the unchanged deterministic fitting code. '
            'No frozen source, model, grid or gate changed. '
            '[Repair provenance](../pairwise-values-20260916/output-repair.json).','']
    else:
        lines += ['Prepared and frozen; numerical tests and training deferred until N19 isolated timing finishes. No result is claimed.','']
    drift=read('own-range-drift-20260916/diagnostic.json')
    if drift:
        lines += ['## Own-range value response (N26)','',
            'All 432 fixed training-input perturbations completed without reference labels or fitting. '
            'Raw and Balanced hand values stayed invariant to own-range changes. The candidate and '
            'its older linear base both showed systematic shifts in values assigned to existing hands. '
            'This is not unique to the neural correction. Smaller perturbations gave larger normalized '
            'responses; zero-weight hands, entropy features and clipping preclude treating these '
            'finite differences as a stable smooth derivative. Own-range dependence can be legitimate, '
            'so this is neither an accuracy test nor proof of the settling cause. '
            '[Detailed results and limitations](../own-range-drift-20260916/RESULTS.md).','']
    current=read('current-policy-20260916/result.json')
    if current:
        largest={arm:max(r['weighted_current_average_tv'] for r in current['rows']
                         if r['arm']==arm and r['weighted_current_average_tv'] is not None)
                 for arm in ['original','candidate']}
        lines += ['## Latest versus averaged strategies (N28)','',
            f"At the same 17 inspected decisions after 1500 iterations, the largest weighted latest/average "
            f"hand-strategy variation was {100*largest['candidate']:.3f} percentage points for the candidate "
            f"and {100*largest['original']:.3f} for ordinary Balanced. "
            'There is no large hidden separation at these decisions at this checkpoint. Deeper nodes '
            'and temporal trajectories remain unmeasured; no latest-policy convergence metric was substituted. '
            '[Read-only audit](../current-policy-20260916/RESULTS.md).','']
    lines += ['## Positive-hand reference coverage','',
        'The completed N15 and N20 coverage audits found observations for every positive-weight hand class '
        'across their 400 and 200 references. This rules out completely missing positive-weight classes in '
        'those tests; it does not establish precise values or coverage of unseen situations. Weighted board '
        'counts are descriptive, not independent sample sizes or confidence guarantees. '
        '[N15 coverage](../shrunk-residual-20260916/COVERAGE.md); '
        '[N20 coverage](../policy-transfer-optimized-20260916/N20/COVERAGE.md).','']
    lines += [
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
