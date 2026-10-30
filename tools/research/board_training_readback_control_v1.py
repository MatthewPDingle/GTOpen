"""Qualify independent board readback on the retained native target fixture."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
from concurrent.futures import ProcessPoolExecutor
import json
import time
from pathlib import Path
import numpy as np
import psutil
from board_training_readback_support_v1 import prepare_readback, check_draw
from board_training_targets_v1 import prepare
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from later_average_support_v1 import OUT, read
from bounded_parallel_evaluation_archive_v2 import production_available

PREFIX='board-training-readback-control-v1'


def main():
    began=time.monotonic()
    assert production_available() and psutil.virtual_memory().available>28*2**30
    assert psutil.cpu_percent(interval=1)<50
    prior=OUT/'board-training-targets-control-v1-result.json'
    rp0=OUT/'board-training-targets-control-v1-registration.json'
    r=read(prior); registration=read(rp0)
    assert r['passed'] and r['registration_sha256']==sha(rp0)
    for p,h in registration['inputs'].items(): assert sha(p)==h,p
    for p,h in r['artifacts'].items(): assert sha(p)==h,p
    ckreg=read(OUT/'board-training-checkpoint-control-v2-registration.json')
    ckr=read(OUT/'board-training-checkpoint-control-v2-result.json')
    objects=Path(ckreg['store']); cp=read(objects/ckr['checkpoints'][-1]['file'])
    model_path=objects/cp['next_model']['file']; assert sha(model_path)==cp['next_model']['sha256']
    config=ckreg['config']['board_root']
    paths=[prior,rp0,model_path,OUT/'board-training-checkpoint-control-v2-registration.json',
        OUT/'board-training-checkpoint-control-v2-result.json',
        OUT/'bb-context-candidate.json',OUT/'preflop-allin-matrix-control-v1-matrix.json',
        Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json'),
        Path('S:/GTOpen-research/board-root-components-control-v1/preflop-catalog.json'),
        ROOT/'target/release/examples/hu_fixed_board_tree_v1.exe',*Path(__file__).parent.glob('*.py')]
    inputs={str(p):sha(p) for p in paths}; inputs.update(r['artifacts'])
    rp=OUT/f'{PREFIX}-registration.json'; assert not rp.exists()
    save(rp,dict(inputs=inputs,workers=4,maximum_seconds=240,gpu_used=False,
        scope='Every retained native board and independent preflop policies/exact terms; synthetic policy, no learning.'))
    try:
        payload=dict(model_source=model_path.read_text(),context_source=(OUT/'bb-context-candidate.json').read_text(),
            catalog_source=paths[7].read_text(),physical_catalog_source=paths[8].read_text(),
            matrix_source=(OUT/'preflop-allin-matrix-control-v1-matrix.json').read_text(),root_config=config)
        independent=prepare_readback(payload); reference=prepare(**payload)
        policy_error=max(float(np.max(abs(p-reference['pre'][n]))) for n,p in independent['pre'].items())
        exact_error=float(np.max(abs(independent['exact_scalar']-reference['exact'])))
        assert policy_error<1e-10 and exact_error<1e-10
        store=Path('S:/GTOpen-research/board-training-targets-control-v1')
        with ProcessPoolExecutor(max_workers=4) as pool:
            jobs=[pool.submit(check_draw,payload,store/f'draw-{i:02d}/request.json',
                read(store/f'draw-{i:02d}/result.json')['record']) for i in range(4)]
            results=[j.result(timeout=180) for j in jobs]
        for p,h in inputs.items(): assert sha(p)==h,p
        seconds=time.monotonic()-began; assert seconds<240
        report=dict(passed=True,registration_sha256=sha(rp),boards=4,root_classes=169,workers=4,
            maximum_policy_error=policy_error,maximum_exact_error=exact_error,
            maximum_dense_forward_error=max(r['maximum_error'] for r in results),
            worker_seconds=[r['seconds'] for r in results],seconds=seconds,
            gpu_used=False,synthetic_policy=True,native_targets=True,production_modified=False,
            trained_pipeline_readback_complete=False,accuracy_qualified=False)
        save(OUT/f'{PREFIX}-result.json',report); print(json.dumps(report),flush=True)
    except BaseException as exc:
        save(OUT/f'{PREFIX}-failure.json',dict(passed=False,error=repr(exc),registration_sha256=sha(rp)))
        raise


if __name__=='__main__': main()
