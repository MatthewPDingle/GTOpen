"""Independently audit the matched prefix through a qualified sequence reader.

The control mode compares the general reader with the existing bounded
trained-state audit. Prefix mode requires that control and audits both arms.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import argparse
import json
from pathlib import Path
import time
import psutil
from board_sequence_readback_v1 import audit_sequence
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from later_average_support_v1 import OUT,read
from bounded_parallel_evaluation_archive_v2 import production_available

CONTROL='board-training-pipeline-control-v1'
OLD_REVIEW='board-training-pipeline-readback-v1'
NEW_CONTROL='board-sequence-readback-control-v1'
PREFIX='board-root-matched-prefix-v1'
NEW_REVIEW='board-matched-prefix-readback-v1'


def bound_result(prefix):
    registration=OUT/f'{prefix}-registration.json'; result=OUT/f'{prefix}-result.json'
    value=read(result); reg=read(registration)
    assert value['passed'] and value['registration_sha256']==sha(registration)
    for p,h in reg['inputs'].items(): assert sha(p)==h,p
    return reg,value,[registration,result]


def jobs_for(mode):
    assert mode in ('control','prefix')
    required=[CONTROL,OLD_REVIEW] if mode=='control' else [NEW_CONTROL,PREFIX]
    missing=[p for p in required if not (OUT/f'{p}-result.json').exists()]
    if missing:return [],[],missing,None
    paths=[]; jobs=[]; reference=None
    if mode=='control':
        reg,result,p=bound_result(CONTROL); paths.extend(p)
        _,reference,p=bound_result(OLD_REVIEW); paths.extend(p)
        assert reference['upstream_result_sha256']==sha(OUT/f'{CONTROL}-result.json')
        assert result['trained_generations']==reference['generations']==2
        jobs.append(dict(name='trained-pipeline-control',objects=str(Path(reg['store'])/'objects'),
            cfg=reg['config'],initial_checkpoint=result['initial_checkpoint'],
            final_checkpoint=result['final_checkpoint'],generations=result['metrics']))
    else:
        _,qualified,p=bound_result(NEW_CONTROL); paths.extend(p)
        assert qualified['mode']=='control' and qualified['agrees_with_bounded_audit']
        reg,result,p=bound_result(PREFIX); paths.extend(p)
        assert result['prefix_generations_per_arm']==2 and reg['generations']==78
        assert [a['arm'] for a in result['arms']]==[a['name'] for a in reg['arms']]
        for arm,record in zip(reg['arms'],result['arms']):
            store=Path(reg['store'])/arm['name']
            progress_path=Path(record['progress_path']); replay_path=Path(record['replay_path'])
            assert progress_path.resolve()==(store/'progress.json').resolve()
            assert replay_path.resolve()==(store/'restart-replay.json').resolve()
            assert sha(progress_path)==record['progress_sha256'] and sha(replay_path)==record['replay_sha256']
            progress=read(progress_path); replay=read(replay_path)
            assert progress['registration_sha256']==replay['registration_sha256']==sha(OUT/f'{PREFIX}-registration.json')
            assert progress['completed']==len(progress['generations'])==2
            assert replay['passed'] and replay['checkpoint']==progress['checkpoint']
            assert sha(replay['metrics_path'])==replay['metrics_sha256']
            paths.extend((progress_path,replay_path,Path(replay['metrics_path'])))
            jobs.append(dict(name=arm['name'],objects=str(store/'objects'),cfg=arm['config'],
                initial_checkpoint=progress['initial_checkpoint'],final_checkpoint=progress['checkpoint'],
                generations=progress['generations']))
    paths.extend([OUT/'bb-context-candidate.json',OUT/'preflop-allin-matrix-control-v1-matrix.json',
        Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json'),
        Path('S:/GTOpen-research/board-root-components-control-v1/preflop-catalog.json'),
        ROOT/'target/release/examples/hu_fixed_board_tree_v1.exe',*Path(__file__).parent.glob('*.py')])
    for job in jobs:
        for g in job['generations']:
            metric=Path(g['path']); assert sha(metric)==g['sha256']
            assert metric.parent.parent.resolve()==Path(job['objects']).parent.resolve()
            paths.extend(p for p in metric.parent.rglob('*') if p.is_file())
    return jobs,paths,[],reference


def main(mode,check_ready=False,workers=8):
    assert type(workers) is int and 1<=workers<=8
    began=time.monotonic(); jobs,paths,missing,reference=jobs_for(mode)
    if check_ready:
        print(json.dumps(dict(ready=not missing,pending=missing,mode=mode,arms=[j['name'] for j in jobs],
            physical_workers=workers,board_workers=min(4,workers),gpu_used=False,readback_started=False)))
        return
    assert not missing,'Required completed readbacks are missing: '+str(missing)
    assert production_available() and psutil.cpu_percent(interval=1)<50
    assert psutil.virtual_memory().available>28_000_000_000
    limit=1800 if mode=='control' else 3600
    last_probe=0.
    def guard():
        nonlocal last_probe
        assert time.monotonic()-began<limit
        if time.monotonic()-last_probe>3:
            assert production_available() and psutil.virtual_memory().available>24_000_000_000
            last_probe=time.monotonic()
    guard(); inputs={str(p):sha(p) for p in paths}
    prefix=NEW_CONTROL if mode=='control' else NEW_REVIEW
    rp=OUT/f'{prefix}-registration.json'; assert not rp.exists()
    save(rp,dict(inputs=inputs,mode=mode,jobs=jobs,workers=workers,board_workers=min(4,workers),
        maximum_seconds=limit,policy_tolerance=1e-10,target_tolerance=1e-9,root_tolerance=1e-8,
        scope='All physical targets and weighted reservoirs; all sampled public boards; scalar root/BTN state; all played-generation identities.',
        gpu_used=False,refit_performed=False,production_modified=False))
    results=[]
    try:
        for job in jobs:
            guard(); arguments={k:v for k,v in job.items() if k!='name'}
            value=audit_sequence(**arguments,workers=workers,guard=guard)
            results.append(dict(arm=job['name'],**value))
        if reference is not None:
            for key in ('generations','boards_checked','physical_roots_checked','postflop_targets_checked',
                        'insertion_counts','final_checkpoint'):
                assert results[0][key]==reference[key],key
            for key in ('maximum_root_state_error','maximum_exact_error','maximum_board_error',
                        'maximum_target_error','maximum_policy_error'):
                assert abs(results[0][key]-reference[key])<1e-12,key
        for p,h in inputs.items():guard(); assert sha(p)==h,p
        result=dict(passed=True,registration_sha256=sha(rp),mode=mode,arms=results,
            agrees_with_bounded_audit=reference is not None,seconds=time.monotonic()-began,
            source_result_sha256=sha(OUT/f'{CONTROL if mode=="control" else PREFIX}-result.json'),
            gpu_used=False,refit_performed=False,production_modified=False,accuracy_qualified=False,
            full_study_storage_admitted=False,
            limitation='Shares native poker engine, feature encoder, sampler and reservoir implementation. Does not certify playing strength or full-study admission.')
        save(OUT/f'{prefix}-result.json',result); print(json.dumps(result),flush=True)
    except BaseException as exc:
        save(OUT/f'{prefix}-failure.json',dict(passed=False,registration_sha256=sha(rp),error=repr(exc),completed_arms=results))
        raise


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--mode',choices=('control','prefix'),required=True)
    parser.add_argument('--check-ready',action='store_true'); parser.add_argument('--workers',type=int,default=8)
    args=parser.parse_args(); main(args.mode,args.check_ready,args.workers)
