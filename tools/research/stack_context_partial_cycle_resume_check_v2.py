"""Run the recovery collector read-only against retained completed contexts."""
import os
os.environ.update(PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',CUBLAS_WORKSPACE_CONFIG=':4096:8')
import json
from pathlib import Path
import time
import psutil
import stack_context_parallel_continuation_v2 as run
from stack_context_partial_cycle_resume_v2 import collect_partial
from stack_context_retained_state_replay_v1 import compare_local
from stack_context_cycle_archive_v1 import read,sha
from owned_columnar_evaluation_archive_v1 import durable,encoded

legacy=run.legacy;NAME='stack-context-partial-cycle-resume-check-v2'


def main():
    began=time.monotonic();psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    from stack_context_interruption_audit_v1 import absent
    absent()  # Recognize the authenticated stale owner; do not remove its lock.
    probe=legacy.gpu_snapshot()
    assert not legacy.OTHER.exists() and legacy.production_available() and psutil.cpu_percent(interval=1)<50
    assert probe['utilization_percent']<65 and probe['free_bytes']>=12_000_000_000
    assert psutil.virtual_memory().available>=40_000_000_000 and psutil.disk_usage('S:/').free>40_000_000_000
    for prefix in ('stack-context-retained-state-replay-check-v1','stack-context-river-transport-resume-check-v2'):
        result=read(legacy.OUT/(prefix+'-result.json'));assert result['complete'] and result['passed']
        for p,h in result['inputs'].items():assert sha(p)==h
    run.torch.set_num_threads(1);run.torch.use_deterministic_algorithms(True)
    run.torch.backends.cuda.matmul.allow_tf32=False;run.torch.backends.cudnn.allow_tf32=False
    run.torch.cuda.set_per_process_memory_fraction(2_000_000_000/run.torch.cuda.get_device_properties(0).total_memory)
    attempt=legacy.OUT/(NAME+'-attempt.json');result_path=legacy.OUT/(NAME+'-result.json')
    assert not attempt.exists() and not result_path.exists()
    sources=[Path(__file__),Path(__file__).with_name('stack_context_partial_cycle_resume_v2.py'),
        Path(__file__).with_name('stack_context_retained_state_replay_v1.py'),
        Path(__file__).with_name('stack_context_river_transport_resume_v1.py')]
    sources += [legacy.OUT/(p+'-result.json') for p in ('stack-context-retained-state-replay-check-v1','stack-context-river-transport-resume-check-v2')]
    inputs={str(p):sha(p) for p in sources}
    durable(attempt,encoded(dict(unix=time.time(),inputs=inputs,retained_data_only=True,
        actual_native_calls=0,new_fits=0,maximum_seconds=1200,maximum_cuda_bytes=2_000_000_000)))
    spec=read(legacy.REG);legacy.verify(spec['inputs'])
    audit=read(legacy.OUT/'stack-context-parallel-interruption-audit-v1-result.json')
    expected={r['path']:r['sha256'] for r in audit['files']};cases=[]
    native={k:legacy.ROOT/'target/release/examples'/n for k,n in dict(
        bridge='hu_sampled_allin_history_bridge_v1.exe',trace='hu_sampled_action_trace_v2.exe',
        integration='hu_sampled_profile_allin_evaluation_v1.exe',river='hu_river_two_stage_stream_v1.exe',board='hu_fixed_board_tree_v1.exe').items()}
    guard=legacy.Guard(read(legacy.ATTEMPT)['admitted_unix']);guard.last_size=float('inf')
    for arm in ('A-baseline','B-relative'):
        rt=run.runtime_for(arm,spec,read(legacy.OUT/'stack-context-population-v1-result.json'))
        cfg=spec['arms'][arm]['config'];key=rt['registry'].fit_contexts[0]
        objects=legacy.STORE/arm/'objects';progress=read(legacy.STORE/arm/'progress.json');row=audit['arms'][arm]
        previous=legacy.checkpoint.restore_checkpoint(objects,progress['checkpoint'],cfg,rt['registry'],rt['resources'])
        reference=legacy.checkpoint.restore_checkpoint(objects,row['checkpoint'],cfg,rt['registry'],rt['resources'])
        model_source=legacy.pipeline.storage.read_object(objects,previous['next_model']).decode()
        cache=legacy.AllinCache(spec['cache_artifact'],spec['cache_sha256'])
        value=collect_partial(Path(row['raw'])/key,previous['contexts'][key],cfg,rt['registry'],rt['resources'],
            key=key,model_source=model_source,used=previous['next_model'],inputs=rt['inputs'][key],cache=cache,
            native=native,guard=guard,workers=4,board_workers=1,batch_prefix=legacy.NAME+'-'+arm[0],
            on_stage=lambda *args:None,expected=expected,allow_missing=False,qualification=True)
        assert compare_local(previous['contexts'][key],reference['contexts'][key],rt['resources'][key])
        cases.append(dict(arm=arm,cycle=row['interrupted_cycle'],context=key,all_arrays_and_rng_exact=True,
            actual_native_calls=0,new_fits=0,seconds=value['seconds']))
        print(json.dumps(cases[-1]),flush=True)
    for p,h in inputs.items():assert sha(p)==h
    value=dict(passed=True,complete=True,seconds=time.monotonic()-began,inputs=inputs,cases=cases,
        both_representations_qualified=True,unchanged_original_collector_math=True,
        actual_native_calls=0,new_fits=0,scientific_progress_modified=False)
    durable(result_path,encoded(value));print(json.dumps(value),flush=True)


if __name__=='__main__':main()
