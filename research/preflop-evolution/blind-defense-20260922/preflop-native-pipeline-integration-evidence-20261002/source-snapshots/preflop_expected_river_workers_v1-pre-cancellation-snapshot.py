"""Typed physical/posterior64 CPU collection for the new expected-policy study.

No sampled preflop visit or legacy integrated root becomes training truth. The
qualified ingester still validates the complete physical transport, then only
ordered postflop events cross the coordinator's real reservoir boundary.
This module does not execute merely by importing it or register a study budget.
"""
import copy
import hashlib
import json
import multiprocessing
import os
from pathlib import Path
import re
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import psutil

from exact_initial_training_ingest_v2 import InitialTargets, digest
from preflop_expected_policy_v1 import ExpectedPolicy, TYPE as POLICY_TYPE
from preflop_expected_native_execution_v1 import run_native, verify_native
import preflop_expected_river_transport_v1 as transport
from reboot_research_idle_v1 import idle
from river_weighted_overlay_ingest_v1 import ingest, METHOD
from sampled_allin_protocol_v3 import policy_document
from sampled_physical_deals_v1 import PhysicalDeals
from sampled_physical_reservoir_v1 import checked_row
from sampled_physical_root_evaluation_v1 import sha, save
from storage_strategic_common_prior_20260920 import PAIRS
from weighted_deal_binding_v1 import DealWeightGeneration
from weighted_physical_reservoir_v1 import WeightedPhysicalReservoir, checked_weight
from weighted_training_v1 import first_action_view

TYPE = 'typed-expected-policy-physical-posterior64-cpu-worker-v1'
RECIPE = dict(method=TYPE, policy_type=POLICY_TYPE, inference='float64-widened-float32-weights-v1',
    device='cpu', threads=1, physical_ingest='qualified-original-exact-weighted-action-transport-v1',
    river_targets=dict(method=METHOD, K=64), training_scope='positive-tag-postflop-only',
    preflop_training='separate-complete-cumulative-expected-state-only',
    source_weights='retain unchanged deal weight; apply once in fitting',
    memory_headroom_bytes=20_000_000_000, disk_reserve_bytes=40_000_000_000,
    production_priority='stop collection when the production application is busy')
_STATE = None
_INIT_FIELDS = ('context_path', 'cache', 'targets', 'generation', 'iteration',
    'executable', 'trace_executable', 'river_payload', 'river_executable',
    'expected_native_identities', 'runtime_limits')


def runtime(value):
    names = {'max_worker_seconds':3600, 'native_timeout_seconds':120, 'river_native_timeout_seconds':60}
    if not isinstance(value, dict) or set(value) != set(names):
        raise ValueError('Explicit worker and native time limits required')
    for name, maximum in names.items():
        v = value[name]
        if (type(v) not in (int, float) or not np.isfinite(v) or not 0 < v <= maximum):
            raise ValueError('Invalid bounded worker runtime limit')
    if max(value['native_timeout_seconds'], value['river_native_timeout_seconds']) > value['max_worker_seconds']:
        raise ValueError('Native invocation timeout exceeds the explicit worker lifetime')
    return copy.deepcopy(value)


def identities(value):
    if (not isinstance(value, dict) or not value or any(not isinstance(p, str) or not p
            or not isinstance(h, str) or re.fullmatch('[0-9a-f]{64}', h) is None
            for p, h in value.items())):
        raise ValueError('Pinned path and SHA256 identities required')
    if any(str(Path(p).resolve()) != p for p in value):
        raise ValueError('Absolute canonical identity paths required')
    for path, expected in value.items():
        if sha(path) != expected: raise ValueError('Authenticated source or executable changed')
    return dict(value)


class CollectedVisits(WeightedPhysicalReservoir):
    def __init__(self, player, source, events):
        super().__init__(1, player, 0, source)
        self.events = events

    def _insert(self, row, iteration, *, deal_weight):
        # No retention RNG draw: the original ingester validates before these
        # events are filtered and later committed in their original order.
        self.events.append((self.player, row, iteration, deal_weight))
        self.seen += 1


def initialize(context_path, cache, targets, generation, iteration, executable,
               trace_executable, river_payload, river_executable,
               expected_native_identities, runtime_limits):
    global _STATE
    if (multiprocessing.current_process().name == 'MainProcess'
            or multiprocessing.get_start_method() != 'spawn'):
        raise RuntimeError('CPU river worker initialization requires a spawned child process')
    os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
    for name in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
        os.environ[name] = '1'
    from threadpoolctl import threadpool_limits
    limits = runtime(runtime_limits)
    paths = [str(Path(p).resolve()) for p in (context_path, executable, trace_executable, river_executable)]
    native_ids = identities(expected_native_identities)
    if any(p not in native_ids for p in paths):
        raise ValueError('Context, bridge, action trace and river executable identities required')
    fields = {'model_source', 'policy_id', 'registry', 'context_sha256', 'resources', 'resources_sha256'}
    if not isinstance(river_payload, dict) or set(river_payload) != fields:
        raise ValueError('Explicit typed frozen model and complete resource payload required')
    payload = river_payload; source = Path(context_path).read_text(encoding='utf-8')
    if (not isinstance(payload['model_source'], str)
            or hashlib.sha256(payload['model_source'].encode()).hexdigest() != payload['policy_id']
            or digest(payload['resources']) != payload['resources_sha256']):
        raise ValueError('Frozen model or complete resource bytes changed')
    model = json.loads(payload['model_source']); registry = payload['registry']; key = payload['context_sha256']
    if (type(iteration) is not int or not 1 <= iteration < 2**63
            or model['generation']+1 != iteration or key not in registry.fit_contexts
            or registry.source(key) != source or hashlib.sha256(source.encode()).hexdigest() != key
            or not isinstance(generation, DealWeightGeneration) or generation.context_source != source):
        raise ValueError('Current played generation, fitted context and qualified physical source required')
    engine = ExpectedPolicy(model, registry, context_sha256=key, resources=payload['resources'], device='cpu')
    if not isinstance(targets, InitialTargets) or targets.context_source != source:
        raise ValueError('Qualified original physical-ingest initial checks required')
    # These compatibility checks are constructed from the typed all-node model,
    # not from obsolete initial-state model documents or retained root tables.
    played = engine.played_preflop(); response = json.loads(source)['nodes'][0]['children'][3]
    matrix = payload['resources'][key]['matrix_source']
    actual = InitialTargets(matrix, source, played[0], played[response][:, 1],
        matrix_sha256=hashlib.sha256(matrix.encode()).hexdigest(), generation=model['generation'])
    if (targets.identity != actual.identity or targets.generation+1 != iteration
            or not np.array_equal(targets.root, actual.root)
            or not np.array_equal(targets.calls, actual.calls)
            or not np.array_equal(targets.jam, actual.jam, equal_nan=True)):
        raise ValueError('Original physical checks disagree with the actual typed played policy')
    weights = PhysicalDeals(source, mode='full_deck', seed=0).weights
    entry = [{tuple(map(int, pair)):float(w) for pair, w in zip(PAIRS, row)} for row in weights]
    source_paths = [Path(__file__).resolve(), Path(transport.__file__).resolve()]
    import preflop_expected_native_execution_v1 as execution
    source_paths.append(Path(execution.__file__).resolve())
    worker_sources = {str(p):sha(p) for p in source_paths}
    _STATE = dict(context_path=paths[0], executable=paths[1], trace_executable=paths[2],
        river_executable=paths[3], cache=cache, targets=targets, generation=generation, iteration=iteration,
        engine=engine, entry=entry, model_sha256=payload['policy_id'], context_sha256=key,
        registry_sha256=registry.sha256, resources_sha256=payload['resources_sha256'],
        native_identities=native_ids, worker_source_identities=worker_sources, runtime_limits=limits,
        thread_limit=threadpool_limits(limits=1), last_guard=0., began=time.monotonic(),
        qualified_ingest_identity=dict(cache_sha256=cache.sha256, targets=actual.identity,
            source_generation_sha256=generation.sha256))
    guard()


def guard():
    if _STATE is None: raise RuntimeError('Worker not initialized')
    s = _STATE; now = time.monotonic()
    if now-s['began'] > s['runtime_limits']['max_worker_seconds']:
        raise RuntimeError('Explicit worker time limit reached')
    if now-s['last_guard'] > 3:
        if psutil.virtual_memory().available < RECIPE['memory_headroom_bytes']:
            raise RuntimeError('Worker memory headroom exhausted')
        if 'folder' in s and psutil.disk_usage(s['folder'].anchor).free < RECIPE['disk_reserve_bytes']:
            raise RuntimeError('Worker disk reserve exhausted')
        listening = any(c.status == psutil.CONN_LISTEN and c.laddr.port == 56708
                        for c in psutil.net_connections(kind='tcp'))
        if listening and not idle(): raise RuntimeError('Production application became busy')
        s['last_guard'] = now


def serialized_events(events):
    return [dict(player=p, iteration=it, deal_weight=float(weight),
        row=dict(keys=[int(v) for v in row[0]], active=row[1].astype(int).tolist(),
                 arity=int(row[2]), advantages=row[3].tolist())) for p, row, it, weight in events]


def _checked_event(event, iteration, *, postflop_only):
    if not isinstance(event, (tuple, list)) or len(event) != 4:
        raise ValueError('Complete ordered weighted event required')
    player, row, it, weight = event
    if type(player) is not int or player not in (0, 1) or type(it) is not int or it != iteration:
        raise ValueError('Worker event actor or iteration mismatch')
    if not isinstance(row, (tuple, list)) or len(row) != 4:
        raise ValueError('Invalid worker row')
    keys, active, arity, values = row
    if (not isinstance(keys, (tuple, list)) or len(keys) != 2
            or any(type(v) is not int for v in keys)
            or not isinstance(active, np.ndarray) or active.dtype != np.uint16
            or active.shape != (36,) or type(arity) is not int
            or not isinstance(values, np.ndarray) or values.dtype != np.float64):
        raise ValueError('Exact checked reservoir row layout required')
    phases = [int(v)-135 for v in active if 135 <= v < 139]
    actors = [int(v)-133 for v in active if 133 <= v < 135]
    if (len(phases) != 1 or actors != [player]
            or (keys[0] >= 1 << 63) != (phases[0] in (1, 2, 3))
            or (postflop_only and phases[0] not in (1, 2, 3))):
        raise ValueError('Visible actor/street and postflop key must agree')
    checked = checked_row(dict(hi=str(keys[0]), lo=str(keys[1]), actor=player, n=arity,
        active_features=active.astype(int).tolist()), values)
    if not np.array_equal(active, checked[1]): raise ValueError('Canonical sorted active row required')
    return (player, checked, it, checked_weight(weight))


def _invoke(executable, arguments, label, part, inputs, invocations, timings):
    s = _STATE; guard(); began = time.monotonic()
    arguments = list(map(str, arguments))
    pinned = dict(s['native_identities'], **s['worker_source_identities'])
    pinned.update({str(Path(p).resolve()):sha(p) for p in inputs})
    result = run_native(executable, arguments, folder=part, label=label,
        expected_identities=pinned, guard=guard, timeout=s['runtime_limits']['native_timeout_seconds'])
    verify_native(result, executable=executable, arguments=arguments, expected_identities=pinned)
    invocations.append(dict(label=label, executable=str(executable), arguments=list(map(str, arguments)),
        expected_identities=pinned, stdin_path=None, result=result))
    timings[label] = time.monotonic()-began


def complete(part, start, expected_inputs):
    if _STATE is None: raise RuntimeError('Worker not initialized')
    began = time.monotonic(); part = Path(part).resolve(); s = _STATE; s['folder'] = part
    timings = {}; invocations = []; guard()
    identities(s['native_identities']); identities(s['worker_source_identities'])
    if type(start) is not int or start < 0: raise ValueError('Nonnegative subbatch offset required')
    paths = {n:part/f'{n}.json' for n in ('batch', 'queries', 'policies', 'updates', 'action-trace')}
    if expected_inputs != {n:sha(paths[n]) for n in ('batch', 'queries', 'policies')}:
        raise ValueError('Worker batch/query/policy bytes changed')
    if any(paths[n].exists() for n in ('updates', 'action-trace')):
        raise ValueError('Native output paths must be new')
    queries = json.loads(paths['queries'].read_text(encoding='utf-8'))
    policy = json.loads(paths['policies'].read_text(encoding='utf-8'))
    if (queries['context_source'] != s['engine'].context_source
            or queries['batch_source'] != paths['batch'].read_text(encoding='utf-8')):
        raise ValueError('Physical input source binding changed')
    s['last_guard'] = 0.; guard()
    response_hi = json.loads(queries['context_source'])['nodes'][0]['children'][3]+1
    prepared = s['engine'].prepare(first_action_view(queries, response_hi))
    probability = s['engine'].infer(prepared)
    supplied = np.asarray([r['probabilities'] for r in policy['policies']], dtype=np.float64)
    if (policy_document(queries, supplied) != policy or supplied.shape != probability.shape
            or np.max(abs(supplied-probability)) > 1e-10
            or not np.array_equal(supplied > 0, probability > 0)):
        raise ValueError('Supplied policy differs from the complete typed frozen model')
    binding = s['generation'].bind(queries, start)
    _invoke(s['executable'], ['verify', s['context_path'], paths['batch'], paths['policies'], paths['updates']],
        'native-updates', part, [paths['batch'], paths['queries'], paths['policies']], invocations, timings)
    _invoke(s['trace_executable'], [s['context_path'], paths['batch'], paths['policies'], paths['action-trace']],
        'native-trace', part, [paths['batch'], paths['queries'], paths['policies'], paths['updates']], invocations, timings)
    updates = json.loads(paths['updates'].read_text(encoding='utf-8'))
    trace = json.loads(paths['action-trace'].read_text(encoding='utf-8'))
    all_events = []; receivers = [CollectedVisits(p, queries['context_source'], all_events) for p in (0, 1)]
    t = time.monotonic()
    pinned = dict(s['native_identities'], **s['worker_source_identities'])
    pinned.update({str(p):sha(p) for p in paths.values()})
    overlay, evidence = transport.generate(queries, updates, policy, trace,
        generation=s['generation'], start=start, iteration=s['iteration'], policy_id=s['model_sha256'],
        case_id=json.loads(queries['batch_source'])['batch_id'], engine=s['engine'], entry=s['entry'],
        executable=s['river_executable'], context_path=s['context_path'], folder=part/'conditional',
        guard=guard, write=save, expected_identities=pinned,
        native_timeout_seconds=s['runtime_limits']['river_native_timeout_seconds'], native_invocations=invocations)
    timings['river-targets'] = time.monotonic()-t; t = time.monotonic()
    observed, initial, later, weighted, river = ingest(queries, updates, policy, receivers,
        s['iteration'], s['cache'], s['targets'], trace, generation=s['generation'], start=start,
        overlay=overlay, expected_policy_id=s['model_sha256'], expected_evidence_sha256=digest(evidence), guard=guard)
    positives = [(i, r) for i, r in enumerate(updates['records']) if r[2] > 0]
    if len(all_events) != len(positives): raise ValueError('Observed native visit count changed')
    events = []; records = []; excluded = [0, 0]; observed_records = []
    for (record, raw), event in zip(positives, all_events):
        p, row, it, weight = _checked_event(event, s['iteration'], postflop_only=False)
        qi, updater, n, _ = raw; o = queries['observations'][qi]
        if (p, row[0], row[2]) != (updater, (int(o['hi']), int(o['lo'])), n):
            raise ValueError('Qualified event moved away from its original visit')
        observed_records.append(dict(record=record, query=qi, player=p, phase=o['phase']))
        if o['phase'] == 0: excluded[p] += 1; continue
        if o['phase'] not in (1, 2, 3): raise ValueError('Unknown physical event phase')
        events.append((p, row, it, weight)); records.append(record)
    counts = np.bincount([e[0] for e in events], minlength=2).tolist()
    if [a+b for a, b in zip(counts, excluded)] != observed:
        raise ValueError('Postflop/excluded counts do not recover all observed visits')
    if weighted['binding'] != binding: raise ValueError('Original source weighting changed')
    timings['qualified-ingestion'] = time.monotonic()-t
    event_doc = dict(format=1, method=TYPE, start=start, iteration=s['iteration'],
        context_sha256=s['context_sha256'], model_sha256=s['model_sha256'],
        resources_sha256=s['resources_sha256'], counts=counts, observed_counts=observed,
        excluded_preflop_counts=excluded, observed_records=observed_records,
        event_records=records, events=serialized_events(events))
    for name, value in (('derived-targets', initial), ('postflop-targets', later),
            ('weighted-targets', weighted), ('river-targets', river), ('ordered-events', event_doc)):
        save(part/f'{name}.json', value)
    identities(s['native_identities']); identities(s['worker_source_identities']); guard()
    if expected_inputs != {n:sha(paths[n]) for n in ('batch', 'queries', 'policies')}:
        raise ValueError('Original batch/query/policy changed during native collection')
    return dict(format=1, worker_type=TYPE, recipe=copy.deepcopy(RECIPE), start=start,
        iteration=s['iteration'], counts=counts, observed_counts=observed, excluded_preflop_counts=excluded,
        native_record_counts=np.bincount([r[1] for r in updates['records']], minlength=2).tolist(),
        opponent_policy_record_counts=np.bincount([r[1] for r in updates['records'] if r[2] < 0], minlength=2).tolist(),
        query_observation_count=len(queries['observations']),
        events=events, event_records=records, observed_records=observed_records, event_document_sha256=digest(event_doc),
        binding=binding, input_identities=dict(expected_inputs), context_sha256=s['context_sha256'],
        registry_sha256=s['registry_sha256'], model_sha256=s['model_sha256'], resources_sha256=s['resources_sha256'],
        native_identities=s['native_identities'], worker_source_identities=s['worker_source_identities'],
        native_roles={k:s[k] for k in ('context_path', 'executable', 'trace_executable', 'river_executable')},
        qualified_ingest_identity=s['qualified_ingest_identity'], native_invocations=invocations,
        runtime_limits=s['runtime_limits'], cuda_visible_devices=os.environ.get('CUDA_VISIBLE_DEVICES'),
        inference_device=s['engine'].device, thread_limit=1, artifact_root=str(part),
        artifacts={str(p.relative_to(part)):sha(p) for p in part.rglob('*') if p.is_file()},
        river=dict(method=METHOD, K=64, replacements=len(overlay['rows']), evidence_sha256=digest(evidence)),
        timings=timings, seconds=time.monotonic()-began, pid=os.getpid(),
        rss_bytes=psutil.Process().memory_info().rss)


def pool(workers, **args):
    if type(workers) is not int or not 1 <= workers <= 4:
        raise ValueError('One to four explicitly admitted CPU workers required')
    if set(args) != set(_INIT_FIELDS): raise ValueError('Complete explicit worker initialization required')
    runtime(args['runtime_limits'])
    return ProcessPoolExecutor(max_workers=workers, mp_context=multiprocessing.get_context('spawn'),
        initializer=initialize, initargs=tuple(args[k] for k in _INIT_FIELDS))


def commit(result, reservoirs, *, expected_start, iteration, expected_context_sha256,
           expected_model_sha256, expected_registry_sha256, expected_resources_sha256,
           expected_native_identities, expected_runtime_limits, expected_artifact_root,
           expected_input_identities):
    """Validate the entire result and every event before any retention RNG draw.

    The runner additionally compares native_roles/worker_source_identities to its
    authenticated configuration and commits each subbatch in declared order.
    """
    if (result.get('format') != 1 or result.get('worker_type') != TYPE or result.get('recipe') != RECIPE
            or result.get('start') != expected_start or result.get('iteration') != iteration
            or result.get('context_sha256') != expected_context_sha256
            or result.get('model_sha256') != expected_model_sha256
            or result.get('registry_sha256') != expected_registry_sha256
            or result.get('resources_sha256') != expected_resources_sha256
            or result.get('native_identities') != expected_native_identities
            or result.get('runtime_limits') != runtime(expected_runtime_limits)
            or result.get('input_identities') != expected_input_identities
            or result.get('cuda_visible_devices') != '-1' or result.get('inference_device') != 'cpu'
            or result.get('thread_limit') != 1):
        raise ValueError('Worker result differs from the typed frozen collection contract')
    if (len(reservoirs) != 2 or any(not isinstance(r, WeightedPhysicalReservoir) or r.player != p
            or r.context_sha256 != expected_context_sha256
            or np.any(r.keys[:r.size, 0] < 1 << 63) for p, r in enumerate(reservoirs))):
        raise ValueError('Real matching postflop-only reservoirs required')
    root = Path(expected_artifact_root).resolve()
    if result.get('artifact_root') != str(root) or not isinstance(result.get('artifacts'), dict):
        raise ValueError('Unexpected native artifact root')
    for relative, identity in result['artifacts'].items():
        path = (root/relative).resolve()
        if not path.is_relative_to(root) or str(path.relative_to(root)) != relative or sha(path) != identity:
            raise ValueError('Worker artifact escaped its root or changed')
    for name in ('batch', 'queries', 'policies'):
        if sha(root/f'{name}.json') != expected_input_identities[name]:
            raise ValueError('Authenticated original worker inputs changed')
    identities(expected_native_identities); identities(result['worker_source_identities'])
    queries = json.loads((root/'queries.json').read_text(encoding='utf-8'))
    updates = json.loads((root/'updates.json').read_text(encoding='utf-8'))
    event_doc = json.loads((root/'ordered-events.json').read_text(encoding='utf-8'))
    expected_events = [_checked_event(e, iteration, postflop_only=True) for e in result['events']]
    if (any(event_doc.get(k) != result[k] for k in ('start', 'iteration', 'context_sha256',
            'model_sha256', 'resources_sha256')) or event_doc.get('format') != 1 or event_doc.get('method') != TYPE
            or digest(event_doc) != result['event_document_sha256'] or event_doc['events'] != serialized_events(expected_events)
            or event_doc['event_records'] != result['event_records']):
        raise ValueError('Returned event rows differ from retained ordered-event evidence')
    positives = [(i, r) for i, r in enumerate(updates['records']) if r[2] > 0]
    if (result.get('native_record_counts') != np.bincount([r[1] for r in updates['records']], minlength=2).tolist()
            or result.get('opponent_policy_record_counts') != np.bincount(
                [r[1] for r in updates['records'] if r[2] < 0], minlength=2).tolist()
            or result.get('query_observation_count') != len(queries['observations'])):
        raise ValueError('Complete native record and query accounting changed')
    observed = [0, 0]; excluded = [0, 0]; kept = []; observed_records = []
    for i, (qi, actor, arity, _) in positives:
        o = queries['observations'][qi]; phase = o['phase']; observed[actor] += 1
        observed_records.append(dict(record=i, query=qi, player=actor, phase=phase))
        if phase == 0: excluded[actor] += 1
        elif phase in (1, 2, 3): kept.append((i, qi, actor, arity))
        else: raise ValueError('Invalid source observation phase')
    if (observed_records != result['observed_records'] or observed_records != event_doc['observed_records']
            or observed != result['observed_counts'] or observed != event_doc['observed_counts']
            or excluded != result['excluded_preflop_counts'] or excluded != event_doc['excluded_preflop_counts']
            or [r[0] for r in kept] != result['event_records'] or len(kept) != len(expected_events)):
        raise ValueError('Observed and postflop insertion accounting changed')
    trace = json.loads((root/'action-trace.json').read_text(encoding='utf-8'))
    weighted = json.loads((root/'weighted-targets.json').read_text(encoding='utf-8'))
    overlay = json.loads((root/'conditional'/'overlay.json').read_text(encoding='utf-8'))
    evidence = json.loads((root/'conditional'/'evidence.json').read_text(encoding='utf-8'))
    if (result['river'] != dict(method=METHOD, K=64, replacements=len(overlay['rows']),
            evidence_sha256=digest(evidence)) or overlay['evidence_sha256'] != digest(evidence)
            or evidence['policy_id'] != expected_model_sha256 or weighted['binding'] != result['binding']
            or weighted['binding']['context_sha256'] != expected_context_sha256
            or weighted['binding']['start'] != expected_start):
        raise ValueError('Retained river evidence or source-deal weights changed')
    values = {v['record']:v['advantages'] for v in trace['conditional_targets']}
    values.update({v['record']:v['advantages'] for v in overlay['rows']})
    weights = {v['record']:v for v in weighted['records']}
    if (len(weights) != len(positives) or set(weights) != {v[0] for v in positives}
            or [v['record'] for v in overlay['rows']] != [i for i, r in positives
                if queries['observations'][r[0]]['phase'] == 3]):
        raise ValueError('Incomplete retained weighted visits or river overlay')
    counts = [0, 0]
    for (record, qi, actor, arity), (player, row, it, weight) in zip(kept, expected_events):
        o = queries['observations'][qi]
        if (player, row[0], row[2]) != (actor, (int(o['hi']), int(o['lo'])), arity):
            raise ValueError('Returned postflop visit order changed')
        witness = weights[record]; source = weighted['binding']; deal = witness['deal']
        if (type(deal) is not int or not 0 <= deal < len(source['deal_weights'])
                or witness['updater'] != actor or witness['source_deal'] != expected_start+deal
                or weight != witness['weight'] or weight != source['deal_weights'][deal]
                or not np.array_equal(row[1], np.asarray(sorted(o['active_features']), dtype=np.uint16))
                or not np.array_equal(row[3], np.asarray(values[record], dtype=np.float64))):
            raise ValueError('Postflop event differs from qualified source weight or target evidence')
        counts[player] += 1
    if (counts != result['counts'] or counts != event_doc['counts']
            or [a+b for a, b in zip(counts, excluded)] != observed
            or any(r.seen+n >= 2**63 for r, n in zip(reservoirs, counts))):
        raise ValueError('Postflop count mismatch or retention counter overflow')
    invocations = result.get('native_invocations')
    if not isinstance(invocations, list) or len(invocations) < 2:
        raise ValueError('Actual bridge and trace process receipts required')
    labels = [v['label'] for v in invocations]
    expected_labels = ['native-updates', 'native-trace'] + [f'chunk-{i:03d}-{mode}'
        for i in range(len(evidence['chunks'])) for mode in ('history', 'selected')]
    if labels != expected_labels or len(set(labels)) != len(labels):
        raise ValueError('Native invocation order or identity changed')
    roles = result['native_roles']; context = roles['context_path']
    for p in roles.values():
        if p not in expected_native_identities: raise ValueError('Unexpected executable/context role')
    for index, invocation in enumerate(invocations):
        pinned = invocation['expected_identities']
        if any(pinned.get(p) != h for p, h in expected_native_identities.items()):
            raise ValueError('Native process receipt lost pinned executable/input identities')
        if any(pinned.get(p) != h for p, h in result['worker_source_identities'].items()):
            raise ValueError('Native process receipt lost worker source identities')
        if index == 0:
            exe = roles['executable']; args = ['verify', context, str(root/'batch.json'),
                str(root/'policies.json'), str(root/'updates.json')]; stdin = None
        elif index == 1:
            exe = roles['trace_executable']; args = [context, str(root/'batch.json'),
                str(root/'policies.json'), str(root/'action-trace.json')]; stdin = None
        else:
            exe = roles['river_executable']; args = [context]
            stdin = str(root/'conditional'/(invocation['label']+'-request.json'))
            if not re.fullmatch(r'chunk-\d{3}-(history|selected)', invocation['label']):
                raise ValueError('Unexpected river request invocation')
            if pinned.get(stdin) != sha(stdin): raise ValueError('River request source identity changed')
        if (invocation['executable'] != exe or invocation['arguments'] != args
                or invocation['stdin_path'] != stdin):
            raise ValueError('Actual native command differs from the bound request')
        for ref in ('receipt_path', 'stdout_path', 'stderr_path'):
            path = Path(invocation['result'][ref]).resolve()
            if not path.is_relative_to(root) or str(path.relative_to(root)) not in result['artifacts']:
                raise ValueError('Process evidence is outside the authenticated artifact set')
        verify_native(invocation['result'], executable=exe, arguments=args,
            expected_identities=pinned, stdin_path=stdin)
        wanted_timeout = expected_runtime_limits['native_timeout_seconds' if index < 2
            else 'river_native_timeout_seconds']
        if invocation['result']['receipt']['timeout_seconds'] != wanted_timeout:
            raise ValueError('Actual native runtime limit differs from the declared worker contract')
        if index >= 2:
            raw = root/'conditional'/(invocation['label']+'-native.json')
            if sha(raw) != invocation['result']['stdout_sha256']:
                raise ValueError('Retained river export differs from the actual native process output')
    # All validation and provenance checks above precede the first real mutation.
    for player, row, it, weight in expected_events:
        reservoirs[player]._insert(row, it, deal_weight=weight)
    return counts
