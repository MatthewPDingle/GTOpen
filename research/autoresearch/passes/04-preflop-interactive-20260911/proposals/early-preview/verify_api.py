"""Explicit later-only isolated preview API qualification. Never writes to live56708."""
import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import threading
import time
import urllib.error
import urllib.request

HERE = Path(__file__).resolve().parent
PASS = HERE.parents[1]
ROOT = PASS.parents[3]
LAB = ROOT / 'target/autoresearch/preflop-interactive-20260911'
OLD = PASS.parent / '03-preflop-20260910'
spec = importlib.util.spec_from_file_location('preview_prior_guard', OLD / 'proposals/final-api-qualification/qualify_api.py')
q = importlib.util.module_from_spec(spec)
spec.loader.exec_module(q)
DEADLINE = dt.datetime.fromisoformat('2026-09-11T02:53:27+00:00')
CASES = ('reference-control', 'reference-preview', 'fast-preview', 'small-api')
REFERENCE = 'coupled_deck_v1'
FAST = 'coupled_preview64_v1'
SOURCES = ('crates/server/src/main.rs', 'crates/server/src/preflop_preview_tests.rs',
           'crates/solver/src/preflop/mod.rs', 'crates/solver/src/preflop/gpu.rs',
           'crates/solver/src/preflop/multiway.rs', 'web/js/preflop_preview.js')


def config3(config):
    return dict(config, positions=['BTN', 'SB', 'BB'], posts=[0, 0.5, 1], stack=20,
                open_raises=[2.5], raise_mults=[3], max_raises=2, add_allin=False,
                call_only_seats=[], open_raises_by_seat=None, raise_mults_by_seat=None, limp=True)


def equity_cache_record(path):
    path = Path(path)
    q.require(path.stat().st_size == 4 + 169*169*4, 'malformed equity cache size')
    with path.open('rb') as stream:
        header = stream.read(4)
    samples = int.from_bytes(header, 'little')
    q.require(samples > 0, 'equity cache has zero samples')
    return {'sha256': q.sha(path), 'samples': samples,
            'header_sha256': hashlib.sha256(header).hexdigest()}


def fixed_environment(samples):
    q.require(isinstance(samples, int) and samples > 0, 'positive frozen sample count required')
    return dict(q.FIXED_ENV, PREFLOP_EQ_SAMPLES=str(samples))


def environment(private, port, samples):
    env = os.environ.copy()
    for key in list(env):
        if key.startswith(('PREFLOP_MW_', 'PREFLOP_GPU_', 'PREFLOP_PHASE_')):
            del env[key]
    env.update(fixed_environment(samples))
    env.update(PORT=str(port), REALIZATION_FIT=str(private / 'cache/realization_fit.json'))
    env['PATH'] = str(ROOT / '.cuda-nvrtc/nvidia/cuda_nvrtc/bin') + os.pathsep + env.get('PATH', '')
    return env


def publication(value, model):
    p = value['publication']
    q.require(p['multiway_model'] == model, 'publication model mismatch')
    q.require(p['published_iteration'] >= 2, 'uniform/unpublished strategy is not usable')
    a = p['accuracy_iteration']
    q.require(a is None or a <= p['published_iteration'], 'accuracy newer than published strategy')
    q.require(not p['converged'] or a == p['published_iteration'], 'stale convergence claim')
    return p


def blind_action(view):
    """Frozen path rule: fold nonblinds; blinds prefer free/passive then smallest raise.

    Only positive-frequency actions are traversed; no zero-reach invented line.
    """
    rows = [(i, a) for i, a in enumerate(view['actions']) if a['freq'] > 0]
    if view['actor_pos'] not in ('SB', 'BB'):
        return next((i for i, a in rows if a['kind'] == 'fold'), None)
    passive = [(i, a) for i, a in rows if a['kind'] in ('check', 'call', 'limp')]
    if passive:
        return passive[0][0]
    raises = [(i, a) for i, a in rows if a['kind'] == 'raise']
    return min(raises, key=lambda row: (row[1]['to'], row[0]))[0] if raises else None


def compare_reference(a, b):
    q.require(a['completed'] and b['completed'], 'reference cases incomplete')
    q.require(a['native'] == b['native'], 'reference preview changed native metadata or full arenas')
    fields = ('iteration', 'published_iteration', 'accuracy_iteration', 'gaps', 'evs',
              'gap_total', 'target_gap', 'stop_reason', 'multiway_equity_model')
    for field in fields:
        q.require(a['final_status'][field] == b['final_status'][field], 'checkpoint mismatch: ' + field)
    return {'native_header_and_all_arena_sha_exact': True,
            'checkpoint_fields_exact': list(fields),
            'excluded_status_fields': 'wall elapsed, progress/phase text and transient diagnostics; native has no elapsed fields'}


def run_case(case, protocol, folder):
    private = folder / case
    (private / 'saves/preflop').mkdir(parents=True)
    (private / 'cache').mkdir()
    for source, dest, digest in [(protocol['exe'], private / 'gto-server.exe', protocol['binary_sha256']),
                                 (protocol['input'], private / 'saves/preflop/input.gtop', protocol['input_sha256'])]:
        shutil.copy2(source, dest)
        q.require(q.sha(dest) == digest, 'copied executable/input changed')
    for name, row in protocol['caches'].items():
        shutil.copy2(row['path'], private / 'cache' / name)
        q.require(q.sha(private / 'cache' / name) == row['sha256'], 'cache copy changed')
    port = q.free_port()
    q.live_idle()
    q.require(dt.datetime.now(dt.timezone.utc) < DEADLINE, 'deadline before launch')
    started = time.monotonic()
    result = {'case': case, 'port': port, 'completed': False, 'raw': [], 'statuses': []}
    stop, failures = threading.Event(), []
    cap = 240 if case == 'small-api' else 600
    with (private / 'server.log').open('x', encoding='utf-8') as log:
        process = subprocess.Popen([str(private / 'gto-server.exe')], cwd=private,
            env=environment(private, port, protocol['caches']['preflop_eq169.bin']['samples']), stdout=log, stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NO_WINDOW)
        (PASS / 'active.json').write_text(json.dumps({'running': True, 'event': 'preview_api',
            'id': folder.name + '-' + case, 'pid': process.pid, 'port': port,
            'exe': str(private / 'gto-server.exe'), 'log': str(private / 'server.log')}), encoding='utf-8')

        def guard():
            while not stop.wait(0.5):
                try:
                    q.live_idle()
                    q.require(dt.datetime.now(dt.timezone.utc) < DEADLINE, 'global deadline')
                    q.require(time.monotonic() - started < cap, 'private case timeout')
                except Exception as error:
                    failures.append(str(error))
                    if process.poll() is None:
                        process.kill()  # Retained child only; never discover/kill a live PID.
                    return
        thread = threading.Thread(target=guard, daemon=True)
        thread.start()
        expected = None

        def own():
            q.require(not failures and process.poll() is None, 'owned server stopped: ' + '; '.join(failures))
            actual = q.owner(port)
            q.require(actual['pid'] == process.pid and actual['sha256'] == protocol['binary_sha256'], 'wrong listener')
            q.require(Path(actual['exe']).samefile(private / 'gto-server.exe'), 'wrong executable path')
            if expected:
                q.require(actual['created'] == expected['created'], 'listener identity changed')
            return actual

        def post(route, body, error_expected=False):
            base = route.split('?', 1)[0]
            q.require(port != 56708 and base in ['/api/preflop/' + s for s in
                ('load', 'save', 'solve', 'stop', 'node', 'export', 'spot')], 'POST forbidden')
            own()
            request = urllib.request.Request(f'http://127.0.0.1:{port}{route}', json.dumps(body).encode(),
                                             headers={'Content-Type': 'application/json'})
            begin = time.monotonic()
            try:
                with urllib.request.urlopen(request, timeout=cap) as response:
                    code, value = response.status, json.load(response)
            except urllib.error.HTTPError as error:
                code, value = error.code, error.read().decode('utf-8')
            end = time.monotonic()
            result['raw'].append({'route': route, 'body': body, 'http': code, 'response': value,
                                  'case_seconds': end-started, 'request_seconds': end-begin})
            q.require((400 <= code < 500) if error_expected else code == 200,
                      f'unexpected HTTP {code}: {route}: {str(value)[:200]}')
            return value, begin, end

        def save(name):
            value, _, _ = post('/api/preflop/save', {'name': name})
            q.require(value.get('ok') is True, 'native save refused')
            path = private / 'saves/preflop' / (name + '.gtop')
            return path, q.native(path)

        def verify_caches(stage):
            actual = {name: (equity_cache_record(private/'cache'/name) if name == 'preflop_eq169.bin'
                            else {'sha256':q.sha(private/'cache'/name)}) for name in protocol['caches']}
            result['cache_'+stage] = actual  # Retain actual header/hash even on rejection.
            for name, row in actual.items():
                q.require(all(row[k] == protocol['caches'][name][k] for k in row), 'private cache changed at '+stage+': '+name)

        def roundtrip(name, expected_native, model):
            post('/api/preflop/load', {'name': name})
            session = q.get(port, '/api/preflop/session')
            result['raw'].append({'route': '/api/preflop/session', 'response': session})
            q.require(session['multiway_equity_model'] == model, 'reload changed model')
            q.require(session['publication']['published_iteration'] == expected_native['header']['iteration'], 'reload publication tag wrong')
            q.require(session['publication']['accuracy_iteration'] is None and not session['publication']['converged'], 'reload invented accuracy')
            _, reread = save(name + '-roundtrip')
            q.require(reread == expected_native, 'reload changed native header or arena bits')
            return session

        def navigate(t0, model):
            path = []
            for _ in range(18):
                view, _, served = post('/api/preflop/node', {'path': path})
                p = publication(view, model)
                if not path and 'first_root_seconds' not in result:
                    q.require(view.get('strategy') is not None and not view.get('strategy_note'), 'published root unusable')
                    result.update(first_root_seconds=served-t0, first_root_publication=p)
                if view.get('strategy_note'):
                    return {'available': False, 'path': path, 'reason': view['strategy_note']}
                if view['exportable']:
                    exported, _, end = post('/api/preflop/export', {'path': path})
                    ep = publication(exported, model)
                    return {'available': True, 'path': path, 'seconds': end-t0, 'publication': ep}
                if view['kind'] != 'action':
                    return {'available': False, 'path': path, 'reason': 'non-exportable terminal'}
                action = blind_action(view)
                if action is None:
                    return {'available': False, 'path': path, 'reason': 'frozen navigation rule has no positive action'}
                path.append(action)
            return {'available': False, 'path': path, 'reason': '18-node navigation bound'}

        try:
            while expected is None:
                q.require(process.poll() is None and not failures, 'startup failed')
                try:
                    candidate = own()
                    if q.get(port, '/api/status')['state'] == 'idle':
                        expected = candidate
                except (OSError, ValueError):
                    pass
                q.require(time.monotonic() - started < 60, 'startup timeout')
                time.sleep(0.2)
            result['owner'] = expected
            caps = q.get(port, '/api/preflop/capabilities')
            result['capabilities'] = caps
            q.require(caps.get('early_preview_v1') is True and FAST in caps['fresh_build_multiway_models'], 'candidate missing capabilities')
            model = FAST if case in ('fast-preview', 'small-api') else REFERENCE
            if model == REFERENCE:
                loaded, _, _ = post('/api/preflop/load', {'name': 'input'})
                q.require(loaded['config'] == protocol['initial']['header']['config'], 'loaded config changed')
            else:
                cfg = config3(protocol['initial']['header']['config']) if case == 'small-api' else protocol['initial']['header']['config']
                post('/api/preflop/spot?multiway_model=' + model, cfg)
            verify_caches('after_load_or_build')
            _, initial = save('loaded-input')
            if case != 'small-api':
                expected_initial = json.loads(json.dumps(protocol['initial']))
                expected_initial['header']['multiway_equity_model'] = model
                q.require(initial == expected_initial, 'initial native state differs beyond selected model')
            else:
                q.require(initial['header']['config'] == cfg and initial['header']['iteration'] == 0, 'small fresh state wrong')
            q.require(initial['header']['multiway_equity_model'] == model, 'native model identity wrong')
            q.require(all(a['sha256'] == q.zero_hash(a['elements']) for a in initial['arrays']), 'initial arenas not zero')
            if case == 'small-api':
                before = q.get(port, '/api/preflop/session')
                for query in ('multiway_model=unknown', 'multiway_model=coupled_deck_v1&unknown=1',
                              'multiway_model=coupled_deck_v1&multiway_model=coupled_preview64_v1'):
                    post('/api/preflop/spot?' + query, cfg, error_expected=True)
                    q.require(q.get(port, '/api/preflop/session') == before, 'invalid query mutated session')
                _, after = save('after-invalid')
                q.require(after == initial, 'invalid query changed native session')
                result['invalid_queries_preserved_session'] = True
            solve = {'iterations': 100000 if case == 'small-api' else protocol['iterations'],
                     'target_gap': 0 if case == 'small-api' else 0.005,
                     'check_every': 50, 'early_preview': case != 'reference-control'}
            _, t0, ack = post('/api/preflop/solve', solve)
            result['ack_seconds'] = ack-t0
            previous, observed = t0, set()
            while True:
                q.require(not failures and process.poll() is None, 'solve interrupted')
                poll_begin = time.monotonic()
                status = q.get(port, '/api/preflop/status')
                now = time.monotonic()
                result['statuses'].append({'seconds': now-t0, 'status': status})
                q.require(not status.get('error') and not status.get('gpu_note') and not status.get('preview_note'), 'solver failure/fallback')
                published = status['published_iteration']
                if published >= 2 and 'first_published_seconds' not in result:
                    result.update(first_published_seconds=now-t0, first_publication_interval=[previous-t0, now-t0],
                                  first_published_status=status)
                    q.require(status['gpu'] is True, 'CPU fallback')
                    if case == 'small-api':
                        post('/api/preflop/save', {'name': 'forbidden-running'}, error_expected=True)
                        q.require(not (private / 'saves/preflop/forbidden-running.gtop').exists(), 'running save wrote a file')
                        q.require(not (private / 'saves/preflop/forbidden-running.gtop.tmp').exists(), 'running save wrote a temporary file')
                        post('/api/preflop/stop', {})
                        result['stop_requested_seconds'] = time.monotonic()-t0
                if case != 'small-api' and published >= 2 and published not in observed and not result.get('first_export', {}).get('available'):
                    observed.add(published)
                    attempt = navigate(t0, model)
                    result.setdefault('export_attempts', []).append(attempt)
                    if attempt['available']:
                        result['first_export'] = attempt
                if status['state'] != 'running':
                    q.require(status['state'] in ('done', 'stopped'), 'unexpected final state')
                    break
                previous = poll_begin
                time.sleep(0.2)
            result['final_status'] = status
            q.require(status['published_iteration'] == status['iteration'], 'final publication/native counter mismatch')
            if case != 'small-api':
                q.require(status['iteration'] == protocol['iterations'] and status['accuracy_iteration'] == protocol['iterations'], 'final checkpoint missing')
            else:
                q.require('stop_requested_seconds' in result and status['state'] == 'stopped', 'small case did not pause')
            output, final = save('paused' if case == 'small-api' else 'result')
            q.require(final['header'] == dict(initial['header'], iteration=status['iteration']), 'native metadata changed')
            result.update(output=str(output), native=final, output_sha256=q.sha(output))
            result['reload_session'] = roundtrip(output.stem, final, model)
            verify_caches('after_roundtrip')
            result.update(completed=True, case_seconds=time.monotonic()-started)
        except Exception as error:
            result['error'] = str(error)
        finally:
            stop.set()
            thread.join(timeout=10)
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=30)
            try:
                verify_caches('end')
            except Exception as error:
                result.update(completed=False, cache_error=str(error))
            result['guard_failures'] = failures
            q.write_new(private / 'result.json', result)
            (PASS / 'active.json').write_text(json.dumps({'running': False, 'last': folder.name+'-'+case}), encoding='utf-8')
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--id', required=True)
    parser.add_argument('--exe', type=Path, required=True)
    parser.add_argument('--sha256', required=True)
    parser.add_argument('--binary-source-ref', required=True, help='Declared build provenance; current source hashes are recorded separately')
    parser.add_argument('--iterations', type=int, default=50)
    parser.add_argument('--cases', nargs='+', choices=CASES, default=list(CASES))
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    q.require(args.execute and os.name == 'nt', 'explicit --execute on Windows required')
    q.require(re.fullmatch(r'[a-z0-9][a-z0-9-]{2,90}', args.id), 'unsafe run ID')
    q.require(args.iterations >= 50 and args.iterations % 50 == 0, 'iterations must be a positive50 multiple')
    q.require(len(args.cases) == len(set(args.cases)), 'duplicate cases')
    q.require(q.sha(args.exe) == args.sha256, 'candidate binary SHA mismatch')
    q.live_idle()
    old = json.loads((OLD / 'build-owned-confirm-a-protocol.json').read_text(encoding='utf-8'))
    source = Path(old['pairs'][0]['baseline']['output'])
    baseline = json.loads((PASS / 'baseline-eight-50-a-protocol.json').read_text(encoding='utf-8'))
    input_sha = q.sha(source)
    q.require(source.samefile(baseline['case']['input']) and input_sha == baseline['case']['input_sha256'], 'input differs from frozen pass04 baseline')
    initial = q.native(source)
    q.require(initial['header']['iteration'] == 0 and len(initial['header']['config']['positions']) == 8, 'wrong frozen fixture')
    q.require(initial['header']['multiway_equity_model'] == REFERENCE, 'wrong frozen payoff model')
    q.require(initial['header']['seat_profiles'] == [None]*8 and initial['header']['seat_frozen'] == [False]*8
              and initial['header']['hero'] is None and not initial['header']['point_locks'], 'fixture is not the all-solver control')
    caps = sum(240 if c == 'small-api' else 600 for c in args.cases) + 120
    q.require((DEADLINE-dt.datetime.now(dt.timezone.utc)).total_seconds() >= caps, 'insufficient bounded qualification time')
    folder = LAB / 'target/interactive-api' / args.id
    q.require(not folder.exists(), 'run ID already exists')
    q.require(shutil.disk_usage(LAB).free > source.stat().st_size * (4*len(args.cases)+1) + 2_000_000_000, 'insufficient unique snapshot reserve')
    protocol = {'id': args.id, 'exe': str(args.exe.resolve()), 'binary_sha256': args.sha256,
        'declared_binary_source_ref': args.binary_source_ref, 'runner_sha256': q.sha(Path(__file__)),
        'guard_sha256': q.sha(Path(q.__file__)), 'native_guard_sha256': q.sha(OLD/'proposals/final-deployment/session_guard.py'),
        'current_worktree_source_sha256': {p:q.sha(LAB/p) for p in SOURCES if (LAB/p).exists()},
        'input': str(source), 'input_sha256': input_sha, 'input_manifest_sha256': q.sha(OLD/'build-owned-confirm-a-protocol.json'),
        'baseline_protocol_sha256': q.sha(PASS/'baseline-eight-50-a-protocol.json'),
        'initial': initial, 'iterations': args.iterations, 'cases': args.cases,
        'deadline': DEADLINE.isoformat(), 'per_case_seconds': {'large':600,'small-api':240},
        'caches': {name:{'path':str(ROOT/'cache'/name),'sha256':q.sha(ROOT/'cache'/name)}
                   for name in ('preflop_eq169.bin','realization_fit.json')},
        'navigation': 'positive frequency only; nonblind fold, blind passive else smallest nonjam raise;18node limit',
        'quality_scope': 'Intermediate strategy/API availability only; no accuracy against the reference game claimed'}
    for name, row in protocol['caches'].items():
        q.require(row['sha256'] == baseline['caches'][name]['sha256'], 'cache changed since frozen baseline: '+name)
    protocol['caches']['preflop_eq169.bin'].update(equity_cache_record(ROOT/'cache/preflop_eq169.bin'))
    protocol['environment'] = fixed_environment(protocol['caches']['preflop_eq169.bin']['samples'])
    protocol['cache_policy'] = 'Frozen source header determines sample count; full file/header SHA verified after load/build and at end; no implicit cache rebuild accepted'
    q.write_new(HERE / (args.id+'-protocol.json'), protocol)  # Frozen before any child launch.
    folder.mkdir(parents=True)
    summary = {'id': args.id, 'results': {}, 'reference_parity': None, 'passed': False}
    try:
        for case in args.cases:
            result = run_case(case, protocol, folder)
            summary['results'][case] = {k:v for k,v in result.items() if k not in ('raw','statuses','reload_session')}
            q.require(result['completed'] and not result['guard_failures'], f'{case} failed: {result.get("error")}')
        if all(c in summary['results'] for c in CASES[:2]):
            summary['reference_parity'] = compare_reference(*(summary['results'][c] for c in CASES[:2]))
        summary['passed'] = True
    except Exception as error:
        summary['error'] = str(error)
    finally:
        q.write_new(HERE / (args.id+'-summary.json'), summary)
    print(json.dumps({'id': args.id, 'passed': summary['passed'], 'error': summary.get('error')}))
    return 0 if summary['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
