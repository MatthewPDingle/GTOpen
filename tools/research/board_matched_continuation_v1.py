"""Prepared full-study continuation; genuine prefix audit and storage admission required."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='2',OMP_NUM_THREADS='2',CUBLAS_WORKSPACE_CONFIG=':4096:8')
import argparse
import json
from pathlib import Path
import subprocess
import time
import uuid
import numpy as np
import psutil
import board_matched_prefix_v2 as prefix
import board_training_checkpoint_v1 as checkpoint
from board_training_pipeline_v1 import update
from board_training_pipeline_control_v1 import compare_states
from board_continuation_sequence_v1 import advance_arm
from board_prefix_publication_v1 import atomic_json,completion,storage_boundary
from board_study_storage_v1 import measure
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from later_average_support_v1 import OUT,read,load_complete_cache
from weighted_learning_cuda_control_20260927 import LOCK,OTHER,safe_read_only_resources

PREFIX='board-root-matched-continuation-v1'
AUDIT='board-matched-prefix-readback-v1'
ADMISSION=OUT/'board-matched-full-storage-admission-v1.json'
STORE=prefix.STORE
LIMIT=800_000_000_000
HEADROOM=2_000_000_000


def preparation():
    arms,paths,args,step=prefix.specification()
    qualified,pending=prefix.qualifications(); paths.extend(qualified)
    rp=OUT/f'{prefix.PREFIX}-registration.json'; result_path=OUT/f'{prefix.PREFIX}-result.json'
    audit_reg=OUT/f'{AUDIT}-registration.json'; audit_path=OUT/f'{AUDIT}-result.json'
    required=[rp,result_path,audit_reg,audit_path,ADMISSION]
    pending.extend(p.name for p in required if not p.exists())
    if pending:return arms,paths,args,step,None,None,None,pending
    original=read(rp); result=read(result_path); audit=read(audit_path); audit_cfg=read(audit_reg)
    assert result['passed'] and result['registration_sha256']==sha(rp)
    assert result['runner_version']==original['runner_version']==2
    assert original['arms']==arms and original['generations']==78 and original['prefix_generations']==2
    assert original['store']==str(STORE)
    assert audit['passed'] and audit['registration_sha256']==sha(audit_reg) and audit['mode']=='prefix'
    assert audit['source_result_sha256']==sha(result_path)
    assert [a['arm'] for a in result['arms']]==[a['name'] for a in arms]==[a['arm'] for a in audit['arms']]
    for arm,record,checked in zip(arms,result['arms'],audit['arms']):
        pp=Path(record['progress_path']); assert pp==STORE/arm['name']/'progress.json'
        assert sha(pp)==record['progress_sha256']
        progress=read(pp)
        assert progress['completed']==len(progress['generations'])==checked['generations']==2
        assert checked['boards_checked']==8 and checked['physical_roots_checked']==1024
        assert checked['final_checkpoint']==progress['checkpoint']
        paths.append(pp)
    for bound in (original,audit_cfg):
        for p,h in bound['inputs'].items():assert sha(p)==h,p
    budget=read(ADMISSION)
    assert budget['format']==1 and budget['passed'] and budget['full_study_storage_admitted']
    assert budget['store']==str(STORE) and budget['generations_per_arm']==78 and budget['arms']==2
    assert budget['prefix_result_sha256']==sha(result_path) and budget['prefix_audit_sha256']==sha(audit_path)
    assert budget['scope']=='Measured full-budget prefix projection; fixed 78-generation study'
    assert budget['measurement_evidence'] and budget['inputs']
    for p,h in budget['inputs'].items():assert sha(p)==h,p
    for p,h in budget['measurement_evidence'].items():assert budget['inputs'][p]==h and sha(p)==h,p
    for key in ('maximum_allocated_bytes','maximum_logical_bytes','reserved_followup_bytes',
                'projected_full_allocated_bytes','projected_full_logical_bytes'):
        assert type(budget[key]) is int and budget[key]>0,key
    assert budget['maximum_logical_bytes']>=budget['maximum_allocated_bytes']>=prefix.CAP
    assert budget['projected_full_logical_bytes']>=budget['projected_full_allocated_bytes']
    assert budget['projected_full_allocated_bytes']<=budget['maximum_allocated_bytes']
    assert budget['projected_full_logical_bytes']<=budget['maximum_logical_bytes']
    assert budget['reserved_followup_bytes']>=4_000_000_000
    for record in result['arms']:
        for row in read(record['progress_path'])['generations']:
            assert budget['measurement_evidence'][row['path']]==row['sha256']
    paths.extend(required)
    return arms,paths,args,step,original,result,budget,[]


def main(run=False,resume=False):
    arms,paths,args,step,original,initial,budget,pending=preparation()
    if not run:
        print(json.dumps(dict(ready=not pending,pending=pending,training_started=False,
            generations_per_arm=78,qualified_prefix_generations=2,
            preserves_prefix_progress=True,independent_full_readback_required=True,
            fresh_runtime_and_storage_admission_required=True)),flush=True);return
    assert not pending,'Genuine prefix audit and measured full-study storage admission must finish first'
    for name in ('weighted-complete-evaluation-queue-v1','board-training-pipeline-queue-v2'):
        rp=OUT/f'{name}-registration.json'; result=OUT/f'{name}-result.json'
        assert read(result)['passed'] and read(result)['registration_sha256']==sha(rp)
        paths.extend((rp,result))
    assert not LOCK.exists() and not OTHER.exists() and safe_read_only_resources()
    assert psutil.cpu_percent(interval=1)<50 and psutil.virtual_memory().available>28_000_000_000
    probe=subprocess.run(['nvidia-smi','--query-gpu=utilization.gpu,memory.free','--format=csv,noheader,nounits'],
        capture_output=True,text=True,timeout=5,creationflags=subprocess.CREATE_NO_WINDOW)
    assert probe.returncode==0
    util,free=map(float,probe.stdout.strip().splitlines()[0].split(','));assert util<20 and free>6000
    import torch
    assert torch.cuda.is_available()
    assert all(a['config']['torch_version']==torch.__version__ and a['config']['numpy_version']==np.__version__ for a in arms)
    torch.set_num_threads(2);torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    exes=[ROOT/'target/release/examples'/n for n in ('hu_sampled_allin_bridge_v3.exe','hu_sampled_action_trace_v2.exe',
        'hu_sampled_profile_allin_evaluation_v1.exe','hu_fixed_board_tree_v1.exe')]
    paths.extend([*exes,*Path(__file__).parent.glob('*.py')])
    rp=OUT/f'{PREFIX}-registration.json'; result_path=OUT/f'{PREFIX}-result.json'
    if resume:
        reg=read(rp)
        assert reg['arms']==arms and reg['store']==str(STORE) and reg['runner_version']==1
        assert reg['storage_admission_sha256']==sha(ADMISSION)
        assert reg['prefix_result_sha256']==sha(OUT/f'{prefix.PREFIX}-result.json')
    else:
        assert not rp.exists() and not result_path.exists()
        assert all(not (STORE/a['name']/'continuation-progress.json').exists() for a in arms)
        reg=dict(runner_version=1,inputs={str(p):sha(p) for p in paths},arms=arms,store=str(STORE),
            generations_per_arm=78,initial_generations_per_arm=2,physical_workers=2,board_workers=4,
            maximum_invocation_seconds=43200,maximum_allocated_bytes=budget['maximum_allocated_bytes'],
            maximum_logical_bytes=budget['maximum_logical_bytes'],reserved_followup_bytes=budget['reserved_followup_bytes'],
            storage_admission_sha256=sha(ADMISSION),prefix_result_sha256=sha(OUT/f'{prefix.PREFIX}-result.json'),
            production_modified=False,accuracy_qualified=False)
    for p,h in reg['inputs'].items():assert sha(p)==h,p
    began=time.monotonic();last_probe=0.;acquired=False;recovered=[];checks=[];records=[]
    admitted_free=None;allocated_at_start=None
    def guard():
        nonlocal last_probe
        now=time.monotonic();assert now-began<reg['maximum_invocation_seconds']
        if now-last_probe>3:
            assert safe_read_only_resources() and not OTHER.exists()
            assert psutil.virtual_memory().available>24_000_000_000 and torch.cuda.mem_get_info()[0]>4_000_000_000
            free=psutil.disk_usage('S:/').free;assert free>40_000_000_000
            if admitted_free is not None:
                assert allocated_at_start+max(0,admitted_free-free)<reg['maximum_allocated_bytes']
            last_probe=now
    def boundary(stage,reserve=0):
        value=storage_boundary(STORE,reg,stage,reserve_bytes=reserve,guard=guard)
        checks.append(value);return value
    try:
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True
        assert completion(result_path,sha(rp) if resume else '',resume=resume,recovered=recovered) is None,'Preserve completed study'
        from hu_root_retained_storage_admitted_study_20260924 import measure as global_measure
        inventory=global_measure();total=sum(r['allocated_file_bytes'] for r in inventory)
        allocated_at_start=measure(STORE)['allocated_file_bytes']
        reserve=max(0,reg['maximum_allocated_bytes']-allocated_at_start)+reg['reserved_followup_bytes']+HEADROOM
        assert total+reserve<=LIMIT,'Fresh full-study global storage admission failed'
        admitted_free=psutil.disk_usage('S:/').free
        assert admitted_free>40_000_000_000+max(0,reg['maximum_allocated_bytes']-allocated_at_start)
        if not resume:
            reg['admission']=dict(roots=inventory,allocated_bytes=total,reserved_bytes=reserve,limit_bytes=LIMIT)
            atomic_json(rp,reg)
        boundary('continuation-admitted')
        cache=load_complete_cache();assert all(a['config']['allin_cache_sha256']==cache.sha256 for a in arms)
        step.update(cache=cache,executable=exes[0],trace_executable=exes[1],integration_executable=exes[2],
            board_executable=exes[3],guard=guard,workers=2,board_workers=4)
        for arm,start in zip(arms,initial['arms']):
            folder=STORE/arm['name'];objects=folder/'objects';cfg=arm['config']
            model_args=dict(args,root_config=cfg['board_root'])
            def restore(reference):return checkpoint.restore_checkpoint(objects,reference,cfg,**model_args)
            def run_generation(destination,state):
                return update(destination,objects,state,cfg,batch_prefix=arm['name'],**step)
            def published(progress):
                print(json.dumps(dict(arm=arm['name'],completed=progress['completed'],target=78)),flush=True)
            record=advance_arm(folder=folder,prefix_path=start['progress_path'],prefix_sha=start['progress_sha256'],
                registration_sha=sha(rp),restore=restore,compare=compare_states,update=run_generation,
                boundary=lambda stage,reserve:boundary(arm['name']+':'+stage,reserve),guard=guard,on_published=published)
            assert record['completed']==78;records.append(dict(arm=arm['name'],**record))
        for p,h in reg['inputs'].items():guard();assert sha(p)==h,p
        final=boundary('before-full-study-success',65_536)
        inventory=global_measure();total=sum(r['allocated_file_bytes'] for r in inventory)
        assert total+reg['reserved_followup_bytes']+HEADROOM<=LIMIT
        atomic_json(result_path,dict(passed=True,training_complete=True,registration_sha256=sha(rp),
            arms=records,generations_per_arm=78,measurement=final,storage_checks=checks,recovered_markers=recovered,
            seconds=time.monotonic()-began,independent_full_readback_required=True,
            final_global_storage=dict(roots=inventory,allocated_bytes=total,limit_bytes=LIMIT),
            evaluated=False,accuracy_qualified=False,production_modified=False))
    except BaseException as exc:
        if rp.exists():save(OUT/f'{PREFIX}-interruption-{uuid.uuid4().hex[:8]}.json',
            dict(error=repr(exc),registration_sha256=sha(rp),preserve_partial_attempts=True))
        raise
    finally:
        if acquired:assert LOCK.read_text()==str(os.getpid());LOCK.unlink()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run',action='store_true');parser.add_argument('--resume',action='store_true')
    a=parser.parse_args()
    if a.resume and not a.run:parser.error('--resume requires --run')
    main(a.run,a.resume)
