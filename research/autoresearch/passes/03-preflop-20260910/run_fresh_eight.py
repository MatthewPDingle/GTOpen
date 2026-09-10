"""Frozen fresh-state qualification of the accepted optimization; no code changes."""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
from measure import HERE, LAB, live_busy


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def rows(run):
    return [json.loads(line[len('CONVERGENCE '):]) for line in (HERE/'raw'/f'{run}.log').read_text().splitlines()
            if line.startswith('CONVERGENCE ')]


if live_busy():
    raise SystemExit('User workload active')
extended = json.loads((HERE/'extended-convergence-protocol.json').read_text())
build = json.loads((HERE/'build-owned-confirm-a-protocol.json').read_text())
fixture = Path(build['pairs'][0]['baseline']['output'])
with fixture.open('rb') as stream:
    magic, header = stream.readline(), json.loads(stream.readline())
if header['iteration'] != 0 or header.get('hero') is not None:
    raise SystemExit('Fresh fixture must be native iteration zero, no hero')
executables = {}
for variant in ['original', 'compatible']:
    run = extended['runs'][f'extended-convergence-eight-{variant}-a']
    # The protocol's command is represented by executable and input fields.
    executables[variant] = {k: v for k, v in run.items() if 'executable' in k or k == 'compiled_source'}
for value in executables.values():
    if sha(value['executable']) != value['executable_sha256']:
        raise SystemExit('Frozen executable changed')
cache_hashes = {}
for name in ['preflop_eq169.bin', 'realization_fit.json']:
    path = LAB/'cache'/name
    expected = build['inputs_sha256'][str(path)]
    if sha(path) != expected:
        raise SystemExit('Frozen cache changed: ' + name)
    cache_hashes[str(path)] = expected
spec = {
    'purpose': 'Qualify fresh eight-seat time to first checkpoint and fixed-work performance; no new implementation',
    'fixture': str(fixture), 'fixture_sha256': sha(fixture), 'start_iteration': 0,
    'executables': executables, 'cache_hashes': cache_hashes, 'budget_mb': 23000,
    'additional_iterations': 20, 'check_every': 10, 'target_gap_bb': .005,
    'interpretation': 'Fixed 20-iteration work and first 10-iteration checkpoint; not a fresh-game convergence claim',
    'pair_orders': [['original', 'compatible'], ['compatible', 'original'], ['original', 'compatible']],
    'per_run_timeout_seconds': 600, 'stop_before_utc': '2026-09-10T21:29:18+00:00',
    'quality_gate': 'All checkpoint values and full native states exact; preserve interruptions/misses',
}
protocol_path = HERE/'fresh-eight-protocol.json'
mode = sys.argv[1] if len(sys.argv) == 2 else ''
if mode == 'prepare':
    with protocol_path.open('x', encoding='utf8') as stream:
        json.dump({'frozen_utc': dt.datetime.now(dt.timezone.utc).isoformat(), **spec}, stream, indent=2)
    print('Frozen fresh-eight-protocol.json; no hardware run started.')
    raise SystemExit(0)
if mode != 'run':
    raise SystemExit('Use prepare or run')
frozen = json.loads(protocol_path.read_text())
if any(frozen[k] != v for k, v in spec.items()):
    raise SystemExit('Protocol/input changed since freeze')
stop_before = dt.datetime.fromisoformat(spec['stop_before_utc'])
env = os.environ.copy()
env['REALIZATION_FIT'] = str(LAB/'cache/realization_fit.json')
for key in list(env):
    if key.startswith(('PREFLOP_MW_', 'PREFLOP_GPU_', 'PREFLOP_PHASE_')):
        env.pop(key)
results = []
for number, order in enumerate(spec['pair_orders'], 1):
    ids, outputs = {}, {}
    for variant in order:
        if (stop_before-dt.datetime.now(dt.timezone.utc)).total_seconds() < 660:
            raise SystemExit('Insufficient frozen time reserve; retain completed runs')
        ident = f'fresh-eight-{number}-{variant}-a'
        ids[variant] = ident
        outputs[variant] = LAB/'target/research-convergence'/f'{ident}.gtop'
        subprocess.run([sys.executable, str(HERE/'run_guarded.py'), ident,
                        executables[variant]['executable'], str(fixture), '23000', '20', '.005', '10',
                        str(outputs[variant])], env=env, check=True)
    data = {v: rows(ids[v]) for v in ids}
    final = {v: next(r for r in data[v] if r['phase'] == 'result') for v in ids}
    checkpoints = {v: [r for r in data[v] if r['phase'] == 'checkpoint'] for v in ids}
    if any([r['done'] for r in points] != [10, 20] for points in checkpoints.values()):
        raise SystemExit('Unexpected checkpoint sequence')
    for left, right in zip(checkpoints['original'], checkpoints['compatible']):
        for key in ['iteration', 'done', 'gaps', 'evs', 'live_seats', 'learning_gap_bb', 'target_gap_bb', 'target_reached']:
            if left[key] != right[key]:
                raise SystemExit('Fresh checkpoint mismatch: ' + key)
    for key in ['start_iteration', 'done', 'iteration', 'gaps', 'evs', 'learning_gap_bb', 'arena_fnv1a64', 'status', 'converged']:
        if final['original'][key] != final['compatible'][key]:
            raise SystemExit('Fresh final mismatch: ' + key)
    native_id = f'fresh-eight-native-{number}-a'
    subprocess.run([sys.executable, str(HERE/'run_guarded.py'), native_id,
                    str(LAB/'target/release/examples/preflop_compare_saved.exe'), str(outputs['original']),
                    str(outputs['compatible']), str(LAB/'cache/preflop_eq169.bin')], check=True)
    subprocess.run([sys.executable, str(HERE/'assert_saved_exact.py'), native_id], check=True)
    timings = {}
    for variant in ids:
        first = checkpoints[variant][0]
        init = next(r['ms'] for r in data[variant] if r['phase'] == 'gpu_init')
        load = next(r['load_input_ms'] for r in data[variant] if r['phase'] == 'manifest')
        first_ms = first['iterations_ms_total']+first['checks_ms_total']+first['syncs_ms_total']
        timings[variant] = {'gpu_init_ms': init, 'load_ms': load, 'first_checkpoint_solver_ms': first_ms,
                            'load_init_first_checkpoint_ms': load+init+first_ms,
                            'fixed_work_ms': final[variant]['trajectory_ms']}
    results.append({'pair': number, 'order': order, 'timings': timings, 'final': final['compatible'],
                    'exact_checkpoints_and_native': True,
                    'reduction_percent': 100*(1-timings['compatible']['fixed_work_ms']/timings['original']['fixed_work_ms'])})
    (HERE/'fresh-eight-comparisons.json').write_text(json.dumps(results, indent=2)+'\n')
    print(json.dumps({'pair': number, 'exact': True, 'reduction_percent': results[-1]['reduction_percent']}))
print(json.dumps({'completed_pairs': len(results), 'median_paired_reduction_percent': statistics.median(r['reduction_percent'] for r in results)}))
