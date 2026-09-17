"""Independent arithmetic checks and readable report for the fixed Hold'em audit."""
import collections
import hashlib
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import holdem_call_audit as run


def audit(m, result):
    jobs = []
    for job in m['jobs']:
        path = run.OUT/'jobs'/(job['id']+'.json')
        assert run.pilot.sha(path) == result['job_sha256'][job['id']]
        data = run.read(path)
        run.validate(data, job, m)
        for seat, hands in enumerate(data['hands']):
            assert len({h['hand'] for h in hands}) == len(hands)
            assert all(h['pair_mass'] >= 0 and 0 <= h['equity'] <= 1 for h in hands)
            mean = sum(h['pair_mass']*h['ev_bb'] for h in hands)/data['pair_mass']
            assert abs(mean-data['means_bb'][seat]) < .00001
        jobs.append(data)
    labels = run.pilot.LABELS
    counts, equity = run.pilot.matrices()
    weights = np.array(m['case']['weights'])
    # Independent weighted opponent-equity calculation, avoiding pilot.context.
    exact_eq = (equity*counts)@weights[1]/(counts@weights[1])
    board_mass = np.zeros((len(jobs), 169))
    board_ev = board_mass.copy(); board_residual = board_mass.copy()
    native = next(r for r in run.read(run.OUT/'candidate-values.json')['rows'] if r['path'] == [2])
    max_error = 0.
    for k, label in enumerate(labels):
        masses, values, residuals, gains = [], [], [], []
        for i, data in enumerate(jobs):
            entries = [h for h in data['hands'][0] if h['hand'] == label]
            h = entries[0] if entries else dict(pair_mass=0., ev_bb=0., equity=0., br_ev_bb=0.)
            factor = data['job']['iso_weight']/data['job']['inclusion_probability']
            mass = factor*h['pair_mass']
            masses.append(mass); values.append(h['ev_bb'])
            residuals.append(h['ev_bb']-5*h['equity'])
            gains.append(max(0., h['br_ev_bb']-h['ev_bb']))
            board_mass[i, k] = mass; board_ev[i, k] = h['ev_bb']
            board_residual[i, k] = residuals[-1]
        direct = np.average(values, weights=masses)-1.5
        corrected = 5*exact_eq[k]+np.average(residuals, weights=masses)-1.5
        gain = np.average(gains, weights=masses)
        row = result['records'][k]
        assert row['hand'] == label and row['class_index'] == k
        v = native['hands'][k]['action_values_counterfactual_bb']
        pred = v[1]/(-v[0])+1.
        for a, b in [(direct, row['direct_advantage_bb']), (corrected, row['corrected_advantage_bb']),
                     (gain, row['postflop_br_gain_bb']), (pred, row['candidate_advantage_bb'])]:
            max_error = max(max_error, abs(a-b))
        assert row['adequate_call_support'] == (row['call_frequency'] >= .0001)
        assert row['reference_hand_settled'] == (gain <= .025)
    assert max_error < 1e-10, max_error
    # Resample rows directly, independently of the evaluator's count-matrix product.
    groups = collections.defaultdict(list)
    for i, data in enumerate(jobs): groups[data['job']['stratum']].append(i)
    rng = np.random.default_rng(m['bootstrap_seed'])
    raw, cv = [], []
    for _ in range(m['bootstrap_replicates']):
        ids = np.concatenate([rng.choice(g, len(g)) for g in groups.values()])
        mass = board_mass[ids]
        raw.append(np.sum(mass*board_ev[ids], axis=0)/mass.sum(axis=0)-1.5)
        cv.append(5*exact_eq+np.sum(mass*board_residual[ids], axis=0)/mass.sum(axis=0)-1.5)
    raw_ci, cv_ci = np.quantile(raw, [.025, .975], axis=0), np.quantile(cv, [.025, .975], axis=0)
    for k, row in enumerate(result['records']):
        assert np.max(np.abs(raw_ci[:, k]-row['direct_95_interval'])) < 1e-10
        assert np.max(np.abs(cv_ci[:, k]-row['corrected_95_interval'])) < 1e-10
        decision = 'uncertain_or_no_clear_sign_disagreement'
        if row['call_frequency'] < .0001: decision = 'sparse_call_support'
        elif row['postflop_br_gain_bb'] > .025: decision = 'postflop_hand_unsettled'
        elif row['candidate_advantage_bb'] > .05 and max(raw_ci[1, k], cv_ci[1, k]) < -.05:
            decision = 'clear_model_call_reference_fold'
        elif row['candidate_advantage_bb'] < -.05 and min(raw_ci[0, k], cv_ci[0, k]) > .05:
            decision = 'clear_model_fold_reference_call'
        assert row['decision'] == decision
    return dict(passed=True, jobs=len(jobs), classes=len(labels),
                max_independent_arithmetic_error_bb=max_error,
                bootstrap_intervals_independently_recomputed=True,
                source_hashes_unchanged=True, production_enabled=False)


def main():
    m = run.checked(); result = run.read(run.OUT/'evaluation.json')
    checks = audit(m, result)
    records = {r['hand']: r for r in result['records']}
    selected = [records[h] for h in m['probes']]
    fig, ax = plt.subplots(figsize=(11, 6.5))
    for i, row in enumerate(selected):
        for offset, value, interval, color in [
            (-.15, row['direct_advantage_bb'], row['direct_95_interval'], '#3576b5'),
            (.15, row['corrected_advantage_bb'], row['corrected_95_interval'], '#25927b')]:
            ax.plot(interval, [i+offset]*2, color=color, linewidth=2)
            ax.plot(value, i+offset, 'o', color=color, markersize=5)
        ax.plot(row['candidate_advantage_bb'], i, 'D', color='#cb6536', markersize=6)
    names = [r['hand']+(' *' if not r['adequate_call_support'] else '')+
             (' !' if not r['reference_hand_settled'] else '') for r in selected]
    ax.set_yticks(range(len(names)), names); ax.invert_yaxis(); ax.axvline(0, color='gray', linestyle='--')
    ax.set_xlabel('Call advantage over folding (bb); positive favors calling over folding')
    ax.set_title('Hold’em: BB facing SB 2.5bb open, 40bb stacks\nFrozen model versus 50 postflop references')
    ax.grid(axis='x', alpha=.2)
    for color, marker, label in [('#cb6536', 'D', 'Frozen model'), ('#3576b5', 'o', 'Direct references'),
                                ('#25927b', 'o', 'Equity-adjusted references')]:
        ax.plot([], [], marker=marker, color=color, linestyle='none', label=label)
    ax.legend(loc='best')
    fig.text(.05, .02, '* Almost never calls in the saved game.  ! Per-hand reference has not settled.\n'
             'Lines: exploratory 95% board-sampling intervals. This does not compare calling with 3-betting.', fontsize=9)
    fig.tight_layout(rect=(0, .075, 1, 1)); fig.savefig(run.OUT/'call-values.png', dpi=160); plt.close(fig)
    clear = [r for r in result['records'] if r['decision'].startswith('clear_')]
    counts = result['counts']; mae = result['pair_weighted_mae_bb']
    lines = ['# Hold’em call-versus-fold accuracy audit', '',
             f"The frozen experimental model has **{len(clear)} clear call/fold sign disagreements** under the predeclared evidence rules in this one heads-up spot. This is a local accuracy result, not full-game exploitability or a comparison with GTO Wizard.", '',
             '![Call values](call-values.png)', '', '## What was tested', '',
             'BB faces SB’s 2.5bb open at 40bb, with zero rake. The model prices a call using its predicted postflop value. We compared that value with 50 separately solved flops, using the same opening and calling ranges and the model’s postflop action menu. Calling costs another 1.5bb; folding is the zero baseline in this comparison.', '',
             'The N15 model and N20 GPU interface are frozen research versions. Neither was installed in the app. The Balanced comparison below also uses that research interface and the same ranges.', '',
             '## Fixed hand probes', '',
             '| Hand | Saved call % | Model bb | Direct bb [95%] | Equity-adjusted bb [95%] | BR gain bb | Evidence |',
             '|---|---:|---:|---:|---:|---:|---|']
    def estimate(row, name):
        key = 'direct' if name == 'direct' else 'corrected'
        v = row[key+'_advantage_bb']; lo, hi = row[key+'_95_interval']
        return f'{v:+.3f} [{lo:+.3f}, {hi:+.3f}]'
    for r in selected:
        lines.append(f"| {r['hand']} | {r['call_frequency']*100:.5f} | {r['candidate_advantage_bb']:+.3f} | {estimate(r, 'direct')} | {estimate(r, 'corrected')} | {r['postflop_br_gain_bb']:.4f} | {r['decision'].replace('_', ' ')} |")
    lines += ['', 'All 169 classes, including sparse and unsettled ones, are retained in [evaluation.json](evaluation.json).', '',
              '## Clear disagreements under the exploratory screen', '']
    if clear:
        lines += ['| Hand | Model bb | Direct bb [95%] | Equity-adjusted bb [95%] |', '|---|---:|---:|---:|']
        for r in clear:
            lines.append(f"| {r['hand']} | {r['candidate_advantage_bb']:+.3f} | {estimate(r, 'direct')} | {estimate(r, 'corrected')} |")
    else:
        lines.append('No class met every predeclared condition for a clear sign disagreement. This does not establish model accuracy: uncertain estimates and unsupported hands remain unresolved.')
    lines += ['', '## Evidence checks', '',
              f"- All {result['board_count']} references passed both GPU and transported CPU convergence checks. Maximum gaps: {result['max_gpu_gap_pct']:.4f}% / {result['max_cpu_gap_pct']:.4f}% of the pot.",
              f"- Reference solve time: {result['reference_job_seconds']/60:.1f} minutes, excluding launch overhead.",
              f"- {result['qualified_call_pair_mass_fraction']*100:.4f}% of the saved calling range’s compatible pair mass passed the per-hand support and convergence screens.",
              '- Native GPU/Python call-value parity, manifest hashes, weighted means, units, all 169 classifications, and all 5,000-sample confidence intervals were checked independently.', '',
              '| Evidence classification | Classes |', '|---|---:|']
    lines += [f"| {key.replace('_', ' ')} | {value} |" for key, value in sorted(counts.items())]
    lines += ['', '| Pair-weighted mean absolute error (bb) | Direct | Equity-adjusted |', '|---|---:|---:|',
              f"| Frozen model | {mae['candidate_direct']:.4f} | {mae['candidate_corrected']:.4f} |",
              f"| Research Balanced baseline | {mae['balanced_direct']:.4f} | {mae['balanced_corrected']:.4f} |", '',
              'These average errors are weighted by the saved calling range. They are descriptive point estimates, not a statistically established model ranking or a substitute for the per-hand evidence screens.', '',
              '## Interpretation and next step', '',
              'This panel did not reproduce the earlier miniature-game decision failure among the adequately supported call/fold comparisons. That is encouraging, but it does not establish that the model chooses the best preflop action or will behave reliably in larger games.', '',
              'For example, both the model and references value a KQo call above folding in this heads-up spot. A9o looks discrepant on the chart, but its calling frequency is tiny and its reference has a large per-hand best-response gain. It would be misleading to present that unsettled continuation as proof of a model error.', '',
              'The next useful audit is calling versus 3-betting at a fixed decision, including the opponent’s folds, calls and re-raises. A profitable call alone cannot diagnose missing flatting or mixed strategies. More flops can narrow sampling intervals; they cannot replace evaluating those alternative actions. Keep this research model out of production until those action comparisons and broader contexts are checked.', '',
              '## Limits', '',
              'The 50-flop estimate has sampling uncertainty. Equity adjustment can reduce board noise, but uses an approximate cached equity whose error is absent from the intervals. Clear disagreements require both estimates to agree, adequate calling support, and a small per-hand best-response gain. Intervals are exploratory, not simultaneous guarantees across 169 hands.', '',
              'A positive call value does not establish that calling beats raising. This fixed-range test does not measure the entire preflop strategy’s best response, alternative range distributions, richer postflop menus, other stacks, or multiway play. Some flops may overlap old training panels; the range context and reference labels are new, not a board-disjoint test.', '',
              '## Reproduce', '',
              'Run `holdem_call_audit.py run`, then `evaluate_holdem_call_audit.py`, then `report_holdem_call_audit.py` from `tools/research/`. The run checks input hashes and reuses completed references. Required local binaries and saved game are hashed in [manifest.json](manifest.json); they are not committed. See [PROTOCOL.md](PROTOCOL.md) for the frozen rules.', '']
    (run.OUT/'REPORT.md').write_text('\n'.join(lines), encoding='utf-8', newline='\n')
    checks['evaluation_sha256'] = run.pilot.sha(run.OUT/'evaluation.json')
    checks['report_sha256'] = run.pilot.sha(run.OUT/'REPORT.md')
    checks['auditor_sha256'] = run.pilot.sha(Path(__file__))
    run.write(run.OUT/'independent-audit.json', checks)
    print(json.dumps(checks, indent=2))


if __name__ == '__main__': main()
