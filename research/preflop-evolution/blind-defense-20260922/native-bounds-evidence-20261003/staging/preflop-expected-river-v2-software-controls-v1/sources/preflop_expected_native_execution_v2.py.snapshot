"""Owned native executions with declared direct-file acceptance bounds.

The byte limit is polled and checked at terminal. It is not a hard transient
filesystem quota. Failed raw outputs and direct-file witnesses are retained.
V1 source, schemas and receipts are unchanged and unsupported by this verifier.
"""
import ctypes
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import subprocess
import time

import psutil

METHOD = 'native-process-bound-export-v2'
RESULT_FIELDS = {'format', 'method', 'receipt_path', 'receipt_sha256', 'stdout_path',
                 'stdout_sha256', 'stderr_path', 'stderr_sha256', 'receipt'}
ARTIFACT_FIELDS = {'path', 'exists', 'bytes', 'sha256'}
SPEC_FIELDS = {'path', 'argument_index'}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''): h.update(block)
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


def _bounds(timeout, max_output_bytes):
    if (type(timeout) not in (int, float) or not math.isfinite(timeout) or not 0 < timeout <= 86400
            or type(max_output_bytes) is not int or not 1 <= max_output_bytes <= 8_000_000_000):
        raise ValueError('Explicit finite native runtime and logical output bounds required')


def _canonical(path):
    if not isinstance(path, str) or not Path(path).is_absolute() or str(Path(path).resolve()) != path:
        raise ValueError('Canonical absolute native output path required')
    return Path(path)


def _directories(folder, parent):
    if not parent.is_relative_to(folder): raise ValueError('Native output escaped owned folder')
    relative = parent.relative_to(folder)
    current = folder
    for component in (None, *relative.parts):
        if component is not None: current = current/component
        info = current.lstat()
        if (not stat.S_ISDIR(info.st_mode) or current.is_symlink()
                or getattr(info, 'st_file_attributes', 0) & 0x400):
            raise ValueError('Native output parent must be an isolated ordinary directory')


def _file_identity(path):
    """Use the actual Windows handle; Python3.12 nlink can miss hardlinks."""
    if os.name != 'nt':
        value = path.lstat()
        return value.st_dev, value.st_ino, value.st_nlink
    from ctypes import wintypes
    class Information(ctypes.Structure):
        _fields_ = [('attributes', wintypes.DWORD), ('created', wintypes.FILETIME),
            ('accessed', wintypes.FILETIME), ('written', wintypes.FILETIME),
            ('volume', wintypes.DWORD), ('size_high', wintypes.DWORD),
            ('size_low', wintypes.DWORD), ('links', wintypes.DWORD),
            ('index_high', wintypes.DWORD), ('index_low', wintypes.DWORD)]
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    create = kernel.CreateFileW
    create.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID,
                       wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    create.restype = wintypes.HANDLE
    query = kernel.GetFileInformationByHandle
    query.argtypes = [wintypes.HANDLE, ctypes.POINTER(Information)]; query.restype = wintypes.BOOL
    close = kernel.CloseHandle
    close.argtypes = [wintypes.HANDLE]; close.restype = wintypes.BOOL
    handle = create(str(path), 0x80, 7, None, 3, 0x00200000, None)
    if handle == wintypes.HANDLE(-1).value: raise ctypes.WinError(ctypes.get_last_error())
    try:
        value = Information()
        if not query(handle, ctypes.byref(value)): raise ctypes.WinError(ctypes.get_last_error())
        if value.attributes & 0x400: raise ValueError('Redirected native output file refused')
        return value.volume, (value.index_high << 32) | value.index_low, value.links
    finally: close(handle)


def _ordinary_file(path, folder):
    _directories(folder, path.parent)
    info = path.lstat()
    if (not stat.S_ISREG(info.st_mode) or path.is_symlink()
            or getattr(info, 'st_file_attributes', 0) & 0x400):
        raise ValueError('Native output must be an ordinary owned file')
    identity = _file_identity(path)
    if identity[2] != 1: raise ValueError('Shared native output file identity refused')
    return info, identity


def _specs(direct_outputs, *, argv, folder, inputs, reserved, require_new):
    if not isinstance(direct_outputs, (list, tuple)):
        raise ValueError('Explicit ordered direct-output specs required')
    result = []; paths = set(); indexes = set()
    forbidden = {Path(p) for p in inputs} | set(reserved)
    for supplied in direct_outputs:
        if not isinstance(supplied, dict) or set(supplied) != SPEC_FIELDS:
            raise ValueError('Direct-output spec requires exactly path and argument_index')
        path = _canonical(supplied['path']); index = supplied['argument_index']
        if (type(index) is not int or not 1 <= index < len(argv) or argv[index] != str(path)
                or path == folder or not path.is_relative_to(folder)
                or path in forbidden or path in paths or index in indexes):
            raise ValueError('Direct output must match a unique actual argv destination in the owned folder')
        _directories(folder, path.parent)
        if require_new and os.path.lexists(path): raise ValueError('Native direct output path must be new')
        paths.add(path); indexes.add(index)
        result.append(dict(path=str(path), argument_index=index))
    return result


def _size(path, folder):
    try: info, _ = _ordinary_file(path, folder)
    except FileNotFoundError: return 0
    return info.st_size


def _record(path, folder):
    value = dict(path=str(path), exists=os.path.lexists(path), bytes=None, sha256=None)
    if not value['exists']: return value
    try:
        before, identity = _ordinary_file(path, folder)
        value['bytes'] = before.st_size; value['sha256'] = sha(path)
        after, terminal_identity = _ordinary_file(path, folder)
        if (identity != terminal_identity or before.st_size != after.st_size
                or before.st_mtime_ns != after.st_mtime_ns):
            raise ValueError('Native terminal output changed while hashing')
    except BaseException as exc:
        value['error'] = dict(type=type(exc).__name__, message=str(exc))
    return value


def _creation(child):
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
               timeout=120, max_output_bytes=2_000_000_000, stdin_path=None, direct_outputs=()):
    """Launch once; the aggregate limit is an acceptance/polling bound."""
    executable = str(Path(executable).resolve()); supplied_folder = Path(folder)
    folder = supplied_folder.resolve()
    if (str(supplied_folder) != str(folder)
            or not isinstance(label, str) or not re.fullmatch('[A-Za-z0-9-]{1,100}', label)
            or not isinstance(arguments, (list, tuple)) or any(not isinstance(a, str) for a in arguments)):
        raise ValueError('Canonical owned folder, invocation name and string arguments required')
    _bounds(timeout, max_output_bytes); _sources(expected_identities)
    if executable not in expected_identities: raise ValueError('Unregistered native executable')
    incoming = None
    if stdin_path is not None:
        stdin_path = str(Path(stdin_path).resolve())
        if stdin_path not in expected_identities: raise ValueError('Unregistered standard input source')
        incoming = dict(path=stdin_path, sha256=sha(stdin_path), bytes=Path(stdin_path).stat().st_size)
    guard(); folder.mkdir(parents=True, exist_ok=True); _directories(folder, folder)
    paths = {name:folder/(label+'-'+name+suffix) for name, suffix in
             (('stdout','.bin'), ('stderr','.bin'), ('receipt','.json'))}
    argv = [executable, *arguments]
    if any(os.path.lexists(p) for p in paths.values()): raise ValueError('Native capture/receipt paths must be new')
    specs = _specs(direct_outputs, argv=argv, folder=folder, inputs=expected_identities,
                   reserved=paths.values(), require_new=True)
    emitted_paths = [paths['stdout'], paths['stderr'], *[Path(s['path']) for s in specs]]
    caller = dict(pid=os.getpid(), creation_time=psutil.Process().create_time())
    receipt = dict(format=2, method=METHOD, outcome='failed', executable=executable,
        argv=argv, expected_identities=dict(expected_identities), caller=caller, process=None,
        folder=str(folder), label=label, direct_outputs=specs, direct_output_artifacts=[],
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
                receipt['process'] = dict(pid=child.pid, parent_pid=caller['pid'],
                    creation_time=_creation(child), observed_argv=list(child.args))
                while child.poll() is None:
                    guard()
                    if time.monotonic()-began > timeout: raise TimeoutError('Owned native invocation deadline')
                    if sum(_size(p, folder) for p in emitted_paths) > max_output_bytes:
                        raise ValueError('Owned aggregate native output budget exceeded')
                    try: child.wait(timeout=.1)
                    except subprocess.TimeoutExpired: pass
                receipt['returncode'] = child.returncode
            finally:
                if child is not None and child.poll() is None:
                    child.terminate()
                    try: child.wait(timeout=10)
                    except subprocess.TimeoutExpired: child.kill(); child.wait(timeout=10)
                if input_stream is not None: input_stream.close()
        receipt['returncode'] = child.returncode
        if sum(_size(p, folder) for p in emitted_paths) > max_output_bytes:
            raise ValueError('Owned aggregate native output budget exceeded')
        if any(not Path(s['path']).is_file() for s in specs):
            raise ValueError('Required native direct output missing at terminal')
        _sources(expected_identities); guard()
        if child.returncode != 0: raise RuntimeError('Owned native invocation exited '+str(child.returncode))
        receipt['outcome'] = 'success'
    except BaseException as exc:
        failure = exc
        receipt['failure'] = dict(type=type(exc).__name__, message=str(exc))
        if child is not None: receipt['returncode'] = child.returncode
    finally:
        receipt['terminal_unix'] = time.time()
        for name in ('stdout', 'stderr'): receipt[name] = _record(paths[name], folder)
        receipt['direct_output_artifacts'] = [dict(_record(Path(s['path']), folder),
            argument_index=s['argument_index']) for s in specs]
        witnesses = [receipt['stdout'], receipt['stderr'], *receipt['direct_output_artifacts']]
        if receipt['outcome'] == 'success' and any(not v['exists'] or 'error' in v for v in witnesses):
            failure = ValueError('Native terminal output witness is missing or unsafe')
            receipt['outcome'] = 'failed'; receipt['failure'] = dict(type=type(failure).__name__, message=str(failure))
        _write(paths['receipt'], receipt)
    if failure is not None: raise failure
    result = dict(format=2, method=METHOD, receipt_path=str(paths['receipt']), receipt_sha256=sha(paths['receipt']),
        stdout_path=str(paths['stdout']), stdout_sha256=receipt['stdout']['sha256'],
        stderr_path=str(paths['stderr']), stderr_sha256=receipt['stderr']['sha256'], receipt=receipt)
    verify_native(result, executable=executable, arguments=arguments,
        expected_identities=expected_identities, stdin_path=stdin_path, direct_outputs=specs,
        timeout=timeout, max_output_bytes=max_output_bytes)
    return result


def verify_native(result, *, executable, arguments, expected_identities, timeout,
                  max_output_bytes, stdin_path=None, direct_outputs=()):
    if (not isinstance(result, dict) or set(result) != RESULT_FIELDS
            or type(result['format']) is not int or result['format'] != 2 or result['method'] != METHOD
            or not isinstance(arguments, (list, tuple)) or any(not isinstance(a, str) for a in arguments)):
        raise ValueError('Complete v2 native invocation result and string arguments required')
    _bounds(timeout, max_output_bytes); _sources(expected_identities)
    rp = _canonical(result['receipt_path'])
    if sha(rp) != result['receipt_sha256'] or json.loads(rp.read_bytes()) != result['receipt']:
        raise ValueError('Changed native terminal receipt')
    r = result['receipt']; required = {'format','method','outcome','executable','argv',
        'expected_identities','caller','process','started_unix','terminal_unix','returncode',
        'timeout_seconds','max_output_bytes','stdin','stdout','stderr','folder','label',
        'direct_outputs','direct_output_artifacts'}
    exe = str(Path(executable).resolve()); argv = [exe, *arguments]
    incoming = None
    if stdin_path is not None:
        path = str(Path(stdin_path).resolve())
        if path not in expected_identities: raise ValueError('Unregistered standard input source')
        incoming = dict(path=path, sha256=sha(path), bytes=Path(path).stat().st_size)
    if (set(r) != required or type(r['format']) is not int or r['format'] != 2
            or r['method'] != METHOD or r['outcome'] != 'success'
            or r['executable'] != exe or r['argv'] != argv or exe not in expected_identities
            or r['expected_identities'] != expected_identities or r['stdin'] != incoming
            or type(r['returncode']) is not int or r['returncode'] != 0
            or type(r['max_output_bytes']) is not int
            or r['timeout_seconds'] != timeout or r['max_output_bytes'] != max_output_bytes):
        raise ValueError('Native receipt lacks this successful launch or expected operational bounds')
    folder = _canonical(r['folder']); _directories(folder, folder)
    label = r['label']
    if (not isinstance(label, str) or not re.fullmatch('[A-Za-z0-9-]{1,100}', label)
            or rp != folder/(label+'-receipt.json')):
        raise ValueError('Native receipt is outside its owned invocation namespace')
    paths = {name:folder/(label+'-'+name+suffix) for name,suffix in
        (('stdout','.bin'),('stderr','.bin'),('receipt','.json'))}
    specs = _specs(direct_outputs, argv=argv, folder=folder, inputs=expected_identities,
                   reserved=paths.values(), require_new=False)
    if (not isinstance(r['direct_outputs'], list)
            or _specs(r['direct_outputs'], argv=argv, folder=folder, inputs=expected_identities,
                reserved=paths.values(), require_new=False) != specs
            or not isinstance(r['direct_output_artifacts'], list)):
        raise ValueError('Native direct-output declaration changed')
    c, p = r['caller'], r['process']
    if (not isinstance(c, dict) or set(c) != {'pid','creation_time'}
            or not isinstance(p, dict) or set(p) != {'pid','parent_pid','creation_time','observed_argv'}
            or any(type(v) is not int or v <= 0 for v in (c['pid'],p['pid'],p['parent_pid']))
            or p['parent_pid'] != c['pid'] or p['observed_argv'] != argv
            or any(type(v) not in (int,float) or not math.isfinite(v) or v <= 0
                for v in (c['creation_time'],p['creation_time'],r['started_unix'],r['terminal_unix'],r['timeout_seconds']))
            or not c['creation_time'] <= r['started_unix'] <= r['terminal_unix']
            or not r['started_unix']-.01 <= p['creation_time'] <= r['terminal_unix']+.01):
        raise ValueError('Invalid owned native process identity or timing')
    if len(r['direct_output_artifacts']) != len(specs): raise ValueError('Incomplete native direct-file witnesses')
    total = 0
    witnesses = [(r[name], paths[name], None) for name in ('stdout','stderr')]
    witnesses += [(value, Path(spec['path']), spec['argument_index'])
        for spec,value in zip(specs,r['direct_output_artifacts'])]
    for artifact,path,index in witnesses:
        fields = ARTIFACT_FIELDS | ({'argument_index'} if index is not None else set())
        if (not isinstance(artifact, dict) or set(artifact) != fields or artifact['exists'] is not True
                or artifact['path'] != str(path) or type(artifact['bytes']) is not int or artifact['bytes'] < 0
                or not isinstance(artifact['sha256'], str) or not re.fullmatch('[0-9a-f]{64}', artifact['sha256'])
                or (index is not None and (type(artifact['argument_index']) is not int
                    or artifact['argument_index'] != index))):
            raise ValueError('Invalid native terminal output artifact')
        info, _ = _ordinary_file(path, folder)
        if info.st_size != artifact['bytes'] or sha(path) != artifact['sha256']:
            raise ValueError('Changed native raw/direct output artifact')
        total += artifact['bytes']
    for name in ('stdout','stderr'):
        if result[name+'_path'] != str(paths[name]) or result[name+'_sha256'] != r[name]['sha256']:
            raise ValueError('Changed native capture reference')
    if total > max_output_bytes: raise ValueError('Native aggregate output budget was exceeded')
    return r
