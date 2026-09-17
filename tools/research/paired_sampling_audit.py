"""Fixed-model board uncertainty audit and one preregistered panel repeat."""
import argparse
import collections
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.request
import numpy as np
import fit_paired_expansion as fit
from run_paired_expansion import metadata_adapter
import evaluate_shallow_native_feedback as bootstrap

s = fit.study
ROOT = s.ROOT
OUT = s.OUT / 'sampling-audit'
KEYS = ['direct', 'corrected']
CORRECTIONS = {}
s.native.previous.old.validate = metadata_adapter(s.native.previous.old.validate, CORRECTIONS)


def rows_for(name, p):
    rows = {}
    for c in p['contexts']:
        case = c['case']
        if name in ['linear', 'polar']:
            folder = fit.OUT
        elif name == 'shallow':
            folder = s.prior.OUT
        else:
            folder = s.native.previous.prior.OUT if case['id'] == 'call' else s.native.previous.old.OUT
        m = s.read(folder / 'manifest.json')
        jobs = [j for j in m['jobs'] if (name == 'original' and case['id'] == 'call') or j['case'] == case['id']]
        rows[case['id']] = [s.read(folder / 'jobs' / (j['id'] + '.json')) for j in jobs]
    return rows


def panel_draws(rows, seed):
    first = next(iter(rows.values()))
    boards = [r['job'] for r in first]
    for rr in rows.values():
        assert [r['job']['board'] for r in rr] == [b['board'] for b in boards], 'Contexts must share a paired board panel'
    return bootstrap.bootstrap(dict(boards=boards, bootstrap_seed=seed, bootstrap_replicates=5000))


def sample_targets(p, rows, draws):
    """Resample the whole board, retaining covariance between connected leaves."""
    targets = {k: np.broadcast_to(p['base_delta'], (len(draws), 169)).copy() for k in KEYS}
    contributions = {k: [] for k in KEYS}
    for c in p['contexts']:
        case = c['case']
        mass, ev, residual, _ = s.native.fit.arrays(case, rows[case['id']])
        den = draws @ mass[:, 0]
        assert (den > 0).all(), 'A sampled hand has no compatible board support'
        sampled = dict(direct=case['pot'] * (draws @ ev[:, 0]) / den,
                       corrected=case['pot'] * (c['raw'][0] + (draws @ residual[:, 0]) / den))
        term = p['terms'][case['node']]
        coef = term['coefficient'] * (1 if term['action'] == 2 else -1)
        for key in KEYS:
            value = coef * (sampled[key] - p['info'][case['node']]['gross'])
            targets[key] += value
            contributions[key].append(value)
    return targets, contributions


def fixed_prediction(p, model):
    delta = p['base_delta'].copy()
    for c in p['contexts']:
        case = c['case']; term = p['terms'][case['node']]
        delta += (1 if term['action'] == 2 else -1) * term['coefficient'] * case['pot'] * (fit.prediction(c, model)[0] - c['base'][0])
    return delta


def interval(x):
    return np.quantile(x, [.025, .975], axis=0)


def summarize(p, targets, parts, pred, weight=None):
    w = p['mass'] * p['qualified'] if weight is None else np.array(weight)
    w = w / w.sum()
    result = {}
    for key in KEYS:
        truth = p['reference_delta'][key]; samples = targets[key]
        se = samples.std(axis=0, ddof=1); ci = interval(samples)
        base_error = abs(p['base_delta'] - truth) @ w
        candidate_error = abs(pred - truth) @ w
        result[key] = dict(baseline_mae_bb=float(base_error), rejected_control_mae_bb=float(candidate_error),
            weighted_target_se_bb=float(se @ w), weighted_target_95_width_bb=float((ci[1] - ci[0]) @ w),
            baseline_mae_bootstrap_interval_bb=interval(abs(samples - p['base_delta']) @ w).tolist(),
            control_mae_reduction_bb=float(base_error - candidate_error),
            control_mae_reduction_bootstrap_interval_bb=interval((abs(samples - p['base_delta']) - abs(samples - pred)) @ w).tolist(),
            branch_contribution_se_bb={c['case']['branch'] if 'branch' in c['case'] else c['case']['id']: float(v.std(axis=0, ddof=1) @ w) for c, v in zip(p['contexts'], parts[key])},
            unpaired_quadrature_se_bb=float(np.sqrt(sum(v.var(axis=0, ddof=1) for v in parts[key])) @ w),
            hands=[dict(hand=h, weight=float(w[k]), target_bb=float(truth[k]), se_bb=float(se[k]),
                        percentile_95_interval_bb=ci[:, k].tolist()) for k, h in enumerate(s.pilot.LABELS)])
    return result


def audit():
    OUT.mkdir(exist_ok=True)
    assert not (OUT / 'audit.json').exists(), 'Preserve the completed audit'
    fs, inputs = fit.families()
    screen = s.read(fit.OUT / 'training-screen.json')
    choice = min(screen['scores'], key=lambda r: r['mean_action_mae_bb'])
    models = {}; results = {}
    for index, (name, p) in enumerate(fs):
        model = dict(encoder=choice['encoder'], coefficients=(choice['shrink'] * fit.fit(
            [q for other, q in fs if other != name], choice['encoder'], choice['penalty'], choice['action_weight'])).tolist())
        models[name] = model
        rows = rows_for(name, p); draws = panel_draws(rows, 2026091710 + index)
        targets, parts = sample_targets(p, rows, draws)
        # Unit resampling must recover the existing point estimator exactly.
        point, _ = sample_targets(p, rows, np.ones((1, draws.shape[1])))
        for key in KEYS: np.testing.assert_allclose(point[key][0], p['reference_delta'][key], atol=1e-10)
        result = summarize(p, targets, parts, fixed_prediction(p, model))
        result.update(boards=draws.shape[1], qualified_mass=float(p['mass'] @ p['qualified']), qualified_classes=int(p['qualified'].sum()))
        results[name] = result
        print(name, {key: {k: v for k, v in result[key].items() if k != 'hands'} for key in KEYS}, flush=True)
    selected = max(['linear', 'polar'], key=lambda n: results[n]['corrected']['weighted_target_se_bb'])
    s.write(OUT / 'fixed-controls.json', dict(models=models, selection='Previously rejected best-mean screen choice, diagnostic control only; no new model search',
        screen_sha256=s.pilot.sha(fit.OUT / 'training-screen.json'), parameters={k: choice[k] for k in ['encoder', 'penalty', 'action_weight', 'shrink']}, production_enabled=False))
    s.write(OUT / 'audit.json', dict(completed_at=s.now(), families=results, selected_repeat_family=selected,
        selection_rule='Of the two ten-board families, largest qualified-mass-weighted adjusted target bootstrap SE; repeat all three linked contexts',
        inputs=inputs, production_enabled=False, metadata_roundtrips=CORRECTIONS))
    print('Repeat selected:', selected, flush=True)


def prepare():
    assert not (OUT / 'manifest.json').exists(), 'Preserve registered repeat'
    a = s.read(OUT / 'audit.json'); old = fit.expansion.checked(); family = a['selected_repeat_family']
    # A fresh full-population draw: no outcome-based seed search or exclusions.
    seed = 'paired-sampling-independent-panel-v1'
    boards = s.native.previous.panel(seed, 10)
    cases = [c for c in old['cases'] if c['family'] == family]
    jobs = []
    for c in cases:
        template = next(j['config'] for j in old['jobs'] if j['case'] == c['id'])
        for b in boards:
            jobs.append(dict(**b, id=c['id'] + '-' + b['board'], case=c['id'], config=dict(template, board=b['board'])))
    paths = [OUT / p for p in ['PROTOCOL.md', 'audit.json', 'fixed-controls.json']]
    paths += [s.native.previous.prior.REFERENCE, fit.OUT / 'manifest.json', ROOT / old['trees'][family]]
    paths += [Path(mod.__file__) for mod in list(sys.modules.values()) if getattr(mod, '__file__', None) and Path(mod.__file__).parent == ROOT / 'tools/research']
    inputs = dict(a['inputs'])
    inputs.update({p.relative_to(ROOT).as_posix(): s.pilot.sha(p) for p in paths})
    m = dict(registered_at=s.now(), family=family, cases=cases, jobs=jobs, boards=boards,
        tree=old['trees'][family], board_seed=seed, bootstrap_seed=2026091720, bootstrap_replicates=5000,
        overlap_with_old_panel=sorted({b['board'] for b in boards} & {b['board'] for b in old['boards']}),
        inputs=inputs, target_gap_pct=.1, max_iterations=2000, production_enabled=False)
    m['id'] = hashlib.sha256(json.dumps(m, sort_keys=True).encode()).hexdigest()
    s.write(OUT / 'manifest.json', m)
    print('Registered', family, len(jobs), 'references; old board overlap:', m['overlap_with_old_panel'], flush=True)


def checked():
    m = s.read(OUT / 'manifest.json')
    assert hashlib.sha256(json.dumps({k: v for k, v in m.items() if k != 'id'}, sort_keys=True).encode()).hexdigest() == m['id']
    for p, h in m['inputs'].items(): assert s.pilot.sha(ROOT / p) == h, p
    return m


def idle():
    s.native.previous.prior.idle()
    with urllib.request.urlopen('http://localhost:56708/api/reports/status', timeout=10) as response:
        report = json.load(response)
    assert not report.get('running', False), 'Report running; defer GPU research'
    assert report.get('state', '') not in ['running', 'solving'], 'Report running; defer GPU research'


def run():
    m = checked(); env = dict(os.environ)
    env['PATH'] = str(ROOT / '.cuda-nvrtc/nvidia/cuda_nvrtc/bin') + os.pathsep + env.get('PATH', '')
    try:
        for i, j in enumerate(m['jobs']):
            path = OUT / 'jobs' / (j['id'] + '.json')
            if not path.exists():
                while True:
                    try:
                        idle(); break
                    except (AssertionError, OSError) as error:
                        s.write(OUT / 'status.json', dict(stage='waiting_for_idle_app', completed=i, total=len(m['jobs']), reason=str(error), updated=s.now()))
                        time.sleep(30)
                s.write(OUT / 'status.json', dict(stage='references', completed=i, total=len(m['jobs']), active=j['id'], updated=s.now()))
                with (OUT / (j['id'] + '.log')).open('w', encoding='utf-8') as log:
                    subprocess.run([str(s.native.previous.prior.REFERENCE), str(OUT / 'manifest.json'), '1'],
                        cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            s.native.previous.old.validate(s.read(path), j, m)
            print(i + 1, '/', len(m['jobs']), j['id'], flush=True)
        evaluate()
    except Exception as error:
        s.write(OUT / 'status.json', dict(stage='failed', error=str(error), updated=s.now()))
        raise


def evaluate():
    m = checked(); rows = collections.defaultdict(list); hashes = {}; labels = []
    for j in m['jobs']:
        path = OUT / 'jobs' / (j['id'] + '.json'); row = s.read(path)
        s.native.previous.old.validate(row, j, m); rows[j['case']].append(row); labels.append(row)
        hashes[j['id']] = s.pilot.sha(path)
    fs, _ = fit.families(); old_p = dict(fs)[m['family']]
    p = s.model.pack(s.read(ROOT / m['tree']), m['cases'], rows)
    model = s.read(OUT / 'fixed-controls.json')['models'][m['family']]
    pred = fixed_prediction(p, model)
    np.testing.assert_allclose(pred, fixed_prediction(old_p, model), atol=1e-10)
    w = old_p['mass'] * old_p['qualified']; w /= w.sum()
    targets, parts = sample_targets(p, rows, panel_draws(rows, m['bootstrap_seed']))
    old_rows = rows_for(m['family'], old_p)
    old_targets, _ = sample_targets(old_p, old_rows, panel_draws(old_rows, m['bootstrap_seed'] + 1))
    result = summarize(p, targets, parts, pred, w)
    for key in KEYS:
        shift = p['reference_delta'][key] - old_p['reference_delta'][key]
        delta_boot = targets[key] - old_targets[key]
        lo, hi = interval(delta_boot)
        result[key].update(panel_shift_weighted_absolute_bb=float(abs(shift) @ w),
            panel_shift_signed_bb=float(shift @ w), panel_shift_signed_bootstrap_interval_bb=interval(delta_boot @ w).tolist(),
            mass_with_pointwise_shift_interval_excluding_zero=float(w @ ((lo > 0) | (hi < 0))),
            mass_with_baseline_outside_pointwise_target_interval=float(w @ ((p['base_delta'] < interval(targets[key])[0]) | (p['base_delta'] > interval(targets[key])[1]))))
    evaluation = dict(completed_at=s.now(), manifest_id=m['id'], family=m['family'], results=result,
        labels=len(labels), label_sha256=hashes, max_cpu_gap_pct=max(r['gap_pct'] for r in labels),
        max_gpu_gap_pct=max(r['gpu_gap_pct'] for r in labels), solver_seconds=sum(r['seconds'] for r in labels),
        old_qualified_mass=float(old_p['mass'] @ old_p['qualified']), new_qualified_mass=float(p['mass'] @ p['qualified']),
        old_qualified_mass_failing_new_gain_limit=float((old_p['mass'] * old_p['qualified'] * ~p['qualified']).sum()),
        frozen_control_sha256=s.pilot.sha(OUT / 'fixed-controls.json'), metadata_roundtrips=CORRECTIONS, production_enabled=False)
    s.write(OUT / 'evaluation.json', evaluation)
    report(m, evaluation)
    checked()
    s.write(OUT / 'status.json', dict(stage='complete', completed=len(labels), total=len(labels), updated=s.now()))
    print('Completed independent panel; production unchanged.', flush=True)


def report(m, evaluation):
    old = s.read(OUT / 'audit.json')['families'][m['family']]
    new = evaluation['results']; adj = new['corrected']
    lo, hi = adj['control_mae_reduction_bootstrap_interval_bb']
    direction = ('The fixed rejected correction still has unresolved direction on the fresh panel.' if lo <= 0 <= hi else
                 'The fixed rejected correction is worse on the fresh panel.' if hi < 0 else
                 'The fixed rejected correction improves this fresh-panel target; it remains a rejected development control, not a deployable model.')
    lines = ['# Board-sampling audit and independent repeat', '',
        '**Production unchanged. The earlier model screen remains failed.**', '',
        f'All {evaluation["labels"]} fresh reference solves passed. Maximum CPU/GPU gaps were '
        f'{evaluation["max_cpu_gap_pct"]:.5f}% / {evaluation["max_gpu_gap_pct"]:.5f}% pot. '
        f'Recorded solver time: {evaluation["solver_seconds"]/60:.1f} minutes, excluding process overhead and pauses.', '',
        f'The original audit selected the {m["family"]} family because it had the larger adjusted '
        'target standard error among the two ten-board families. The repeat used 50 independently '
        'sampled boards shared across all three branches. Ranges, action menus, models and accuracy limits stayed fixed.', '',
        '| Adjusted action metric | Original 10 boards | Fresh 50 boards |',
        '|---|---:|---:|']
    for title, key in [('Weighted target standard error', 'weighted_target_se_bb'),
                       ('Mean pointwise 95% target interval width', 'weighted_target_95_width_bb'),
                       ('Unchanged baseline MAE', 'baseline_mae_bb'),
                       ('Fixed rejected control MAE', 'rejected_control_mae_bb')]:
        lines.append(f'| {title} | {old["corrected"][key]:.4f}bb | {adj[key]:.4f}bb |')
    lines += ['', direction, '',
        f'Fresh-panel adjusted MAE reduction is {adj["control_mae_reduction_bb"]:.4f}bb; '
        f'its conditional bootstrap interval is [{lo:.4f}, {hi:.4f}]bb. Positive means less error. '
        'This interval holds coefficients fixed and excludes model-selection uncertainty.', '',
        f'The action targets moved by {adj["panel_shift_weighted_absolute_bb"]:.4f}bb in weighted absolute terms '
        'between panels. That shift must not be interpreted as the fraction of model error caused by sampling.', '',
        f'Original qualified decision mass: {evaluation["old_qualified_mass"]:.1%}. '
        f'Fresh qualification: {evaluation["new_qualified_mass"]:.1%}. '
        f'Original mass failing the fresh per-hand BR limit: {evaluation["old_qualified_mass_failing_new_gain_limit"]:.1%}. '
        'Comparison weights retain the original mask.', '',
        f'Incidental old/new board overlap: {len(m["overlap_with_old_panel"])}. '
        'Both panels sample the full canonical population; neither excludes old boards.', '',
        '## Limits and next decision', '',
        'These are approximate stratified bootstrap intervals, especially for the old panel with '
        'only two boards per stratum. There is no finite-population correction. They describe board '
        'sampling, not solver bias, postflop abstraction or uncertainty about other ranges and stacks. '
        'Pointwise coverage summaries are not simultaneous significance tests.', '',
        'The repeat is complete and stops here. Inspect the direct estimator and adjusted estimator '
        'together in evaluation.json before choosing another model design. A remaining systematic '
        'error would motivate explicit interactions between both ranges; more sampling alone does '
        'not repair that error. Do not tune on this repeat and present it as independent validation.', '',
        'See PROTOCOL.md, audit.json, fixed-controls.json, manifest.json and evaluation.json for '
        'the frozen design, complete hand-level results and hashes.', '']
    (OUT / 'REPORT.md').write_text('\n'.join(lines), encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('command', choices=['audit', 'prepare', 'run', 'evaluate'])
    globals()[parser.parse_args().command]()
