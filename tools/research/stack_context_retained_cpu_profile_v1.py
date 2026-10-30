"""Profile one fixed retained river-target chunk, without new scientific work.

The first history/selected chunk of batch zero in the first A-relative cycle-2
context is fixed in advance. Read original query bytes, compare with original
probability arrays, then profile a fresh identical CPU policy. Instrumented
times are diagnostic and not used as an end-to-end speed benchmark.
"""
import os
os.environ.update(CUDA_VISIBLE_DEVICES='-1', OPENBLAS_NUM_THREADS='1',
                  OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1')
import cProfile
import hashlib
import json
from pathlib import Path
import pstats
import time
import traceback
import numpy as np
import psutil
import torch
from threadpoolctl import threadpool_limits
import stack_context_parallel_continuation_v2 as continuation
from stack_context_current_policy_v1 import CurrentPolicy

OUT = continuation.legacy.OUT
NAME = 'stack-context-retained-cpu-profile-v1'


def encoded(x):return (json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
def write(path,value):
    with path.open('xb') as f:f.write(encoded(value))


def main():
    attempt,result,failure=(OUT/(NAME+s+'.json') for s in ('-attempt','-result','-failure'))
    if any(p.exists() for p in (attempt,result,failure)):
        raise ValueError('Preserve existing profile evidence')
    if psutil.virtual_memory().available<28_000_000_000 or psutil.cpu_percent(interval=.2)>50:
        print(json.dumps(dict(deferred=True,reason='CPU/RAM pressure',profile_started=False)));return
    if not continuation.legacy.production_available():
        print(json.dumps(dict(deferred=True,reason='active production',profile_started=False)));return
    process=psutil.Process();process.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    torch.set_num_threads(1);limit=threadpool_limits(limits=1)
    spec=continuation.legacy.read(continuation.legacy.REG)
    continuation.legacy.verify(spec['inputs'])
    prepared_path=OUT/'stack-context-population-v1-result.json'
    prepared=continuation.legacy.read(prepared_path)
    folder=continuation.legacy.STORE/'A-relative'
    metric_path=folder/'cycle-0002'/'metrics.json';metric=continuation.legacy.read(metric_path)
    diagnosis=continuation.known_failure()
    assert continuation.sha(metric_path)==diagnosis['inputs'][str(metric_path)]
    context=metric['collections'][0];key=context['context_sha256']
    row=context['subbatches'][0];worker_path=Path(row['path'])
    assert continuation.sha(worker_path)==row['sha256']
    worker=continuation.legacy.read(worker_path);native=worker_path.parent/'conditional'
    names=['chunk-000-history-native.json','chunk-000-selected-native.json','chunk-000-policies.npz']
    paths={Path(__file__).resolve(),continuation.legacy.REG,continuation.DIAGNOSIS,
           prepared_path,metric_path,worker_path,folder/'objects'/metric['used_model']['file']}
    for name in names:
        p=native/name
        assert continuation.sha(p)==worker['artifacts'][str(Path('conditional')/name)]
        paths.add(p)
    inputs=dict(spec['inputs']);inputs.update({str(p):continuation.sha(p) for p in paths})
    write(attempt,dict(inputs=inputs,pid=process.pid,created=process.create_time(),
        maximum_seconds=300,math_threads=1,device='cpu',new_deals=False,new_fits=False,
        native_execution=False,scientific_evaluation=False,registered_inputs_changed=False))
    started=time.monotonic();outputs={};records=[]
    def guard():
        if time.monotonic()-started>300 or psutil.virtual_memory().available<24_000_000_000:
            raise RuntimeError('Profile resource/time bound')
        if not continuation.legacy.production_available():raise RuntimeError('Production became active')
    try:
        rt=continuation.runtime_for('A-relative',spec,prepared)
        model=continuation.legacy.full.read_model(folder/'objects',metric['used_model'],rt['registry'],rt['resources'])
        queries={name:json.loads((native/f'chunk-000-{name}-native.json').read_bytes())['queries']
                 for name in ('history','selected')}
        with np.load(native/'chunk-000-policies.npz',allow_pickle=False) as f:
            expected={name:f[name] for name in ('history','selected')}
        def new_engine():return CurrentPolicy(model,rt['registry'],context_sha256=key,resources=rt['resources'],device='cpu')
        for instrumented in (False,True):
            guard();engine=new_engine()
            for name in ('history','selected'):
                guard();profiler=cProfile.Profile() if instrumented else None
                if profiler:profiler.enable()
                before=time.perf_counter();cpu=time.process_time()
                batch=engine.prepare(queries[name]);middle=time.perf_counter()
                probability=engine.infer(batch);after=time.perf_counter()
                if profiler:profiler.disable()
                error=float(np.max(abs(probability-expected[name])))
                assert error<1e-10 and np.array_equal(probability>0,expected[name]>0)
                record=dict(phase=name,instrumented=instrumented,rows=len(probability),
                    prepare_seconds=middle-before,infer_seconds=after-middle,
                    process_cpu_seconds=time.process_time()-cpu,maximum_original_probability_error=error,
                    original_positive_support_preserved=True,relative_cache_entries=len(engine.relative_cache))
                if profiler:
                    path=OUT/(NAME+'-'+name+'.pstats');profiler.dump_stats(str(path))
                    outputs[str(path)]=continuation.sha(path)
                    stats=pstats.Stats(profiler);top=[]
                    for (file,line,function),(primitive,calls,own,cumulative,callers) in sorted(
                            stats.stats.items(),key=lambda item:item[1][3],reverse=True)[:25]:
                        top.append(dict(file=file,line=line,function=function,primitive_calls=primitive,calls=calls,
                                        own_seconds=own,cumulative_seconds=cumulative))
                    record['top_cumulative_functions']=top
                records.append(record);print(json.dumps({k:v for k,v in record.items() if k!='top_cumulative_functions'}),flush=True)
        guard();continuation.legacy.verify(inputs)
        assert not torch.cuda.is_initialized()
        write(result,dict(complete=True,passed=True,seconds=time.monotonic()-started,inputs=inputs,artifacts=outputs,
            records=records,scope='First retained river history/selected chunk, A-relative cycle2, first context and batch',
            full_target_generation_profiled=False,end_to_end_speedup_measured=False,
            cuda_initialized=False,new_scientific_deals=False,new_fits=False,native_execution=False,
            registered_inputs_changed=False,production_modified=False))
    except BaseException as error:
        write(failure,dict(error=repr(error),traceback=traceback.format_exc(),study_processes_untouched=True));raise


if __name__=='__main__':main()
