"""Spawned CPU board targets for the typed, complete all-node policy.

The payload has exactly state/model_source/registry/resources and is consumed by
FrozenExpectedTargets v2. Runtime limits are explicit operational bounds, not a
scientific stopping rule; hitting any guard fails the unfinished generation.
The caller validates every returned artifact and restores declared board order
before admitting a complete generation. This module never publishes a model or
checkpoint and does not retry or reuse partially completed board directories.
"""
import copy
import hashlib
import json
import math
import multiprocessing
import os
from pathlib import Path
import time
from concurrent.futures import ProcessPoolExecutor


METHOD = 'typed-all-preflop-native-board-worker-v1'
PAYLOAD_FIELDS = {'state', 'model_source', 'registry', 'resources'}
RAM_RESERVE_BYTES = 20_000_000_000
DISK_RESERVE_BYTES = 40_000_000_000
DEFAULT_MAX_OUTPUT_BYTES = 2_000_000_000
_STATE = None


def sha(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b''):
            value.update(chunk)
    return value.hexdigest()


def _digest(document):
    return hashlib.sha256(json.dumps(document, sort_keys=True, separators=(',', ':'),
        allow_nan=False).encode('utf-8')).hexdigest()


def _save(path, document):
    with Path(path).open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(document, separators=(',', ':'), allow_nan=False)+'\n')


def _limits(value):
    required = {'max_worker_seconds', 'native_timeout_seconds'}
    if (not isinstance(value, dict) or not required <= set(value)
            or set(value)-required-{'max_output_bytes'}):
        raise ValueError('Explicit worker lifetime and native timeout limits required')
    result = copy.deepcopy(value)
    for name in required:
        x = result[name]
        if type(x) not in (int, float) or not math.isfinite(x) or x <= 0:
            raise ValueError('Worker runtime limits must be positive finite seconds')
    if result['native_timeout_seconds'] > result['max_worker_seconds']:
        raise ValueError('Native timeout cannot exceed the worker lifetime limit')
    if result['native_timeout_seconds'] > 86400:
        raise ValueError('Native timeout exceeds the authenticated execution limit')
    result.setdefault('max_output_bytes', DEFAULT_MAX_OUTPUT_BYTES)
    if (type(result['max_output_bytes']) is not int
            or not 1 <= result['max_output_bytes'] <= 8_000_000_000):
        raise ValueError('Native output byte limit must fit authenticated execution bounds')
    return result


def _payload(value):
    if not isinstance(value, dict) or set(value) != PAYLOAD_FIELDS:
        raise ValueError('Typed v2 payload requires exactly state/model_source/registry/resources')


def _identities(value, context_path, executable):
    if not isinstance(value, dict) or not value:
        raise ValueError('Pinned native context/executable/source identities required')
    result = copy.deepcopy(value)
    resolved = {}
    for path, identity in result.items():
        if (not isinstance(path, str) or str(Path(path).resolve()) != path
                or not isinstance(identity, str) or len(identity) != 64
                or any(c not in '0123456789abcdef' for c in identity)):
            raise ValueError('Absolute source paths and lowercase SHA256 identities required')
        target = Path(path).resolve()
        if target in resolved:
            raise ValueError('Repeated native source path identity')
        resolved[target] = identity
    if not {Path(context_path).resolve(), Path(executable).resolve()} <= set(resolved):
        raise ValueError('Both original native context and executable identities required')
    _check_identities(result)
    return result


def _check_identities(identities):
    for path, identity in identities.items():
        if sha(path) != identity:
            raise ValueError('Board worker source or request identity changed: '+path)


def initialize(payload, context_path, executable, folder, expected_native_identities,
               runtime_limits, cancel_event=None):
    global _STATE
    _STATE = None
    if (multiprocessing.current_process().name == 'MainProcess'
            or multiprocessing.get_start_method() != 'spawn'):
        raise RuntimeError('CPU board worker initialization requires a spawned child process')
    # These mutations occur only in the spawned worker; training retains CUDA.
    os.environ.update(CUDA_VISIBLE_DEVICES='-1', OPENBLAS_NUM_THREADS='1',
        OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', NUMEXPR_NUM_THREADS='1',
        BLIS_NUM_THREADS='1', VECLIB_MAXIMUM_THREADS='1')
    import psutil
    from threadpoolctl import threadpool_limits
    from bounded_parallel_evaluation_archive_v2 import production_available
    from preflop_expected_native_targets_v2 import FrozenExpectedTargets
    import preflop_expected_native_execution_v1 as native

    began, initialized_unix = time.monotonic(), time.time()
    _payload(payload)
    limits = _limits(runtime_limits)
    root = Path(folder).resolve()
    if not root.is_dir():
        raise ValueError('Existing isolated worker output directory required')
    context_path, executable = Path(context_path).resolve(), Path(executable).resolve()
    identities = _identities(expected_native_identities, context_path, executable)
    key = payload['state'].config['context_sha256']
    # read_bytes preserves exact UTF-8 bytes, including the source newline form.
    if context_path.read_bytes().decode('utf-8') != payload['registry'].source(key):
        raise ValueError('Native context differs from the exact frozen registered source')
    limit = threadpool_limits(limits=1)
    try:
        prepared = FrozenExpectedTargets(**payload)
        recipe, plan = prepared.recipe, copy.deepcopy(prepared._plan)
        if (recipe['context_sha256'] != key
                or recipe['model_sha256'] != hashlib.sha256(payload['model_source'].encode('utf-8')).hexdigest()
                or recipe['registry_sha256'] != payload['registry'].sha256
                or plan != payload['state'].plan()):
            raise ValueError('Frozen provider identities or ordered generation plan differ')
        sources = {str(Path(__file__).resolve()): sha(__file__),
            str(Path(native.__file__).resolve()): sha(native.__file__)}
        for module_name, field in (
                ('preflop_expected_native_targets_v2', 'provider_sha256'),
                ('preflop_expected_native_targets_v1', 'transport_sha256'),
                ('preflop_expected_policy_v1', 'policy_sha256')):
            path = str(Path(__import__(module_name).__file__).resolve())
            sources[path] = recipe[field]
        _check_identities(sources)
        _check_identities(identities)
        _STATE = dict(prepared=prepared, recipe=recipe, plan=plan,
            context_path=context_path, executable=executable, folder=root,
            identities=identities, source_identities=sources, runtime_limits=limits,
            limit=limit, began=began, initialized_unix=initialized_unix,
            pid=os.getpid(), creation_time=psutil.Process().create_time(),
            psutil=psutil, production_available=production_available, native=native,
            cancel_event=cancel_event)
        guard()
    except BaseException:
        _STATE = None
        limit.restore_original_limits()
        raise


def guard():
    if _STATE is None:
        raise RuntimeError('Board worker has not initialized')
    s = _STATE
    if s.get('cancel_event') is not None and s['cancel_event'].is_set():
        raise InterruptedError('Board collection canceled by the coordinating process')
    if s['pid'] != os.getpid():
        raise RuntimeError('Board worker state belongs to another process')
    if time.monotonic()-s['began'] > s['runtime_limits']['max_worker_seconds']:
        raise TimeoutError('Explicit board worker lifetime limit reached; incomplete generation refused')
    if s['psutil'].virtual_memory().available < RAM_RESERVE_BYTES:
        raise RuntimeError('Board worker RAM reserve')
    if s['psutil'].disk_usage(str(s['folder'])).free < DISK_RESERVE_BYTES:
        raise RuntimeError('Board worker disk reserve')
    # Existing production availability probe does not prohibit light video use.
    if not s['production_available']():
        raise RuntimeError('Production became busy')


def complete(index, board):
    guard()
    s = _STATE
    if type(index) is not int or not 0 <= index < len(s['plan']['boards']):
        raise ValueError('Declared ordered generation draw index required')
    if (not isinstance(board, list) or any(type(card) is not int for card in board)
            or board != s['plan']['boards'][index]):
        raise ValueError('Board differs from the declared ordered generation plan')
    began, started_unix = time.monotonic(), time.time()
    _check_identities(s['identities'])
    _check_identities(s['source_identities'])
    if s['prepared'].recipe != s['recipe'] or s['prepared']._plan != s['plan']:
        raise ValueError('Frozen target provider recipe or board plan changed')
    req, ids = s['prepared'].request(board)
    if (req.get('board') != board or set(req) != {'board', 'hands'}
            or len(ids) != 1081 or len(req['hands']) != 2
            or any(len(hands) != 1081 for hands in req['hands'])
            or req['hands'][0] != req['hands'][1]):
        raise ValueError('Complete identical ordered 1081-hand private domains required')
    folder = s['folder']/f'board-{index:03d}'
    folder.mkdir(exist_ok=False)
    request_path = folder/'request.json'
    _save(request_path, req)
    request_sha256 = sha(request_path)
    invocation_identities = dict(s['identities'])
    if str(request_path) in invocation_identities:
        raise ValueError('Request artifact overlaps an original native source')
    invocation_identities[str(request_path)] = request_sha256
    arguments = [str(s['context_path']), str(request_path)]
    native = s['native'].run_native(s['executable'], arguments, folder=folder,
        label='board-tree', expected_identities=invocation_identities, guard=guard,
        timeout=s['runtime_limits']['native_timeout_seconds'],
        max_output_bytes=s['runtime_limits']['max_output_bytes'])
    s['native'].verify_native(native, executable=s['executable'], arguments=arguments,
        expected_identities=invocation_identities)
    receipt = native['receipt']
    if (receipt['caller'] != dict(pid=s['pid'], creation_time=s['creation_time'])
            or receipt['timeout_seconds'] != s['runtime_limits']['native_timeout_seconds']
            or receipt['max_output_bytes'] != s['runtime_limits']['max_output_bytes']
            or receipt['started_unix'] < started_unix
            or receipt['terminal_unix'] > time.time()):
        raise ValueError('Native invocation is detached from this worker and declared runtime')
    _check_identities(invocation_identities)
    _check_identities(s['source_identities'])
    guard()
    tree_path = Path(native['stdout_path'])
    raw = tree_path.read_bytes()
    tree_sha256 = hashlib.sha256(raw).hexdigest()
    if tree_sha256 != native['stdout_sha256']:
        raise ValueError('Authenticated native stdout changed before board reduction')
    record = s['prepared'].draw_record(raw, expected_tree_sha256=tree_sha256,
        draw_index=index)
    del raw
    if (record['draw_index'] != index or record['board'] != board
            or record['tree_sha256'] != tree_sha256
            or record['model_sha256'] != s['recipe']['model_sha256']
            or record['policy_recipe_sha256'] != _digest(s['recipe'])):
        raise ValueError('Board result differs from its frozen request/model/recipe')
    s['native'].verify_native(native, executable=s['executable'], arguments=arguments,
        expected_identities=invocation_identities)
    _check_identities(invocation_identities)
    _check_identities(s['source_identities'])
    guard()
    terminal_unix = time.time()
    result = dict(format=1, method=METHOD, record=record, draw_index=index,
        board=board.copy(), generation=s['recipe']['generation'],
        context_sha256=s['recipe']['context_sha256'],
        registry_sha256=s['recipe']['registry_sha256'],
        model_sha256=s['recipe']['model_sha256'],
        recipe=copy.deepcopy(s['recipe']), recipe_sha256=_digest(s['recipe']),
        plan_sha256=_digest(s['plan']), parent_state_sha256=s['plan']['parent_state_sha256'],
        native_identities=copy.deepcopy(s['identities']),
        invocation_identities=invocation_identities,
        worker_source_identities=copy.deepcopy(s['source_identities']),
        request_artifact=str(request_path), request_sha256=request_sha256,
        request_document_sha256=_digest(req),
        tree_artifact=str(tree_path), tree_sha256=tree_sha256,
        native_invocation=native, runtime_limits=copy.deepcopy(s['runtime_limits']),
        initialized_unix=s['initialized_unix'], started_unix=started_unix,
        terminal_unix=terminal_unix, seconds=time.monotonic()-began,
        worker_seconds=time.monotonic()-s['began'], pid=s['pid'],
        creation_time=s['creation_time'], rss_bytes=s['psutil'].Process().memory_info().rss,
        cuda_visible_devices=os.environ.get('CUDA_VISIBLE_DEVICES'), threadpool_limit=1)
    target = folder/'result.json'
    _save(target, result)
    guard()
    _check_identities(invocation_identities)
    _check_identities(s['source_identities'])
    return dict(result=result, path=str(target), sha256=sha(target))


def pool(workers, *, payload, context_path, executable, folder,
         expected_native_identities, runtime_limits, cancel_event=None):
    if type(workers) is not int or not 1 <= workers <= 4:
        raise ValueError('One to four board workers required')
    _payload(payload)
    limits = _limits(runtime_limits)
    identities = _identities(expected_native_identities, context_path, executable)
    root = Path(folder).resolve()
    if not root.is_dir():
        raise ValueError('Existing isolated worker output directory required')
    return ProcessPoolExecutor(max_workers=workers,
        mp_context=multiprocessing.get_context('spawn'), initializer=initialize,
        initargs=(payload, str(Path(context_path).resolve()), str(Path(executable).resolve()),
            str(root), identities, limits, cancel_event))
