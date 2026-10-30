"""Synthetic source controls only; no worker initialization or native execution."""
import ast
import copy
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

sys.dont_write_bytecode = True
STAGE = Path(__file__).resolve().parent
RESEARCH = Path(r'T:\Dev\GTOpen\tools\research')
sys.path[:0] = [str(STAGE), str(RESEARCH)]

import numpy as np
import preflop_expected_river_workers_v1 as worker
from weighted_physical_reservoir_v1 import WeightedPhysicalReservoir


def expect_rejected(function):
    try: function()
    except (ValueError, KeyError, TypeError): return
    raise AssertionError('Invalid synthetic control was accepted')


def transport_math_unchanged():
    original = ast.parse((RESEARCH/'stack_context_river_transport_v1.py').read_text(encoding='utf-8'))
    staged = ast.parse((STAGE/'preflop_expected_river_transport_v1.py').read_text(encoding='utf-8'))
    def math(tree):
        function = next(v for v in tree.body if isinstance(v, ast.FunctionDef) and v.name == 'generate')
        # The function's new explicit export parameters and private execution
        # helper are the only differences allowed within generate.
        function = copy.deepcopy(function)
        function.args.kwonlyargs = [v for v in function.args.kwonlyargs
            if v.arg not in ('expected_identities', 'native_timeout_seconds', 'native_invocations')]
        function.args.kw_defaults = [None]*len(function.args.kwonlyargs)
        function.body = [v for v in function.body if not isinstance(v, ast.FunctionDef)]
        return ast.dump(function, include_attributes=False)
    assert math(original) == math(staged), 'Posterior/draw/evaluate/overlay math changed'


def row(player, phase, key):
    active = np.asarray(sorted([*range(34), 133+player, 135+phase]), dtype=np.uint16)
    return ((key, 0), active, 2, np.array([1., -1., 0., 0.]))


def fixture(folder):
    source = '{}'; key = hashlib.sha256(source.encode()).hexdigest()
    roles = {name:str((folder/(name+'.fixture')).resolve()) for name in
        ('context_path', 'executable', 'trace_executable', 'river_executable')}
    for path in roles.values(): Path(path).write_text(source, encoding='utf-8')
    pinned = {path:worker.sha(path) for path in roles.values()}
    worker_sources = {str(Path(worker.__file__).resolve()):worker.sha(worker.__file__)}
    events = [(0, row(0, 1, (1 << 63)+1), 1, 2.), (1, row(1, 2, (1 << 63)+2), 1, 3.)]
    observations = []
    for actor, phase, token in ((0, 0, 1), (0, 1, (1 << 63)+1),
                                (1, 0, 2), (1, 2, (1 << 63)+2)):
        value = row(actor, phase, token)
        observations.append(dict(hi=str(token), lo='0', actor=actor, phase=phase, n=2,
            active_features=value[1].astype(int).tolist()))
    queries = dict(context_source=source, observations=observations)
    records = [[i, o['actor'], 2, [1., -1., 0., 0.]] for i, o in enumerate(observations)]
    updates = dict(records=records)
    observed_records = [dict(record=i, query=i, player=o['actor'], phase=o['phase'])
                        for i, o in enumerate(observations)]
    binding = dict(context_sha256=key, start=0, deal_weights=[2., 3.])
    weighted = dict(binding=binding, records=[dict(record=i, deal=i//2, updater=o['actor'],
        source_deal=i//2, weight=[2., 3.][i//2]) for i, o in enumerate(observations)])
    trace = dict(conditional_targets=[dict(record=i, advantages=records[i][3]) for i in range(4)])
    evidence = dict(policy_id='model', chunks=[])
    overlay = dict(rows=[], evidence_sha256=worker.digest(evidence))
    event_doc = dict(format=1, method=worker.TYPE, start=0, iteration=1, context_sha256=key,
        model_sha256='model', resources_sha256='resources', counts=[1, 1], observed_counts=[2, 2],
        excluded_preflop_counts=[1, 1], event_records=[1, 3], observed_records=observed_records,
        events=worker.serialized_events(events))
    (folder/'conditional').mkdir()
    for name, value in (('batch', {}), ('queries', queries), ('policies', {}),
            ('updates', updates), ('action-trace', trace), ('weighted-targets', weighted),
            ('ordered-events', event_doc), ('conditional/evidence', evidence), ('conditional/overlay', overlay)):
        worker.save(folder/(name+'.json'), value)
    runtime = dict(max_worker_seconds=1200, native_timeout_seconds=120, river_native_timeout_seconds=60)
    invocations = []
    for name, exe, args in (('native-updates', roles['executable'], ['verify', roles['context_path'],
                str(folder/'batch.json'), str(folder/'policies.json'), str(folder/'updates.json')]),
            ('native-trace', roles['trace_executable'], [roles['context_path'], str(folder/'batch.json'),
                str(folder/'policies.json'), str(folder/'action-trace.json')])):
        paths = {}
        for suffix in ('receipt', 'stdout', 'stderr'):
            path = folder/(name+'-'+suffix+'.synthetic'); path.write_text('{}')
            paths[suffix+'_path'] = str(path)
        paths['receipt'] = dict(timeout_seconds=120)
        invocations.append(dict(label=name, executable=exe, arguments=args,
            expected_identities=dict(pinned, **worker_sources), stdin_path=None, result=paths))
    inputs = {name:worker.sha(folder/(name+'.json')) for name in ('batch', 'queries', 'policies')}
    result = dict(format=1, worker_type=worker.TYPE, recipe=copy.deepcopy(worker.RECIPE), start=0,
        iteration=1, counts=[1, 1], observed_counts=[2, 2], excluded_preflop_counts=[1, 1],
        native_record_counts=[2, 2], opponent_policy_record_counts=[0, 0], query_observation_count=4,
        events=events, event_records=[1, 3], observed_records=observed_records,
        event_document_sha256=worker.digest(event_doc), context_sha256=key, model_sha256='model',
        registry_sha256='registry', resources_sha256='resources', native_identities=pinned,
        runtime_limits=runtime, input_identities=inputs, cuda_visible_devices='-1',
        inference_device='cpu', thread_limit=1, artifact_root=str(folder), worker_source_identities=worker_sources,
        binding=binding, native_roles=roles, native_invocations=invocations,
        river=dict(method=worker.METHOD, K=64, replacements=0, evidence_sha256=worker.digest(evidence)),
        artifacts={str(p.relative_to(folder)):worker.sha(p) for p in folder.rglob('*') if p.is_file()})
    args = dict(expected_start=0, iteration=1, expected_context_sha256=key,
        expected_model_sha256='model', expected_registry_sha256='registry', expected_resources_sha256='resources',
        expected_native_identities=pinned, expected_runtime_limits=runtime,
        expected_artifact_root=str(folder), expected_input_identities=inputs)
    return result, args, source


def reservoir_snapshot(reservoirs):
    return [(r.seen, copy.deepcopy(r.rng.bit_generator.state), r.keys.copy(), r.values.copy()) for r in reservoirs]


def unchanged(reservoirs, snapshot):
    for r, (seen, rng, keys, values) in zip(reservoirs, snapshot):
        assert r.seen == seen and r.rng.bit_generator.state == rng
        assert np.array_equal(r.keys, keys) and np.array_equal(r.values, values)


def main():
    transport_math_unchanged()
    before_environment = dict(os.environ)
    try: worker.initialize(*([None]*11))
    except RuntimeError as error: assert 'spawned child' in str(error)
    else: raise AssertionError('MainProcess CPU environment mutation was accepted')
    assert dict(os.environ) == before_environment
    # Invalid runtime limits are rejected without implicit study admission.
    expect_rejected(lambda:worker.runtime({}))
    expect_rejected(lambda:worker.runtime(dict(max_worker_seconds=True, native_timeout_seconds=120,
        river_native_timeout_seconds=60)))
    expect_rejected(lambda:worker.runtime(dict(max_worker_seconds=1200, native_timeout_seconds=120,
        river_native_timeout_seconds=61)))
    expect_rejected(lambda:worker._checked_event((0, row(0, 0, 1), 1, 1.), 1, postflop_only=True))
    with tempfile.TemporaryDirectory(prefix='river-source-control-') as temporary:
        result, args, source = fixture(Path(temporary).resolve())
        reservoirs = [WeightedPhysicalReservoir(4, p, p, source) for p in (0, 1)]
        snapshot = reservoir_snapshot(reservoirs)
        # Native verification is intentionally replaced: no child can launch.
        with patch.object(worker, 'verify_native', return_value={}):
            for mutate in (
                    lambda r:r['events'][1][1][3].__setitem__(0, float('nan')),
                    lambda r:r['events'].append((0, row(0, 0, 1), 1, 2.)),
                    lambda r:r['event_records'].reverse(),
                    lambda r:r['observed_counts'].__setitem__(0, 3),
                    lambda r:r['native_invocations'].pop(),
                    lambda r:r['native_invocations'][0]['arguments'].__setitem__(0, 'wrong-mode')):
                bad = copy.deepcopy(result); mutate(bad)
                expect_rejected(lambda:worker.commit(bad, reservoirs, **args))
                unchanged(reservoirs, snapshot)
            assert worker.commit(result, reservoirs, **args) == [1, 1]
            assert [r.seen for r in reservoirs] == [1, 1]
            assert all(int(r.keys[0, 0]) >= 1 << 63 for r in reservoirs)
    print(json.dumps(dict(passed=True, controls='source-only synthetic',
        transport_math_ast_identical=True, invalid_event_commit_preserves_reservoirs=True,
        valid_commit_preserves_postflop_order=True, main_process_environment_preserved=True,
        native_executions=0, sources={str(p):worker.sha(p) for p in
            (RESEARCH/'stack_context_river_transport_v1.py', STAGE/'preflop_expected_river_transport_v1.py',
             STAGE/'preflop_expected_river_workers_v1.py', Path(__file__).resolve())})))


if __name__ == '__main__': main()
