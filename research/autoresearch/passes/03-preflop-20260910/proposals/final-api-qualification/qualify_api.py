"""Later-only isolated API checkpoint latency qualification; no live mutation."""
import argparse
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys
import threading
import time
import urllib.request

HERE = Path(__file__).resolve().parents[2]
ROOT = HERE.parents[3]
LAB = ROOT / 'target/autoresearch/preflop-20260910'
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'final-deployment'))
from session_guard import native, sha, write_new, require, owner

DEADLINE = dt.datetime.fromisoformat('2026-09-10T21:29:18+00:00')
ORIGINAL = ROOT / 'target/research-deployment/Before preflop deployment 20260911-054159-f22e270e/previous-gto-server.exe'
CANDIDATE = ROOT / 'target/desktop-runtime/release/gto-server.exe'
HASHES = {'original': '9c095b6e654867dd0965366a7443442c2f65db906b384759cfe9424a3c8070be',
          'candidate': '7e96cde87bb87ee6dbdd693e010275851eb4d1cc6b4d2bcb550c4ef89173bb6d'}
MIN_PAIR_REMAINING_SECONDS = 1260
FIXED_ENV = {'SOLVER_THREADS': '16', 'RAYON_NUM_THREADS': '16', 'SOLVER_GPU': '1',
             'SOLVER_GPU_MEM_MB': '23000', 'PREFLOP_EQ_SAMPLES': '1024'}
SOLVE = {'iterations': 50, 'target_gap': 0.005}  # Intentionally omit check_every: exercise default50.


def require_pair_time(now):
    require((DEADLINE - now).total_seconds() >= MIN_PAIR_REMAINING_SECONDS,
            'need at least1260 seconds before deadline for two600second cases and comparator')


def get(port, route):
    with urllib.request.urlopen(f'http://127.0.0.1:{port}{route}', timeout=5) as response:
        return json.load(response)


def live_idle():
    require(get(56708, '/api/status')['state'] != 'running', 'live postflop started')
    require(get(56708, '/api/preflop/status')['state'] != 'running', 'live preflop started')
    require(get(56708, '/api/reports/status').get('running') is False, 'live report started')


def free_port():
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    require(port != 56708, 'live port forbidden')
    return port


def checkpoint(status):
    return (status.get('iteration') == 50 and status.get('phase') != 'measuring'
            and len(status.get('gaps', [])) == 8 and len(status.get('evs', [])) == 8)


def zero_hash(elements):
    digest = hashlib.sha256()
    zeros = bytes(1024 * 1024)
    remaining = elements * 4
    while remaining:
        n = min(remaining, len(zeros))
        digest.update(zeros[:n])
        remaining -= n
    return digest.hexdigest()


def strict_comparator(result):
    require(result['headers_identical_after_point_lock_order_canonicalization'], 'native header mismatch')
    require(result['all_compared_values_finite'], 'nonfinite compared values')
    require(result['invalid_effective_entries'] == result['invalid_reach_classes'] == 0, 'invalid policies/reaches')
    require(result['iteration'] == 50 and result['payoff_model'] == 'coupled_deck_v1', 'wrong comparison state')
    stats = [*result['raw_arenas'].values(), result['effective_average_strategy'], result['raw_arena_normalized_strategy']]
    for row in stats:
        require(row['entries'] == row['bit_equal'] == row['finite_pairs'] and row['max_abs'] == row['max_ulp'] == 0,
                'full native effective/raw strategy mismatch')


def run_case(case, input_native, folder, caches):
    private = folder / case['side']
    (private / 'saves/preflop').mkdir(parents=True)
    (private / 'cache').mkdir()
    shutil.copy2(case['exe'], private / 'gto-server.exe')
    require(sha(private / 'gto-server.exe') == case['sha256'], 'copied executable changed')
    shutil.copy2(case['input'], private / 'saves/preflop/input.gtop')
    require(sha(private / 'saves/preflop/input.gtop') == case['input_sha256'], 'input copy changed')
    for name, item in caches.items():
        shutil.copy2(item['path'], private / 'cache' / name)
        require(sha(private / 'cache' / name) == item['sha256'], 'cache copy changed')
    env = os.environ.copy()
    for key in list(env):
        if key.startswith(('PREFLOP_MW_', 'PREFLOP_GPU_', 'PREFLOP_PHASE_')):
            env.pop(key)
    env.update(FIXED_ENV)
    env.update(PORT=str(case['port']), REALIZATION_FIT=str(private / 'cache/realization_fit.json'))
    env['PATH'] = str(ROOT / '.cuda-nvrtc/nvidia/cuda_nvrtc/bin') + os.pathsep + env['PATH']
    live_idle()
    if case['side'] == 'original':
        require_pair_time(dt.datetime.now(dt.timezone.utc))  # Recheck after hashing/copying.
    require(dt.datetime.now(dt.timezone.utc) < DEADLINE, 'deadline before server launch')
    started = time.monotonic()
    result = {'case': case, 'statuses': [], 'completed': False, 'error': None}
    stop = threading.Event()
    failure = []
    with (private / 'server.log').open('x', encoding='utf-8') as log:
        process = subprocess.Popen([str(private / 'gto-server.exe')], cwd=private, env=env,
                                   stdout=log, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
        (HERE/'active.json').write_text(json.dumps({'running': True, 'event': 'api_qualification',
            'id': folder.name+'-'+case['side'], 'pid': process.pid, 'port': case['port'],
            'exe': str(private/'gto-server.exe'), 'log': str(private/'server.log')}), encoding='utf-8')
        def monitor():
            while not stop.wait(0.5):
                try:
                    live_idle()
                    require(dt.datetime.now(dt.timezone.utc) < DEADLINE, 'global deadline')
                    require(time.monotonic() - started < 600, 'case600second deadline')
                except Exception as error:
                    failure.append(str(error))
                    if process.poll() is None:
                        process.kill()  # Only this retained child handle, never the live app.
                    return
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
        expected = None
        def own():
            require(not failure and process.poll() is None, 'owned server stopped: ' + '; '.join(failure))
            actual = owner(case['port'])
            require(actual['pid'] == process.pid and actual['sha256'] == case['sha256'], 'wrong isolated listener')
            if expected is not None:
                require(actual['created'] == expected['created'] and Path(actual['exe']).samefile(expected['exe']), 'listener identity changed')
            return actual
        def post(route, body):
            require(case['port'] != 56708 and route in ['/api/preflop/load', '/api/preflop/solve', '/api/preflop/node', '/api/preflop/save'], 'POST forbidden')
            own()
            request = urllib.request.Request(f'http://127.0.0.1:{case["port"]}{route}',
                json.dumps(body).encode(), headers={'Content-Type': 'application/json'})
            before = time.monotonic()
            with urllib.request.urlopen(request, timeout=600) as response:
                value = json.load(response)
            return value, before, time.monotonic()
        try:
            while True:
                require(not failure and process.poll() is None, 'startup failed: ' + '; '.join(failure))
                try:
                    expected = own()
                    if get(case['port'], '/api/status')['state'] == 'idle':
                        break
                except (OSError, ValueError):
                    pass
                require(time.monotonic() - started < 60, 'startup timeout')
                time.sleep(0.2)
            result['owner'] = expected
            loaded, _, _ = post('/api/preflop/load', {'name': 'input'})
            require(loaded['iteration'] == 0 and loaded['config'] == input_native['header']['config'], 'load changed starting state')
            require(loaded['multiway_equity_model'] == 'coupled_deck_v1' and all(s['profile'] is None and s['frozen'] is False for s in loaded['seats']), 'wrong models/seats')
            response, t0, ack = post('/api/preflop/solve', SOLVE)
            result.update(solve_response=response, post_ack_seconds=ack-t0)
            last_poll = t0
            while True:
                require(not failure and process.poll() is None, 'solve interrupted: ' + '; '.join(failure))
                poll_started = time.monotonic()
                status = get(case['port'], '/api/preflop/status')
                now = time.monotonic()
                result['statuses'].append({'seconds': now-t0, 'status': status})
                require(not status.get('error') and not status.get('gpu_note'), 'solver error/fallback: ' + str(status))
                if checkpoint(status):
                    result.update(first_published_checkpoint_seconds=now-t0,
                                  publication_interval_lower_seconds=last_poll-t0,
                                  publication_interval_upper_seconds=now-t0,
                                  final_status=status)
                    break
                require(status['state'] == 'running', 'solver ended before qualifying checkpoint')
                last_poll = poll_started
                time.sleep(0.2)
            require(status['gpu'] is True, 'GPU qualification fell back to CPU')
            require(all(math.isfinite(x) for x in status['gaps'] + status['evs']), 'nonfinite checkpoint')
            root, _, served = post('/api/preflop/node', {'path': []})
            result.update(first_strategy_response_seconds=served-t0, root_strategy=root)
            session = get(case['port'], '/api/preflop/session')
            require(session['iteration'] == 50 and session['state'] == 'done', 'final native state not50/done')
            saved, _, _ = post('/api/preflop/save', {'name': 'result'})
            require(saved.get('ok') is True and saved['iteration'] == 50, 'result save failed')
            output = private / 'saves/preflop/result.gtop'
            result_native = native(output)
            expected_header = dict(input_native['header'], iteration=50)
            require(result_native['header'] == expected_header, 'native metadata changed beyond iteration')
            result.update(completed=True, output=str(output), output_sha256=sha(output), native=result_native,
                          case_seconds=time.monotonic()-started)
        except Exception as error:
            result['error'] = str(error)
            raise
        finally:
            stop.set()
            thread.join(timeout=10)
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=30)
            result['guard_failures'] = failure
            write_new(private / 'result.json', result)
            (HERE/'active.json').write_text(json.dumps({'running': False,
                'last': folder.name+'-'+case['side']}), encoding='utf-8')
    require(not failure, 'case guard failed')
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--id', required=True)
    parser.add_argument('--comparator', default=str(LAB / 'target/release/examples/preflop_compare_saved.exe'))
    parser.add_argument('--comparator-sha256', default='155e8f1ee3661d29ab3e8e3e4ee9b33e02b7583e3c28cb5625b7b09702398e89')
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    require(args.execute and os.name == 'nt', 'explicit later --execute on Windows required')
    require(re.fullmatch('[A-Za-z0-9_-]+', args.id), 'unsafe ID')
    require(json.loads((HERE/'active.json').read_text()).get('running') is False, 'research queue active')
    require_pair_time(dt.datetime.now(dt.timezone.utc))
    live_idle()
    source_protocol = HERE / 'build-owned-confirm-a-protocol.json'
    pair = json.loads(source_protocol.read_text())['pairs'][0]
    require(pair['case'] == 'eight-fresh' and pair['mode'] == 'fresh-from-config', 'wrong fresh source pair')
    source = Path(pair['baseline']['output'])
    verified = [json.loads(l[12:]) for l in Path(pair['baseline']['log']).read_text().splitlines() if l.startswith('BUILD_BENCH ') and '"verified"' in l]
    require(len(verified) == 1 and all(a['nonzero_bytes'] == 0 for a in verified[0]['native_arenas']['arrays']), 'source not verified zero arenas')
    initial = native(source)
    require(all(a['sha256'] == zero_hash(a['elements']) for a in initial['arrays']), 'actual source arenas are not zero')
    h = initial['header']
    require(h['iteration'] == 0 and len(h['config']['positions']) == 8 and h['multiway_equity_model'] == 'coupled_deck_v1', 'wrong native fixture')
    require(all(p is None for p in h['seat_profiles']) and not any(h['seat_frozen']) and h['hero'] is None and not h['point_locks'], 'not all-solver fixture')
    comparator = Path(args.comparator).resolve()
    require(sha(comparator) == args.comparator_sha256, 'comparator binary changed')
    folder = LAB / 'target/research-api-qualification' / args.id
    folder.parent.mkdir(parents=True, exist_ok=True)
    require(shutil.disk_usage(folder.parent).free > source.stat().st_size * 5 + 1024**3, 'insufficient disk for private native copies')
    folder.mkdir(exist_ok=False)
    caches = {name: {'path': str(LAB/'cache'/name), 'sha256': sha(LAB/'cache'/name)} for name in ['preflop_eq169.bin', 'realization_fit.json']}
    cases = []
    for side, exe in [('original', ORIGINAL), ('candidate', CANDIDATE)]:
        require(sha(exe) == HASHES[side], 'runtime binary changed: ' + side)
        cases.append({'side': side, 'exe': str(exe), 'sha256': HASHES[side], 'port': free_port(),
                      'input': str(source), 'input_sha256': sha(source)})
    require(cases[0]['port'] != cases[1]['port'], 'choose distinct private ports; retry unused ID')
    require(not (HERE/'raw'/(args.id+'-native-exact.log')).exists(), 'native comparator run ID exists')
    protocol = {'frozen_utc': dt.datetime.now(dt.timezone.utc).isoformat(), 'deadline_utc': DEADLINE.isoformat(),
                'case_timeout_seconds': 600, 'minimum_pair_remaining_seconds': MIN_PAIR_REMAINING_SECONDS,
                'fixed_environment': FIXED_ENV, 'root_response_exclusions': [],
                'root_response_comparison': 'Complete semantic PreflopNodeView JSON, no timing or nondeterministic fields',
                'order': ['original', 'candidate'], 'cases': cases, 'caches': caches,
                'solve_body': SOLVE, 'omitted_check_every_default': 50, 'threads': 16, 'gpu_budget_mb': 23000,
                'source_protocol_sha256': sha(source_protocol), 'comparator': str(comparator), 'comparator_sha256': args.comparator_sha256,
                'runner_sha256': sha(__file__), 'poll_seconds': 0.2, 'live_guard_seconds': 0.5,
                'helper_sha256': {str(p): sha(p) for p in [Path(__file__).resolve().parents[1]/'final-deployment/session_guard.py', HERE/'run_guarded.py', HERE/'assert_saved_exact.py']},
                'candidate_source': 'main184f17a integrated lab4878044', 'original_source': 'archived original runtime SHA pinned above'}
    write_new(folder/'protocol.json', protocol)  # Freeze before any child server launch.
    rows = [run_case(case, initial, folder, caches) for case in cases]
    require(rows[0]['native'] == rows[1]['native'], 'complete native metadata/arena mismatch')
    require(rows[0]['root_strategy'] == rows[1]['root_strategy'], 'root response differs')
    run_id = args.id + '-native-exact'
    env = os.environ.copy()
    env['PREFLOP_VALIDATION_TIMEOUT'] = str(max(1, min(600, int((DEADLINE-dt.datetime.now(dt.timezone.utc)).total_seconds()))))
    require(dt.datetime.now(dt.timezone.utc) < DEADLINE, 'deadline before full comparator')
    subprocess.run([sys.executable, str(HERE/'run_guarded.py'), run_id, str(comparator), rows[0]['output'], rows[1]['output'], caches['preflop_eq169.bin']['path']], env=env, check=True)
    comparison = json.loads((HERE/'raw'/(run_id+'.log')).read_text())
    strict_comparator(comparison)
    subprocess.run([sys.executable, str(HERE/'assert_saved_exact.py'), run_id], check=True)
    write_new(folder/'summary.json', {'full_native_exact': True, 'fixed_pair_only': True,
        'first_checkpoint_seconds': {c['case']['side']: c['first_published_checkpoint_seconds'] for c in rows},
        'first_strategy_response_seconds': {c['case']['side']: c['first_strategy_response_seconds'] for c in rows},
        'native_iteration': 50, 'comparator_run': run_id,
        'interpretation': 'One independent API pair; includes GPU initialization and default50 checkpoint. Poll observations bound publication time; no general speed estimate.'})
    print(str(folder/'summary.json'))


if __name__ == '__main__':
    main()
