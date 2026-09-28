"""Four/eight-worker full-state equivalence and bounded paired timing replay.

Runs only after successful pilot analysis. Every case restores the same source
boundary; no case extends scientific training or supplies new evaluation deals.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
                  CUBLAS_WORKSPACE_CONFIG=':4096:8', PYTHONDONTWRITEBYTECODE='1')
import argparse
import gc
import json
from pathlib import Path
import sys
import time
import traceback
import uuid
import numpy as np
import psutil
import river_matched_training_pilot_v1 as pilot
from board_training_pipeline_wait_v1 import update as baseline_four
from river_training_pipeline_wait_v1 import update as river_four
from board_training_pipeline_eight_v2 import update as baseline_eight
from river_training_pipeline_eight_v2 import update as river_eight

NAME = 'eight-worker-full-update-control-v1'
OUT = pilot.OUT
REG = OUT/(NAME+'-registration.json')
RESULT = OUT/(NAME+'-result.json')
STATUS = OUT/(NAME+'-status.json')
STORE = Path('S:/GTOpen-research')/NAME
PLAN = OUT/'EIGHT-WORKER-FULL-UPDATE-PLAN.md'
PILOT_STORE = pilot.STORE
PILOT_REG = pilot.REG
PILOT_RESULT = pilot.RESULT
PILOT_STATUS = pilot.STATUS
REVIEW = OUT/'river-matched-training-pilot-v1-independent-review-v2.json'
LIMIT = 6_000_000_000
MAX_SECONDS = 5400
CASES = (('baseline-four', 'A-baseline', 4), ('baseline-eight', 'A-baseline', 8),
         ('river-eight', 'A-river', 8), ('river-four', 'A-river', 4))
UPDATES = {('baseline', 4): baseline_four, ('baseline', 8): baseline_eight,
           ('river', 4): river_four, ('river', 8): river_eight}


def terminal_pilot():
    state = pilot.read(PILOT_STATUS)
    try:
        process = psutil.Process(state['pid'])
        if process.is_running() and process.create_time() == state['process_created']:
            return False
    except psutil.NoSuchProcess:
        pass
    return PILOT_RESULT.exists() and REVIEW.exists()


def specification():
    assert terminal_pilot(), 'Wait for successful pilot termination and independent readback'
    result, review = pilot.read(PILOT_RESULT), pilot.read(REVIEW)
    assert result['passed'] and result['complete'] and review['passed']
    assert review['source_result_sha256'] == pilot.sha(PILOT_RESULT)
    reg = pilot.read(PILOT_REG)
    assert result['registration_sha256'] == pilot.sha(PILOT_REG)
    amendment = Path(result['execution_amendment'])
    assert pilot.sha(amendment) == result['execution_amendment_sha256']
    amendment_doc = pilot.read(amendment)
    assert amendment_doc['unchanged_science']
    dispatch_reg = OUT/'eight-worker-training-control-v3-registration.json'
    dispatch_result = OUT/'eight-worker-training-control-v3-result.json'
    dispatch = pilot.read(dispatch_result)
    assert dispatch['passed'] and dispatch['registration_sha256'] == pilot.sha(dispatch_reg)
    assert len(dispatch['cases']) == 32 and dispatch['guarded_waits']
    inputs = dict(amendment_doc['inputs'])
    for path, digest in pilot.read(dispatch_reg)['inputs'].items():
        assert path not in inputs or inputs[path] == digest
        inputs[path] = digest
    paths = [Path(__file__), PLAN, PILOT_REG, PILOT_RESULT, REVIEW, amendment,
             dispatch_reg, dispatch_result]
    oracles = {}
    for name in ('A-baseline', 'A-river'):
        progress_path = PILOT_STORE/name/'progress.json'
        progress = pilot.read(progress_path)
        assert progress['completed'] == 80 and progress['updates'][0]['iteration'] == 79
        metric_path = PILOT_STORE/name/progress['updates'][0]['metrics']
        assert pilot.sha(metric_path) == progress['updates'][0]['sha256']
        metric = pilot.read(metric_path)
        assert metric['iteration'] == 79 and metric['used_model']['generation'] == 78
        assert metric['workers'] == metric['board_workers'] == 4
        paths.extend([progress_path, metric_path])
        oracles[name] = dict(metrics=str(metric_path), sha256=pilot.sha(metric_path),
                             checkpoint=metric['checkpoint'])
    for module in list(sys.modules.values()):
        path = getattr(module, '__file__', None)
        if path and Path(path).is_relative_to(pilot.ROOT) and Path(path).suffix == '.py':
            paths.append(Path(path))
    inputs.update({str(path): pilot.sha(path) for path in paths})
    pilot.verify(inputs)
    return dict(format=1, inputs=inputs, oracles=oracles,
        source_registration_sha256=pilot.sha(PILOT_REG), source_boundary=78, output_boundary=79,
        cases=[dict(name=n, arm=a, workers=w) for n, a, w in CASES], board_workers=4,
        maximum_seconds=MAX_SECONDS, maximum_new_bytes=LIMIT, reserve_bytes=2_000_000_000,
        global_allocated_cap=pilot.GLOBAL_LIMIT, initial_resource_wait_seconds=3600,
        repeated_existing_training_deals=True, new_evaluation_deals=0,
        requirements='Exact complete checkpoint/state and per-subbatch identity against original four-worker scientific update.',
        timing='One fresh four/eight pair per method with reversed order; descriptive wall time, no statistical speedup guarantee.',
        gpu_sharing='Existing pilot guard: light desktop allowed; active solves/heavy workloads have priority.',
        production_modified=False)


def validate(folder, arm, metric, oracle, args, guard):
    guard()
    assert metric['iteration'] == 79 and metric['used_model'] == oracle['used_model']
    assert metric['checkpoint'] == oracle['checkpoint']
    assert metric['next_model'] == oracle['next_model']
    assert metric['subbatches'] == oracle['subbatches']
    assert metric['exact_btn_delta'] == oracle['exact_btn_delta']
    assert metric['reservoirs'] == oracle['reservoirs']
    current = pilot.checkpoint.restore_checkpoint(folder/'objects', metric['checkpoint'],
        arm['config'], **pilot.model_args(args, arm))
    original = pilot.checkpoint.restore_checkpoint(PILOT_STORE/arm['name']/'objects', oracle['checkpoint'],
        arm['config'], **pilot.model_args(args, arm))
    pilot.compare_states(current, original)
    assert current['completed_iterations'] == 79
    assert current['played_bank'][-1]['generation'] == 78 and current['next_model']['generation'] == 79
    del current, original
    gc.collect()


def main(run=False, resume=False, wait=False):
    if not run:
        print(json.dumps(dict(source_prepared=True, pilot_and_review_terminal=terminal_pilot(),
            training_started=False, new_evaluation_deals=0)), flush=True)
        return
    spec = specification()
    assert not RESULT.exists()
    if resume:
        assert pilot.read(REG) == spec
    else:
        assert not REG.exists() and not STORE.exists()
        pilot.atomic_json(REG, spec)
    began = time.monotonic()
    while True:
        ready, probe = pilot.available()
        if ready:
            break
        if not wait or time.monotonic()-began > spec['initial_resource_wait_seconds']:
            print(json.dumps(dict(waiting_for_resources=True, registration=str(REG))), flush=True)
            return
        time.sleep(15)
    acquired = False
    # Reuse the guarded resource semantics in this separate process only.
    pilot.STORE, pilot.STATUS, pilot.LIMIT = STORE, STATUS, LIMIT
    try:
        with pilot.LOCK.open('x') as handle:
            handle.write(str(os.getpid()))
        acquired = True
        inventory = pilot.global_measure()
        allocated = sum(row['allocated_file_bytes'] for row in inventory)
        used = pilot.study_measure(STORE)['allocated_file_bytes'] if STORE.exists() else 0
        assert allocated+max(0, LIMIT-used)+spec['reserve_bytes'] <= pilot.GLOBAL_LIMIT
        if not STORE.exists():
            pilot.create(STORE)
        pilot.atomic_json(STORE/('admission-'+uuid.uuid4().hex[:8]+'.json'), dict(
            registration_sha256=pilot.sha(REG), allocated_bytes=allocated, inventory=inventory,
            reserved_bytes=max(0, LIMIT-used)+spec['reserve_bytes'], gpu=probe,
            pid=os.getpid(), process_created=psutil.Process().create_time(), unix=time.time()))
        pilot.verify(spec['inputs'])
        original_reg = pilot.read(PILOT_REG)
        source = pilot.CONTEXT.read_text()
        matrix = pilot.AllinMatrix(pilot.read(pilot.MATRIX), source)
        args = dict(context_source=source, catalog_source=pilot.CATALOG.read_text(),
            matrix_sha256=pilot.sha(pilot.MATRIX), entry_mass=matrix.btn_mass)
        cache_review = pilot.read(OUT/'complete-private-allin-cache-v2-independent-review.json')
        assert cache_review['passed']
        cache = pilot.AllinCache(cache_review['cache_artifact'], cache_review['cache_sha256'])
        import torch
        assert torch.cuda.is_available()
        for name in ('A-baseline', 'A-river'):
            cfg = original_reg['arms'][name]['config']
            assert cfg['torch_version'] == torch.__version__ and cfg['numpy_version'] == np.__version__
        torch.set_num_threads(1)
        torch.use_deterministic_algorithms(True)
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        torch.cuda.set_per_process_memory_fraction(pilot.CUDA_BUDGET_BYTES/torch.cuda.get_device_properties(0).total_memory)
        resources = pilot.Guard()
        def guard():
            assert time.monotonic()-resources.started < MAX_SECONDS
            resources()
        records = []
        for case, name, workers in CASES:
            guard()
            arm = dict(original_reg['arms'][name], name=name)
            folder = STORE/case
            folder.mkdir(exist_ok=True)
            proof_path = folder/'complete.json'
            oracle = pilot.read(spec['oracles'][name]['metrics'])
            if proof_path.exists():
                proof = pilot.read(proof_path)
                assert proof['registration_sha256'] == pilot.sha(REG)
                metric_path = folder/proof['metrics']
                assert pilot.sha(metric_path) == proof['metrics_sha256']
                metric = pilot.read(metric_path)
            else:
                state, fork = pilot.copy_source(folder, arm, args)
                assert state['completed_iterations'] == 78
                destination = folder/('update-'+uuid.uuid4().hex[:8])
                step = pilot.step_arguments(arm, args, cache, guard)
                step['workers'] = workers
                if arm['treatment'] == 'river':
                    step['river_executable'] = pilot.EXES['river_executable']
                pilot.status('full_update_parity', case=case, workers=workers)
                waited = resources.wait_seconds
                metric = UPDATES[(arm['treatment'], workers)](destination, folder/'objects', state, arm['config'], **step)
                metric_path = destination/'metrics.json'
                proof = dict(registration_sha256=pilot.sha(REG), case=case, arm=name, workers=workers,
                    source_fork=fork, metrics=str(metric_path.relative_to(folder)), metrics_sha256=pilot.sha(metric_path),
                    seconds=metric['seconds'], external_gpu_wait_seconds=resources.wait_seconds-waited,
                    full_state_and_artifacts_identical=True)
                del state
            assert metric['workers'] == workers and metric['board_workers'] == 4
            for sub in metric['subbatches']:
                part = metric_path.parent/f"batch-{sub['chunk']:02d}"
                for filename, digest in sub['artifacts'].items():
                    guard()
                    assert pilot.sha(part/filename) == digest
            validate(folder, arm, metric, oracle, args, guard)
            if not proof_path.exists():
                pilot.atomic_json(proof_path, proof)
            records.append(proof)
            print(json.dumps(dict(case=case, passed=True, seconds=metric['seconds'],
                checkpoint_identical=True, observed_physical_workers=len({w['pid'] for w in metric['worker_stats']}))), flush=True)
        comparisons = []
        for kind in ('baseline', 'river'):
            four, eight = [next(r for r in records if r['case'] == kind+'-'+suffix) for suffix in ('four', 'eight')]
            comparisons.append(dict(method=kind, four_seconds=four['seconds'], eight_seconds=eight['seconds'],
                observed_wall_ratio_four_over_eight=four['seconds']/eight['seconds'],
                external_gpu_wait_seconds=[four['external_gpu_wait_seconds'], eight['external_gpu_wait_seconds']]))
        pilot.verify(spec['inputs'])
        guard()
        measurement = pilot.study_measure(STORE)
        assert measurement['logical_bytes'] < LIMIT
        pilot.atomic_json(RESULT, dict(passed=True, complete=True, registration_sha256=pilot.sha(REG),
            cases=records, comparisons=comparisons, storage=measurement,
            seconds_this_invocation=time.monotonic()-resources.started,
            gpu_used=True, new_evaluation_deals=0, independent_timing_repetitions=1,
            accuracy_claim=False, production_modified=False,
            limitation='Single full-update replay per method and worker count; order, OS caching and external load can affect wall time. No accuracy or universal speedup claim.'))
        pilot.status('complete', result=str(RESULT))
    except BaseException as error:
        failure = OUT/(NAME+'-interruption-'+uuid.uuid4().hex[:8]+'.json')
        pilot.atomic_json(failure, dict(registration_sha256=pilot.sha(REG), error=repr(error),
            traceback=traceback.format_exc(), preserve_partial_attempts=True))
        pilot.status('interrupted', evidence=str(failure))
        raise
    finally:
        if acquired:
            assert pilot.LOCK.read_text() == str(os.getpid())
            pilot.LOCK.unlink()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--wait', action='store_true')
    a = parser.parse_args()
    if (a.resume or a.wait) and not a.run:
        parser.error('--resume/--wait require --run')
    main(a.run, a.resume, a.wait)
