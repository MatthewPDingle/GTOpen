"""Read-only reconstruction check against two fully calculated checkpoints."""
import os
os.environ.update(PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp
import json
from pathlib import Path
import time
import psutil
import stack_context_parallel_continuation_v2 as run
from stack_context_retained_state_replay_v1 import replay_complete_context,compare_local
from stack_context_cycle_archive_v1 import read,sha
from owned_columnar_evaluation_archive_v1 import durable,encoded

legacy=run.legacy;NAME='stack-context-retained-state-replay-check-v1'


def arm_check(arm):
    began=time.monotonic();psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    run.torch.set_num_threads(1)
    from threadpoolctl import threadpool_limits
    limiter=threadpool_limits(limits=1)
    spec=read(legacy.REG);legacy.verify(spec['inputs'])
    rt=run.runtime_for(arm,spec,read(legacy.OUT/'stack-context-population-v1-result.json'))
    cfg=spec['arms'][arm]['config'];registry,resources=rt['registry'],rt['resources']
    folder=legacy.STORE/arm;progress=read(folder/'progress.json');objects=folder/'objects'
    audit=read(legacy.OUT/'stack-context-parallel-interruption-audit-v1-result.json')
    row=audit['arms'][arm];expected={r['path']:r['sha256'] for r in audit['files']}
    assert row['complete_checkpoint_restored'] and row['published_cycles']==progress['completed_cycles']
    previous=legacy.checkpoint.restore_checkpoint(objects,progress['checkpoint'],cfg,registry,resources)
    reference=legacy.checkpoint.restore_checkpoint(objects,row['checkpoint'],cfg,registry,resources)
    model_source=legacy.pipeline.storage.read_object(objects,previous['next_model']).decode()
    cache=legacy.AllinCache(spec['cache_artifact'],spec['cache_sha256'])
    def guard():
        assert time.monotonic()-began<1200 and psutil.virtual_memory().available>24_000_000_000
    contexts=[]
    for key in registry.fit_contexts:
        proof=replay_complete_context(Path(row['raw'])/key,previous['contexts'][key],cfg,registry,resources,
            key=key,model_source=model_source,used=previous['next_model'],inputs=rt['inputs'][key],cache=cache,
            expected=expected,batch_prefix=legacy.NAME+'-'+arm[0],guard=guard)
        assert compare_local(previous['contexts'][key],reference['contexts'][key],resources[key])
        contexts.append(proof);print(json.dumps(dict(arm=arm,stage='exact-state-match',**proof)),flush=True)
    assert not run.torch.cuda.is_initialized()
    return dict(arm=arm,cycle=row['interrupted_cycle'],seconds=time.monotonic()-began,
        contexts=contexts,complete_checkpoint_sha256=row['checkpoint']['sha256'],all_arrays_and_rng_exact=True)


def main():
    began=time.monotonic();attempt=legacy.OUT/(NAME+'-attempt.json');result=legacy.OUT/(NAME+'-result.json')
    assert not attempt.exists() and not result.exists()
    paths=[Path(__file__),Path(__file__).with_name('stack_context_retained_state_replay_v1.py'),
        legacy.REG,legacy.OUT/'stack-context-parallel-interruption-audit-v1-result.json']
    inputs={str(p):sha(p) for p in paths}
    durable(attempt,encoded(dict(unix=time.time(),inputs=inputs,new_native_calls=False,new_fits=False,
        original_files_read_only=True,maximum_seconds=1200,maximum_cpu_workers=2)))
    with ProcessPoolExecutor(max_workers=2,mp_context=mp.get_context('spawn')) as pool:
        arms=list(pool.map(arm_check,('A-baseline','B-relative')))
    for path,h in inputs.items():assert sha(path)==h
    value=dict(passed=True,complete=True,seconds=time.monotonic()-began,inputs=inputs,arms=arms,
        all_retained_arrays_rng_and_accumulators_exact=True,native_calls=0,fits=0,new_target_draws=0,
        partial_transport_qualified=False,scientific_progress_modified=False)
    durable(result,encoded(value));print(json.dumps(value),flush=True)


if __name__=='__main__':main()
