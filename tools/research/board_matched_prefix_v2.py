"""First two full-budget generations of the prospectively fixed board study.

Preparation is read-only. Execution requires trained-pipeline readback and
fresh global storage admission. This runner cannot continue past generation 2.
Version 2 checks quiescent storage before publication and writes completion
markers atomically. The scientific configuration and output identity are unchanged.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='2', OMP_NUM_THREADS='2', CUBLAS_WORKSPACE_CONFIG=':4096:8')
import argparse
import copy
import json
from pathlib import Path
import subprocess
import time
import uuid
import numpy as np
import psutil
from later_average_support_v1 import OUT, read, load_complete_cache
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from weighted_learning_cuda_control_20260927 import safe_read_only_resources, LOCK, OTHER
from preflop_allin_matrix_v1 import AllinMatrix
from board_root_accumulator_v1 import BoardRootRegrets
import board_training_checkpoint_v1 as checkpoint
import sampled_visible_hybrid_checkpoint_v1 as storage
from board_training_pipeline_v1 import initialize, update
from board_training_pipeline_control_v1 import compare_states
from board_study_storage_v1 import create, measure
from board_prefix_publication_v1 import atomic_json, completion, storage_boundary

PREFIX='board-root-matched-prefix-v1'
STORE=Path('S:/GTOpen-research')/PREFIX
CAP=4_000_000_000  # Entire two-arm prefix, including deterministic replay artifacts.
RESERVE=2_000_000_000
LIMIT=800_000_000_000
CONTROL='board-training-pipeline-control-v1'
REVIEW='board-training-pipeline-readback-v1'


def atomic(path,value):
    atomic_json(path,value,replace=True)


def specification():
    cp=OUT/'bb-context-candidate.json'; mp=OUT/'preflop-allin-matrix-control-v1-matrix.json'
    cat=Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')
    physical=Path('S:/GTOpen-research/board-root-components-control-v1/preflop-catalog.json')
    original=OUT/'weighted-stratified-study-v1-registration.json'
    source=cp.read_text(); matrix=AllinMatrix(read(mp),source)
    paths=[original,cp,mp,cat,physical,OUT/'BOARD-ROOT-MATCHED-STUDY-PLAN.md']
    arms=[]
    for index,old in enumerate(read(original)['arms']):
        assert old['name']==('9266201-stratified','9266301-stratified')[index]
        cfg=copy.deepcopy(old['config'])
        root=BoardRootRegrets(context_sha256=storage.digest(source),matrix_sha256=sha(mp),
            entry_mass=matrix.bb_mass,physical_budget=512,boards_per_generation=4,board_seed=9281001+index)
        cfg.update(policy_type=checkpoint.POLICY_TYPE,board_root=root.config)
        assert {k for k in cfg if cfg[k]!=old['config'].get(k)}=={'policy_type','board_root'}
        assert (cfg['deals_per_generation'],cfg['deals_per_subbatch'],cfg['reservoir_capacity'],
                cfg['fit_steps'],cfg['chunk_size'],cfg['learning_rate'])==(512,64,262144,512,4096,.003)
        checkpoint.require_config(cfg)
        arms.append(dict(name=old['name'].replace('stratified','board-root'),control=old['name'],config=cfg))
    return arms,paths,dict(context_source=source,catalog_source=cat.read_text(),matrix_sha256=sha(mp),
                          entry_mass=matrix.btn_mass),dict(context_path=cp,physical_catalog_source=physical.read_text(),
                          matrix_source=mp.read_text(),catalog_source=cat.read_text(),matrix_sha256=sha(mp))


def qualifications():
    paths=[]; pending=[]
    from weighted_complete_evaluation_support_v1 import complete_training_paths
    paths.extend(complete_training_paths())
    for name in (CONTROL,REVIEW):
        rp=OUT/f'{name}-registration.json'; result=OUT/f'{name}-result.json'
        if not result.exists(): pending.append(name); continue
        value=read(result)
        assert value['passed'] and value['registration_sha256']==sha(rp)
        for p,h in read(rp)['inputs'].items(): assert sha(p)==h,p
        paths.extend((rp,result))
    if not pending:
        c=read(OUT/f'{CONTROL}-result.json'); r=read(OUT/f'{REVIEW}-result.json')
        assert c['exact_restart_replay'] and c['trained_generations']==2
        assert r['upstream_result_sha256']==sha(OUT/f'{CONTROL}-result.json')
        assert r['generations']==2 and r['boards_checked']==8 and r['physical_roots_checked']==1024
        assert r['final_checkpoint']==c['final_checkpoint']
    return paths,pending


def main(run=False,resume=False):
    arms,paths,args,step=specification(); qualified,pending=qualifications()
    if not run:
        print(json.dumps(dict(configurations_prepared=True,ready=not pending,pending=pending,
            arms=[dict(name=a['name'],control=a['control'],sampler_seed=a['config']['sampler_seed'],
                  board_seed=a['config']['board_root']['board_seed']) for a in arms],
            prefix_generations_per_arm=2,scientific_generations_per_arm=78,
            allocated_cap_bytes=CAP,independent_prefix_readback_required=True,
            fresh_resource_and_storage_admission_still_required=True,training_started=False)))
        return
    assert not pending,'GPU pipeline and independent trained-state readback must finish first'
    # Both upstream jobs must be terminal; no overlapping GPU work or output reservations.
    for prefix in ('weighted-complete-evaluation-queue-v1','board-training-pipeline-queue-v2'):
        rp=OUT/f'{prefix}-registration.json'; result=OUT/f'{prefix}-result.json'; value=read(result)
        assert value['passed'] and value['registration_sha256']==sha(rp)
        paths.extend((rp,result))
    assert not LOCK.exists() and not OTHER.exists() and safe_read_only_resources()
    assert psutil.cpu_percent(interval=1)<50 and psutil.virtual_memory().available>28_000_000_000
    gpu=subprocess.run(['nvidia-smi','--query-gpu=utilization.gpu,memory.free','--format=csv,noheader,nounits'],
        capture_output=True,text=True,timeout=5,creationflags=subprocess.CREATE_NO_WINDOW)
    assert gpu.returncode==0
    util,free=map(float,gpu.stdout.strip().splitlines()[0].split(',')); assert util<20 and free>6000
    import torch
    assert torch.cuda.is_available()
    assert all(a['config']['torch_version']==torch.__version__ and a['config']['numpy_version']==np.__version__ for a in arms)
    torch.set_num_threads(2); torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32=False; torch.backends.cudnn.allow_tf32=False
    exes=[ROOT/'target/release/examples'/name for name in ('hu_sampled_allin_bridge_v3.exe',
        'hu_sampled_action_trace_v2.exe','hu_sampled_profile_allin_evaluation_v1.exe','hu_fixed_board_tree_v1.exe')]
    rp=OUT/f'{PREFIX}-registration.json'; result_path=OUT/f'{PREFIX}-result.json'
    paths.extend([*qualified,*exes,*Path(__file__).parent.glob('*.py')])
    if resume:
        reg=read(rp); assert reg['arms']==arms and reg['store']==str(STORE) and STORE.is_dir()
        assert reg['runner_version']==2,'Only this qualified runner version may resume its registration'
    else:
        assert not rp.exists() and not STORE.exists() and not result_path.exists()
        reg=dict(runner_version=2,inputs={str(p):sha(p) for p in paths},arms=arms,store=str(STORE),
            generations=78,prefix_generations=2,maximum_allocated_bytes=CAP,maximum_logical_bytes=8_000_000_000,
            maximum_invocation_seconds=14400,physical_workers=2,board_workers=4,
            scope='First two actual-budget generations count toward the fixed study; independent prefix audit and full-study admission required before further learning.',
            production_modified=False,accuracy_qualified=False)
    for p,h in reg['inputs'].items(): assert sha(p)==h,p
    recovered=[]; storage_checks=[]
    acquired=False; began=time.monotonic(); last=0.; records=[]
    admitted_free=None; allocated_at_start=None
    def guard():
        nonlocal last
        now=time.monotonic(); assert now-began<reg['maximum_invocation_seconds']
        if now-last>3:
            assert safe_read_only_resources() and not OTHER.exists()
            assert psutil.virtual_memory().available>24_000_000_000
            disk_free=psutil.disk_usage('S:/').free
            assert disk_free>40_000_000_000 and torch.cuda.mem_get_info()[0]>4_000_000_000
            # Avoid walking files while board workers create/remove temporary
            # native trees. This coarse early stop charges other S: writes too,
            # but unrelated frees can mask growth. Quiescent directory scans
            # below are authoritative for every successful publication.
            if admitted_free is not None:
                assert allocated_at_start+max(0,admitted_free-disk_free)<CAP
            last=now
    def boundary(stage,reserve=0):
        value=storage_boundary(STORE,reg,stage,reserve_bytes=reserve,guard=guard)
        storage_checks.append(value); return value
    try:
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True
        existing_result=completion(result_path,sha(rp) if resume else '',resume=resume,recovered=recovered)
        assert existing_result is None,'Preserve completed prefix'
        from hu_root_retained_storage_admitted_study_20260924 import measure as global_measure
        inventory=global_measure(); total=sum(r['allocated_file_bytes'] for r in inventory)
        existing=measure(STORE)['allocated_file_bytes'] if STORE.exists() else 0
        assert total+max(0,CAP-existing)+RESERVE<=LIMIT,'Global research storage admission failed'
        assert psutil.disk_usage('S:/').free>40_000_000_000+CAP
        admitted_free=psutil.disk_usage('S:/').free; allocated_at_start=existing
        if not resume:
            reg['admission']=dict(roots=inventory,allocated_bytes=total,reserved_bytes=CAP+RESERVE,limit_bytes=LIMIT)
            atomic_json(rp,reg); create(STORE)
        boundary('resume' if resume else 'initial-admission')
        cache=load_complete_cache(); assert all(a['config']['allin_cache_sha256']==cache.sha256 for a in arms)
        step.update(cache=cache,executable=exes[0],trace_executable=exes[1],integration_executable=exes[2],
                    board_executable=exes[3],guard=guard,workers=2,board_workers=4)
        for arm in arms:
            cfg=arm['config']; model_args=dict(args,root_config=cfg['board_root']); folder=STORE/arm['name']
            folder.mkdir(exist_ok=True); objects=folder/'objects'; objects.mkdir(exist_ok=True)
            progress_path=folder/'progress.json'
            if progress_path.exists():
                progress=read(progress_path); assert progress['registration_sha256']==sha(rp)
                state=checkpoint.restore_checkpoint(objects,progress['checkpoint'],cfg,**model_args)
                assert state['completed_iterations']==progress['completed']==len(progress['generations'])<=2
                for row in progress['generations']: assert sha(row['path'])==row['sha256']
            else:
                state=initialize(objects,cfg,**model_args); initial=checkpoint.save_checkpoint(objects,state,cfg,**model_args)
                progress=dict(registration_sha256=sha(rp),completed=0,checkpoint=initial,initial_checkpoint=initial,generations=[])
                boundary(arm['name']+':initialized',65_536)
                atomic(progress_path,progress)
                boundary(arm['name']+':initial-progress-published')
            while state['completed_iterations']<2:
                guard(); iteration=state['completed_iterations']+1
                boundary(f'{arm["name"]}:before-generation-{iteration}',1_000_000_000)
                destination=folder/f'generation-{iteration:04d}-{uuid.uuid4().hex[:8]}'
                metric=update(destination,objects,state,cfg,batch_prefix=arm['name'],**step)
                boundary(f'{arm["name"]}:after-generation-{iteration}',65_536)
                restored=checkpoint.restore_checkpoint(objects,metric['checkpoint'],cfg,**model_args)
                compare_states(state,restored)
                row=dict(path=str(destination/'metrics.json'),sha256=sha(destination/'metrics.json'))
                progress.update(completed=iteration,checkpoint=metric['checkpoint'],generations=[*progress['generations'],row])
                atomic(progress_path,progress)
                boundary(f'{arm["name"]}:generation-{iteration}-published')
                print(json.dumps(dict(arm=arm['name'],completed=iteration,seconds=metric['seconds'],timings=metric['timings'])),flush=True)
            replay_path=folder/'restart-replay.json'
            replay=completion(replay_path,sha(rp),resume=resume,recovered=recovered)
            if replay is None:
                first=read(progress['generations'][0]['path']); second=read(progress['generations'][1]['path'])
                resumed=checkpoint.restore_checkpoint(objects,first['checkpoint'],cfg,**model_args)
                guard(); boundary(arm['name']+':before-replay',1_000_000_000)
                replay_folder=folder/('replay-0002-'+uuid.uuid4().hex[:8])
                replay=update(replay_folder,objects,resumed,cfg,batch_prefix=arm['name'],**step)
                boundary(arm['name']+':after-replay',65_536)
                compare_states(state,resumed)
                assert second['checkpoint']==replay['checkpoint'] and second['subbatches']==replay['subbatches']
                atomic_json(replay_path,dict(passed=True,registration_sha256=sha(rp),checkpoint=replay['checkpoint'],
                    metrics_path=str(replay_folder/'metrics.json'),metrics_sha256=sha(replay_folder/'metrics.json')))
            boundary(arm['name']+':replay-published')
            replay=completion(replay_path,sha(rp))
            assert replay['passed'] and replay['registration_sha256']==sha(rp) and replay['checkpoint']==progress['checkpoint']
            assert sha(replay['metrics_path'])==replay['metrics_sha256']
            records.append(dict(arm=arm['name'],progress_path=str(progress_path),progress_sha256=sha(progress_path),
                replay_path=str(replay_path),replay_sha256=sha(replay_path)))
        for p,h in reg['inputs'].items(): guard(); assert sha(p)==h,p
        final_measurement=boundary('before-success-publication')
        final_inventory=global_measure(); final_total=sum(r['allocated_file_bytes'] for r in final_inventory)
        assert final_total+RESERVE<=LIMIT,'Global research storage exceeded before publication'
        atomic_json(result_path,dict(passed=True,registration_sha256=sha(rp),arms=records,measurement=final_measurement,
            runner_version=2,storage_checks=storage_checks,recovered_markers=recovered,
            final_global_storage=dict(roots=final_inventory,allocated_bytes=final_total,reserved_bytes=RESERVE,limit_bytes=LIMIT),
            prefix_generations_per_arm=2,scientific_generations_per_arm=78,seconds=time.monotonic()-began,
            independent_prefix_readback_required=True,full_study_storage_admitted=False,accuracy_qualified=False,
            production_modified=False))
    except BaseException as error:
        if rp.exists():
            save(OUT/f'{PREFIX}-interruption-{uuid.uuid4().hex[:8]}.json',dict(error=repr(error),registration_sha256=sha(rp),
                note='Preserve partial attempts. Resume only published complete generation boundaries; no automatic retry.'))
        raise
    finally:
        if acquired:
            assert LOCK.read_text()==str(os.getpid()); LOCK.unlink()


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--run',action='store_true'); parser.add_argument('--resume',action='store_true')
    options=parser.parse_args()
    if options.resume and not options.run: parser.error('--resume requires --run')
    main(options.run,options.resume)
