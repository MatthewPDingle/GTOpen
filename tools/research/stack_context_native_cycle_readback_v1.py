"""Replay saved joint-cycle evidence; no fresh native labels or network fitting."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
                  PYTHONDONTWRITEBYTECODE='1', CUDA_VISIBLE_DEVICES='-1')
import copy
import hashlib
import json
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, TimeoutError
from pathlib import Path
import sys
import time
import traceback
import numpy as np
import psutil
import stack_context_training_checkpoint_v1 as cp
import stack_context_full_policy_v1 as full
from stack_context_native_cycle_control_v4 import inputs_and_resources, fingerprint
from stack_context_board_targets_v1 import prepare
from sampled_allin_protocol_v3 import AllinCache
from sampled_physical_bank_v1 import histories
from sampled_visible_hybrid_checkpoint_v1 import encoded
from sampled_physical_root_evaluation_v1 import save, sha
from weighted_deal_binding_v1 import DealWeightGeneration
from exact_initial_training_ingest_v2 import InitialTargets, digest
from river_weighted_overlay_ingest_v1 import ingest
from weighted_physical_reservoir_v1 import ARRAYS
from river_matched_training_pilot_v1 import ROOT, OUT, LOCK, OTHER, production_available

NAME = 'stack-context-native-cycle-readback-v1'
STUDY = 'stack-context-native-cycle-control-v4'
STORE = Path('S:/GTOpen-research') / STUDY
GEOMETRY = Path('S:/GTOpen-research/stack-geometry-control-v1')
REG, ATTEMPT, RESULT, FAILURE = (OUT / (NAME + suffix + '.json')
                                for suffix in ('-registration', '-attempt', '-result', '-failure'))


def read(path):
    return json.loads(Path(path).read_bytes())


def guard():
    if (not production_available() or OTHER.exists() or psutil.virtual_memory().available < 24_000_000_000
            or psutil.disk_usage('S:/').free < 40_000_000_000):
        raise RuntimeError('Readback yields to production or resource pressure')


def context_readback(args):
    from threadpoolctl import threadpool_limits
    limits = threadpool_limits(limits=1)
    key, initial, expected, config, registry, resources, inputs, model_source, cache_path, cache_hash, collection = args
    guard()
    started = time.monotonic()
    source = registry.source(key)
    local_config = config['contexts'][key]
    folder = STORE / 'cycle-1' / key
    generation = read(folder / 'source-generation.json')
    replay_generation = initial['sampler'].sample(local_config['deals_per_generation'])
    if encoded(replay_generation) != encoded(generation):
        raise ValueError('Physical source generation does not replay')
    weighted = DealWeightGeneration(generation, source)
    current = read(folder / 'current-initial-policy.json')
    model = json.loads(model_source)
    if current['used_model']['sha256'] != hashlib.sha256(model_source.encode()).hexdigest():
        raise ValueError('Initial policy belongs to another model')
    if model['generation'] != 0 or current['context_sha256'] != key:
        raise ValueError('Expected first complete context cycle')
    prep = prepare(model_source=model_source, registry=registry, context_sha256=key, resources=resources,
                   physical_catalog_source=Path(inputs[key]['physical_catalog']).read_text(),
                   matrix_source=Path(inputs[key]['matrix']).read_text())
    root = np.asarray(current['root'])
    calls = np.asarray(current['calls'])
    if not np.array_equal(prep['pre'][0], root):
        raise ValueError('Retained current root policy differs from full model')
    response = json.loads(source)['nodes'][0]['children'][3]
    if not np.array_equal(prep['pre'][response][:, 1], calls):
        raise ValueError('Retained exact response differs from full model')
    targets = InitialTargets(Path(inputs[key]['matrix']).read_text(), source, root, calls,
                             matrix_sha256=resources[key]['matrix_sha256'], generation=0)
    if targets.identity != current['target_identity']:
        raise ValueError('Exact initial-target identity changed')
    cache = AllinCache(cache_path, cache_hash)
    subsize = local_config['deals_per_subbatch']
    records = []
    coverage = set()
    for chunk, start in enumerate(range(0, local_config['deals_per_generation'], subsize)):
        guard()
        part = folder / f'batch-{chunk:03d}'
        saved = read(part / 'worker-result.json')
        expected_seed = int(initial['action_rng'].integers(0, 2**63))
        batch, queries, policies, updates, trace = (read(part / (name + '.json'))
                                                 for name in ('batch', 'queries', 'policies', 'updates', 'action-trace'))
        if (batch['seed'] != expected_seed or batch['deals'] != generation['deals'][start:start+subsize]
                or queries['context_source'] != source or queries['batch_source'] != (part / 'batch.json').read_text()):
            raise ValueError('Subbatch lost sampler/action-RNG or native source binding')
        histories(queries['observations'])
        if saved['start'] != start or saved['context_sha256'] != key or saved['cuda_visible_devices'] != '-1':
            raise ValueError('Worker order/context/backend changed')
        if saved['model_sha256'] != current['used_model']['sha256'] or saved['registry_sha256'] != registry.sha256:
            raise ValueError('Worker is not bound to the frozen full model')
        for path, expected_hash in saved['native_identities'].items():
            if config['source_identities'].get(path) != expected_hash:
                raise ValueError('Unregistered native worker input')
        for name, expected_hash in saved['artifacts'].items():
            if sha(part / name) != expected_hash:
                raise ValueError('Retained worker artifact changed')
        for name, expected_hash in saved['input_identities'].items():
            if sha(part / (name + '.json')) != expected_hash:
                raise ValueError('Retained worker input changed')
        evidence = read(part / 'conditional/evidence.json')
        overlay = read(part / 'conditional/overlay.json')
        for name, expected_hash in evidence['artifacts'].items():
            if sha(part / 'conditional' / name) != expected_hash:
                raise ValueError('Conditional target evidence changed')
        counts, derived, later, weights, river = ingest(queries, updates, policies, initial['reservoirs'], 1,
            cache, targets, trace, generation=weighted, start=start, overlay=overlay,
            expected_policy_id=current['used_model']['sha256'], expected_evidence_sha256=digest(evidence), guard=guard)
        if counts != saved['counts']:
            raise ValueError('Replayed worker counts differ')
        for name, actual in (('derived-targets', derived), ('postflop-targets', later),
                             ('weighted-targets', weights), ('river-targets', river)):
            if encoded(actual) != encoded(read(part / (name + '.json'))):
                raise ValueError('Saved weighted derivation does not replay: ' + name)
        for query, actor, tag, _ in updates['records']:
            if tag > 0:
                row = queries['observations'][query]
                coverage.add((actor, row['phase'], row['n']))
        records.append(dict(chunk=chunk, counts=counts, river_replacements=len(overlay['rows'])))
    for actual, wanted in zip(initial['reservoirs'], expected['reservoirs']):
        if actual.summary() != wanted.summary() or actual.rng.bit_generator.state != wanted.rng.bit_generator.state:
            raise ValueError('Reservoir metadata or RNG does not replay')
        for name in ARRAYS:
            if not np.array_equal(getattr(actual, name), getattr(wanted, name)):
                raise ValueError('Reservoir array differs after ordered replay: ' + name)
    if (initial['sampler'].checkpoint() != expected['sampler'].checkpoint()
            or initial['action_rng'].bit_generator.state != expected['action_rng'].bit_generator.state):
        raise ValueError('Final sampler/action RNG changed')
    plan = read(folder / 'board-plan.json')
    evidence = read(folder / 'board-generation-evidence.json')
    if plan != initial['root_regret_state'].plan():
        raise ValueError('Board draw plan does not replay')
    delta = initial['root_regret_state'].step(plan, evidence, played_policy=root, exact_terms=prep['exact'])
    if not np.array_equal(delta, np.asarray(collection['root_delta'])):
        raise ValueError('Root update arithmetic changed')
    from preflop_allin_matrix_v1 import AllinMatrix
    matrix = AllinMatrix(read(inputs[key]['matrix']), source)
    exact = matrix.evaluate(root, calls)
    delta = initial['exact_btn_state'].step(1, calls, exact['btn_jam_mass'], exact['btn_fold_entries'], exact['btn_call_entries'])
    if not np.array_equal(delta, np.asarray(collection['exact_delta'])):
        raise ValueError('Exact response update arithmetic changed')
    for name in ('root_regret_state', 'exact_btn_state'):
        if initial[name].document() != expected[name].document():
            raise ValueError('Local accumulated model state does not replay')
    return dict(context_sha256=key, depth=registry._get(key)['context']['config']['stack'],
                subbatches=records, visited_actor_street_arity=sorted(coverage),
                reservoir_seen=[r.seen for r in initial['reservoirs']],
                exact_arrays_rng_and_accumulators=True, seconds=time.monotonic()-started)


def main():
    if any(p.exists() for p in (REG, ATTEMPT, RESULT, FAILURE, LOCK, OTHER)):
        raise ValueError('Existing readback attempt or active research owner')
    guard()
    main_result = OUT / (STUDY + '-result.json')
    main_registration = OUT / (STUDY + '-registration.json')
    result, spec = read(main_result), read(main_registration)
    if (not result['complete'] or not result['passed'] or result['completed_cycles'] != 1
            or result['scientific_comparison'] or result['accuracy_qualified']
            or result['registration_sha256'] != sha(main_registration)):
        raise ValueError('Successful bounded implementation control required')
    if (OUT / (STUDY + '-failure.json')).exists():
        raise ValueError('Control has conflicting terminal evidence')
    # Require the actual controller identity to be gone before touching saved state.
    owner = read(OUT / (STUDY + '-attempt.json'))
    try:
        process = psutil.Process(owner['pid'])
        if abs(process.create_time() - owner['process_created']) < .001:
            raise ValueError('Main controller is still live')
    except psutil.NoSuchProcess:
        pass
    identities = dict(spec['inputs'])
    identities.update({str(main_result): sha(main_result), str(main_registration): sha(main_registration)})
    for module in list(sys.modules.values()):
        path = getattr(module, '__file__', None)
        if path and Path(path).is_relative_to(ROOT) and Path(path).suffix == '.py':
            identities.setdefault(str(Path(path)), sha(path))
    identities[str(Path(__file__).resolve())] = sha(__file__)
    with LOCK.open('x') as stream:
        stream.write(str(os.getpid()))
    started = time.monotonic()
    try:
        save(REG, dict(inputs=identities, source_result_sha256=sha(main_result),
             maximum_seconds=1200, cpu_workers=4, fresh_native_calls=False, fitting=False,
             scope='Source-order, weights, full checkpoint and native artifact replay; not an independent poker oracle'))
        save(ATTEMPT, dict(pid=os.getpid(), process_created=psutil.Process().create_time(), registration_sha256=sha(REG)))
        for path, expected_hash in {**spec['inputs'], **result['artifacts']}.items():
            if sha(path) != expected_hash:
                raise ValueError('Control input/artifact changed: ' + path)
        entries = []
        for depth in (20, 40, 60, 100, 150, 200, 400):
            context = GEOMETRY / 'fixtures' / f'stack-{depth}-context.json'
            entries.append(dict(name=f'{depth}bb', split='heldout' if depth in (60, 150) else 'fit',
                                context_source=context.read_text(), public_document=read(GEOMETRY / f'stack-{depth}-public.json')))
        prepared = read(OUT / 'stack-context-resources-v1-result.json')
        registry, resources, inputs, _ = inputs_and_resources(entries, prepared)
        config = spec['config']
        initial_ref = read(STORE / 'initial.json')['checkpoint']
        initial = cp.restore_checkpoint(STORE / 'objects', initial_ref, config, registry, resources)
        expected = cp.restore_checkpoint(STORE / 'objects', result['checkpoint'], config, registry, resources)
        if fingerprint(expected) != result['restored_fingerprint'] or fingerprint(initial) != result['initial_fingerprint']:
            raise ValueError('Saved complete-state fingerprint differs')
        if expected['played_bank'] != [initial['next_model']] or expected['next_model'] in expected['played_bank']:
            raise ValueError('Final unplayed model was included in the played bank')
        model = full.read_model(STORE / 'objects', initial['next_model'], registry, resources)
        model_source = encoded(model).decode()
        metrics = read(STORE / 'cycle-1/metrics.json')
        collections = {row['context_sha256']: row for row in metrics['collections']}
        if set(collections) != set(registry.fit_contexts):
            raise ValueError('Incomplete or extra fitting context')
        review = read(OUT / 'stack-context-complete-allin-cache-v1-readback.json')
        args = [(key, initial['contexts'][key], expected['contexts'][key], config, registry, resources, inputs,
                 model_source, review['cache_artifact'], review['cache_sha256'], collections[key]) for key in registry.fit_contexts]
        with ProcessPoolExecutor(max_workers=4, mp_context=multiprocessing.get_context('spawn')) as pool:
            futures = [pool.submit(context_readback, arg) for arg in args]
            records = []
            for future in futures:
                while True:
                    guard()
                    if time.monotonic()-started > 1200:
                        raise RuntimeError('Readback runtime bound')
                    try:
                        records.append(future.result(timeout=1))
                        print(json.dumps(dict(context=records[-1]['depth'], replayed=True)), flush=True)
                        break
                    except TimeoutError:
                        if future.done():
                            future.result()
        coverage = {tuple(row) for context in records for row in context['visited_actor_street_arity']}
        if ({row[0] for row in coverage} != {0, 1} or {row[1] for row in coverage} != {0, 1, 2, 3}
                or {row[2] for row in coverage} != {2, 3, 4}):
            raise ValueError('Incomplete actual actor/street/action-menu coverage')
        for path, expected_hash in identities.items():
            if sha(path) != expected_hash:
                raise ValueError('Readback input changed')
        save(RESULT, dict(complete=True, passed=True, registration_sha256=sha(REG), source_result_sha256=sha(main_result),
             contexts=records, visited_actor_street_arity=sorted(coverage),
             complete_checkpoint_replayed=True, no_unplayed_model_in_average=True,
             seconds=time.monotonic()-started, training=False, preflop_accuracy_qualified=False,
             limits='Replay reuses qualified ingesters; no independent reconstruction of every posterior target or full native tree value.'))
    except BaseException as error:
        save(FAILURE, dict(error=repr(error), traceback=traceback.format_exc(), retry_allowed=False))
        raise
    finally:
        if LOCK.exists() and LOCK.read_text().strip() == str(os.getpid()):
            LOCK.unlink()


if __name__ == '__main__':
    main()
