"""Evaluate fixed Hold'em references; no training, server mutations or new solves."""
import collections
import json
from pathlib import Path
import numpy as np
import holdem_call_audit as run

OUT = run.OUT


def summarize(m, rows):
    n = len(rows)
    den = np.zeros((n, 169)); ev = den.copy(); residual = den.copy(); br = den.copy()
    groups = collections.defaultdict(list)
    for i, r in enumerate(rows):
        groups[r['job']['stratum']].append(i)
        factor = r['job']['iso_weight']/r['job']['inclusion_probability']
        for h in r['hands'][0]:
            k = run.pilot.INDEX[h['hand']]; w = factor*h['pair_mass']
            den[i, k] = w; ev[i, k] = w*h['ev_bb']
            residual[i, k] = w*(h['ev_bb']-5*h['equity'])
            br[i, k] = w*max(0, h['br_ev_bb']-h['ev_bb'])
    total = den.sum(axis=0)
    assert (total > 0).all()
    counts, eq = run.pilot.matrices()
    context = run.pilot.context(m['case'], counts, eq)
    raw_advantage = ev.sum(axis=0)/total-1.5
    corrected_advantage = 5*context['raw'][0]+residual.sum(axis=0)/total-1.5
    convergence = br.sum(axis=0)/total
    rng = np.random.default_rng(m['bootstrap_seed'])
    draw = np.zeros((m['bootstrap_replicates'], n))
    for b in range(len(draw)):
        for ids in groups.values():
            draw[b] += np.bincount(rng.choice(ids, len(ids)), minlength=n)
    sampled_den = draw@den
    assert (sampled_den > 0).all()
    raw_boot = (draw@ev)/sampled_den-1.5
    corrected_boot = 5*context['raw'][0]+(draw@residual)/sampled_den-1.5
    native = run.read(OUT/'candidate-values.json')
    base = run.read(OUT/'balanced-values.json')
    bb = next(r for r in native['rows'] if r['path'] == [2])
    baseline = next(r for r in base['rows'] if r['path'] == [2])
    records = []
    for k, hand in enumerate(bb['hands']):
        assert hand['class_index'] == k
        v = hand['action_values_counterfactual_bb']; prediction = (v[1]-v[0])/-v[0]
        vbase = baseline['hands'][k]['action_values_counterfactual_bb']
        balanced = (vbase[1]-vbase[0])/-vbase[0]
        frequency = hand['average_probabilities'][1]
        raw_ci = np.quantile(raw_boot[:, k], [.025, .975])
        cv_ci = np.quantile(corrected_boot[:, k], [.025, .975])
        support_ok = frequency >= .0001
        quality_ok = convergence[k] <= .025
        conclusion = 'uncertain_or_no_clear_sign_disagreement'
        if not support_ok: conclusion = 'sparse_call_support'
        elif not quality_ok: conclusion = 'postflop_hand_unsettled'
        elif prediction > .05 and max(raw_ci[1], cv_ci[1]) < -.05:
            conclusion = 'clear_model_call_reference_fold'
        elif prediction < -.05 and min(raw_ci[0], cv_ci[0]) > .05:
            conclusion = 'clear_model_fold_reference_call'
        records.append(dict(hand=run.pilot.LABELS[k], class_index=k,
            source_action_frequencies=hand['average_probabilities'], call_frequency=frequency,
            candidate_advantage_bb=prediction, balanced_advantage_bb=balanced,
            direct_advantage_bb=float(raw_advantage[k]), corrected_advantage_bb=float(corrected_advantage[k]),
            direct_95_interval=raw_ci.tolist(), corrected_95_interval=cv_ci.tolist(),
            postflop_br_gain_bb=float(convergence[k]), adequate_call_support=bool(support_ok),
            reference_hand_settled=bool(quality_ok), decision=conclusion,
            sampled_boards_with_observations=int((den[:, k] > 0).sum()),
            reference_pair_weight=float(total[k]/total.sum())))
    w = context['mass'][0]
    qualified = np.array([r['adequate_call_support'] and r['reference_hand_settled'] for r in records])
    pred = np.array([r['candidate_advantage_bb'] for r in records])
    balanced = np.array([r['balanced_advantage_bb'] for r in records])
    return dict(records=records, counts=dict(collections.Counter(r['decision'] for r in records)),
                pair_weighted_mae_bb={
                    'candidate_direct': float(w@np.abs(pred-raw_advantage)),
                    'candidate_corrected': float(w@np.abs(pred-corrected_advantage)),
                    'balanced_direct': float(w@np.abs(balanced-raw_advantage)),
                    'balanced_corrected': float(w@np.abs(balanced-corrected_advantage))},
                qualified_call_pair_mass_fraction=float(w@qualified),
                max_gpu_gap_pct=max(r['gpu_gap_pct'] for r in rows),
                max_cpu_gap_pct=max(r['gap_pct'] for r in rows),
                reference_job_seconds=sum(r['seconds'] for r in rows),
                board_count=n, production_enabled=False)


def main():
    m = run.checked(); rows = []
    for job in m['jobs']:
        row = run.read(OUT/'jobs'/(job['id']+'.json')); run.validate(row, job, m); rows.append(row)
    result = summarize(m, rows)
    result.update(manifest_id=m['id'], evaluated_at=run.now(),
        input_hashes_unchanged=True,
        job_sha256={job['id']: run.pilot.sha(OUT/'jobs'/(job['id']+'.json')) for job in m['jobs']},
        caveats=['Local call versus fold audit, not full-game exploitability.',
                 'Fifty-flop stratified estimate; intervals are exploratory, not simultaneous.',
                 'Control variate uses cached approximate preflop equity; its error is not in bootstrap intervals.',
                 'Positive call advantage does not show calling beats raising.',
                 'Sparse or unsettled classes are not reliable per-hand accuracy verdicts.'])
    run.write(OUT/'evaluation.json', result)
    print(json.dumps({k: v for k, v in result.items() if k not in ['records', 'job_sha256']}, indent=2))


if __name__ == '__main__': main()
