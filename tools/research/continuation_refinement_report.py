"""Publish the fixed refinement experiment without changing its candidate."""
import json
import numpy as np
import continuation_policy_refinement as study


def report():
    out = study.OUT
    dev = study.read(out/'development-comparison.json')
    evaluation = study.read(out/'evaluation-comparison.json')
    candidate = study.read(out/'candidate.json')
    frozen = study.read(out/'candidate-freeze.json')
    assert study.pilot.sha(out/'candidate.json')==frozen['sha256']
    assert dev['candidate_sha256']==evaluation['candidate_sha256']==frozen['sha256']
    assert len(candidate['training_case_ids'])==26
    for partition in ['development','evaluation']:
        study.checked(partition)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1,2,figsize=(12,5),layout='constrained')
    for ax, result, title in zip(axes,[dev,evaluation],['Development (included in fitting)','Fresh-board evaluation (families excluded from fitting)']):
        x = np.arange(len(result['cases']))
        for offset, name, label, color in [(-.25,'balanced','Balanced','#888888'),(0,'previous','Previous learned','#4682b4'),(.25,'candidate','Targeted revision','#70a454')]:
            bars=ax.bar(x+offset,[c['mae_pct_pot'][name] for c in result['cases']],.23,label=label,color=color)
            ax.bar_label(bars,fmt='%.2f',padding=3,fontsize=9)
        ax.set_xticks(x,[c['case'] for c in result['cases']],fontsize=9)
        ax.set_title(title,fontsize=10)
        ax.set_ylabel('Weighted hand-value MAE (% of starting pot)')
        ax.set_ylim(0,max(c['mae_pct_pot'][n] for c in result['cases'] for n in ['balanced','previous','candidate'])*1.2)
        ax.grid(axis='y',alpha=.2); ax.set_axisbelow(True)
    axes[0].legend(fontsize=9)
    fig.supxlabel('Lower is better. Fixed zero-rake heads-up postflop menu.\nThese are value errors, not action frequencies or full-preflop exploitability.',fontsize=10)
    fig.savefig(out/'comparison.png',dpi=160);plt.close(fig)
    passed=evaluation['all_screen_pass']
    lines=['# Targeted continuation-data revision: results','',
        '**Fixed accuracy screen: '+('passed on these two cases; broader validation still required.' if passed else 'failed; keep this candidate out of the application.')+'**','',
        'Completed 260 fresh postflop references. Together with 40 reused references, '
        'the two development cases have 100 flops each and two evaluation cases have 50 fresh flops each. '
        'The candidate was frozen before generating the new evaluation results. Port 56708 was unchanged.','',
        'The revised model uses the same 104-feature shape encoder and ridge penalty 0.1 as the previous model. '
        'Only its fitting data changed: the original 24 cases plus two blind-call cases from the earlier preflop study.','',
        '![Development and evaluation errors](comparison.png)','',
        '| Partition / case | Balanced | Previous model | Revision | Improvement vs Balanced | Change vs previous |',
        '|---|---:|---:|---:|---:|---:|']
    for partition, result in [('Development',dev),('Evaluation',evaluation)]:
        for c in result['cases']:
            e=c['mae_pct_pot']
            lines.append(f"| {partition}: {c['case']} | {e['balanced']:.3f} | {e['previous']:.3f} | {e['candidate']:.3f} | {100*c['improvement_vs_balanced']:+.1f}% | {100*c['improvement_vs_previous']:+.1f}% |")
    lines+=['','Errors are mean absolute per-hand continuation-value errors in percentage points of the starting pot, '
        'weighted by compatible range mass. Positive improvement means lower error. '
        'Development results include fitting data and do not establish generalization.','',
        '## Prospective evaluation','',
        '| Case | Improvement vs Balanced, 90% interval | Improvement vs previous, 90% interval | Point screen |',
        '|---|---:|---:|---|']
    for c in evaluation['cases']:
        ci=c['paired_90_improvement_ci']
        lines.append(f"| {c['case']} | {100*ci['balanced'][0]:+.1f}% to {100*ci['balanced'][1]:+.1f}% | {100*ci['previous'][0]:+.1f}% to {100*ci['previous'][1]:+.1f}% | {'Pass' if c['screen_pass'] else 'Fail'} |")
    lines+=['','The fixed point screen requires at least 15% lower error than original Balanced in each evaluation '
        'case, and no more than 5% greater error than the previous model. Intervals use 500 paired stratified '
        'board resamples and condition on the fitted models and cached equities; they exclude training uncertainty. '
        'Evaluation source families never entered fitting, but these case identities were tested in earlier work. '
        'The fresh boards provide prospective evaluation, not proof on entirely unseen game contexts.','',
        '## Reference quality','',
        '| Case | Largest CPU gap (% pot) | Largest GPU gap (% pot) | Largest pot-accounting error (bb) | Negative predictions |',
        '|---|---:|---:|---:|---:|']
    for c in dev['cases']+evaluation['cases']:
        lines.append(f"| {c['case']} | {c['max_reference_gap_pct']:.5f} | {c['max_gpu_gap_pct']:.5f} | {c['max_reference_accounting_error_bb']:.2e} | {len(c['negative_predictions'])} |")
    lines+=['','Every reference must pass both GPU and full CPU best-response stopping criteria at 0.1% of the '
        'starting pot. Per-hand probe best-response gains are retained in the comparison JSON files: a small '
        'range-average gap does not certify each rare-hand label. Neither negative nor greater-than-pot individual '
        'gross values alone violate conservation; accounting is checked over compatible range mass.','',
        'This sample uses five texture strata and excludes all earlier study boards except the explicitly reused '
        'development subset. It retains the fixed half-pot postflop menu and zero rake. Broader menus, different '
        'rake structures, multiway play and range evolution remain outside this test.','',
        '## Reproducibility','',
        'The data-boundary tests passed, including reproduction of the previous frozen predictor from its original '
        'training data. Source references, configurations, input hashes, the candidate freeze and per-job solver '
        'traces are retained. No GPU predictor integration or performance claim follows from this data experiment.','',
        'The final comparison initially stopped because evaluation fixtures store position labels as '
        '`oop_position` / `ip_position`, while the report expected a `positions` list. '
        '[Reporting recovery](report-recovery.json) supplies those labels in memory and calls the original '
        'comparison unchanged. No reference, candidate, numerical calculation or eligibility rule changed.','',
        'See [protocol](protocol.json), [run instructions](README.md), [development details](development-comparison.json), '
        '[evaluation details](evaluation-comparison.json), [frozen candidate](candidate-freeze.json) and [status](status.json).','']
    (out/'RESULTS.md').write_text('\n'.join(lines),encoding='utf-8')


if __name__=='__main__':
    report()
