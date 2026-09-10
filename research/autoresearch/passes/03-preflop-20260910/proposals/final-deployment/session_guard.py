"""Explicit later backup/smoke and empty-server restore; never stops the live app.

Prepared source only. No solves, builds, stop endpoints, or automatic cutover.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import struct
import subprocess
import time
import urllib.request
import uuid

import psutil

PASS = Path(__file__).resolve().parents[2]
ROOT = PASS.parents[3]
LAB = ROOT / 'target/autoresearch/preflop-20260910'
ENV_KEYS = ['SOLVER_COMPRESS', 'SOLVER_MEM_MB', 'SOLVER_THREADS',
            'RAYON_NUM_THREADS', 'REALIZATION_FIT', 'PREFLOP_MAX_ARENA_MB',
            'SOLVER_GPU', 'SOLVER_GPU_MEM_MB', 'PREFLOP_EQ_SAMPLES']


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def write_new(path, value):
    with Path(path).open('x', encoding='utf-8') as f:
        json.dump(value, f, indent=2)


def api(port, route, body=None):
    # Deliberately tiny mutation allowlist: no solver execution or stop routes.
    if body is not None:
        require(route in ['/api/save', '/api/load', '/api/preflop/save', '/api/preflop/load'], 'route forbidden')
    request = urllib.request.Request(f'http://127.0.0.1:{port}{route}',
                                    None if body is None else json.dumps(body).encode(),
                                    headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(request, timeout=300) as response:
        return json.load(response)


def owner(port):
    pids = {c.pid for c in psutil.net_connections(kind='tcp')
            if c.status == psutil.CONN_LISTEN and c.laddr.port == port}
    require(len(pids) == 1 and None not in pids, 'port must have one identifiable listener')
    p = psutil.Process(pids.pop())
    env = p.environ()
    return {'pid': p.pid, 'created': p.create_time(), 'exe': p.exe(), 'cwd': p.cwd(),
            'sha256': sha(p.exe()), 'environment': {k: env.get(k) for k in ENV_KEYS}}


def check_owner(port, expected):
    actual = owner(port)
    for key in ['pid', 'created', 'exe', 'sha256', 'cwd']:
        require(actual[key] == expected[key], 'server owner changed: ' + key)
    return actual


def queues_clear():
    active = json.loads((PASS / 'active.json').read_text(encoding='utf-8'))
    require(active.get('running') is False, 'research active.json is not explicitly stopped')
    for p in psutil.process_iter(['pid', 'exe', 'cmdline']):
        try:
            exe = p.info['exe']
            require(not exe or not Path(exe).resolve().is_relative_to(LAB.resolve()),
                    'isolated research executable still running')
            commands = ' '.join(p.info['cmdline'] or [])
            require(not any(name in commands for name in ['run_convergence.py', 'run_extended_convergence.py',
                    'sweep_cdf.py', 'run_build_pairs.py']), 'research queue controller still running')
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue


def snapshot(port):
    post = api(port, '/api/status')
    pre_status = api(port, '/api/preflop/status')
    pre = api(port, '/api/preflop/session')
    require(post['state'] in ['done', 'stopped', 'ready'], 'postflop must be built and idle')
    require(pre['state'] in ['done', 'stopped', 'ready'] and pre_status['state'] != 'running', 'preflop must be idle')
    # Reports also launch solves, independently of the two foreground statuses.
    report = api(port, '/api/reports/status')
    require(report.get('running') is False, 'report running or malformed status')
    return {'post': post, 'pre': pre, 'pre_status': pre_status, 'report': report}


def compare_api(before, after):
    for key in ['config', 'iteration', 'seats', 'hero', 'frozen', 'multiway_equity_model', 'nodes', 'action_nodes']:
        require(before['pre'][key] == after['pre'][key], 'preflop session differs: ' + key)
    for key in ['iteration', 'spot_request', 'tree']:
        require(before['post'][key] == after['post'][key], 'postflop status differs: ' + key)


def native(path):
    """Every header field plus SHA256 of every length-prefixed arena byte."""
    with Path(path).open('rb') as f:
        magic = f.readline(32)
        require(magic in [b'GTOPREFLOP1\n', b'GTOPREFLOP2\n', b'GTOSOLVE2\n'], 'unknown native magic')
        line = f.readline(128 * 1024 * 1024)
        require(line.endswith(b'\n'), 'native header missing/too large')
        header = json.loads(line)
        for key in ['point_locks', 'locks', 'lock_labels']:
            if key in header:
                values = header[key]
                require(len({row[0] for row in values}) == len(values), 'duplicate lock id')
                header[key] = sorted(values, key=lambda row: row[0])
        count = 4 if magic == b'GTOSOLVE2\n' or header.get('hero_backup') is not None else 2
        arrays = []
        for index in range(count):
            raw = f.read(8)
            require(len(raw) == 8, 'missing arena length')
            elements = struct.unpack('<Q', raw)[0]
            remaining = elements * 4
            digest = hashlib.sha256()
            while remaining:
                chunk = f.read(min(remaining, 1024 * 1024))
                require(bool(chunk), 'truncated native arena')
                remaining -= len(chunk)
                digest.update(chunk)
            arrays.append({'index': index, 'elements': elements, 'sha256': digest.hexdigest()})
        require(f.read(1) == b'', 'unexpected trailing native bytes')
    return {'magic': magic.decode().strip(), 'header': header, 'arrays': arrays}


def save_pair(port, cwd, label):
    paths = {'pre': Path(cwd) / 'saves/preflop' / (label + '.gtop'),
             'post': Path(cwd) / 'saves' / (label + '.gto')}
    for p in paths.values():
        require(not p.exists() and not Path(str(p) + '.tmp').exists(), 'save path already exists')
    a = api(port, '/api/preflop/save', {'name': label})
    b = api(port, '/api/save', {'name': label})
    require(a.get('ok') is True and b.get('ok') is True, 'save not acknowledged')
    result = {key: {'path': str(path), 'sha256': sha(path), 'native': native(path)} for key, path in paths.items()}
    require(result['pre']['native']['header']['iteration'] == a['iteration'], 'preflop save iteration mismatch')
    return result


def verify_restore(port, cwd, manifest, label):
    before = manifest['snapshot']
    api(port, '/api/preflop/load', {'name': manifest['label']})
    api(port, '/api/load', {'name': manifest['label']})
    after = snapshot(port)
    compare_api(before, after)
    saves = save_pair(port, cwd, label)
    for key in ['pre', 'post']:
        require(saves[key]['native'] == manifest['backups'][key]['native'], 'native header/arena differs: ' + key)
    return {'snapshot': after, 'verification_saves': saves}


def smoke(args):
    require(args.execute and args.queues_complete, 'requires explicit --execute --queues-complete')
    queues_clear()
    candidate = Path(args.candidate).resolve()
    require(sha(candidate) == args.candidate_sha256, 'candidate executable hash mismatch')
    old = owner(args.port)
    require(old['pid'] == args.expected_pid and old['sha256'] == args.expected_old_sha256, 'unexpected old server')
    require(Path(old['cwd']).samefile(ROOT), 'old server cwd differs from expected repository')
    before = snapshot(args.port)
    label = 'Before preflop deployment ' + dt.datetime.now().strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:8]
    folder = ROOT / 'target/research-deployment' / label
    folder.mkdir(parents=True, exist_ok=False)
    rollback_exe = folder / 'previous-gto-server.exe'
    shutil.copy2(old['exe'], rollback_exe)
    require(sha(rollback_exe) == old['sha256'], 'rollback executable copy mismatch')
    check_owner(args.port, old)
    backups = save_pair(args.port, old['cwd'], label)
    compare_api(before, snapshot(args.port))
    manifest = {'created_utc': dt.datetime.now(dt.timezone.utc).isoformat(), 'port': args.port, 'label': label,
                'old_owner': old, 'snapshot': before, 'backups': backups,
                'rollback_executable': str(rollback_exe),
                'candidate': {'path': str(candidate), 'sha256': args.candidate_sha256}, 'cutover_performed': False}
    write_new(folder / 'backup.json', manifest)
    # New private working directory: loading/saving smoke cannot replace live sessions/files.
    private = folder / 'smoke'
    (private / 'saves/preflop').mkdir(parents=True)
    (private / 'cache').mkdir()
    for key, relative in [('pre', 'saves/preflop'), ('post', 'saves')]:
        source = Path(backups[key]['path'])
        shutil.copy2(source, private / relative / source.name)
    for name in ['preflop_eq169.bin', 'realization_fit.json']:
        source = ROOT / 'cache' / name
        if name == 'realization_fit.json' and old['environment']['REALIZATION_FIT']:
            source = Path(old['environment']['REALIZATION_FIT'])
            if not source.is_absolute():
                source = Path(old['cwd']) / source
        require(source.is_file(), 'required pinned cache missing: ' + name)
        shutil.copy2(source, private / 'cache' / name)
    copied = private / 'gto-server.exe'
    shutil.copy2(candidate, copied)
    require(sha(copied) == args.candidate_sha256, 'copied candidate mismatch')
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    env = os.environ.copy()
    for key in list(env):
        if key.startswith('PREFLOP_MW_') or key.startswith('PREFLOP_GPU_') or key.startswith('PREFLOP_PHASE_'):
            env.pop(key)
    for key, value in old['environment'].items():
        if value is None:
            env.pop(key, None)
        else:
            env[key] = value
    env['PORT'] = str(port)
    env['REALIZATION_FIT'] = str(private / 'cache/realization_fit.json')
    env['PATH'] = str(ROOT / '.cuda-nvrtc/nvidia/cuda_nvrtc/bin') + os.pathsep + env['PATH']
    with (private / 'server.log').open('x', encoding='utf-8') as log:
        process = subprocess.Popen([str(copied)], cwd=private, env=env, stdout=log, stderr=subprocess.STDOUT,
                                   creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            deadline = time.monotonic() + 120
            while True:
                require(process.poll() is None, 'isolated smoke server exited')
                try:
                    current = owner(port)
                    if current['pid'] == process.pid and api(port, '/api/status')['state'] == 'idle':
                        break
                except (OSError, ValueError):
                    pass
                require(time.monotonic() < deadline, 'isolated smoke startup timed out')
                time.sleep(0.3)
            result = verify_restore(port, private, manifest, label + ' smoke verification')
            check_owner(args.port, old)
            compare_api(before, snapshot(args.port))
            write_new(folder / 'smoke-passed.json', result)
        finally:
            # Only the child created by this helper is terminated; never the live server.
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=30)
    print(str(folder / 'backup.json'))


def restore(args):
    require(args.execute and args.queues_complete, 'requires explicit --execute --queues-complete')
    queues_clear()
    manifest = json.loads(Path(args.manifest).read_text(encoding='utf-8'))
    current = owner(args.port)
    require(current['pid'] == args.expected_pid and current['sha256'] == args.expected_sha256, 'restore server identity mismatch')
    require(Path(current['cwd']).samefile(ROOT), 'restore cwd must be repository')
    require(api(args.port, '/api/status')['state'] == 'idle', 'restore requires empty postflop server')
    pre = api(args.port, '/api/preflop/status')
    # PreflopStatus derives Default: no session returns state="", not "idle".
    require(pre['state'] in ['', 'idle'] and pre['iteration'] == 0 and not pre['frozen'],
            'restore requires empty preflop server')
    for item in manifest['backups'].values():
        require(sha(item['path']) == item['sha256'], 'backup changed')
    label = manifest['label'] + ' restored ' + uuid.uuid4().hex[:8]
    result = verify_restore(args.port, current['cwd'], manifest, label)
    check_owner(args.port, current)
    write_new(Path(args.manifest).parent / ('restore-' + str(current['pid']) + '-' + uuid.uuid4().hex[:8] + '.json'), result)
    print('Both native sessions restored exactly; no solve started.')


def check_live(args):
    require(args.execute and args.queues_complete, 'requires explicit --execute --queues-complete')
    queues_clear()
    manifest = json.loads(Path(args.manifest).read_text(encoding='utf-8'))
    current = check_owner(args.port, manifest['old_owner'])
    require(current['pid'] == args.expected_pid and current['sha256'] == args.expected_sha256,
            'live recheck identity mismatch')
    compare_api(manifest['snapshot'], snapshot(args.port))
    label = manifest['label'] + ' final recheck ' + uuid.uuid4().hex[:8]
    latest = save_pair(args.port, current['cwd'], label)
    for key in ['pre', 'post']:
        require(latest[key]['native'] == manifest['backups'][key]['native'],
                'user state changed since smoke, including possible locks; restart from fresh smoke')
    compare_api(manifest['snapshot'], snapshot(args.port))
    write_new(Path(args.manifest).parent / ('live-recheck-' + uuid.uuid4().hex[:8] + '.json'), latest)
    print('Latest native state still matches smoke; live server remains untouched.')


def main():
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers(dest='command', required=True)
    p = subs.add_parser('smoke')
    p.add_argument('--candidate', required=True)
    p.add_argument('--candidate-sha256', required=True)
    p.add_argument('--expected-old-sha256', required=True)
    r = subs.add_parser('restore')
    r.add_argument('--manifest', required=True)
    r.add_argument('--expected-sha256', required=True)
    c = subs.add_parser('check-live')
    c.add_argument('--manifest', required=True)
    c.add_argument('--expected-sha256', required=True)
    for item in [p, r, c]:
        item.add_argument('--port', type=int, default=56708)
        item.add_argument('--expected-pid', type=int, required=True)
        item.add_argument('--execute', action='store_true')
        item.add_argument('--queues-complete', action='store_true')
    args = parser.parse_args()
    require(os.name == 'nt', 'Windows deployment helper')
    {'smoke': smoke, 'restore': restore, 'check-live': check_live}[args.command](args)


if __name__ == '__main__':
    main()
