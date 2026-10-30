"""Prepare a complete board-root report only after the fixed evaluation audit.

Readiness is read-only and never opens unfinished payoff data. This reporter
does not train, select checkpoints, draw deals, or change production.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'research/preflop-evolution/blind-defense-20260922'
TRAINING = 'board-root-matched-continuation-v1'
TRAINING_AUDIT = 'board-matched-complete-readback-v1'
EVAL = 'weighted-complete-board-root-study-v1'
CONTROL = 'board-complete-evaluation-control-v1'
ARMS = ('9266201-stratified', '9266201-board-root',
        '9266301-stratified', '9266301-board-root')
POLICIES = ('first-old', 'first-new', 'replication-old', 'replication-new')
ACTIONS = ('fold', 'call', 'raise', 'jam')
CONTRASTS = tuple(f'{seed}:{name}' for seed in ('first', 'replication') for name in (
    'newBB-v-oldBB-against-oldBTN', 'newBB-v-oldBB-against-newBTN',
    'newBTN-v-oldBTN-against-oldBB', 'newBTN-v-oldBTN-against-newBB'))


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def close(a, b, tolerance=1e-10):
    return math.isfinite(a) and math.isfinite(b) and abs(a-b) <= tolerance


def requirements(out):
    names = ['BOARD-ROOT-MATCHED-STUDY-PLAN.md',
             'weighted-stratified-study-v1-registration.json',
             'weighted-stratified-study-v1-training-result.json',
             'board-root-matched-prefix-v1-result.json']
    for prefix in (TRAINING, TRAINING_AUDIT, CONTROL, EVAL):
        names.extend(f'{prefix}-{suffix}.json' for suffix in ('registration', 'result'))
    for prefix in (CONTROL, EVAL):
        names.extend(f'{prefix}-{suffix}.json' for suffix in
                     ('readback-registration', 'independent-review'))
    for arm in ARMS[::2]:
        names.extend(f'weighted-training-readback-parallel-v1-w4-{arm}-0078-{suffix}.json'
                     for suffix in ('registration', 'result'))
    return [out/name for name in names]


def validate_outcomes(analysis, roots):
    rows = analysis['contrasts']
    require(analysis['deals'] == 65536 and analysis['control_only'] is False,
            'Only the complete fixed fresh evaluation can be reported')
    require(tuple(x['name'] for x in rows) == CONTRASTS,
            'All eight contrasts must retain their registered order')
    require(analysis['family_error_probability'] == .05 and analysis['units'] == 'bb per entry',
            'Wrong units or statistical family')
    require(analysis['interval_method'] ==
            'two-sided bounded empirical Bernstein; Bonferroni over eight contrasts and one final look',
            'Do not substitute a post-hoc interval')
    for row in rows:
        require(row['count'] == 65536 and all(math.isfinite(row[k]) for k in
                ('mean', 'lower', 'upper', 'standard_error')) and
                row['lower'] <= row['mean'] <= row['upper'] and row['standard_error'] >= 0,
                'Incomplete or invalid payoff comparison')
    require(tuple(roots['policy_order']) == POLICIES and tuple(roots['action_order']) == ACTIONS,
            'Wrong policy or action ordering')
    p, masses = roots['root_probabilities'], roots['entry_masses']
    require(len(p) == 4 and len(masses) == 169 and all(len(bank) == 169 for bank in p),
            'Every one of the 169 hand classes is required')
    require(all(math.isfinite(m) and m > 0 for m in masses) and close(sum(masses), 1, 1e-12),
            'Entry masses must be positive and normalized')
    for bank in p:
        for row in bank:
            require(len(row) == 4 and all(math.isfinite(v) and 0 <= v <= 1 for v in row)
                    and close(sum(row), 1), 'Invalid root probabilities')
    aggregate = [[sum(masses[c]*bank[c][a] for c in range(169)) for a in range(4)] for bank in p]
    require(len(roots['aggregate_action_frequencies']) == 4 and all(
        len(actual) == 4 and all(close(a, b) for a, b in zip(actual, expected))
        for actual, expected in zip(roots['aggregate_action_frequencies'], aggregate)),
        'Reported aggregate frequencies differ from the full class table')
    pairs = (('baseline_cross_seed', 0, 2), ('candidate_cross_seed', 1, 3),
             ('first_matched_change', 0, 1), ('replication_matched_change', 2, 3))
    require(set(roots['comparisons']) == {x[0] for x in pairs}, 'Missing range comparison')
    for name, a, b in pairs:
        actual = roots['comparisons'][name]
        tv = [.5*sum(abs(x-y) for x, y in zip(p[a][c], p[b][c])) for c in range(169)]
        different = sum(max(range(4), key=p[a][c].__getitem__) !=
                        max(range(4), key=p[b][c].__getitem__) for c in range(169))
        require(len(actual['class_total_variation']) == 169 and all(
                close(x, y) for x, y in zip(actual['class_total_variation'], tv)) and
                close(actual['entry_weighted_total_variation'], sum(m*v for m, v in zip(masses, tv))) and
                actual['classes_with_different_most_frequent_action'] == different,
                'Range summary differs from the complete probabilities')
    require(close(roots['candidate_minus_baseline_variation'],
            roots['comparisons']['candidate_cross_seed']['entry_weighted_total_variation'] -
            roots['comparisons']['baseline_cross_seed']['entry_weighted_total_variation']),
            'Wrong sign in candidate-minus-control stability')


def cost_summary(arm, metrics):
    require(len(metrics) == 78 and [m['iteration'] for m in metrics] == list(range(1, 79)),
            'Costs require all 78 committed updates, counted once')
    keys = ('pipeline_wall', 'fit', 'sampling', 'native_queries', 'native_updates',
            'native_trace', 'inference', 'ingestion', 'root_integration', 'publication')
    totals = {k: 0. for k in keys}
    wall = board_wait = fit_setup = fit_optimizer = fit_capture = 0.
    for metric in metrics:
        require(math.isfinite(metric['seconds']) and metric['seconds'] >= 0, 'Invalid update wall time')
        wall += metric['seconds']
        for key in keys:
            value = metric['timings'][key]
            require(math.isfinite(value) and value >= 0, 'Invalid stage time')
            totals[key] += value
        if arm.endswith('board-root'):
            value = metric['timings']['board_wait']
            require(math.isfinite(value) and value >= 0, 'Invalid residual board wait')
            board_wait += value
        require(len(metric['fits']) == 2 and all(f['device'] == 'cuda' for f in metric['fits']),
                'Expected two GPU fits per update')
        for fit in metric['fits']:
            for key in ('setup_seconds', 'optimizer_seconds', 'graph_capture_seconds'):
                require(math.isfinite(fit[key]) and fit[key] >= 0, 'Invalid fit timing')
            fit_setup += fit['setup_seconds']
            fit_optimizer += fit['optimizer_seconds']
            fit_capture += fit['graph_capture_seconds']
    return dict(arm=arm,updates=78,committed_update_wall_seconds=wall,stage_seconds=totals,
        residual_board_wait_seconds=board_wait if arm.endswith('board-root') else None,
        fit_setup_seconds=fit_setup,fit_optimizer_seconds=fit_optimizer,
        fit_graph_capture_seconds=fit_capture,
        note='Stage durations overlap. Do not add them to estimate elapsed time or GPU utilization.')


def verified_data(out):
    paths = requirements(out)
    missing = [str(p) for p in paths if not p.exists()]
    require(not missing, 'Final report prerequisites are missing: '+', '.join(missing))
    evidence = {}
    def bound(path, expected=None):
        path = Path(path)
        actual = sha(path)
        require(expected is None or actual == expected, 'Changed evidence: '+str(path))
        evidence[str(path)] = actual
        return read(path)
    for path in paths:
        evidence[str(path)] = sha(path)
    records = {}
    for prefix in (TRAINING, TRAINING_AUDIT, CONTROL, EVAL):
        rp = out/f'{prefix}-registration.json'
        reg, result = bound(rp), bound(out/f'{prefix}-result.json')
        require(result['passed'] and result['registration_sha256'] == sha(rp),
                'Incomplete or unrelated result: '+prefix)
        records[prefix] = (reg, result)
    train_reg, train = records[TRAINING]
    _, audit = records[TRAINING_AUDIT]
    require(train['training_complete'] and train['generations_per_arm'] == 78 and
            audit['complete_training'] and audit['reader_version'] == 2 and
            audit['source_result_sha256'] == sha(out/f'{TRAINING}-result.json'),
            'Full independently checked candidate training required')
    require([a['arm'] for a in train['arms']] == list(ARMS[1::2]) and
            [a['arm'] for a in audit['arms']] == list(ARMS[1::2]), 'Wrong training arm order')
    for result, check in zip(train['arms'], audit['arms']):
        require(result['completed'] == check['generations'] == 78 and check['boards_checked'] == 312 and
                check['physical_roots_checked'] == 39936 and check['final_checkpoint'] == result['checkpoint'],
                'Incomplete training audit')
    for prefix, deals in ((CONTROL, 64), (EVAL, 65536)):
        reg, result = records[prefix]
        review = bound(out/f'{prefix}-independent-review.json')
        review_reg = bound(out/f'{prefix}-readback-registration.json')
        require(result['complete'] and result['deals'] == deals and tuple(result['arms']) == ARMS and
                review['passed'] and review['deals'] == deals and
                review['source_registration_sha256'] == sha(out/f'{prefix}-registration.json') and
                review['source_result_sha256'] == sha(out/f'{prefix}-result.json') and
                review['readback_registration_sha256'] == sha(out/f'{prefix}-readback-registration.json') and
                review_reg['source_result_sha256'] == sha(out/f'{prefix}-result.json'),
                'Complete matching independent evaluation audit required')
    reg, result = records[EVAL]
    require(reg['mode'] == result['mode'] == 'study' and reg['test_seed'] == result['test_seed'] == 9281101
            and reg['deals'] == 65536, 'Wrong final evaluation or chance stream')
    final_review = bound(out/f'{EVAL}-independent-review.json')
    require(final_review['batches'] == 2048, 'All batches must be audited')
    store = Path(result['store'])
    require(str(store) == reg['store'], 'Evaluation store mismatch')
    analysis = bound(store/'analysis.json', result['analysis_sha256'])
    roots = bound(store/'root-stability.json', result['root_stability_sha256'])
    validate_outcomes(analysis, roots)
    old_reg_path = out/'weighted-stratified-study-v1-registration.json'
    old_reg = bound(old_reg_path)
    old_result = bound(out/'weighted-stratified-study-v1-training-result.json')
    require(old_result['training_complete'] and old_result['registration_sha256'] == sha(old_reg_path)
            and old_reg['generations'] == 78 and [a['name'] for a in old_reg['arms']] == list(ARMS[::2]),
            'Historical controls do not match the registered design')
    costs = []
    for arm in ARMS:
        if arm.endswith('board-root'):
            record = next(a for a in train['arms'] if a['arm'] == arm)
            progress = bound(record['progress_path'], record['progress_sha256'])
            require(progress['completed'] == 78 and progress['registration_sha256'] == sha(out/f'{TRAINING}-registration.json'),
                    'Wrong candidate progress')
            rows = progress['generations']
        else:
            prefix = f'weighted-training-readback-parallel-v1-w4-{arm}-0078'
            rpath = out/f'{prefix}-registration.json'
            historical, checked = bound(rpath), bound(out/f'{prefix}-result.json')
            require(checked['passed'] and checked['readback_registration_sha256'] == sha(rpath) and
                    checked['source_registration_sha256'] == sha(old_reg_path) and checked['complete_arm'] and
                    checked['completed_updates'] == 78 and historical['arm'] == arm and
                    historical['completed'] == 78, 'Unverified control training')
            rows = [dict(path=str(Path(f)/'metrics.json'),sha256=historical['inputs'][str(Path(f)/'metrics.json')])
                    for f in historical['folders']]
        require(len({r['path'] for r in rows}) == 78, 'Duplicate or missing committed update')
        costs.append(cost_summary(arm, [bound(r['path'], r['sha256']) for r in rows]))
    prefix_result = bound(out/'board-root-matched-prefix-v1-result.json')
    checks = prefix_result['storage_checks'] + train['storage_checks']
    peak = max(c['allocated_file_bytes'] for c in checks)
    resources = dict(arms=costs,observed_candidate_boundary_peak_allocated_bytes=peak,
        candidate_final_allocated_bytes=train['measurement']['allocated_file_bytes'],
        candidate_allocation_limit_bytes=train_reg['maximum_allocated_bytes'],
        candidate_prefix_invocation_seconds=prefix_result['seconds'],
        candidate_final_continuation_invocation_seconds=train['seconds'],
        training_audit_seconds=audit['seconds'],final_evaluation_invocation_seconds=result['seconds_this_invocation'],
        final_evaluation_audit_seconds=final_review['seconds'],
        control_final_allocated_bytes=bound(out/'weighted-stratified-study-v1-training-result.json')['storage']['allocated_file_bytes'],
        limitations=['Peak is observed at quiescent storage boundaries, not continuous telemetry.',
            'Invocation times are not total research elapsed time; earlier interrupted attempts and idle gaps may be excluded.',
            'Historical controls were timed earlier; this is not a controlled throughput benchmark.',
            'File allocation excludes filesystem overhead; separate free-volume guards apply.'])
    return analysis, roots, final_review, resources, evidence


def class_table(roots):
    # Native order: ranks ascend 2..A, lower triangle suited, upper offsuit.
    ranks = '23456789TJQKA'
    rows = []
    for c in range(169):
        a, b = divmod(c, 13)
        label = ranks[max(a,b)]+ranks[min(a,b)]+('' if a == b else 's' if a > b else 'o')
        rows.append(dict(native_class_index=c,hand=label,entry_mass=roots['entry_masses'][c],
            policies={name:dict(zip(ACTIONS, bank[c])) for name,bank in zip(POLICIES,roots['root_probabilities'])},
            total_variation={name:value['class_total_variation'][c] for name,value in roots['comparisons'].items()}))
    return rows


def render(analysis, roots, review, resources):
    rows = analysis['contrasts']
    positive = sum(x['lower'] > 0 for x in rows)
    negative = sum(x['upper'] < 0 for x in rows)
    old, new = [roots['comparisons'][name] for name in ('baseline_cross_seed','candidate_cross_seed')]
    payoff = '\n'.join(f"| {x['name']} | {x['mean']:+.4f} | {x['standard_error']:.4f} | [{x['lower']:+.4f}, {x['upper']:+.4f}] |" for x in rows)
    frequencies = '\n'.join('| '+arm+' | '+' | '.join(f'{100*v:.2f}%' for v in freq)+' |'
                            for arm,freq in zip(ARMS,roots['aggregate_action_frequencies']))
    timings = '\n'.join(f"| {c['arm']} | {c['committed_update_wall_seconds']/60:.2f} | {c['stage_seconds']['pipeline_wall']/60:.2f} | {c['stage_seconds']['fit']/60:.2f} | "+
                        ('n/a' if c['residual_board_wait_seconds'] is None else f"{c['residual_board_wait_seconds']/60:.2f}")+' |'
                        for c in resources['arms'])
    return f'''# Board-integrated root training: completed comparison

All eight registered payoff comparisons are included. The simultaneous intervals
support positive gains in **{positive}**, negative gains in **{negative}**, and leave
**{8-positive-negative} inconclusive**. This concerns a replacement player against
a fixed opponent; it does not rank complete strategies or certify equilibrium.

## Scope and fixed design

Two board-root runs are compared with their two historical stratified controls
in the restricted 200bb BB-versus-BTN game: 2bb open, 0.5bb dead money, 5% rake
capped at 2bb. Each arm has 78 updates, 512 physical deals per update, and the
same optimizer budget. The paired arms share the physical source-deal seeds,
but evolving policies can produce different action paths.

Only the BB root regret estimator changes: four sampled public boards per
update are evaluated across compatible private hands, with original entry
weights and the qualified chance correction. Exact preflop terms remain separate.
The physical neural training targets are unchanged. This tests whether that
different root estimator improves learning, not whether it can look smoother.

Every played generation 0-77 is averaged with weights 1-78 and own-action reach.
Unplayed generation 78 is excluded. The comparison matches learning updates and
physical samples, **not total compute or elapsed time**.

## Range consistency

Entry-weighted cross-seed total variation is **{100*old['entry_weighted_total_variation']:.2f}% for controls**
and **{100*new['entry_weighted_total_variation']:.2f}% for board-root training**;
the difference is **{100*roots['candidate_minus_baseline_variation']:+.2f} percentage points**.
A negative difference means greater agreement between these two runs. This is
descriptive consistency, not accuracy or EV loss. The most frequent action differs
in {old['classes_with_different_most_frequent_action']} control classes and
{new['classes_with_different_most_frequent_action']} candidate classes, out of 169.

| Complete policy bank | Fold | Call | Raise | Jam |
| --- | ---: | ---: | ---: | ---: |
{frequencies}

The [complete hand table](board-final-all-hand-classes.json) includes every class,
its entry mass, all four policies, and all four per-class comparisons.

## Payoff comparisons

The fixed evaluation uses 65,536 fresh common physical deals, seed **9281101**.
Positive gains favor the replacement player against the named fixed opponent.
Units are **bb per entry into this research spot**, not bb/100 dealt hands.
Intervals are the registered bounded empirical-Bernstein simultaneous 95%
intervals, with Bonferroni adjustment across eight contrasts at one final look.

| Replacement and fixed opponent | Mean gain | Paired standard error | Simultaneous 95% interval |
| --- | ---: | ---: | ---: |
{payoff}

![All eight payoff comparisons](board-final-gains.png)

An interval containing zero is inconclusive, not evidence of equivalence.
No favorable seed or checkpoint was selected. No additional deals, training
updates, or alternative interval were chosen after inspecting the outcomes.

## Computing cost

All times below are minutes, summed over each arm's 78 committed updates exactly
once. Retries, checkpoint validation between updates and other orchestration are
outside those update timers. Stages overlap and must not be added together.

| Arm | Update wall time | Physical pipeline wall time | GPU-fit stage wall time | Residual board wait |
| --- | ---: | ---: | ---: | ---: |
{timings}

Board calculations overlap physical preparation and fitting. Zero residual wait
therefore does not mean zero board computation. The fit stage includes setup and
transfer work, not just GPU kernels. [Detailed cost evidence](board-final-costs.json)
also includes physical worker categories, optimizer timings and audit durations.
Historical controls ran earlier; these timings do not isolate a speedup.

The observed candidate storage peak at recorded quiescent boundaries was
**{resources['observed_candidate_boundary_peak_allocated_bytes']/1e9:.2f} GB allocated**;
the enforced study allocation limit was {resources['candidate_allocation_limit_bytes']/1e9:.2f} GB.
Final candidate allocation was {resources['candidate_final_allocated_bytes']/1e9:.2f} GB,
versus {resources['control_final_allocated_bytes']/1e9:.2f} GB recorded for the controls.
These are file-allocation measurements, not continuous peak telemetry. Candidate
storage includes retained prefix/recovery evidence, so the ratio is not a pure
algorithm-storage comparison. Decimal GB are used throughout.

## Verification and interpretation limits

Both 78-update candidate histories passed full independent readback. Complete
policy-bank GPU/CPU checks passed before the fresh evaluation. Its independent
review checked {review['batches']:,} batches and {review['observations']:,} policy
observations, with maximum statistical discrepancy {review['maximum_statistical_error']:.3g}.
These checks share the native poker engine; they are not an independent poker
implementation or a best-response/exploitability certificate.

Scientific interpretation remains required before choosing the next experiment.
Other seats, stacks, bet sizes, multiway pots and agreement with GTO Wizard remain
unproven. No deployment or automatic promotion follows this report.
'''


def main(run=False):
    required = requirements(OUT)
    missing = [str(p) for p in required if not p.exists()]
    if not run:
        print(json.dumps(dict(prerequisites_present=not missing,pending=missing,
            full_validation_performed=False,payoffs_opened=False,report_written=False,
            production_modified=False)),flush=True)
        return
    analysis,roots,review,resources,evidence = verified_data(OUT)
    names = ('BOARD-FINAL-FINDINGS.md','board-final-all-hand-classes.json','board-final-costs.json',
             'board-final-gains.png','board-final-report-evidence.json')
    paths = [OUT/n for n in names]
    require(not any(p.exists() for p in paths), 'Preserve existing report outputs')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax = plt.subplots(figsize=(11,5.8),layout='constrained')
    for i,row in enumerate(analysis['contrasts']):
        ax.errorbar(row['mean'],i,xerr=[[row['mean']-row['lower']],[row['upper']-row['mean']]],
                    fmt='o',capsize=4,color='#286e9e' if i < 4 else '#b36326')
    ax.axvline(0,color='#555',linewidth=1)
    ax.invert_yaxis(); ax.grid(axis='x',alpha=.2)
    labels = [x.replace('first:','Run 1: ').replace('replication:','Run 2: ')
              .replace('newBB-v-oldBB','Replace BB').replace('newBTN-v-oldBTN','Replace BTN')
              .replace('-against-old',' vs control ').replace('-against-new',' vs candidate ') for x in CONTRASTS]
    ax.set_yticks(range(8),labels)
    ax.set_xlabel('Gain from replacing one player (bb per entry; positive favors board-root training)')
    ax.set_title('Board-root training: all eight payoff comparisons\n65,536 common deals; registered simultaneous 95% intervals')
    fig.savefig(paths[3],dpi=150);plt.close(fig)
    paths[0].write_text(render(analysis,roots,review,resources),encoding='utf-8')
    for path,value in ((paths[1],class_table(roots)),(paths[2],resources)):
        with path.open('x',encoding='utf-8') as stream:
            json.dump(value,stream,indent=2,allow_nan=False);stream.write('\n')
    evidence[str(Path(__file__))] = sha(__file__)
    with paths[4].open('x',encoding='utf-8') as stream:
        json.dump(dict(inputs=evidence,outputs={str(p):sha(p) for p in paths[:4]},
            interpretation_pending=True,visual_review_pending=True,accuracy_qualified=False,
            production_modified=False),stream,indent=2,allow_nan=False)
    print('Complete verified report rendered; interpretation and visual review remain required.',flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--run',action='store_true')
    main(parser.parse_args().run)
