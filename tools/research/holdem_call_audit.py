"""Frozen heads-up call/fold value audit. Uses offline reference executables only."""
import argparse
import collections
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import urllib.request
import numpy as np
import range_value_pilot as pilot
import continuation_nonlinear_residual as network

ROOT = pilot.ROOT
BASE = ROOT/'research/preflop-evolution/continuation'
OUT = BASE/'holdem-call-audit-20260917'
SNAPSHOT = BASE/'heads-up-settling-20260916/40/candidate/1500/iteration-1500.json'
SAVE = SNAPSHOT.with_name('policy.gtop')
MODEL = BASE/'shrunk-residual-20260916/candidate.json'
REFERENCE = ROOT/'target/range-value-reference-night2.exe'
PROBES = ['KQo', 'KJo', 'QJo', 'JTo', 'A5s', 'A9o', 'T9s', '98s', '76s', '22']


def read(path): return json.loads(path.read_text(encoding='utf-8'))
def write(path, data): path.write_text(json.dumps(data, indent=2, allow_nan=False)+'\n', encoding='utf-8', newline='\n')
def now(): return dt.datetime.now(dt.timezone.utc).isoformat()


def idle():
    state = {}
    for part, url in [('preflop', '/api/preflop/status'), ('postflop', '/api/status')]:
        with urllib.request.urlopen('http://localhost:56708'+url, timeout=10) as response:
            state[part] = json.load(response)
        assert state[part]['state'] in ['', 'idle', 'done', 'stopped'], 'Live app busy; defer new reference jobs'
    return state


def prepare():
    assert not (OUT/'manifest.json').exists(), 'Preserve registered study'
    snapshot = read(SNAPSHOT)
    assert snapshot['config']['stack'] == 40 and snapshot['config']['rake_pct'] == 0
    leaf, = snapshot['leaves']
    assert leaf['path'] == [2, 1] and leaf['pot'] == 5 and leaf['stack'] == 37.5
    assert leaf['positions'] == ['BB', 'SB']
    weights = np.array(leaf['weights'])
    # Preserve all positive support, including rare classes, using nine significant digits.
    texts = [','.join(f'{pilot.LABELS[h]}:{v:.9g}' for h, v in enumerate(row) if v > 0) for row in weights]
    parsed = np.array([pilot.weights(t) for t in texts])
    assert np.max(np.abs(parsed-weights)) < 1e-9
    case = dict(id='hu40-candidate-bb-call', pot=5., stack=37.5, weights=weights.tolist(),
                range_oop=texts[0], range_ip=texts[1], positions=['BB', 'SB'])
    counts, eq = pilot.matrices()
    context = pilot.context(case, counts, eq)
    context.update(case=case, base_x=context['x'].copy(), base_names=list(context['names']))
    prediction = network.predict(context, read(MODEL))*5-1.5
    native = read(OUT/'candidate-values.json')
    bb = next(r for r in native['rows'] if r['path'] == [2])
    assert bb['actor'] == 1 and len(bb['hands']) == 169
    native_advantage = []
    for h in bb['hands']:
        values = h['action_values_counterfactual_bb']
        assert values[0] < 0
        # Fold loses the already posted 1bb. Its CF value is minus the compatible
        # opponent reach factor. The call-minus-fold difference cancels that factor.
        native_advantage.append((values[1]-values[0])/-values[0])
    native_advantage = np.array(native_advantage)
    max_error = float(np.max(np.abs(prediction[0]-native_advantage)))
    assert max_error < 2e-5, max_error
    reference_prior = read(BASE/'shrunk-residual-20260916/prospective/manifest.json')
    assert pilot.sha(REFERENCE) == reference_prior['binary_sha256']
    pool = read(pilot.AUDIT/'fixtures.json')['canonical_flops']
    groups = collections.defaultdict(list)
    for board, iso in pool:
        cards = [board[i:i+2] for i in range(0, 6, 2)]
        key = ('paired' if len({c[0] for c in cards}) < 3 else 'unpaired')+'/'+str(len({c[1] for c in cards}))+'suits'
        groups[key].append((board, iso))
    boards = []
    for key, items in sorted(groups.items()):
        items.sort(key=lambda item: hashlib.sha256(('holdem-call-audit-20260917'+item[0]).encode()).digest())
        for board, iso in items[:10]:
            boards.append(dict(board=board, iso_weight=iso, stratum=key, inclusion_probability=10/len(items)))
    assert len(boards) == 50 and len(pool) == 1755
    size = {'bet': [{'PotPct': 50}], 'raise': [{'PotPct': 100}], 'donk': [{'PotPct': 50}]}
    tree = dict(starting_pot=5., effective_stack=37.5, rake_pct=0., rake_cap=0.,
                oop=[size]*3, ip=[size]*3, max_raises=1, add_allin=False, allin_threshold=.85)
    jobs = [dict(**board, id='bb-call-'+board['board'], case=case['id'],
                config=dict(board=board['board'], range_oop=texts[0], range_ip=texts[1], tree=tree)) for board in boards]
    paths = [Path(__file__), OUT/'PROTOCOL.md', SNAPSHOT, SAVE, MODEL,
             OUT/'candidate-values.json', OUT/'balanced-values.json',
             BASE/'full-precision-20260916/double/interface.cu',
             REFERENCE, ROOT/'target/learned-interface-filtered/release/examples/learned_interface.exe',
             ROOT/'crates/solver/examples/range_value_reference.rs',
             ROOT/'crates/solver/examples/learned_interface.rs',
             ROOT/'tools/research/range_value_pilot.py', ROOT/'tools/research/continuation_nonlinear_residual.py',
             ROOT/'tools/research/continuation_overnight_fit.py', ROOT/'cache/preflop_eq169.bin',
             ROOT/'cache/realization_fit.json', pilot.AUDIT/'fixtures.json']
    data = dict(registered_at=now(), case=case, boards=boards, jobs=jobs, target_gap_pct=.1,
                max_iterations=2000, probes=PROBES, bootstrap_replicates=5000, bootstrap_seed=20260917,
                inputs={p.relative_to(ROOT).as_posix(): pilot.sha(p) for p in paths}, production_enabled=False)
    data['id'] = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
    write(OUT/'manifest.json', data)
    write(OUT/'preflight.json', dict(max_native_python_call_value_error_bb=max_error,
        native_call_advantage_bb=native_advantage.tolist(), python_call_advantage_bb=prediction[0].tolist(),
        live_app=idle(), source_save_sha256=pilot.sha(SAVE), reference_binary_sha256=pilot.sha(REFERENCE),
        production_enabled=False))
    print('Registered 50 boards; native/Python error', max_error, flush=True)


def checked():
    m = read(OUT/'manifest.json')
    assert hashlib.sha256(json.dumps({k: v for k, v in m.items() if k != 'id'}, sort_keys=True).encode()).hexdigest() == m['id']
    for p, digest in m['inputs'].items(): assert pilot.sha(ROOT/p) == digest, p
    return m


def validate(result, job, m):
    assert result['manifest_id'] == m['id'] and result['job'] == job
    assert result['target_met'], (job['id'], result['gap_pct'], result['gpu_gap_pct'])
    assert 0 <= result['gap_pct'] <= .1 and 0 <= result['gpu_gap_pct'] <= .1
    assert result['query_mode'] == 'materialized_full_enumeration'
    assert abs(sum(result['means_bb'])-5) < .002
    for hands in result['hands']:
        assert all(np.isfinite([h['pair_mass'], h['ev_bb'], h['equity'], h['br_ev_bb']]).all() for h in hands)
        assert abs(sum(h['pair_mass'] for h in hands)/result['pair_mass']-1) < 1e-5


def run():
    m = checked()
    env = dict(os.environ); env['PATH'] = str(ROOT/'.cuda-nvrtc/nvidia/cuda_nvrtc/bin')+os.pathsep+env.get('PATH', '')
    start = time.perf_counter()
    for i, job in enumerate(m['jobs']):
        path = OUT/'jobs'/(job['id']+'.json')
        if not path.exists():
            idle()
            write(OUT/'status.json', dict(stage='references', completed=i, total=50, active=job['id'], updated=now()))
            with (OUT/(job['id']+'.log')).open('w', encoding='utf-8', newline='\n') as log:
                subprocess.run([str(REFERENCE), str(OUT/'manifest.json'), '1'], cwd=ROOT, env=env,
                               stdout=log, stderr=subprocess.STDOUT, check=True)
        validate(read(path), job, m)
        print('reference', i+1, '/ 50', job['board'], 'elapsed', round(time.perf_counter()-start), flush=True)
    checked()
    write(OUT/'status.json', dict(stage='references_complete', completed=50, total=50, updated=now()))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('command', choices=['prepare', 'run'])
    {'prepare': prepare, 'run': run}[parser.parse_args().command]()
