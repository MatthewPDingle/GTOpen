"""Independent full 78-generation readback of both completed board-root arms."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',CUDA_VISIBLE_DEVICES='-1')
import argparse
import json
from pathlib import Path
import time
import psutil
from board_sequence_readback_v1 import audit_sequence
from board_prefix_publication_v1 import atomic_json
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from later_average_support_v1 import OUT,read
from bounded_parallel_evaluation_archive_v2 import production_available

PREFIX='board-matched-complete-readback-v1'
TRAINING='board-root-matched-continuation-v1'
INITIAL='board-root-matched-prefix-v1'


def preparation():
    names=[f'{TRAINING}-registration.json',f'{TRAINING}-result.json',
        f'{INITIAL}-registration.json',f'{INITIAL}-result.json',
        'board-matched-prefix-readback-v1-registration.json','board-matched-prefix-readback-v1-result.json',
        'board-sequence-readback-control-v1-registration.json','board-sequence-readback-control-v1-result.json']
    paths=[OUT/n for n in names];missing=[p.name for p in paths if not p.exists()]
    if missing:return [],paths,missing
    training=read(paths[0]);done=read(paths[1]);initial=read(paths[2]);prefix=read(paths[3])
    for rp,result_path in zip(paths[::2],paths[1::2]):
        reg=read(rp);result=read(result_path)
        assert result['passed'] and result['registration_sha256']==sha(rp)
        for p,h in reg['inputs'].items():assert sha(p)==h,p
    assert done['training_complete'] and done['generations_per_arm']==training['generations_per_arm']==78
    assert training['initial_generations_per_arm']==2 and training['arms']==initial['arms']
    assert training['prefix_result_sha256']==sha(paths[3])
    assert read(paths[5])['source_result_sha256']==sha(paths[3])
    assert read(paths[7])['agrees_with_bounded_audit']
    names=[a['name'] for a in training['arms']]
    assert len(names)==2 and [x['arm'] for x in done['arms']]==[x['arm'] for x in prefix['arms']]==names
    store=Path(training['store']);assert store==Path('S:/GTOpen-research/board-root-matched-prefix-v1')
    jobs=[]
    for arm,end,start in zip(training['arms'],done['arms'],prefix['arms']):
        folder=store/arm['name'];pp=Path(end['progress_path']);old=Path(start['progress_path'])
        assert pp==folder/'continuation-progress.json' and old==folder/'progress.json'
        assert sha(pp)==end['progress_sha256'] and sha(old)==start['progress_sha256']
        progress=read(pp);first=read(old)
        assert progress['registration_sha256']==sha(paths[0])
        assert progress['prefix_progress_sha256']==sha(old)
        assert progress['completed']==len(progress['generations'])==end['completed']==78
        assert progress['initial_checkpoint']==first['initial_checkpoint']
        assert progress['checkpoint']==end['checkpoint']
        assert progress['generations'][:2]==first['generations'] and first['completed']==2
        seen=set()
        for generation,row in enumerate(progress['generations'],1):
            metric=Path(row['path']);assert metric.resolve()==metric
            assert metric.parent.parent==folder and metric.name=='metrics.json' and str(metric) not in seen
            seen.add(str(metric));assert sha(metric)==row['sha256']
            value=read(metric);assert value['iteration']==generation
            if generation==78:assert value['checkpoint']==progress['checkpoint']
            paths.extend(p for p in metric.parent.rglob('*') if p.is_file())
        paths.extend((pp,old))
        jobs.append(dict(name=arm['name'],objects=str(folder/'objects'),cfg=arm['config'],
            initial_checkpoint=progress['initial_checkpoint'],final_checkpoint=progress['checkpoint'],
            generations=progress['generations']))
    paths.extend([OUT/'bb-context-candidate.json',OUT/'preflop-allin-matrix-control-v1-matrix.json',
        Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json'),
        Path('S:/GTOpen-research/board-root-components-control-v1/preflop-catalog.json'),
        ROOT/'target/release/examples/hu_fixed_board_tree_v1.exe',*Path(__file__).parent.glob('*.py')])
    return jobs,paths,[]


def main(check_ready=False,workers=8):
    assert type(workers) is int and 1<=workers<=8
    began=time.monotonic();jobs,paths,missing=preparation()
    if check_ready:
        print(json.dumps(dict(ready=not missing,pending=missing,arms=[j['name'] for j in jobs],
            generations_per_arm=78,physical_workers=workers,board_workers=min(4,workers),
            gpu_used=False,readback_started=False)),flush=True);return
    assert not missing,'Completed qualified training is required before full readback'
    assert production_available() and psutil.cpu_percent(interval=1)<50 and psutil.virtual_memory().available>28_000_000_000
    last_probe=0.
    def guard():
        nonlocal last_probe
        assert time.monotonic()-began<43200
        if time.monotonic()-last_probe>3:
            assert production_available() and psutil.virtual_memory().available>24_000_000_000
            last_probe=time.monotonic()
    inputs={str(p):sha(p) for p in paths}
    rp=OUT/f'{PREFIX}-registration.json';assert not rp.exists()
    atomic_json(rp,dict(inputs=inputs,jobs=jobs,workers=workers,board_workers=min(4,workers),
        maximum_seconds=43200,policy_tolerance=1e-10,target_tolerance=1e-9,root_tolerance=1e-8,
        gpu_used=False,refit_performed=False,production_modified=False))
    results=[]
    try:
        for job in jobs:
            guard();value=audit_sequence(**{k:v for k,v in job.items() if k!='name'},workers=workers,guard=guard)
            assert value['generations']==78 and value['boards_checked']==312 and value['physical_roots_checked']==39936
            assert value['final_checkpoint']==job['final_checkpoint']
            results.append(dict(arm=job['name'],**value))
        for p,h in inputs.items():guard();assert sha(p)==h,p
        report=dict(passed=True,registration_sha256=sha(rp),source_result_sha256=sha(OUT/f'{TRAINING}-result.json'),
            complete_training=True,arms=results,seconds=time.monotonic()-began,gpu_used=False,refit_performed=False,
            production_modified=False,accuracy_qualified=False,
            limitation='Shares native engine, feature encoder, sampler and reservoir. Verifies saved training mechanics, not playing strength.')
        atomic_json(OUT/f'{PREFIX}-result.json',report);print(json.dumps(report),flush=True)
    except BaseException as exc:
        save(OUT/f'{PREFIX}-failure.json',dict(passed=False,error=repr(exc),registration_sha256=sha(rp),completed_arms=results))
        raise


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check-ready',action='store_true');parser.add_argument('--workers',type=int,default=8)
    a=parser.parse_args();main(a.check_ready,a.workers)
