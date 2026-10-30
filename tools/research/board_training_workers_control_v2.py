"""Replay native target fixtures through isolated production-style CPU workers."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',CUDA_VISIBLE_DEVICES='-1')
import json
from pathlib import Path
import time
import psutil
from board_training_board_workers_v1 import pool,complete
from board_root_accumulator_v1 import BoardRootRegrets
from board_fixed_policy_control_v1 import ROOT,OUT,read,save,sha
from bounded_parallel_evaluation_archive_v2 import production_available

PREFIX='board-training-workers-control-v2'
STORE=Path('S:/GTOpen-research')/PREFIX


def main():
    began=time.monotonic();assert production_available() and psutil.cpu_percent(interval=1)<50
    assert psutil.virtual_memory().available>28*2**30 and psutil.disk_usage('S:/').free>40*2**30
    prior=OUT/'board-training-targets-control-v1-result.json';result=read(prior);assert result['passed']
    rr=OUT/'board-training-targets-control-v1-registration.json';assert result['registration_sha256']==sha(rr)
    for p,h in read(rr)['inputs'].items():assert sha(p)==h,p
    for p,h in result['artifacts'].items():assert sha(p)==h,p
    cr=OUT/'board-training-checkpoint-control-v2-registration.json';config=read(cr)['config']['board_root']
    cp_result=read(OUT/'board-training-checkpoint-control-v2-result.json');objects=Path(read(cr)['store'])
    ckp=objects/cp_result['checkpoints'][-1]['file'];checkpoint=read(ckp)
    mp=objects/checkpoint['next_model']['file'];assert sha(mp)==checkpoint['next_model']['sha256']
    model_source=mp.read_text();model=json.loads(model_source)
    root=BoardRootRegrets.restore(model['board_root_state'],expected_config=config);plan=root.plan()
    cp=OUT/'bb-context-candidate.json'
    payload=dict(model_source=model_source,context_source=cp.read_text(),
        catalog_source=Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json').read_text(),
        physical_catalog_source=Path('S:/GTOpen-research/board-root-components-control-v1/preflop-catalog.json').read_text(),
        matrix_source=(OUT/'preflop-allin-matrix-control-v1-matrix.json').read_text(),root_config=config)
    exe=ROOT/'target/release/examples/hu_fixed_board_tree_v1.exe'
    rp=OUT/f'{PREFIX}-registration.json';assert not rp.exists() and not STORE.exists();STORE.mkdir()
    inputs=dict(read(rr)['inputs']);inputs.update({str(p):sha(p) for p in [prior,rr,mp,cp,exe,Path(__file__),
        ROOT/'tools/research/board_training_board_workers_v1.py']})
    save(rp,dict(inputs=inputs,workers=2,replayed_draws=[0,1],maximum_seconds=120,gpu_used=False,production_modified=False))
    parent_cuda=os.environ.get('CUDA_VISIBLE_DEVICES')
    with pool(2,payload=payload,context_path=cp,executable=exe,folder=STORE) as executor:
        futures=[executor.submit(complete,i,plan['boards'][i]) for i in (0,1)]
        actual=[f.result(timeout=90) for f in futures]
    for i,x in enumerate(actual):
        expected=read(Path('S:/GTOpen-research/board-training-targets-control-v1')/f'draw-{i:02d}/result.json')
        assert x['result']['record']==expected['record']
        own_request=Path(x['path']).parent/'request.json'
        assert sha(own_request)==x['result']['request_sha256']
        assert read(own_request)==read(Path('S:/GTOpen-research/board-training-targets-control-v1')/f'draw-{i:02d}/request.json')
        assert x['result']['cuda_visible_devices']=='-1' and x['result']['pid']!=os.getpid()
        assert sha(x['path'])==x['sha256']
    assert os.environ.get('CUDA_VISIBLE_DEVICES')==parent_cuda
    for p,h in inputs.items():assert sha(p)==h,p
    seconds=time.monotonic()-began;assert seconds<120
    report=dict(passed=True,registration_sha256=sha(rp),exact_records=True,equal_request_semantics=True,draws=2,workers=2,
        parent_cuda_setting_unchanged=True,worker_cuda_disabled=True,seconds=seconds,
        results=actual,gpu_used=False,training_admitted=False,accuracy_qualified=False,production_modified=False)
    save(OUT/f'{PREFIX}-result.json',report)
    print(json.dumps({k:v for k,v in report.items() if k!='results'}))


if __name__=='__main__':main()
