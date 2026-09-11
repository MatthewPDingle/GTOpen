"""Opt-in, owned, <=300-second UI sandbox. No automatic solve; no live writes."""
import argparse
import datetime as dt
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import threading
import time
import urllib.request
import uuid

spec = importlib.util.spec_from_file_location('ui_preview_api', Path(__file__).with_name('verify_api.py'))
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
q = v.q
AREA = v.LAB / 'target/interactive-ui'


def bounded_path(path, root):
    path, root = Path(path).resolve(), Path(root).resolve()
    q.require(path != root and path.is_relative_to(root), 'path outside private research root')
    return path


def check_owner(actual, process, port, exe, digest, expected=None):
    q.require(port != 56708 and process.poll() is None, 'private child is unavailable')
    q.require(actual['pid'] == process.pid and actual['sha256'] == digest, 'wrong private listener')
    q.require(Path(actual['exe']).resolve() == Path(exe).resolve(), 'wrong private executable path')
    if expected is not None:
        q.require(actual['created'] == expected['created'], 'private listener identity changed')
    return actual


def guard_reason(now, started, cap, stop_path, live_check):
    if now - started >= cap:
        return 'timeout'
    if stop_path.exists():
        return 'owner_stop_file'
    if dt.datetime.now(dt.timezone.utc) >= v.DEADLINE:
        return 'research_deadline'
    try:
        live_check()  # Read-only; uncertainty also stops the owned child.
    except Exception as error:
        return 'live_guard: ' + str(error)
    return None


def request_stop(owner_path, token):
    owner_path = bounded_path(owner_path, AREA)
    row = json.loads(owner_path.read_text(encoding='utf-8'))
    q.require(row['token'] == token and row['port'] != 56708, 'owner token/port mismatch')
    stop_path = bounded_path(row['stop_file'], owner_path.parent)
    q.require(stop_path.name == 'stop-' + token, 'unexpected stop filename')
    stop_path.touch(exist_ok=True)  # No process discovery, kill, or network request.


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stop-owner', type=Path)
    parser.add_argument('--token')
    parser.add_argument('--id')
    parser.add_argument('--exe', type=Path)
    parser.add_argument('--sha256')
    parser.add_argument('--binary-source-ref')
    parser.add_argument('--input', type=Path)
    parser.add_argument('--input-sha256')
    parser.add_argument('--seconds', type=int, default=300)
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--production-reference-only', action='store_true')
    args = parser.parse_args()
    if args.stop_owner:
        q.require(args.token, '--token required')
        request_stop(args.stop_owner, args.token)
        return 0
    q.require(args.execute and os.name == 'nt', 'explicit --execute on Windows required')
    q.require(args.id and re.fullmatch(r'[a-z0-9][a-z0-9-]{2,90}', args.id), 'unsafe run ID')
    q.require(1 <= args.seconds <= 300, 'lifetime must be 1..300 seconds')
    q.require(args.binary_source_ref and args.exe and args.input, 'source, executable and input required')
    source_root = v.source_worktree(args.production_reference_only)
    # Explicit binary SHA remains authoritative even if parent used the lab's
    # shared target directory to build the separately recorded production source.
    exe_root = source_root if Path(args.exe).resolve().is_relative_to((source_root/'target').resolve()) else v.LAB
    exe = bounded_path(args.exe, exe_root / 'target')
    source = bounded_path(args.input, v.LAB / 'target')
    q.require(exe.name == 'gto-server.exe' and q.sha(exe) == args.sha256, 'candidate path/SHA mismatch')
    q.require(source.stat().st_size <= 140*1024*1024, 'small fixture file cap exceeded')
    q.require(q.sha(source) == args.input_sha256, 'small fixture SHA mismatch')
    initial = q.native(source)
    header = initial['header']
    q.require(initial['magic'] == 'GTOPREFLOP2' and header['iteration'] == 0, 'fresh preflop native required')
    q.require(len(header['config']['positions']) == 3, 'three-seat UI fixture required')
    q.require(header['seat_profiles'] == [None]*3 and header['seat_frozen'] == [False]*3
              and header['hero'] is None and not header['point_locks'], 'all-solver fixture required')
    allowed_models = (v.REFERENCE,) if args.production_reference_only else (v.REFERENCE, v.FAST)
    q.require(header['multiway_equity_model'] in allowed_models, 'unsupported fixture model')
    baseline = json.loads((v.PASS/'baseline-eight-50-a-protocol.json').read_text(encoding='utf-8'))
    caches = {}
    for name in ('preflop_eq169.bin', 'realization_fit.json'):
        cache = v.ROOT/'cache'/name
        row = {'path': str(cache), 'sha256': q.sha(cache)}
        q.require(row['sha256'] == baseline['caches'][name]['sha256'], 'frozen cache changed')
        if name == 'preflop_eq169.bin':
            row.update(v.equity_cache_record(cache))
            q.require(row['samples'] == 20000, 'expected frozen 20000-sample cache')
        caches[name] = row
    q.live_idle()
    q.require(dt.datetime.now(dt.timezone.utc) < v.DEADLINE, 'research deadline passed')
    private = bounded_path(AREA/args.id, AREA)
    q.require(not private.exists(), 'private run ID already exists')
    (private/'saves/preflop').mkdir(parents=True)
    (private/'cache').mkdir()
    for src, dest, digest in [(exe, private/'gto-server.exe', args.sha256),
                               (source, private/'saves/preflop/input.gtop', args.input_sha256)]:
        shutil.copy2(src, dest)
        q.require(q.sha(dest) == digest, 'private copy changed')
    for name, row in caches.items():
        shutil.copy2(row['path'], private/'cache'/name)
        q.require(q.sha(private/'cache'/name) == row['sha256'], 'cache copy changed')
    provenance = v.source_record(args.production_reference_only)
    web = Path(provenance['web_source'])
    web_hashes = provenance['web_sha256']
    shutil.copytree(web, private/'web')
    q.require(all(q.sha(private/'web'/p) == sha for p, sha in web_hashes.items()), 'web copy changed')
    protocol = {'scope': 'manual UI smoke only; no accuracy or performance qualification',
        'id': args.id, 'binary_source_ref_declared': args.binary_source_ref,
        'exe': str(exe), 'binary_sha256': args.sha256, 'input': str(source),
        'input_sha256': args.input_sha256, 'initial': initial, 'caches': caches,
        'production_reference_only': args.production_reference_only, **provenance,
        'source_sha256': provenance['current_worktree_source_sha256'],
        'harness_sha256': q.sha(Path(__file__)), 'api_helper_sha256': q.sha(Path(v.__file__)),
        'guard_sha256': q.sha(Path(q.__file__)), 'environment': v.fixed_environment(20000),
        'lifetime_seconds': args.seconds, 'deadline': v.DEADLINE.isoformat(),
        'automatic_mutations': ['/api/preflop/load'], 'automatic_solves': False}
    q.write_new(private/'protocol.json', protocol)
    port, token = q.free_port(), uuid.uuid4().hex
    stop_path = private/('stop-' + token)
    stopped, reasons = threading.Event(), []
    started = time.monotonic()
    with (private/'server.log').open('x', encoding='utf-8') as log:
        process = subprocess.Popen([str(private/'gto-server.exe')], cwd=private,
            env=v.environment(private, port, 20000), stdout=log, stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NO_WINDOW)

        def guard():
            while not stopped.wait(.5):
                reason = guard_reason(time.monotonic(), started, args.seconds, stop_path, q.live_idle)
                if reason:
                    reasons.append(reason)
                    if process.poll() is None:
                        process.kill()  # Retained child handle only, never an externally supplied PID.
                    return
        thread = threading.Thread(target=guard, daemon=True)
        thread.start()
        expected = None
        ready = False
        error = None
        try:
            while expected is None:
                q.require(not reasons and process.poll() is None, 'owned server stopped')
                try:
                    actual = check_owner(q.owner(port), process, port, private/'gto-server.exe', args.sha256)
                    if q.get(port, '/api/status')['state'] == 'idle':
                        expected = actual
                except (OSError, ValueError):
                    pass
                q.require(time.monotonic()-started < min(60, args.seconds), 'startup timeout')
                time.sleep(.2)
            caps = q.get(port, '/api/preflop/capabilities')
            if args.production_reference_only:
                v.validate_capabilities(caps, True)
            else:
                q.require(caps.get('early_preview_v1') is True, 'missing preview capability')
            check_owner(q.owner(port), process, port, private/'gto-server.exe', args.sha256, expected)
            request = urllib.request.Request(f'http://127.0.0.1:{port}/api/preflop/load',
                json.dumps({'name':'input'}).encode(), headers={'Content-Type':'application/json'})
            with urllib.request.urlopen(request, timeout=30) as response:
                loaded = json.load(response)
            q.require(loaded['iteration'] == 0 and loaded['config'] == header['config'], 'wrong loaded fixture')
            q.require(loaded['multiway_equity_model'] == header['multiway_equity_model'], 'loaded model changed')
            q.require(q.get(port, '/api/preflop/status')['state'] != 'running', 'unexpected automatic solve')
            owner = {'ready': True, 'pid': process.pid, 'port': port, 'url': f'http://127.0.0.1:{port}',
                'owner': expected, 'token': token, 'stop_file': str(stop_path),
                'owner_json': str(private/'owner.json'), 'protocol': str(private/'protocol.json'),
                'remaining_seconds': max(0, args.seconds-(time.monotonic()-started))}
            q.write_new(private/'owner.json', owner)
            print(json.dumps(owner), flush=True)
            ready = True
            while process.poll() is None and not reasons:
                # Independent clock/owner-stop check even while live HTTP guard is blocked.
                if time.monotonic()-started >= args.seconds or stop_path.exists():
                    reasons.append('owner_stop_file' if stop_path.exists() else 'timeout')
                    process.kill()
                    break
                time.sleep(.2)
        except Exception as exc:
            error = str(exc)
        finally:
            stopped.set()
            if process.poll() is None:
                process.kill()
            process.wait(timeout=10)
            thread.join(timeout=20)
            final_caches = {name:q.sha(private/'cache'/name) for name in caches}
            unchanged = all(final_caches[name] == row['sha256'] for name,row in caches.items())
            q.write_new(private/'result.json', {'ready': ready, 'error': error, 'stop_reasons': reasons,
                'elapsed_seconds': time.monotonic()-started, 'owned_child_exit': process.returncode,
                'cache_sha256_after': final_caches, 'frozen_caches_unchanged': unchanged,
                'not_a_solve_quality_gate': True})
    return 0 if ready and error is None and unchanged else 1


if __name__ == '__main__':
    raise SystemExit(main())
