"""Four-arm continuation with an explicit, evidence-bound chance-check correction.

Keep original failure, registration, models, seeds and cycle order within each
arm. Recover only the already-complete A-relative cycle two; never recollect it.
Other partial cycles and new terminal failures remain non-retryable.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
    CUBLAS_WORKSPACE_CONFIG=':4096:8', PYTHONDONTWRITEBYTECODE='1')
import argparse
import gc
import hashlib
import json
import multiprocessing as mp
from pathlib import Path
import sys
import time
import traceback
import uuid
import psutil
import torch
import stack_context_matched_learning_v1 as legacy
from stack_context_parallel_continuation_v1 import runtime_for, logical_bytes, require
from stack_context_paired_chance_v1 import chance_identity
from owned_research_archive_v1 import unpack
from board_prefix_publication_v1 import atomic_json
from sampled_physical_root_evaluation_v1 import sha, save
from board_study_storage_v1 import measure
from global_research_inventory_v3 import measure as inventory

NAME = 'stack-context-parallel-continuation-v2'
ARMS = tuple(legacy.ORDER)
PLAN = legacy.OUT/'STACK-CONTEXT-PARALLEL-CONTINUATION-V2-PLAN.md'
CONTROL = legacy.OUT/(NAME+'-check-result.json')
DIAGNOSIS = legacy.OUT/'stack-context-paired-chance-readback-v1-result.json'
AMENDMENT, STATUS, FAILURE, RESULT = (legacy.OUT/(NAME+s+'.json') for s in
    ('-amendment', '-status', '-failure', '-training-result'))
MAX_LOGICAL = 70_000_000_000
RECOGNIZED_FAILURE = "ValueError('Matched representations did not use identical physical/action/board streams')"


def known_failure():
    proof = legacy.read(DIAGNOSIS)
    require(proof['complete'] and proof['passed'] and proof['false_positive_parent_state_comparison']
        and not proof['actual_chance_mismatch'] and proof['exact_non_board_source_hash_matches'] == 70
        and proof['board_draw_matches'] == 5, 'Exact completed diagnosis required')
    require(legacy.read(legacy.FAILURE)['error'] == RECOGNIZED_FAILURE
        and sha(legacy.FAILURE) == proof['inputs'][str(legacy.FAILURE)], 'Unrecognized or altered failure')
    return proof


def recoverable_metric(arm, cycle, progress, raw):
    """Allow only the diagnosed complete publication failure, never a redo."""
    require(arm == 'A-relative' and cycle == 2 and progress['completed_cycles'] == 1,
        'Unregistered partial scientific cycle; preserve without retry')
    proof = known_failure()
    path = raw/'metrics.json'
    require(str(path) in proof['inputs'] and sha(path) == proof['inputs'][str(path)],
        'Completed recovery metrics differ from diagnosed evidence')
    metric = legacy.read(path)
    require(metric['completed_cycles'] == 2, 'Incomplete recovery cycle')
    return metric


def board_plan(raw, dest, key, expected, guard):
    direct = raw/key/'board-plan.json'
    if direct.exists():
        data = direct.read_bytes()
    else:
        plan = legacy.read(dest/'plan.json')
        job = next(j for j in plan['jobs'] if Path(j['source']).name == key and 'board-plan.json' in j['names'])
        path = Path(job['destination'])
        require(path.resolve().is_relative_to(dest.resolve()), 'Archive escaped its cycle')
        data = unpack(path, legacy.read(path.with_suffix('.xz.json')), guard=guard)['board-plan.json']
    require(hashlib.sha256(data).hexdigest() == expected, 'Changed original board-plan bytes')
    return json.loads(data)


def chance_receipt(arm, cycle, used_model, raw_sources, spec, rt, guard):
    folder = legacy.STORE/arm
    parent = legacy.full.read_model(folder/'objects', used_model, rt['registry'], rt['resources'])
    require(parent['generation'] == cycle-1, 'Wrong generation for chance parent')
    chance = {}; compared = dict(raw_sources)
    for key in rt['registry'].fit_contexts:
        name = key+'/board-plan.json'
        plan = board_plan(folder/f'cycle-{cycle:04d}', folder/f'archive-{cycle:04d}', key, raw_sources[name], guard)
        chance[key] = chance_identity(plan, parent_state=parent['local_states'][key]['board_root_state'],
            expected_config=spec['arms'][arm]['config']['contexts'][key]['board_root'])
        compared[name] = chance[key]['chance_sha256']
    return dict(format=1, arm=arm, cycle=cycle, registration_sha256=sha(legacy.REG),
        parent_model=used_model, original_source_hashes=raw_sources, board_chance=chance,
        matched_input_identities=compared, own_parent_validated=True,
        comparator_sha256=sha(Path(__file__).with_name('stack_context_paired_chance_v1.py')))


def compare_receipts(a, b):
    require(a['cycle'] == b['cycle'] and a['arm'][0] == b['arm'][0]
        and a['arm'] != b['arm'] and a['own_parent_validated'] and b['own_parent_validated']
        and a['registration_sha256'] == b['registration_sha256']
        and a['comparator_sha256'] == b['comparator_sha256'], 'Wrong matching receipt identities')
    require(a['matched_input_identities'] == b['matched_input_identities'],
        'Physical/action/board chance inputs genuinely differ')


def publish_receipt(receipt):
    path = legacy.STORE/receipt['arm']/f"chance-{receipt['cycle']:04d}.json"
    if path.exists():require(legacy.read(path) == receipt, 'Changed immutable chance evidence')
    else:atomic_json(path, receipt)
    partner = receipt['arm'][0]+('-relative' if receipt['arm'].endswith('baseline') else '-baseline')
    other = legacy.STORE/partner/path.name
    if other.exists():compare_receipts(receipt, legacy.read(other))
    return path


def validate_boundaries(spec, prepared, *, write_receipts=False, guard=lambda:None):
    """Restore every published checkpoint and authenticate its archived prefix."""
    result = {}
    for arm in ARMS:
        folder = legacy.STORE/arm; progress = legacy.read(folder/'progress.json')
        rt = runtime_for(arm, spec, prepared); cfg = spec['arms'][arm]['config']
        n = progress['completed_cycles']
        require(progress['registration_sha256'] == sha(legacy.REG) and type(n) is int
            and 1 <= n <= 64 and len(progress['updates']) == n, 'Invalid existing prefix')
        state = legacy.checkpoint.restore_checkpoint(folder/'objects', progress['checkpoint'], cfg, rt['registry'], rt['resources'])
        require(state['completed_cycles'] == n, 'Progress/checkpoint count differs')
        for cycle, record in enumerate(progress['updates'], 1):
            dest = folder/f'archive-{cycle:04d}'
            require(record['cycle'] == cycle and record['archive'] == str(dest.relative_to(legacy.STORE))
                and sha(dest/'index.json') == record['archive_index_sha256']
                and sha(dest/'retired.json') == record['retirement_sha256'], 'Unverified published archive')
            if write_receipts:
                receipt = chance_receipt(arm, cycle, state['played_bank'][cycle-1], record['paired_sources'], spec, rt, guard)
                publish_receipt(receipt)
        raw = folder/f'cycle-{n+1:04d}'; dest = folder/f'archive-{n+1:04d}'
        if raw.exists():
            require(not dest.exists(), 'Partial archive needs separate transport review')
            metric = recoverable_metric(arm, n+1, progress, raw)
            require(metric['used_model'] == state['next_model'], 'Wrong recovered parent model')
            recovered = legacy.checkpoint.restore_checkpoint(folder/'objects', metric['checkpoint'], cfg, rt['registry'], rt['resources'])
            require(recovered['completed_cycles'] == 2 and recovered['next_model'] == metric['next_model']
                and recovered['played_bank'][-1] == metric['used_model'], 'Invalid complete recovery checkpoint')
        else:require(not dest.exists(), 'Unpublished archive without raw requires review')
        result[arm] = n
    return result


def boundary_stop(stop, began):
    return stop.is_set() or time.monotonic()-began >= 12*3600


def arm_loop(arm, spec, rt, native, guard, stop, publish):
    cache = legacy.AllinCache(spec['cache_artifact'], spec['cache_sha256'])
    began = time.monotonic(); folder = legacy.STORE/arm; objects = folder/'objects'
    cfg = spec['arms'][arm]['config']; registry, resources = rt['registry'], rt['resources']
    progress = legacy.read(folder/'progress.json')
    for cycle in range(progress['completed_cycles']+1, 65):
        if boundary_stop(stop, began):return False
        state = legacy.checkpoint.restore_checkpoint(objects, progress['checkpoint'], cfg, registry, resources)
        require(state['completed_cycles'] == cycle-1, 'Missing sequential cycle boundary')
        guard(); raw = folder/f'cycle-{cycle:04d}'; dest = folder/f'archive-{cycle:04d}'
        def stage(phase, key=None):publish('training', cycle=cycle, phase=phase, context_sha256=key)
        stage('start')
        recovered = raw.exists()
        if recovered:
            require(not dest.exists(), 'Partial archive requires transport review')
            metric = recoverable_metric(arm, cycle, progress, raw)
            require(metric['used_model'] == state['next_model'], 'Wrong recovered source model')
            candidate = legacy.checkpoint.restore_checkpoint(objects, metric['checkpoint'], cfg, registry, resources)
        else:
            require(not dest.exists(), 'Unpublished archive; no scientific retry')
            candidate, _, metric = legacy.pipeline.update(raw, objects, state, cfg, registry, resources,
                inputs=rt['inputs'], cache=cache, native=native, guard=guard, workers=4, board_workers=1,
                batch_prefix=legacy.NAME+'-'+arm[0], on_stage=stage)
        restored = legacy.checkpoint.restore_checkpoint(objects, metric['checkpoint'], cfg, registry, resources)
        require(restored['next_model'] == candidate['next_model'] and restored['completed_cycles'] == cycle
            and restored['played_bank'][-1] == state['next_model'], 'Complete checkpoint restore differs')
        raw_sources = legacy.paired_sources(raw, dest, registry.fit_contexts)
        receipt = chance_receipt(arm, cycle, state['next_model'], raw_sources, spec, rt, guard)
        proof = publish_receipt(receipt)
        stage('archive-completed-evidence')
        archived = legacy.archive.archive_cycle(raw, dest, root=legacy.STORE, token=legacy.TOKEN, guard=guard, workers=4)
        record = dict(cycle=cycle, checkpoint=metric['checkpoint'], archive=str(dest.relative_to(legacy.STORE)),
            archive_index_sha256=sha(dest/'index.json'), retirement_sha256=sha(dest/'retired.json'),
            collection_seconds=metric['seconds'], packed_bytes=archived['packed_bytes'], paired_sources=raw_sources,
            chance_receipt_sha256=sha(proof), continuation_amendment_sha256=sha(AMENDMENT),
            recovered_without_scientific_repeat=recovered)
        progress = dict(progress, completed_cycles=cycle, checkpoint=metric['checkpoint'], updates=[*progress['updates'],record])
        atomic_json(folder/'progress.json', progress, replace=True)
        stage('checkpoint-published')
        print(json.dumps(dict(stage='complete-cycle', arm=arm, cycle=cycle, seconds=metric['seconds'],
            packed_bytes=archived['packed_bytes'], recovered_without_repeat=recovered)), flush=True)
        del state, candidate, restored; gc.collect()
    return True


def worker(arm, spec, native, stop, invocation):
    path = legacy.OUT/(NAME+'-'+arm+'-status.json')
    outcome = legacy.STORE/(NAME+'-'+invocation+'-'+arm+'.json')
    def publish(stage, **values):
        atomic_json(path, dict(stage=stage, arm=arm, pid=os.getpid(), process_created=psutil.Process().create_time(),
            unix=time.time(), **{k:v for k,v in values.items() if k != 'arm'}), replace=True)
    try:
        legacy.status = publish
        publish('loading-existing-arm')
        rt = runtime_for(arm, spec, legacy.read(legacy.OUT/'stack-context-population-v1-result.json'))
        torch.set_num_threads(1); torch.use_deterministic_algorithms(True)
        torch.backends.cuda.matmul.allow_tf32 = False; torch.backends.cudnn.allow_tf32 = False
        torch.cuda.set_per_process_memory_fraction(2_000_000_000/torch.cuda.get_device_properties(0).total_memory)
        guard = legacy.Guard(legacy.read(legacy.ATTEMPT)['admitted_unix']); guard.last_size = float('inf')
        complete = arm_loop(arm, spec, rt, native, guard, stop, publish)
        save(outcome, dict(arm=arm, complete=complete, stopped_at_complete_boundary=not complete,
            pid=os.getpid(), process_created=psutil.Process().create_time(), unix=time.time(),
            progress_sha256=sha(legacy.STORE/arm/'progress.json')))
        publish('arm-complete' if complete else 'complete-boundary-awaiting-resume')
    except BaseException as error:
        stop.set()
        save(outcome, dict(arm=arm, failed=True, error=repr(error), traceback=traceback.format_exc(),
            automatic_retry_allowed=False, pid=os.getpid(), process_created=psutil.Process().create_time()))
        publish('terminal-failure')
        raise


def main(run=False):
    if not run:
        print(json.dumps(dict(prepared=True, admitted=AMENDMENT.exists(), control_passed=CONTROL.exists(),
            research_owner_present=legacy.LOCK.exists(), new_failure=FAILURE.exists(), maximum_concurrent_arms=4)))
        return
    require(not legacy.LOCK.exists() and not legacy.OTHER.exists() and not FAILURE.exists()
        and not RESULT.exists() and not legacy.RESULT.exists(), 'Live owner or terminal outcome; no duplicate/retry')
    known_failure()
    control = legacy.read(CONTROL)
    require(control['passed'] and control['complete'] and control['runner_sha256'] == sha(__file__), 'Qualified runner required')
    legacy.verify(control['inputs'])
    spec = legacy.read(legacy.REG); legacy.verify(spec['inputs'])
    require(time.time()-legacy.read(legacy.ATTEMPT)['admitted_unix'] < 72*3600, 'Original deadline reached')
    ready, probe = legacy.available()
    if not ready or psutil.virtual_memory().available < 40_000_000_000 or probe['free_bytes'] < 12_000_000_000:
        print(json.dumps(dict(deferred=True, reason='resource-admission', probe=probe, training_started=False))); return
    accounting = inventory(); allocated = sum(row['allocated_file_bytes'] for row in accounting)
    own = measure(legacy.STORE)['allocated_file_bytes']
    require(allocated+max(0, MAX_LOGICAL-own) <= 800_000_000_000, 'Expanded transient reservation exceeds cap')
    prepared = legacy.read(legacy.OUT/'stack-context-population-v1-result.json')
    boundaries = validate_boundaries(spec, prepared)
    native = {key:legacy.ROOT/'target/release/examples'/name for key,name in dict(
        bridge='hu_sampled_allin_history_bridge_v1.exe', trace='hu_sampled_action_trace_v2.exe',
        integration='hu_sampled_profile_allin_evaluation_v1.exe', river='hu_river_two_stage_stream_v1.exe',
        board='hu_fixed_board_tree_v1.exe').items()}
    for path in native.values():require(sha(path) == spec['inputs'][str(path)], 'Changed executable')
    amendment = dict(format=1, original_registration_sha256=sha(legacy.REG), original_failure_sha256=sha(legacy.FAILURE),
        diagnosis_sha256=sha(DIAGNOSIS), runner_sha256=sha(__file__), plan_sha256=sha(PLAN), check_sha256=sha(CONTROL),
        purpose='User-authorized parallel continuation and diagnosed false-positive comparison correction',
        correction='Validate each complete board plan against its own parent; compare chance fields across arms',
        failed_evidence_preserved=True, scientific_cycles_retried=False, seeds_models_targets_fits_unchanged=True,
        cycles_per_arm=64, maximum_concurrent_arms=4, target_workers_per_arm=4, board_workers_per_arm=1,
        cuda_bytes_per_arm=2_000_000_000, combined_cuda_bytes=8_000_000_000,
        logical_reservation=MAX_LOGICAL, global_allocated_cap=800_000_000_000, original_deadline_unchanged=True,
        evaluation_gates_unchanged=True, production_modified=False)
    if AMENDMENT.exists():require(legacy.read(AMENDMENT) == amendment, 'Changed amendment')
    with legacy.LOCK.open('x') as stream:stream.write(str(os.getpid()))
    invocation = uuid.uuid4().hex; ctx = mp.get_context('spawn'); stop = ctx.Event(); processes = []
    try:
        if not AMENDMENT.exists():save(AMENDMENT, amendment)
        save(legacy.STORE/(NAME+'-invocation-'+invocation+'.json'), dict(pid=os.getpid(),
            process_created=psutil.Process().create_time(), unix=time.time(), boundaries=boundaries, admission=accounting))
        validate_boundaries(spec, prepared, write_receipts=True)
        for arm in ARMS:
            if boundaries[arm] == 64:continue
            process = ctx.Process(target=worker, args=(arm,spec,native,stop,invocation), name=arm)
            process.start(); processes.append((arm,process))
        last_report = 0.; pressure = None
        while any(p.is_alive() for _,p in processes):
            for _,p in processes:
                if p.exitcode not in (None,0):stop.set()
            if time.monotonic()-last_report > 30:
                size = logical_bytes(legacy.STORE)
                if size > MAX_LOGICAL:pressure='Logical cap exceeded'; stop.set()
                atomic_json(STATUS, dict(stage='parallel-training' if not stop.is_set() else 'draining-current-cycles',
                    pid=os.getpid(), process_created=psutil.Process().create_time(), unix=time.time(), logical_bytes=size,
                    arms=[dict(arm=a,pid=p.pid,alive=p.is_alive(),exit_code=p.exitcode) for a,p in processes]), replace=True)
                last_report = time.monotonic()
            for _,p in processes:p.join(timeout=.2)
        failed = [(a,p.exitcode) for a,p in processes if p.exitcode != 0]
        require(not failed and pressure is None, 'Parallel failure requires review: '+repr((failed,pressure)))
        outcomes = [legacy.read(legacy.STORE/(NAME+'-'+invocation+'-'+a+'.json')) for a,_ in processes]
        require(all(not row.get('failed') for row in outcomes), 'Arm failure; no automatic retry')
        legacy.verify(spec['inputs'])
        boundaries = validate_boundaries(spec, prepared)
        complete = all(n == 64 for n in boundaries.values())
        if complete:
            for seed in ('A','B'):
                for cycle in range(1,65):
                    compare_receipts(*(legacy.read(legacy.STORE/(seed+'-'+rep)/f'chance-{cycle:04d}.json')
                        for rep in ('baseline','relative')))
            save(RESULT, dict(training_complete=True, scientific_evaluation_complete=False, accuracy_qualified=False,
                registration_sha256=sha(legacy.REG), continuation_amendment_sha256=sha(AMENDMENT),
                original_failure_sha256=sha(legacy.FAILURE), arms={a:legacy.read(legacy.STORE/a/'progress.json') for a in ARMS},
                storage=measure(legacy.STORE), production_modified=False))
        atomic_json(STATUS, dict(stage='training-complete-awaiting-fresh-evaluation' if complete else 'complete-boundary-awaiting-resume',
            pid=os.getpid(),process_created=psutil.Process().create_time(),unix=time.time(),completed_cycles=boundaries), replace=True)
    except BaseException as error:
        stop.set()
        for _,p in processes:p.join()
        save(FAILURE,dict(error=repr(error),traceback=traceback.format_exc(),automatic_retry_allowed=False,
            invocation=invocation,original_registration_sha256=sha(legacy.REG)))
        raise
    finally:
        if legacy.LOCK.exists() and legacy.LOCK.read_text() == str(os.getpid()):legacy.LOCK.unlink()


if __name__ == '__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--run',action='store_true')
    main(run=parser.parse_args().run)
