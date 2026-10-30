"""Owned native executions with retained process, source and terminal evidence.

This module does not admit/retry scientific work. A caller must supply its
registered executable/input hashes, resource guard and explicit time limit.
Observation polling never relaunches a child. Failed evidence is retained.
"""
import ctypes
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import time

import psutil

METHOD = 'native-process-bound-export-v1'
RESULT_FIELDS = {'receipt_path', 'receipt_sha256', 'stdout_path', 'stdout_sha256',
                 'stderr_path', 'stderr_sha256', 'receipt'}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024), b''): h.update(block)
    return h.hexdigest()


def _write(path, value):
    raw = (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)+'\n').encode()
    with Path(path).open('xb') as stream:
        stream.write(raw); stream.flush(); os.fsync(stream.fileno())


def _sources(expected):
    if not isinstance(expected, dict) or not expected:
        raise ValueError('Explicit native and request/input identities required')
    for path, identity in expected.items():
        if (not isinstance(path, str) or str(Path(path).resolve()) != path
                or not isinstance(identity, str) or not re.fullmatch('[0-9a-f]{64}', identity)
                or sha(path) != identity):
            raise ValueError('Changed or noncanonical native input identity')


def _creation(child):
    # The Windows handle remains valid after a fast child exits. Querying only
    # a live PID can lose the identity of such a completed native export.
    if os.name == 'nt':
        from ctypes import wintypes
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        query = kernel.GetProcessTimes
        query.argtypes = [wintypes.HANDLE, *([ctypes.POINTER(wintypes.FILETIME)]*4)]
        query.restype = wintypes.BOOL
        created, ended, kern, user = (wintypes.FILETIME() for _ in range(4))
        if not query(int(child._handle), ctypes.byref(created), ctypes.byref(ended),
                     ctypes.byref(kern), ctypes.byref(user)):
            raise OSError(ctypes.get_last_error(), 'Cannot authenticate owned process creation')
        return ((created.dwHighDateTime << 32) | created.dwLowDateTime)/10_000_000-11_644_473_600
    return psutil.Process(child.pid).create_time()


def run_native(executable, arguments, *, folder, label, expected_identities, guard,
               timeout=120, max_output_bytes=2_000_000_000, stdin_path=None):
    """Launch exactly once, retain raw output and record the owned exit handle."""
    executable = str(Path(executable).resolve()); folder = Path(folder).resolve()
    if (not isinstance(label, str) or not re.fullmatch('[A-Za-z0-9-]{1,100}', label)
            or not isinstance(arguments, (list, tuple)) or any(not isinstance(a, str) for a in arguments)
            or type(timeout) not in (int, float) or not math.isfinite(timeout) or not 0 < timeout <= 86400
            or type(max_output_bytes) is not int or not 1 <= max_output_bytes <= 8_000_000_000):
        raise ValueError('Explicit safe invocation name, arguments and runtime/output limits required')
    _sources(expected_identities)
    if executable not in expected_identities: raise ValueError('Unregistered native executable')
    incoming = None
    if stdin_path is not None:
        stdin_path = str(Path(stdin_path).resolve())
        if stdin_path not in expected_identities: raise ValueError('Unregistered standard input source')
        incoming = dict(path=stdin_path, sha256=sha(stdin_path), bytes=Path(stdin_path).stat().st_size)
    guard(); folder.mkdir(parents=True, exist_ok=True)
    paths = {name:folder/(label+'-'+name+suffix) for name, suffix in
             (('stdout','.bin'), ('stderr','.bin'), ('receipt','.json'))}
    argv = [executable, *arguments]
    caller = dict(pid=os.getpid(), creation_time=psutil.Process().create_time())
    receipt = dict(format=1, method=METHOD, outcome='failed', executable=executable,
        argv=argv, expected_identities=dict(expected_identities), caller=caller, process=None,
        started_unix=time.time(), terminal_unix=None, returncode=None, timeout_seconds=timeout,
        max_output_bytes=max_output_bytes, stdin=incoming, stdout=None, stderr=None)
    child = None; failure = None; began = time.monotonic()
    try:
        with paths['stdout'].open('xb') as output, paths['stderr'].open('xb') as error:
            input_stream = open(stdin_path, 'rb') if incoming else None
            try:
                child = subprocess.Popen(argv, stdin=input_stream or subprocess.DEVNULL,
                    stdout=output, stderr=error,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                # These arguments are read from the actual Popen launch object;
                # creation_time comes from its owned OS handle, not a state file.
                receipt['process'] = dict(pid=child.pid, parent_pid=caller['pid'],
                    creation_time=_creation(child), observed_argv=list(child.args))
                while child.poll() is None:
                    guard()
                    if time.monotonic()-began > timeout: raise TimeoutError('Owned native invocation deadline')
                    if paths['stdout'].stat().st_size+paths['stderr'].stat().st_size > max_output_bytes:
                        raise ValueError('Owned native output budget exceeded')
                    try: child.wait(timeout=.1)
                    except subprocess.TimeoutExpired: pass
                receipt['returncode'] = child.returncode
            finally:
                if child is not None and child.poll() is None:
                    # Only this exact Popen handle is stopped; no PID lookup or
                    # unrelated application termination occurs.
                    child.terminate()
                    try: child.wait(timeout=10)
                    except subprocess.TimeoutExpired: child.kill(); child.wait(timeout=10)
                if input_stream is not None: input_stream.close()
        receipt['returncode'] = child.returncode
        if sum(paths[n].stat().st_size for n in ('stdout','stderr')) > max_output_bytes:
            raise ValueError('Owned native output budget exceeded')
        _sources(expected_identities); guard()
        if child.returncode != 0: raise RuntimeError('Owned native invocation exited '+str(child.returncode))
        receipt['outcome'] = 'success'
    except BaseException as exc:
        failure = exc
        receipt['failure'] = dict(type=type(exc).__name__, message=str(exc))
        if child is not None: receipt['returncode'] = child.returncode
    finally:
        receipt['terminal_unix'] = time.time()
        for name in ('stdout','stderr'):
            if paths[name].exists():
                receipt[name] = dict(path=str(paths[name]), sha256=sha(paths[name]), bytes=paths[name].stat().st_size)
        _write(paths['receipt'], receipt)
    if failure is not None: raise failure
    result = dict(receipt_path=str(paths['receipt']), receipt_sha256=sha(paths['receipt']),
        stdout_path=str(paths['stdout']), stdout_sha256=receipt['stdout']['sha256'],
        stderr_path=str(paths['stderr']), stderr_sha256=receipt['stderr']['sha256'], receipt=receipt)
    verify_native(result, executable=executable, arguments=arguments,
                  expected_identities=expected_identities, stdin_path=stdin_path)
    return result


def verify_native(result, *, executable, arguments, expected_identities, stdin_path=None):
    if not isinstance(result, dict) or set(result) != RESULT_FIELDS:
        raise ValueError('Complete native invocation result required')
    _sources(expected_identities)
    rp = Path(result['receipt_path']).resolve()
    if sha(rp) != result['receipt_sha256'] or json.loads(rp.read_bytes()) != result['receipt']:
        raise ValueError('Changed native terminal receipt')
    r = result['receipt']; required = {'format','method','outcome','executable','argv',
        'expected_identities','caller','process','started_unix','terminal_unix','returncode',
        'timeout_seconds','max_output_bytes','stdin','stdout','stderr'}
    exe = str(Path(executable).resolve()); argv = [exe, *arguments]
    incoming = None
    if stdin_path is not None:
        path = str(Path(stdin_path).resolve())
        if path not in expected_identities: raise ValueError('Unregistered standard input source')
        incoming = dict(path=path, sha256=sha(path), bytes=Path(path).stat().st_size)
    if (set(r) != required or type(r['format']) is not int or r['format'] != 1
            or r['method'] != METHOD or r['outcome'] != 'success'
            or r['executable'] != exe or r['argv'] != argv or exe not in expected_identities
            or r['expected_identities'] != expected_identities or r['stdin'] != incoming
            or type(r['returncode']) is not int or r['returncode'] != 0):
        raise ValueError('Native receipt belongs to another launch or lacks successful exit')
    c, p = r['caller'], r['process']
    if (not isinstance(c, dict) or set(c) != {'pid','creation_time'}
            or not isinstance(p, dict) or set(p) != {'pid','parent_pid','creation_time','observed_argv'}
            or any(type(v) is not int or v <= 0 for v in (c['pid'],p['pid'],p['parent_pid']))
            or p['parent_pid'] != c['pid'] or p['observed_argv'] != argv
            or any(type(v) not in (int,float) or not math.isfinite(v) or v <= 0
                for v in (c['creation_time'],p['creation_time'],r['started_unix'],r['terminal_unix'],r['timeout_seconds']))
            or not c['creation_time'] <= r['started_unix'] <= r['terminal_unix']
            or not r['started_unix']-.01 <= p['creation_time'] <= r['terminal_unix']+.01
            or type(r['max_output_bytes']) is not int or r['max_output_bytes'] <= 0):
        raise ValueError('Invalid owned native process identity or timing')
    total = 0
    for name in ('stdout','stderr'):
        artifact = r[name]; path = Path(result[name+'_path']).resolve()
        if (not isinstance(artifact, dict) or set(artifact) != {'path','sha256','bytes'}
                or artifact['path'] != str(path) or path.parent != rp.parent
                or type(artifact['bytes']) is not int or artifact['bytes'] < 0
                or path.stat().st_size != artifact['bytes'] or sha(path) != artifact['sha256']
                or result[name+'_sha256'] != artifact['sha256']):
            raise ValueError('Changed native raw output artifact')
        total += artifact['bytes']
    if total > r['max_output_bytes']: raise ValueError('Native output budget was exceeded')
    return r
