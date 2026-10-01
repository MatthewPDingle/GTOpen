"""Presentation of the completed, independently checked seven-stack comparison.

Never fit, sample, replay a poker policy, select a checkpoint or run a consumer.
The live-study path refuses interim/failed/unverified evidence before reading
any comparison values. Pure rendering functions also accept synthetic controls.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
                  PYTHONDONTWRITEBYTECODE='1')
import argparse
import hashlib
import json
import math
from pathlib import Path
import time
import psutil
from stack_context_matched_analysis_v1 import DEPTHS, DEALS, finish
from crossed_complete_policy_comparison_v1 import CONTRAST_NAMES, PROFILE_NAMES

ROOT = Path('T:/Dev/GTOpen')
OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
NAME = 'stack-context-final-report-v1'
HANDOFF = 'stack-context-pressure-evaluation-handoff-v1'
EVALUATION = 'stack-context-matched-evaluation-v5'
READER = 'stack-context-matched-readback-v6'
THROUGHPUT = 'stack-context-final-bank-throughput-v4'
LOCKS = (ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock',
         ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock',
         OUT/(HANDOFF+'-owner.json'))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_bytes())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def live(record, key):
    try:
        process = psutil.Process(record['pid'])
        return abs(process.create_time()-record[key]) < .01 and process.is_running()
    except psutil.NoSuchProcess:
        return False


def final_evidence():
    # Check presence/ownership before opening the scientific result.
    required = [OUT/(name+'-result.json') for name in (HANDOFF, THROUGHPUT, EVALUATION, READER)]
    failures = [OUT/(name+'-failure.json') for name in
                (HANDOFF, THROUGHPUT, EVALUATION, READER, 'stack-context-pressure-continuation-v2')]
    require(all(path.is_file() for path in required), 'All successful terminal phases required; no interim look')
    require(not any(path.exists() for path in (*LOCKS, *failures)), 'Live ownership or failed current attempt')
    inputs = {}
    def bound(path):
        inputs[str(path)] = sha(path)
        return read(path)
    handoff = bound(required[0]); owner = bound(OUT/(HANDOFF+'-attempt.json'))
    require(handoff['handoff_complete'] is True and handoff['production_modified'] is False
            and not live(owner, 'created'), 'Handoff is not successfully terminal and released')
    state = handoff['state']
    require(state['training_complete'] is True and not state['training_alive']
            and not state['failure'] and not state['external_owner'], 'Incomplete handoff training/ownership evidence')
    for phase, name, script in (
            ('throughput', THROUGHPUT, 'stack_context_final_bank_throughput_v4.py'),
            ('evaluation', EVALUATION, 'stack_context_matched_evaluation_v5.py'),
            ('readback', READER, 'stack_context_matched_readback_v6.py')):
        require(state[phase] == dict(started=True, alive=False, complete=True), 'Incomplete terminal '+phase)
        attempt = bound(OUT/(name+'-attempt.json'))
        created = attempt.get('process_created', attempt.get('created'))
        require(created is not None and not live(dict(pid=attempt['pid'], created=created), 'created'),
                'Scientific child remains live')
        starts = [path for path in OUT.glob(HANDOFF+'-*-'+phase+'-started.json')
                  if read(path)['pid'] == attempt['pid'] and abs(read(path)['created']-created) < .01]
        require(len(starts) == 1, 'Ambiguous child identity')
        start = bound(starts[0]); prefix = str(starts[0]).removesuffix('-started.json')
        ended = bound(Path(prefix+'-finished.json'))
        require(all(ended[key] == start[key] for key in start) and ended['exit_code'] == 0
                and handoff['unix'] >= ended['finished_unix'], 'Unsuccessful or detached child exit')
        require(start['command'] == ['C:/Program Files/Python312/python.exe', '-B',
                str(ROOT/'tools/research'/script), '--run'], 'Unexpected child command')
        for stream in ('stdout', 'stderr'):
            log = Path(prefix+'-'+stream+'.log'); inputs[str(log)] = sha(log)
            require(inputs[str(log)] == ended[stream+'_sha256'], 'Changed terminal log')
    throughput = bound(required[1]); terminal = bound(required[2]); reader = bound(required[3])
    registration = OUT/(EVALUATION+'-registration.json'); inputs[str(registration)] = sha(registration)
    require(all(throughput[key] is True for key in
                ('complete', 'passed', 'full_played_banks_64', 'cuda_passed', 'reference_agreement_passed')),
            'Unsuccessful complete-bank GPU/reference gate')
    require(terminal['fixed_policy_evaluation_complete'] is True and terminal['production_modified'] is False
            and terminal['registration_sha256'] == inputs[str(registration)], 'Unbound evaluation result')
    require(all(reader[key] is True for key in ('complete', 'passed', 'independent_readback_complete',
                'training_heldout_stack_separation_verified')) and reader['production_modified'] is False,
            'Independent readback has not passed')
    require(reader['evaluation_result_sha256'] == inputs[str(required[2])]
            and reader['evaluation_registration_sha256'] == inputs[str(registration)], 'Readback binds other evidence')
    require(reader['original_archive_batches'] == 896 and reader['reference_policy_replay_batches'] == 14
            and reader['reference_complete_preflop_range_replays'] == 28
            and reader['independent_chance_cycles'] == 256 and reader['strictly_board_disjoint_test'] is False
            and reader['native_payoff_oracle_independent'] is False, 'Changed audited scope')
    require(set(terminal['journals']) == {str(depth) for depth in DEPTHS}
            and all(row['completed_deals'] == DEALS for row in terminal['journals'].values())
            and len(terminal['range_exports']) == 28, 'Incomplete final journal/range coverage')
    for path, digest in terminal['range_exports'].items():
        require(sha(path) == digest, 'Changed final range export'); inputs[path] = digest
    validate_comparison(terminal['comparison'], reader['arithmetic'])
    for path in (Path(__file__).resolve(), Path(__file__).with_name('stack_context_matched_analysis_v1.py'),
                 Path(__file__).with_name('crossed_complete_policy_comparison_v1.py')):
        inputs[str(path)] = sha(path)
    return terminal['comparison'], reader, inputs


def validate_comparison(comparison, arithmetic):
    require(comparison == finish(comparison['contexts']), 'Changed original primary calculations or gate')
    require(arithmetic['passed'] is True and arithmetic['depths'] == 7 and arithmetic['contrasts'] == 56
            and arithmetic['deals_per_depth'] == DEALS
            and arithmetic['independent_primary_gate'] == comparison['registered_policy_improvement_criterion_met'],
            'Missing matching independent numerical audit')
    for context in comparison['contexts']:
        require(context['split'] == ('heldout' if context['depth'] in (60, 150) else 'fit'), 'Wrong fitting split')
        require(context['dead_money'] == .5 and len(context['per_deal_value_ranges']) == 8
                and tuple(row['profile'] for row in context['per_deal_value_ranges']) == PROFILE_NAMES,
                'Incomplete individual-deal value ranges')
        for row in context['contrasts']:
            require(all(math.isfinite(row[key]) for key in ('mean', 'lower', 'upper', 'negative_deal_fraction',
                    'paired_loss_95_bb', 'paired_loss_99_bb', 'worst_observed_paired_loss_bb',
                    'mean_positive_paired_loss_bb')), 'Nonfinite statistic')
            require(0 <= row['negative_deal_fraction'] <= 1 and row['mean_positive_paired_loss_bb'] >= 0
                    and row['paired_loss_95_bb'] <= row['paired_loss_99_bb'] <= row['worst_observed_paired_loss_bb'],
                    'Invalid loss summary')
    return comparison


def labels(index):
    return ('A' if index < 4 else 'B', 'BB' if index % 4 < 2 else 'BTN',
            ('baseline BTN', 'candidate BTN', 'baseline BB', 'candidate BB')[index % 4])


def verdict(comparison):
    if comparison['registered_policy_improvement_criterion_met']:
        return 'The registered improvement criterion is met for this fixed-entry comparison.'
    if comparison['negative_depth_point_estimates']:
        return 'The registered improvement criterion is not met; at least one stack/actor comparison has a negative mean gain.'
    return 'The registered improvement criterion is not met; bounded intervals do not establish every pooled improvement.'


def markdown(comparison, *, synthetic=False):
    lines = ['# Matched stack-depth model comparison', '',
             '**SYNTHETIC SOFTWARE CONTROL — NOT A POKER RESULT.**' if synthetic else verdict(comparison), '',
             'Candidate = baseline plus 25 river hand-versus-board inputs. Both learn the existing heads-up all-street tree. '
             'BB faces a BTN min-raise, SB has folded, dead money is 0.5bb, and rake is 5% capped at 2bb. '
             'The inherited 200bb BTN entry range is fixed across stacks.', '',
             'Each depth uses 4,096 fresh physical deals and eight crossed profiles. A and B are separate training runs. '
             'Each gain replaces one player while holding the indicated opponent fixed. '
             'These are bb per entry, not cash-game win rates or equilibrium/exploitability estimates.', '',
             'All primary intervals use the original simultaneous bounded empirical-Bernstein method across 56 comparisons '
             '(family alpha 0.05, one final look). Improvement requires all eight pooled lower bounds above zero '
             'and no negative per-depth mean. A failed criterion does not establish equivalence.', '',
             '## Equal-depth pooled gains', '',
             'Divide each depth gain by its starting stack, then average the seven depths with equal weight. '
             'Values below are percentages of starting stack per entry, not range-frequency percentage points.', '',
             '| Run | Player replaced | Fixed opponent | Mean % | Primary lower % | Primary upper % |',
             '| --- | --- | --- | ---: | ---: | ---: |']
    for index, row in enumerate(comparison['equal_depth_normalized_gains']):
        a, b, c = labels(index)
        lines.append(f'| {a} | {b} | {c} | {100*row["mean"]:.6f} | {100*row["lower"]:.6f} | {100*row["upper"]:.6f} |')
    lines.extend(['', '## All stack-specific comparisons', '',
                  '60bb and 150bb were held out from fitting. Test draws are fresh but training/test boards are not strictly disjoint. '
                  'The intervals measure payoff uncertainty, not uncertainty in hand frequencies.', '',
                  'Signed paired loss = baseline value minus candidate value; a negative loss is a gain. '
                  '95th/99th percentiles are linear empirical quantiles, not tail guarantees. '
                  '“Mean positive loss” averages max(loss, 0) over every deal.'])
    for context in comparison['contexts']:
        depth = context['depth']; split = 'held out from fitting' if context['split'] == 'heldout' else 'fitting depth'
        lines.extend(['', f'### {depth}bb — {split}', '',
            '| Run | Player replaced | Fixed opponent | Mean bb | Primary lower bb | Primary upper bb | Negative deals % |',
            '| --- | --- | --- | ---: | ---: | ---: | ---: |'])
        for index, row in enumerate(context['contrasts']):
            a, b, c = labels(index)
            lines.append(f'| {a} | {b} | {c} | {row["mean"]:.6f} | {row["lower"]:.6f} | {row["upper"]:.6f} | {100*row["negative_deal_fraction"]:.4f} |')
        lines.extend(['', '| Run | Player | Fixed opponent | Loss p95 bb | Loss p99 bb | Worst loss bb | Mean positive loss bb |',
                      '| --- | --- | --- | ---: | ---: | ---: | ---: |'])
        for index, row in enumerate(context['contrasts']):
            a, b, c = labels(index)
            lines.append(f'| {a} | {b} | {c} | {row["paired_loss_95_bb"]:.6f} | {row["paired_loss_99_bb"]:.6f} | {row["worst_observed_paired_loss_bb"]:.6f} | {row["mean_positive_paired_loss_bb"]:.6f} |')
        lines.extend(['', '| Run | BB policy | BTN policy | BB min bb | BB max bb | BTN min bb | BTN max bb |',
                      '| --- | --- | --- | ---: | ---: | ---: | ---: |'])
        for index, row in enumerate(context['per_deal_value_ranges']):
            a = 'A' if index < 4 else 'B'; bb = 'candidate' if index % 4 >= 2 else 'baseline'; btn = 'candidate' if index % 2 else 'baseline'
            lo, hi = row['minimum_player_value_bb'], row['maximum_player_value_bb']
            lines.append(f'| {a} | {bb} | {btn} | {lo[0]:.6f} | {hi[0]:.6f} | {lo[1]:.6f} | {hi[1]:.6f} |')
    lines.extend(['', '## Verification scope', '',
        'The independent reader checks 256 reconstructed training chance cycles, 896 evaluation archives, '
        '28 complete preflop catalog CPU-reference replays and 14 first/last test-batch replays. '
        'It shares the native payoff oracle and does not replay every postflop policy row.', '',
        'All four frozen banks use played generations 0–63, weights 1–64 and exclude unplayed generation 64. '
        'Test results do not select a checkpoint. The preserved JSON contains the original full precision statistics, '
        'including exploratory normal intervals, which do not replace the primary gate.', '',
        'This comparison does not qualify complete preflop accuracy, flexible multiway play, GTO Wizard agreement '
        'or production readiness. Range behavior and supported hand changes still require plain-English analysis.', ''])
    return '\n'.join(lines)


def figure(comparison, path, *, synthetic=False):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 4, figsize=(17, 8), sharex=True, sharey=True, layout='constrained')
    for index, axis in enumerate(axes.flat):
        rows = [context['contrasts'][index] for context in comparison['contexts']]
        means = [100*row['mean']/depth for row, depth in zip(rows, DEPTHS)]
        lows = [100*row['lower']/depth for row, depth in zip(rows, DEPTHS)]
        highs = [100*row['upper']/depth for row, depth in zip(rows, DEPTHS)]
        run, player, opponent = labels(index)
        axis.axhline(0, color='#777777', linewidth=.8)
        axis.errorbar(range(7), means, yerr=([m-l for m, l in zip(means, lows)], [u-m for m, u in zip(means, highs)]),
                      fmt='o', color='#2878b5' if run == 'A' else '#26834c', capsize=3, linewidth=1.4)
        for x in (2, 4):
            axis.axvspan(x-.3, x+.3, color='#ddc36b', alpha=.15)
        axis.set_title(f'Run {run}: replace {player}\nagainst {opponent}', fontsize=11)
        axis.set_xticks(range(7), [str(d)+('*' if d in (60, 150) else '') for d in DEPTHS])
        axis.grid(axis='y', alpha=.2)
    fig.supxlabel('Starting stack (bb); * = held out from fitting')
    fig.supylabel('Candidate gain (% of starting stack per entry)')
    fig.suptitle(('SYNTHETIC SOFTWARE CONTROL — NOT A POKER RESULT\n' if synthetic else '')+
        'Seven-stack fixed-opponent comparison\nOriginal simultaneous bounded intervals; no equilibrium or all-position accuracy claim', fontsize=13)
    fig.savefig(path, dpi=180); plt.close(fig)


def main(render=False):
    if not render:
        print(json.dumps(dict(prepared=True, terminal_results_present={name:(OUT/(name+'-result.json')).is_file()
              for name in (HANDOFF, EVALUATION, READER)}, comparison_values_read=False))); return
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    paths = {kind:OUT/(NAME+suffix) for kind, suffix in
             (('table', '.md'), ('figure', '.png'), ('values', '-comparison.json'), ('receipt', '-receipt.json'))}
    require(not any(path.exists() for path in paths.values()), 'Report output already exists; preserve it')
    comparison, reader, inputs = final_evidence()
    paths['table'].write_text(markdown(comparison), encoding='utf-8')
    figure(comparison, paths['figure'])
    paths['values'].write_text(json.dumps(comparison, allow_nan=False, sort_keys=True, separators=(',', ':')), encoding='utf-8')
    require(all(sha(path) == digest for path, digest in inputs.items()), 'Source evidence changed during rendering')
    receipt = dict(complete=True, unix=time.time(), inputs=inputs,
        outputs={str(path):sha(path) for key, path in paths.items() if key != 'receipt'},
        comparison_count=56, pooled_comparison_count=8, independent_readback_complete=True,
        range_interpretation_complete=False, plain_english_analysis_complete=False,
        scientific_decision_changed=False, new_scientific_deals=False, fitting=False,
        native_execution=False, gpu_used=False, production_modified=False, broad_goal_complete=False)
    paths['receipt'].write_text(json.dumps(receipt, allow_nan=False, sort_keys=True, separators=(',', ':')), encoding='utf-8')
    print(json.dumps(dict(complete=True, outputs={key:str(path) for key, path in paths.items()})))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--render', action='store_true')
    main(parser.parse_args().render)
