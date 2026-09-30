"""Once-only, qualified continuation of the four interrupted cycle boundaries.

Two complete checkpoints are published without fitting. Two partial cycles
reuse retained targets and complete only missing work. Afterwards the unchanged
parallel v2 trainer may continue from these complete boundaries.
"""
import os
os.environ.update(PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',CUBLAS_WORKSPACE_CONFIG=':4096:8')
from concurrent.futures import ProcessPoolExecutor,ThreadPoolExecutor
import multiprocessing as mp
from pathlib import Path
import json
import time
import traceback
import psutil
import stack_context_parallel_continuation_v2 as run
from stack_context_partial_cycle_resume_v2 import update
from stack_context_interruption_audit_v1 import absent
from stack_context_cycle_archive_v1 import read,sha,finish_retirement
from owned_columnar_evaluation_archive_v1 import durable,encoded
from board_prefix_publication_v1 import atomic_json

legacy=run.legacy;NAME='stack-context-interrupted-cycle-recovery-v1'
AMENDMENT=legacy.OUT/(NAME+'-amendment.json');RESULT=legacy.OUT/(NAME+'-result.json')
FAILURE=legacy.OUT/(NAME+'-failure.json');STATUS=legacy.OUT/(NAME+'-status.json')


def recover_arm(arm):
    began=time.monotonic();psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    def stage(phase,key=None):
        atomic_json(legacy.OUT/(NAME+'-'+arm+'-status.json'),dict(arm=arm,phase=phase,context=key,
            unix=time.time(),pid=os.getpid(),created=psutil.Process().create_time()),replace=True)
    legacy.status=lambda phase,**kw:stage(phase)
    stage('restoring-reviewed-cycle')
    spec=read(legacy.REG);legacy.verify(spec['inputs'])
    audit=read(legacy.OUT/'stack-context-parallel-interruption-audit-v1-result.json');row=audit['arms'][arm]
    expected={r['path']:r['sha256'] for r in audit['files']}
    folder=legacy.STORE/arm;progress=read(folder/'progress.json');objects=folder/'objects'
    assert progress['completed_cycles']==row['published_cycles']
    cycle=row['interrupted_cycle'];raw=Path(row['raw']);dest=Path(row['archive'])
    rt=run.runtime_for(arm,spec,read(legacy.OUT/'stack-context-population-v1-result.json'))
    cfg=spec['arms'][arm]['config'];registry,resources=rt['registry'],rt['resources']
    state=legacy.checkpoint.restore_checkpoint(objects,progress['checkpoint'],cfg,registry,resources)
    run.torch.set_num_threads(1);run.torch.use_deterministic_algorithms(True)
    run.torch.backends.cuda.matmul.allow_tf32=False;run.torch.backends.cudnn.allow_tf32=False
    run.torch.cuda.set_per_process_memory_fraction(2_000_000_000/run.torch.cuda.get_device_properties(0).total_memory)
    guard=legacy.Guard(read(legacy.ATTEMPT)['admitted_unix']);guard.last_size=float('inf')
    if row['complete_metric']:
        assert arm in ('A-baseline','B-relative') and sha(raw/'metrics.json')==row['metric_sha256']
        metric=read(raw/'metrics.json');action='publish-already-complete-checkpoint'
    else:
        assert arm in ('A-relative','B-baseline') and not (raw/'metrics.json').exists() and not dest.exists()
        native={k:legacy.ROOT/'target/release/examples'/n for k,n in dict(bridge='hu_sampled_allin_history_bridge_v1.exe',
            trace='hu_sampled_action_trace_v2.exe',integration='hu_sampled_profile_allin_evaluation_v1.exe',
            river='hu_river_two_stage_stream_v1.exe',board='hu_fixed_board_tree_v1.exe').items()}
        cache=legacy.AllinCache(spec['cache_artifact'],spec['cache_sha256'])
        candidate,_,metric=update(raw,objects,state,cfg,registry,resources,expected=expected,
            inputs=rt['inputs'],cache=cache,native=native,guard=guard,workers=4,board_workers=1,
            batch_prefix=legacy.NAME+'-'+arm[0],on_stage=stage)
        action='continue-retained-partial-cycle'
    restored=legacy.checkpoint.restore_checkpoint(objects,metric['checkpoint'],cfg,registry,resources)
    assert restored['completed_cycles']==cycle and metric['used_model']==state['next_model']
    assert restored['next_model']==metric['next_model'] and restored['played_bank'][-1]==state['next_model']
    # Every file present before interruption must still match before transport
    # retires its duplicate raw copy. All original bytes remain in verified XZ.
    for path,h in expected.items():
        p=Path(path)
        if p.is_relative_to(raw) or p.is_relative_to(dest):assert sha(p)==h,path
    sources=legacy.paired_sources(raw,dest,registry.fit_contexts)
    chance=run.chance_receipt(arm,cycle,state['next_model'],sources,spec,rt,guard)
    receipt=run.publish_receipt(chance);stage('archiving-complete-boundary')
    if row['complete_metric']:
        archived=finish_retirement(dest,root=legacy.STORE,token=legacy.TOKEN,guard=guard,workers=4)
    else:
        archived=legacy.archive.archive_cycle(raw,dest,root=legacy.STORE,token=legacy.TOKEN,guard=guard,workers=4)
    record=dict(cycle=cycle,checkpoint=metric['checkpoint'],archive=str(dest.relative_to(legacy.STORE)),
        archive_index_sha256=sha(dest/'index.json'),retirement_sha256=sha(dest/'retired.json'),
        collection_seconds=metric['seconds'],packed_bytes=archived['packed_bytes'],paired_sources=sources,
        chance_receipt_sha256=sha(receipt),continuation_amendment_sha256=sha(run.AMENDMENT),
        recovered_without_scientific_repeat=True,interruption_recovery_amendment_sha256=sha(AMENDMENT),
        recovery_action=action,recovery_seconds=time.monotonic()-began)
    progress=dict(progress,completed_cycles=cycle,checkpoint=metric['checkpoint'],updates=[*progress['updates'],record])
    atomic_json(folder/'progress.json',progress,replace=True);stage('recovered-boundary-published')
    print(json.dumps(dict(arm=arm,cycle=cycle,action=action,seconds=time.monotonic()-began)),flush=True)
    return dict(arm=arm,cycle=cycle,checkpoint=metric['checkpoint'],action=action,
        progress_sha256=sha(folder/'progress.json'),all_preinterruption_bytes_preserved_in_archives=True)


def main():
    began=time.monotonic();absent();assert not any(p.exists() for p in (AMENDMENT,RESULT,FAILURE))
    ready=legacy.gpu_snapshot()
    assert ready['utilization_percent']<65 and ready['free_bytes']>=12_000_000_000
    assert legacy.production_available() and psutil.cpu_percent(interval=1)<50
    assert psutil.virtual_memory().available>40_000_000_000 and psutil.disk_usage('S:/').free>40_000_000_000
    assert time.time()-read(legacy.ATTEMPT)['admitted_unix']<72*3600
    proofs=['stack-context-archive-recovery-check-v1','stack-context-archive-transport-recovery-v1',
        'stack-context-retained-state-replay-check-v1','stack-context-river-transport-resume-check-v2',
        'stack-context-partial-cycle-resume-check-v2']
    bound={}
    for prefix in proofs:
        path=legacy.OUT/(prefix+'-result.json');proof=read(path)
        assert proof['complete'] and proof['passed'];bound[str(path)]=sha(path)
        for p,h in proof.get('inputs',{}).items():assert sha(p)==h;bound[p]=h
    spec=read(legacy.REG);legacy.verify(spec['inputs'])
    audit_path=legacy.OUT/'stack-context-parallel-interruption-audit-v1-result.json';audit=read(audit_path)
    def verify_record(r):
        assert sha(r['path'])==r['sha256'],r['path']
    with ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(verify_record,audit['files']))
    assert run.logical_bytes(legacy.STORE)<run.MAX_LOGICAL
    accounting=run.inventory();allocated=sum(r['allocated_file_bytes'] for r in accounting)
    own=run.measure(legacy.STORE)['allocated_file_bytes']
    assert allocated+max(0,run.MAX_LOGICAL-own)<=800_000_000_000,'Original global storage reservation'
    for p in (Path(__file__),audit_path,run.AMENDMENT,legacy.REG,legacy.ATTEMPT):bound[str(p)]=sha(p)
    absent()
    amendment=dict(format=1,unix=time.time(),inputs=bound,original_invocation_pid=75720,
        original_stale_lock=legacy.LOCK.read_text(),original_stale_lock_sha256=sha(legacy.LOCK),
        preserved_interruption_audit_sha256=sha(audit_path),old_processes_verified_absent=True,
        policy='Reuse authenticated outputs and exact ordered state; only finish missing operations.',
        arms={a:audit['arms'][a]['interrupted_cycle'] for a in run.ARMS},
        completed_cycles_refitted=False,partial_cycles_discarded=False,seeds_budgets_targets_unchanged=True,
        original_deadline_unchanged=True,evaluation_gates_unchanged=True,maximum_concurrent_recovery_arms=2,
        target_workers_per_arm=4,board_workers_per_arm=1,global_allocated_cap=800_000_000_000,
        logical_reservation=run.MAX_LOGICAL,allocated_including_reservation=allocated+max(0,run.MAX_LOGICAL-own),
        production_modified=False,github_push=False)
    durable(AMENDMENT,encoded(amendment))
    # Replace only the specifically authenticated stale ownership marker,
    # atomically, preserving its exact old content/hash above.
    temp=legacy.LOCK.with_name(NAME+'-lock-claim.tmp');durable(temp,str(os.getpid()).encode())
    assert legacy.LOCK.read_text()==amendment['original_stale_lock'];os.replace(temp,legacy.LOCK)
    try:
        atomic_json(STATUS,dict(stage='recovering-retained-cycles',pid=os.getpid(),created=psutil.Process().create_time(),unix=time.time()),replace=True)
        with ProcessPoolExecutor(max_workers=2,mp_context=mp.get_context('spawn')) as pool:
            # Publish complete checkpoints first, then continue the two partial
            # cycles simultaneously. No next scientific cycle starts here.
            complete=list(pool.map(recover_arm,('A-baseline','B-relative')))
            partial=list(pool.map(recover_arm,('A-relative','B-baseline')))
        for p,h in bound.items():assert sha(p)==h,p
        boundaries=run.validate_boundaries(spec,read(legacy.OUT/'stack-context-population-v1-result.json'))
        assert boundaries=={'A-baseline':4,'A-relative':4,'B-baseline':4,'B-relative':3}
        value=dict(complete=True,passed=True,unix=time.time(),seconds=time.monotonic()-began,
            amendment_sha256=sha(AMENDMENT),arms=complete+partial,boundaries=boundaries,
            original_parallel_v2_compatible=True,full_training_complete=False,scientific_evaluation_complete=False,
            final_readback_must_verify_recovery_amendment=True,production_modified=False)
        durable(RESULT,encoded(value));atomic_json(STATUS,dict(stage='complete-boundaries-recovered',unix=time.time(),boundaries=boundaries),replace=True)
        print(json.dumps(value),flush=True)
    except BaseException as e:
        durable(FAILURE,encoded(dict(error=repr(e),traceback=traceback.format_exc(),automatic_retry_allowed=False)));raise
    finally:
        if legacy.LOCK.exists() and legacy.LOCK.read_text()==str(os.getpid()):legacy.LOCK.unlink()


if __name__=='__main__':main()
