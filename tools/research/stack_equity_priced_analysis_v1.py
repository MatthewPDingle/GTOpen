"""Reporting-only analysis of the completed matched comparison and CPU audit."""
import hashlib
import json
import math
from pathlib import Path

OUT = Path('T:/Dev/GTOpen/research/preflop-evolution/blind-defense-20260922')
NAME = 'stack-equity-priced-learning-v1'
ARMS = ('direct_value', 'equity_priced')


def read(path):
    return json.loads(Path(path).read_bytes())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def mean(values):
    return math.fsum(values) / len(values)


def summarize(reg, result, audit):
    assert result['complete'] and result['passed'] and audit['complete']
    assert reg['arms'] == list(ARMS) and reg['heldout_depths'] == [60, 150]
    assert len(result['tests']) == len(audit['cpu_replayed']) == 8
    verified = bool(audit['passed'])
    tests = {(t['seed'], t['arm'], t['split']): t for t in result['tests']}
    assert len(tests) == 8
    fits = {(f['seed'], f['arm']): f for f in result['fits']}
    primary, summaries, partitions, cells = [], [], [], []
    for seed in reg['seeds']:
        pair = [{c['stack']: c for c in tests[(seed, a, 'test')]['score']['contexts']} for a in ARMS]
        before, after = [mean([cs[d]['mean_regret_stack_fraction'] for d in reg['heldout_depths']]) for cs in pair]
        absolute = all(pair[1][d]['mean_regret_stack_fraction'] <= .001 for d in reg['heldout_depths'])
        passed = before > 0 and after <= .8 * before and absolute
        stored = next(g for g in result['diagnostic_gates'] if g['seed'] == seed)
        assert stored['passed'] == passed and stored['absolute_gate'] == absolute
        assert abs(stored['baseline'] - before) < 1e-12 and abs(stored['candidate'] - after) < 1e-12
        primary.append(dict(seed=seed, baseline=before, candidate=after,
            relative_reduction=1 - after / before if before else None,
            absolute_gate=absolute, gpu_gate_passed=passed,
            independently_qualified_pass=verified and passed,
            depths=[dict(stack=d, baseline_mean_bb=pair[0][d]['mean_regret_bb'],
                candidate_mean_bb=pair[1][d]['mean_regret_bb'], maximum_allowed_mean_bb=d * .001,
                baseline_p99_bb=pair[0][d]['p99_regret_bb'], candidate_p99_bb=pair[1][d]['p99_regret_bb'],
                baseline_maximum_bb=pair[0][d]['maximum_regret_bb'], candidate_maximum_bb=pair[1][d]['maximum_regret_bb'])
                for d in reg['heldout_depths']]))
        for partition in ('seats', 'price_bands', 'hand_groups'):
            for i, row in enumerate(pair[0][60][partition]):
                identity = {k: row[k] for k in ('actor', 'name', 'minimum_equity', 'maximum_equity') if k in row}
                contributions = {}
                for arm, contexts in zip(ARMS, pair):
                    values = []
                    for depth in reg['heldout_depths']:
                        context, sub = contexts[depth], contexts[depth][partition][i]
                        assert all(sub[k] == v for k, v in identity.items())
                        values.append(sub.get('mean_regret_bb', 0) * sub['rows'] / context['rows'] / depth)
                    contributions[arm] = mean(values)
                partitions.append(dict(seed=seed, partition=partition, identity=identity,
                    normalized_loss_contribution=contributions,
                    candidate_minus_baseline=contributions[ARMS[1]] - contributions[ARMS[0]]))
    for key, test in tests.items():
        seed, arm, split = key
        fit = fits[(seed, arm)]
        best = min(fit['checkpoints'], key=lambda c: (c['validation']['context_balanced_mean_regret_stack_fraction'], c['step']))
        assert best == fit['selected'] and test['selected_step'] == best['step']
        contexts = {c['stack']: c for c in test['score']['contexts']}
        summaries.append(dict(seed=seed, arm=arm, split=split, selected_step=best['step'],
            selected_validation_normalized_mean=best['validation']['context_balanced_mean_regret_stack_fraction'],
            heldout_normalized_mean=mean([contexts[d]['mean_regret_stack_fraction'] for d in reg['heldout_depths']])))
        lookup = {b['index']: b for b in result['board_records'] if b['split'] == split}
        boards = [lookup[b['index']] for b in test['board_keys']]
        assert all(b['canonical_group'] == k['canonical_group'] for b, k in zip(boards, test['board_keys']))
        for context in contexts.values():
            members = {}
            assert len(context['per_board']) == len(boards)
            for i, (row, board) in enumerate(zip(context['per_board'], boards)):
                assert row['board_index'] == i
                members.setdefault(board['cell'], []).append(row)
            rows = []
            for cell, group in sorted(members.items()):
                count = sum(r['rows'] for r in group)
                rows.append(dict(cell=cell, boards=len(group), rows=count,
                    mean_regret_bb=math.fsum(r['mean_regret_bb'] * r['rows'] for r in group) / count,
                    maximum_regret_bb=max(r['maximum_regret_bb'] for r in group)))
            assert sum(r['rows'] for r in rows) == context['rows']
            assert abs(math.fsum(r['mean_regret_bb'] * r['rows'] for r in rows) / context['rows'] - context['mean_regret_bb']) < 1e-10
            cells.append(dict(seed=seed, arm=arm, split=split, stack=context['stack'], cells=rows))
    discrepancies = []
    for test in audit['cpu_replayed']:
        p = test['comparison']
        for context in p['contexts']:
            for failure in context['failures']:
                discrepancies.append(dict(seed=test['seed'], arm=test['arm'], split=test['split'],
                                          stack=context['stack'], failure=failure))
        for failure in p['failures']:
            discrepancies.append(dict(seed=test['seed'], arm=test['arm'], split=test['split'], failure=failure))
    qualified = verified and all(p['gpu_gate_passed'] for p in primary)
    return dict(independent_readback_passed=verified, restricted_primary_comparison_passed=qualified,
                primary=primary, all_arm_summaries=summaries, primary_partition_contributions=partitions,
                board_cell_summaries=cells, numeric_discrepancies=discrepancies,
                decision_rows_are_not_independent_samples=True, preflop_accuracy_qualified=False,
                new_inference=False, new_training=False, promotion=False, production_modified=False,
                main_seconds=result['total_work_seconds'], readback_seconds=audit['seconds'],
                peak_cuda_reserved_bytes=result['peak_cuda_reserved_bytes'])


def render(analysis):
    verified = analysis['independent_readback_passed']
    passed = analysis['restricted_primary_comparison_passed']
    lines = ['# Equity-pricing comparison: completed findings', '',
        ('The candidate passed the registered primary comparison in this restricted reference.' if passed else
         'The candidate did not achieve an independently qualified pass of the registered primary comparison.'), '',
        f"Independent CPU verification: {'passed' if verified else 'FAILED'}.",
        'The table uses retained GPU measurements. ' + ('Independent CPU reconstruction agrees within the fixed tolerances.' if verified else
        'The complete CPU discrepancies are retained; these are not independently qualified accuracy results.'), '',
        '| Seed | Baseline loss / stack | Candidate loss / stack | Error reduction | Recorded primary gate |',
        '| --- | ---: | ---: | ---: | --- |']
    for p in analysis['primary']:
        reduction = 'undefined' if p['relative_reduction'] is None else f"{p['relative_reduction']:+.2%}"
        lines.append(f"| {p['seed']} | {p['baseline']:.5%} | {p['candidate']:.5%} | {reduction} | {'Pass' if p['gpu_gate_passed'] else 'Fail'} |")
    lines += ['', 'The fixed requirement was at least 20% lower mean normalized loss in BOTH',
        'seeds, plus mean loss no greater than 0.001 starting stacks at EACH of 60bb',
        'and 150bb. These depths were excluded from fitting and model selection.', '',
        '| Seed | Stack | Baseline mean, bb | Candidate mean, bb | Required maximum, bb | Baseline p99, bb | Candidate p99, bb |',
        '| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for p in analysis['primary']:
        for d in p['depths']:
            lines.append(f"| {p['seed']} | {d['stack']} | {d['baseline_mean_bb']:.5f} | {d['candidate_mean_bb']:.5f} | {d['maximum_allowed_mean_bb']:.3f} | {d['baseline_p99_bb']:.4f} | {d['candidate_p99_bb']:.4f} |")
    lines += ['', 'Loss is foregone value per evaluated terminal river decision, not bb/100',
        'or whole-game exploitability. Rows share boards and public situations; the',
        'large decision count is not a count of independent samples.', '',
        '## Model selection and separate stress results', '',
        '| Seed | Approach | Evaluation boards | Selected update | Validation loss / stack | Held-out-depth loss / stack |',
        '| --- | --- | --- | ---: | ---: | ---: |']
    for r in sorted(analysis['all_arm_summaries'], key=lambda r: (r['seed'], r['split'], r['arm'])):
        lines.append(f"| {r['seed']} | {r['arm']} | {r['split']} | {r['selected_step']} | {r['selected_validation_normalized_mean']:.5%} | {r['heldout_normalized_mean']:.5%} |")
    lines += ['', 'Both approaches received the same batch objects and training budget. All four',
        'selected model identities were frozen before the new final-test/stress labels',
        'were generated. Ordinary and deliberately rare stress boards stay separate.',
        'The candidate has fewer learned parameters and different known structure;',
        'this is not an equal-capacity comparison or an isolated feature ablation.', '',
        '## What this does and does not establish', '',
        'This reference fixes the opponent to a uniform distribution of legal hands.',
        'It tests learning visible-card equity and known terminal calling economics.',
        'It does not test actual opponent ranges selected by previous betting, future',
        'betting decisions, multiway continuation, or end-to-end preflop ranges.', '',
        'Earlier evidence already rejected substituting uniform-opponent equity for',
        'betting-conditioned equity in larger pots. A positive result here would',
        'justify a range-conditioned follow-up, not a production replacement.', '',
        'The companion JSON retains hand/actor/price contributions, board-cell means',
        'and every numerical discrepancy, including adverse outcomes. No historical',
        'failure is retried or relabeled, and no numerical tolerance is relaxed.', '',
        '## Resources', '',
        f"Main work: {analysis['main_seconds']:.1f}s. CPU verification: {analysis['readback_seconds']:.1f}s.",
        f"Peak reserved CUDA memory: {analysis['peak_cuda_reserved_bytes'] / 1e9:.3f} GB.",
        'No production change or GitHub push. The broader preflop goal remains incomplete.', '']
    return '\n'.join(lines)


def main():
    rp, result_path, audit_path = (OUT / (NAME + suffix + '.json') for suffix in ('-registration', '-result', '-readback-v1'))
    reg, result, audit = read(rp), read(result_path), read(audit_path)
    assert result['registration_sha256'] == sha(rp)
    assert audit['inputs'][str(result_path)] == sha(result_path) and audit['inputs'][str(rp)] == sha(rp)
    for path, digest in audit['inputs'].items():
        assert sha(path) == digest, path
    lock = OUT.parent / 'representative-coverage-20260919' / 'running.lock'
    assert not lock.exists(), 'Wait for terminal execution and lock release'
    analysis = summarize(reg, result, audit)
    analysis['inputs'] = {str(p): sha(p) for p in (rp, result_path, audit_path, Path(__file__))}
    dest, note = OUT / (NAME + '-analysis-v1.json'), OUT / 'STACK-EQUITY-PRICED-FINDINGS.md'
    assert not dest.exists() and not note.exists(), 'Do not overwrite analysis'
    text = render(analysis)
    with dest.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(analysis, stream, indent=2, allow_nan=False)
        stream.write('\n')
    with note.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(text)
    print(json.dumps(dict(analysis=str(dest), findings=str(note), primary=analysis['primary'],
                         verified=analysis['independent_readback_passed'])))


if __name__ == '__main__':
    main()
