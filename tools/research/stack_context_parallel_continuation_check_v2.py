"""One-shot parallel scheduling and four-process CUDA inference control.

Uses existing completed first-cycle models and retained native preflop catalogs.
No model fitting, fresh physical deals or scientific evaluation. Includes a
read-only dry run recovering the diagnosed complete cycle two. These are compatibility checks, not a full-cycle speedup.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
    CUBLAS_WORKSPACE_CONFIG=':4096:8', PYTHONDONTWRITEBYTECODE='1')
import argparse
import hashlib
import json
import multiprocessing as mp
from pathlib import Path
import sys
import time
import traceback
import numpy as np
import psutil
import torch
import stack_context_parallel_continuation_v2 as runner
import stack_context_full_policy_v1 as full
from stack_context_current_policy_v1 import CurrentPolicy
from stack_context_preflop_export_v1 import queries_from_catalog

NAME = runner.NAME+'-check'
STORE = Path('S:/GTOpen-research')/NAME
OUT = runner.legacy.OUT


def record(path, value):
    runner.save(path, value)


def scheduling_control():
    from unittest.mock import patch
    import copy
    import threading
    legacy = runner.legacy
    runner.known_failure()
    assert not legacy.LOCK.exists() and not legacy.OTHER.exists()
    spec = legacy.read(legacy.REG)
    prepared = legacy.read(OUT/'stack-context-population-v1-result.json')
    before = {str(legacy.STORE/a/'progress.json'):runner.sha(legacy.STORE/a/'progress.json') for a in runner.ARMS}
    boundaries = runner.validate_boundaries(spec, prepared)
    assert boundaries == {'A-baseline':2,'A-relative':1,'B-baseline':1,'B-relative':1}
    rt = runner.runtime_for('A-relative',spec,prepared)
    progress = legacy.read(legacy.STORE/'A-relative/progress.json')
    raw = legacy.STORE/'A-relative/cycle-0002'
    metric = runner.recoverable_metric('A-relative',2,progress,raw)
    rejects = []
    for arm, cycle in [('A-baseline',2),('A-relative',3),('B-relative',2)]:
        try:runner.recoverable_metric(arm,cycle,progress,raw)
        except ValueError:rejects.append(arm+str(cycle))
        else:raise AssertionError('Undiagnosed partial cycle accepted')
    left_progress=legacy.read(legacy.STORE/'A-baseline/progress.json')
    left_rt=runner.runtime_for('A-baseline',spec,prepared)
    left_checkpoint=json.loads(legacy.read_object(legacy.STORE/'A-baseline/objects',left_progress['checkpoint']))
    left=runner.chance_receipt('A-baseline',2,left_checkpoint['played_bank'][-1],
        left_progress['updates'][-1]['paired_sources'],spec,left_rt,lambda:None)
    right=runner.chance_receipt('A-relative',2,metric['used_model'],
        legacy.paired_sources(raw,legacy.STORE/'A-relative/archive-0002',rt['registry'].fit_contexts),spec,rt,lambda:None)
    runner.compare_receipts(left,right)
    assert left['original_source_hashes'] != right['original_source_hashes']
    for field in ('cycle','arm','registration_sha256','comparator_sha256','own_parent_validated','matched_input_identities'):
        damaged=copy.deepcopy(right)
        if field=='cycle':damaged[field]+=1
        elif field=='arm':damaged[field]=left[field]
        elif field.endswith('sha256'):damaged[field]='0'*64
        elif field=='own_parent_validated':damaged[field]=False
        else:damaged[field][next(iter(damaged[field]))]='0'*64
        try:runner.compare_receipts(left,damaged)
        except ValueError:rejects.append(field)
        else:raise AssertionError('Damaged paired evidence accepted: '+field)
    stop=threading.Event(); published=[]; stages=[]
    def publish(stage,**values):
        stages.append(values.get('phase'))
        if values.get('phase')=='checkpoint-published':stop.set()
    def archive(*args,**kwargs):
        assert args == (raw,legacy.STORE/'A-relative/archive-0002')
        return dict(packed_bytes=0)
    # Real immutable checkpoint and board-plan restoration, mocked publication
    # and archive only. The completed scientific pipeline MUST NOT execute.
    original_sha=runner.sha
    def test_sha(path):
        path=Path(path)
        if path.name in ('index.json','retired.json') or path==runner.AMENDMENT:return '0'*64
        return original_sha(path)
    with patch.object(legacy.pipeline,'update',side_effect=AssertionError('Repeated completed science')) as update, \
         patch.object(legacy.archive,'archive_cycle',side_effect=archive) as arch, \
         patch.object(runner,'publish_receipt',return_value=runner.DIAGNOSIS), \
         patch.object(runner,'sha',side_effect=test_sha), \
         patch.object(runner,'atomic_json',side_effect=lambda p,v,**k:published.append((p,v))):
        complete=runner.arm_loop('A-relative',spec,rt,{},lambda:None,stop,publish)
        assert complete is False and update.call_count==0 and arch.call_count==1 and len(published)==1
    assert published[0][1]['completed_cycles']==2
    assert published[0][1]['updates'][-1]['recovered_without_scientific_repeat']
    assert stages==['start','archive-completed-evidence','checkpoint-published']
    assert runner.boundary_stop(stop,time.monotonic())
    stop.clear(); assert not runner.boundary_stop(stop,time.monotonic())
    assert runner.boundary_stop(stop,time.monotonic()-12*3600-1)
    for path,identity in before.items():assert runner.sha(path)==identity
    return dict(completed_cycle_recovery_readback=True, scientific_pipeline_calls=0,
        stopped_before_next_cycle=True, old_progress_unchanged=True, matched_chance_despite_distinct_parents=True,
        rejected_corruptions=rejects, complete_boundaries=boundaries)


def cuda_worker(arm, reference, start, stop, ready):
    try:
        spec = runner.legacy.read(runner.legacy.REG)
        prepared = runner.legacy.read(OUT/'stack-context-population-v1-result.json')
        rt = runner.runtime_for(arm, spec, prepared)
        model = full.read_model(runner.legacy.STORE/arm/'objects', reference, rt['registry'], rt['resources'])
        source = next(r for r in prepared['contexts'].values() if r['depth'] == 20)
        context_source = Path(source['context_path']).read_text()
        query, _ = queries_from_catalog(context_source, runner.legacy.read(source['physical_catalog']))
        torch.set_num_threads(1); torch.use_deterministic_algorithms(True)
        torch.backends.cuda.matmul.allow_tf32 = False; torch.backends.cudnn.allow_tf32 = False
        torch.cuda.set_per_process_memory_fraction(2_000_000_000/torch.cuda.get_device_properties(0).total_memory)
        engine = CurrentPolicy(model, rt['registry'], context_sha256=source['context_sha256'],
                               resources=rt['resources'], device='cuda')
        ready.put(arm)
        if not start.wait(timeout=180) or stop.is_set():raise RuntimeError('Parallel check start admission failed')
        begin = time.time()
        p = engine.infer(engine.prepare(query))
        torch.cuda.synchronize()
        ended = time.time()
        np.save(STORE/(arm+'-cuda.npy'), p, allow_pickle=False)
        record(STORE/(arm+'-worker.json'), dict(arm=arm, pid=os.getpid(), process_created=psutil.Process().create_time(),
            begin=begin, end=ended, cuda_reserved_bytes=torch.cuda.memory_reserved(),
            model_sha256=reference['sha256'], rows=len(p)))
    except BaseException as error:
        stop.set()
        record(STORE/(arm+'-failure.json'), dict(error=repr(error), traceback=traceback.format_exc()))
        raise


def cpu_control():
    name=NAME+'-cpu'
    attempt,output,failure=(OUT/(name+s+'.json') for s in ('-attempt','-result','-failure'))
    runner.require(not any(p.exists() for p in (attempt,output,failure)), 'Preserve previous CPU check')
    runner.require(runner.legacy.production_available() and psutil.virtual_memory().available>40_000_000_000,
        'CPU recovery check yields to production or memory pressure')
    paths={Path(__file__).resolve(),Path(runner.__file__).resolve(),runner.PLAN,runner.DIAGNOSIS,runner.legacy.FAILURE,runner.legacy.REG}
    for module in list(sys.modules.values()):
        p=getattr(module,'__file__',None)
        if p and Path(p).is_relative_to(runner.legacy.ROOT) and Path(p).suffix=='.py':paths.add(Path(p))
    inputs={str(p):runner.sha(p) for p in paths}
    record(attempt,dict(inputs=inputs,new_fits=False,new_scientific_deals=False,GPU_used=False))
    began=time.monotonic()
    try:
        result=scheduling_control()
        runner.legacy.verify(inputs)
        record(output,dict(complete=True,passed=True,seconds=time.monotonic()-began,inputs=inputs,
            scheduling=result,runner_sha256=runner.sha(runner.__file__),new_fits=False,new_scientific_deals=False,GPU_used=False))
        print(json.dumps(dict(passed=True,seconds=time.monotonic()-began,cpu_recovery_check=True)))
    except BaseException as error:
        record(failure,dict(error=repr(error),traceback=traceback.format_exc(),preserve_evidence=True))
        raise


def main():
    attempt, output, failure = (OUT/(NAME+s+'.json') for s in ('-attempt', '-result', '-failure'))
    if any(p.exists() for p in (STORE, attempt, output, failure)):
        raise ValueError('Preserve completed or failed check; no automatic repeat')
    require = runner.require
    require(runner.legacy.production_available() and psutil.virtual_memory().available > 40_000_000_000,
            'Insufficient idle headroom for bounded check')
    gpu = runner.legacy.gpu_snapshot()
    if gpu['free_bytes'] <= 12_000_000_000 or gpu['utilization_percent'] >= 65:
        print(json.dumps(dict(deferred=True,reason='heavy-GPU-work',probe=gpu,check_started=False))); return
    cpu_path=OUT/(NAME+'-cpu-result.json'); cpu=runner.legacy.read(cpu_path)
    require(cpu['passed'] and cpu['complete'] and cpu['runner_sha256']==runner.sha(runner.__file__), 'Passed CPU recovery check required')
    runner.legacy.verify(cpu['inputs'])
    spec = runner.legacy.read(runner.legacy.REG); runner.legacy.verify(spec['inputs'])
    prepared = runner.legacy.read(OUT/'stack-context-population-v1-result.json')
    refs = {}; paths = {Path(__file__).resolve(), Path(runner.__file__).resolve(), runner.legacy.REG,runner.DIAGNOSIS,runner.legacy.FAILURE,runner.PLAN,cpu_path}
    for arm in runner.ARMS:
        progress = runner.legacy.read(runner.legacy.STORE/arm/'progress.json')
        first = progress['updates'][0]['checkpoint']
        objects = runner.legacy.STORE/arm/'objects'
        checkpoint = json.loads(runner.legacy.read_object(objects, first))
        require(checkpoint['completed_cycles'] == 1, 'Retained first complete model required')
        refs[arm] = checkpoint['next_model']; paths.update((objects/first['file'], objects/refs[arm]['file']))
    paths.add(OUT/'stack-context-population-v1-result.json')
    paths.update(Path(p) for p in prepared['artifacts'])
    for module in list(sys.modules.values()):
        p = getattr(module, '__file__', None)
        if p and Path(p).is_relative_to(runner.legacy.ROOT) and Path(p).suffix == '.py':paths.add(Path(p))
    inputs = {str(p):runner.sha(p) for p in paths}
    record(attempt, dict(inputs=inputs, models=refs, cuda_processes=4, per_process_cap=2_000_000_000,
        new_fits=False, scientific_evaluation=False, maximum_seconds=900))
    STORE.mkdir(); began = time.monotonic(); processes = []
    try:
        scheduling = cpu['scheduling']
        source = next(r for r in prepared['contexts'].values() if r['depth'] == 20)
        text = Path(source['context_path']).read_text()
        query, _ = queries_from_catalog(text, runner.legacy.read(source['physical_catalog']))
        torch.set_num_threads(1)
        for arm in runner.ARMS:
            rt = runner.runtime_for(arm, spec, prepared)
            model = full.read_model(runner.legacy.STORE/arm/'objects', refs[arm], rt['registry'], rt['resources'])
            p, _, _ = full.predict(model, rt['registry'], query, context_sha256=source['context_sha256'],
                resources=rt['resources'], device='cpu')
            np.save(STORE/(arm+'-reference.npy'), p, allow_pickle=False)
        ctx = mp.get_context('spawn'); start = ctx.Event(); stop = ctx.Event(); ready = ctx.Queue()
        for arm in runner.ARMS:
            process = ctx.Process(target=cuda_worker, args=(arm, refs[arm], start, stop, ready))
            process.start(); processes.append((arm, process))
        admitted = [ready.get(timeout=180) for _ in runner.ARMS]
        require(set(admitted) == set(runner.ARMS) and not stop.is_set(), 'All four CUDA workers must initialize successfully')
        start.set()
        for arm, process in processes:
            process.join(timeout=180)
            require(not process.is_alive() and process.exitcode == 0, 'Parallel worker did not complete successfully')
        records = []
        for arm in runner.ARMS:
            a = np.load(STORE/(arm+'-reference.npy'), allow_pickle=False)
            b = np.load(STORE/(arm+'-cuda.npy'), allow_pickle=False)
            error = float(np.max(np.abs(a-b)))
            require(a.shape == b.shape and error < 1e-10 and np.array_equal(a > 0, b > 0),
                    'Concurrent inference differs from serial full reference')
            row = runner.legacy.read(STORE/(arm+'-worker.json'))
            require(row['cuda_reserved_bytes'] <= 2_000_000_000, 'Worker exceeded fixed CUDA cap')
            records.append(dict(**row, maximum_reference_error=error))
        require(min(r['end'] for r in records) > max(r['begin'] for r in records), 'CUDA scoring intervals did not overlap')
        require(time.monotonic()-began < 900, 'Check time bound exceeded')
        runner.legacy.verify(inputs); runner.legacy.verify(spec['inputs'])
        result = dict(complete=True, passed=True, seconds=time.monotonic()-began, inputs=inputs,
            runner_sha256=runner.sha(runner.__file__), scheduling=scheduling, concurrent_cuda=records,
            peak_sum_cuda_reserved_bytes=sum(r['cuda_reserved_bytes'] for r in records),
            full_cycle_throughput_measured=False, exact_fit_replay_checked=False, new_fits=False,
            new_scientific_deals=False, scientific_accuracy_qualified=False, production_modified=False,
            artifacts={str(p):runner.sha(p) for p in STORE.iterdir() if p.is_file()})
        record(output, result)
        print(json.dumps(dict(passed=True, seconds=result['seconds'], concurrent_arms=4,
            maximum_reference_error=max(r['maximum_reference_error'] for r in records))))
    except BaseException as error:
        # Never touch the live scientific trainer. Only these bounded fixture
        # processes are signalled, and all check evidence remains on disk.
        if 'stop' in locals():stop.set()
        if 'start' in locals():start.set()
        for _, process in processes:process.join(timeout=180)
        record(failure, dict(error=repr(error), traceback=traceback.format_exc(), preserve_evidence=True,
            automatic_retry_allowed=False))
        raise


if __name__ == '__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--cpu-only',action='store_true')
    if parser.parse_args().cpu_only:cpu_control()
    else:main()
