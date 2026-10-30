"""Actual native board targets on a typed synthetic-policy fixture; CPU only."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',CUDA_VISIBLE_DEVICES='-1')
from concurrent.futures import ProcessPoolExecutor
import copy
import hashlib
import json
import math
from pathlib import Path
import subprocess
import time
import numpy as np
import psutil
from board_fixed_policy_control_v1 import ROOT,OUT,read,save,sha
from board_training_targets_v1 import prepare,request,draw_record,generation_evidence,policy_rows
from board_root_components_control_v1 import forward_variable
from board_root_accumulator_v1 import BoardRootRegrets,digest
from storage_strategic_common_prior_20260920 import CLASSES
from bounded_parallel_evaluation_archive_v2 import production_available

PREFIX='board-training-targets-control-v1'
STORE=Path('S:/GTOpen-research')/PREFIX


def worker(payload,index,board):
    from threadpoolctl import threadpool_limits
    with threadpool_limits(limits=1):
        began=time.monotonic();prepared=prepare(**payload)
        req,ids=request(prepared,board);folder=STORE/f'draw-{index:02d}';folder.mkdir()
        path=folder/'request.json';save(path,req)
        raw=subprocess.check_output([str(ROOT/'target/release/examples/hu_fixed_board_tree_v1.exe'),
            str(OUT/'bb-context-candidate.json'),str(path)],timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
        tree_sha=hashlib.sha256(raw).hexdigest();tree=json.loads(raw);del raw
        record=draw_record(prepared,tree,tree_sha256=tree_sha,draw_index=index,board=board)
        dense_error=None
        if index==0:
            post=policy_rows(tree,prepared['model'],'saved-network')
            weights=[prepared['sampler'].weights[p,i] for p,i in enumerate(ids)]
            classes=[CLASSES[i] for i in ids]
            expected=np.zeros((169,4))
            for action,start in ((1,2),(2,3)):
                v=forward_variable(tree,post,prepared['pre'],prepared['context'],weights,classes,start)
                expected[:,action]=np.bincount(classes[0],weights=v,minlength=169)
            expected*=math.comb(52,5)/math.comb(48,5)/prepared['sampler'].masses[0]/prepared['class_mass'][:,None]
            dense_error=float(np.max(abs(expected-np.asarray(record['values']))));assert dense_error<1e-9
        evidence=dict(record=record,request_sha256=sha(path),dense_error=dense_error,
            seconds=time.monotonic()-began,maximum_preflop_suit_difference=prepared['maximum_preflop_suit_difference'])
        save(folder/'result.json',evidence)
        return evidence


def main():
    began=time.monotonic();assert production_available() and psutil.cpu_percent(interval=1)<50
    assert psutil.virtual_memory().available>28*2**30 and psutil.disk_usage('S:/').free>40*2**30
    rp=OUT/f'{PREFIX}-registration.json';assert not rp.exists() and not STORE.exists();STORE.mkdir()
    prior=OUT/'board-training-checkpoint-control-v2-result.json';r=read(prior);assert r['passed']
    ckreg=OUT/'board-training-checkpoint-control-v2-registration.json'
    assert r['registration_sha256']==sha(ckreg)
    for p,h in read(ckreg)['inputs'].items():assert sha(p)==h,p
    old=Path(read(ckreg)['store']);cp=old/r['checkpoints'][-1]['file']
    assert sha(cp)==r['checkpoints'][-1]['sha256']
    checkpoint=read(cp);model_path=old/checkpoint['next_model']['file']
    assert sha(model_path)==checkpoint['next_model']['sha256']
    model_source=model_path.read_text();model=json.loads(model_source);config=read(ckreg)['config']['board_root']
    root=BoardRootRegrets.restore(model['board_root_state'],expected_config=config)
    plan=root.plan();assert len(plan['boards'])==4
    payload=dict(model_source=model_source,context_source=(OUT/'bb-context-candidate.json').read_text(),
        catalog_source=Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json').read_text(),
        physical_catalog_source=Path('S:/GTOpen-research/board-root-components-control-v1/preflop-catalog.json').read_text(),
        matrix_source=(OUT/'preflop-allin-matrix-control-v1-matrix.json').read_text(),root_config=config)
    paths=[prior,ckreg,cp,model_path,ROOT/'target/release/examples/hu_fixed_board_tree_v1.exe',
        OUT/'bb-context-candidate.json',OUT/'preflop-allin-matrix-control-v1-matrix.json',
        Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json'),
        Path('S:/GTOpen-research/board-root-components-control-v1/preflop-catalog.json'),
        *Path(__file__).parent.glob('*.py')]
    save(rp,dict(inputs={str(p):sha(p) for p in paths},plan=plan,workers=4,maximum_seconds=240,
        scope='Native chance/terminal targets under a synthetic typed policy, not learned ranges.',gpu_used=False,production_modified=False))
    prepared=prepare(**payload)
    with ProcessPoolExecutor(max_workers=4) as pool:
        futures=[pool.submit(worker,payload,i,b) for i,b in enumerate(plan['boards'])]
        results=[f.result(timeout=180) for f in futures]
    evidence=generation_evidence(root,prepared,plan,[x['record'] for x in results])
    before=root.document();bad=copy.deepcopy(evidence);bad['draws'][0]['model_sha256']='c'*64
    try:root.step(plan,bad,played_policy=prepared['pre'][0],exact_terms=prepared['exact'])
    except ValueError:pass
    else:raise AssertionError('Accepted detached native targets')
    assert root.document()==before and root.plan()==plan
    delta=root.step(plan,evidence,played_policy=prepared['pre'][0],exact_terms=prepared['exact'])
    expected=np.zeros((169,4))
    for c in range(169):
        q=[float(prepared['exact'][c,a])+math.fsum(x['record']['values'][c][a] for x in results)/4 for a in range(4)]
        baseline=math.fsum(float(prepared['pre'][0][c,a])*q[a] for a in range(4))
        for a in range(4):expected[c,a]=512*float(config['entry_mass'][c])*(q[a]-baseline)
    error=float(np.max(abs(delta-expected)));assert error<1e-9
    restored=BoardRootRegrets.restore(root.document(),expected_config=config)
    assert restored.document()==root.document() and restored.plan()==root.plan()
    save(STORE/'generation-evidence.json',evidence);save(STORE/'root-after.json',root.document())
    for p,h in read(rp)['inputs'].items():assert sha(p)==h,p
    seconds=time.monotonic()-began;assert seconds<240
    report=dict(passed=True,registration_sha256=sha(rp),boards=4,root_classes=169,workers=4,
        maximum_dense_forward_error=results[0]['dense_error'],maximum_scalar_update_error=error,
        worker_seconds=[x['seconds'] for x in results],seconds=seconds,
        artifacts={str(p):sha(p) for p in STORE.rglob('*.json')},gpu_used=False,
        synthetic_policy=True,native_targets=True,training_admitted=False,accuracy_qualified=False,production_modified=False)
    save(OUT/f'{PREFIX}-result.json',report);print(json.dumps({k:v for k,v in report.items() if k!='artifacts'}))


if __name__=='__main__':main()
