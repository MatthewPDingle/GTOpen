"""Audit and publish the fixed range-diversity experiment, including rejection."""
import datetime as dt
import continuation_bridge_run as run

study=run.study
OUT=run.OUT


def audit():
    partitions=[]
    for name in ['training','evaluation']:
        manifest=run.checked(name)
        checked=0;missing=0;cpu=0.;gpu=0.;accounting=0.
        for job in manifest['jobs']:
            path=OUT/name/'jobs'/f"{job['id']}.json"
            if not path.exists():missing+=1;continue
            row=study.read(path);run.validate_reference(row,job,manifest)
            checked+=1;cpu=max(cpu,row['gap_pct']);gpu=max(gpu,row['gpu_gap_pct'])
            accounting=max(accounting,abs(sum(row['means_bb'])-job['config']['tree']['starting_pot']))
            if name=='evaluation':
                freeze=study.read(OUT/'candidate-freeze.json')
                assert freeze['evaluation_manifest_id']==manifest['id'] and freeze['evaluation_completed_jobs']==0
                assert study.pilot.sha(OUT/'candidate.json')==freeze['sha256']
                assert path.stat().st_mtime>=dt.datetime.fromisoformat(freeze['frozen_at']).timestamp()
        partitions.append(dict(partition=name,audited=checked,missing=missing,max_cpu_gap_pct=cpu,
            max_gpu_gap_pct=gpu,max_pot_accounting_error_bb=accounting))
    result=dict(checked_at=study.night.now(),partitions=partitions,production_enabled=False,
        all_reserved_references_complete=all(p['missing']==0 for p in partitions))
    study.night.dump(OUT/'reference-audit.json',result)
    return result


def report():
    quality=audit()
    screen=study.read(OUT/'training-screen.json')
    assert quality['partitions'][0]['missing']==0
    control=study.read(study.ROOT/'research/preflop-evolution/continuation/night-shift-20260916/curvature-pilot-selection.json')
    control=next(r for r in control['scores'] if r['kind']=='shape' and r['alpha']==.1)
    evaluation=study.read(OUT/'evaluation.json') if (OUT/'evaluation.json').exists() else None
    if evaluation:
        assert screen['eligible'] and quality['all_reserved_references_complete']
        assert evaluation['candidate_sha256']==study.pilot.sha(OUT/'candidate.json')
    verdict=('Passed the training-family screen; prospective evaluation is pending.' if screen['eligible']
        else 'Rejected by the training-family screen. No evaluation labels were generated or used.')
    if not screen['eligible']:
        assert quality['partitions'][1]['audited']==0
    if evaluation:
        verdict=('Passed the fixed fresh-board accuracy screen. Runtime and changed-policy checks are still required.'
            if evaluation['accuracy_screen_passed'] else 'Failed the fixed fresh-board accuracy screen. Keep the candidate out of the application.')
    lines=['# Training range diversity: results','',f'**{verdict}**','',
        'Port 56708 is unchanged. This is an offline continuation-value experiment, not a deployed preflop solver.', '',
        '## What changed','',
        'Added 36 synthetic training contexts between concentrated and broad ranges from four existing training '
        'families. Each pair is tested at stack-to-pot ratios 4, 10 and 16, using 20 new stratified flops. '
        'These are controlled training examples, not measured player profiles. The model retains the same '
        '104 features and ridge penalty 0.1. Original data, new blind-call data and the bridges total 62 fitting cases.', '',
        '## Training-family screen','',
        'Each family is excluded in turn, including its related synthetic and development cases. '
        'The eligibility score uses only the unchanged original 24 validation cases. '
        'It requires at least 5% lower equal-family mean error and no family more than 5% worse.', '',
        '| Excluded training family | Original predictor | Expanded training |',
        '|---|---:|---:|']
    for family,mean in screen['family_means'].items():
        lines.append(f"| {family} | {control['family_means'][family]:.3f} | {mean:.3f} |")
    lines+=['',f"Mean improvement: **{100*screen['improvement']:+.2f}%**. "
        f"Worst family error ratio: **{screen['worst_family_ratio']:.3f}**.",'',
        'Errors are compatible-mass-weighted mean absolute hand-value errors, as a percentage of starting pot. '
        'Training-family screening selects a candidate; it does not establish prospective accuracy.','']
    if evaluation:
        lines+=['## Fresh-board evaluation','',
            'Eight previously studied case identities from two families excluded from fitting use 50 new flops each. '
            'The fixed gate requires 15% lower mean error than Balanced in each family and no individual case '
            'more than 10% worse than the previous frozen predictor.', '',
            '| Family | Balanced | Previous predictor | New predictor | Improvement vs Balanced, 90% interval |',
            '|---|---:|---:|---:|---:|']
        for family in evaluation['families']:
            e=family['mae_pct_pot'];lo,hi=family['paired_90_improvement_ci']['balanced']
            lines.append(f"| {family['family']} | {e['balanced']:.3f} | {e['previous']:.3f} | {e['candidate']:.3f} | {100*lo:+.1f}% to {100*hi:+.1f}% |")
        lines+=['','| Case | Balanced | Previous predictor | New predictor | Maximum probe BR gain (% pot) |',
            '|---|---:|---:|---:|---:|']
        for case in evaluation['cases']:
            e=case['mae_pct_pot']
            lines.append(f"| {case['case']} | {e['balanced']:.3f} | {e['previous']:.3f} | {e['candidate']:.3f} | {case['max_probe_br_gain_pct_pot']:.3f} |")
        lines+=['','Paired 90% intervals resample boards within texture strata. They condition on the fitted '
            'model and cached equities; they exclude training uncertainty. Case identities were used historically, '
            'so this is fresh-board evidence on held-out families, not entirely unseen-context validation.','']
    lines+=['## Reference integrity','',
        '| Partition | Audited / planned | Maximum CPU gap (% pot) | Maximum GPU gap (% pot) | Maximum pot-sum error (bb) |',
        '|---|---:|---:|---:|---:|']
    for part in quality['partitions']:
        lines.append(f"| {part['partition']} | {part['audited']} / {part['audited']+part['missing']} | {part['max_cpu_gap_pct']:.5f} | {part['max_gpu_gap_pct']:.5f} | {part['max_pot_accounting_error_bb']:.2e} |")
    lines+=['','Persisted references are checked against their immutable manifests and both numerical '
        'stopping gates. Per-hand compatible masses and weighted values must reconcile with aggregates; '
        'zero-rake player values must sum to the starting pot. Evaluation outputs must follow the candidate freeze.', '',
        'All references retain the fixed half-pot postflop menu. Low range-average best-response gaps do not '
        'certify every rare-hand label. These value errors do not measure action-frequency accuracy or full-game '
        'exploitability. Multiway card-removal approximation, broader bet menus and range evolution remain limitations.', '',
        'See [frozen protocol](README.md), [training screen](training-screen.json), '
        '[reference audit](reference-audit.json) and [status](status.json).','']
    (OUT/'RESULTS.md').write_text('\n'.join(lines),encoding='utf-8')


if __name__=='__main__':report()
