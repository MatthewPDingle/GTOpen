"""Bounded CUDA/CPU comparison on the saved genuine two-generation control.

Default invocation is read-only readiness. This does not qualify a 78-model
bank or playing strength and does not fit or modify any saved model.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='2',OMP_NUM_THREADS='2',CUBLAS_WORKSPACE_CONFIG=':4096:8')
import argparse
import json
from pathlib import Path
import subprocess
import time
import numpy as np
import psutil
from later_average_support_v1 import OUT,read
from sampled_physical_root_evaluation_v1 import ROOT,sha
from board_prefix_publication_v1 import atomic_json
from weighted_learning_cuda_control_20260927 import safe_read_only_resources,LOCK,OTHER
from preflop_allin_matrix_v1 import AllinMatrix
from sampled_physical_bank_v1 import histories
from board_training_policy_v1 import probabilities,average
from board_training_gpu_bank_v1 import BoardRootCudaBank64
from sampled_visible_hybrid_gpu_bank_shared_v1 import prepare_cuda_queries
import board_training_checkpoint_v1 as checkpoint

PREFIX='board-training-bank-cuda-control-v1'
CONTROL='board-training-pipeline-control-v1'
REVIEW='board-training-pipeline-readback-v1'
REQUIRED=(CONTROL,REVIEW,'board-training-bank-layout-control-v2',
          'weighted-complete-evaluation-queue-v1','board-training-pipeline-queue-v2')
LIMIT=600


def dependencies():
    missing=[p for p in REQUIRED if not (OUT/f'{p}-result.json').exists()]
    if missing:return None,None,[],missing
    records={};paths=[]
    for prefix in REQUIRED:
        rp=OUT/f'{prefix}-registration.json';result=OUT/f'{prefix}-result.json'
        reg=read(rp);value=read(result)
        assert value['passed'] and value['registration_sha256']==sha(rp)
        for p,h in reg['inputs'].items():assert sha(p)==h,p
        paths.extend((rp,result));records[prefix]=(reg,value)
    reg,control=records[CONTROL];review=records[REVIEW][1]
    assert control['trained_generations']==review['generations']==2 and control['exact_restart_replay']
    assert review['upstream_result_sha256']==sha(OUT/f'{CONTROL}-result.json')
    assert review['final_checkpoint']==control['final_checkpoint']
    assert review['boards_checked']==8 and review['physical_roots_checked']==1024
    assert control['played_generations']==[0,1]
    return reg,control,paths,[]


def main(run=False):
    reg,control,paths,missing=dependencies()
    if not run:
        print(json.dumps(dict(ready=not missing,pending=missing,gpu_started=False,
            generations=2,chunks=[1,2,8],policy_and_reach_tolerance=1e-10,
            fresh_resource_admission_required=True,full_bank_qualified=False)))
        return
    assert not missing,'Missing genuine qualifications: '+str(missing)
    assert not LOCK.exists() and not OTHER.exists() and safe_read_only_resources()
    assert psutil.cpu_percent(interval=1)<30 and psutil.virtual_memory().available>28_000_000_000
    assert psutil.disk_usage('S:/').free>40_000_000_000
    gpu=subprocess.run(['nvidia-smi','--query-gpu=utilization.gpu,memory.free','--format=csv,noheader,nounits'],
        capture_output=True,text=True,timeout=5,creationflags=subprocess.CREATE_NO_WINDOW)
    assert gpu.returncode==0
    util,free=map(float,gpu.stdout.strip().splitlines()[0].split(','))
    assert util<10 and free>6000,'Wait for spare GPU capacity'
    import torch
    assert torch.cuda.is_available()
    torch.set_num_threads(2);torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    began=time.monotonic();last_probe=0.;acquired=False;registered=False;cases=[]
    rp=OUT/f'{PREFIX}-registration.json';result_path=OUT/f'{PREFIX}-result.json'
    failure_path=OUT/f'{PREFIX}-failure.json'
    assert not any(p.exists() for p in (rp,result_path,failure_path))
    def guard():
        nonlocal last_probe
        now=time.monotonic();assert now-began<LIMIT
        if now-last_probe>3:
            assert safe_read_only_resources() and not OTHER.exists()
            assert psutil.virtual_memory().available>24_000_000_000
            assert torch.cuda.mem_get_info()[0]>3_000_000_000
            last_probe=now
    try:
        with LOCK.open('x') as stream:stream.write(str(os.getpid()))
        acquired=True;guard()
        cp=OUT/'bb-context-candidate.json';mp=OUT/'preflop-allin-matrix-control-v1-matrix.json'
        cat=Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')
        qp=Path('S:/GTOpen-research/board-precision-repeat-v1/private-000/queries.json')
        source=cp.read_text();catalog_source=cat.read_text();matrix=AllinMatrix(read(mp),source)
        args=dict(context_source=source,catalog_source=catalog_source,matrix_sha256=sha(mp),
            entry_mass=matrix.btn_mass,root_config=reg['config']['board_root'])
        objects=Path(reg['store'])/'objects'
        state=checkpoint.restore_checkpoint(objects,control['final_checkpoint'],reg['config'],**args)
        assert state['completed_iterations']==2 and len(state['played_bank'])==2
        assert state['next_model']==control['unplayed_excluded']
        documents=[checkpoint.model_document(objects,r,**args) for r in state['played_bank']]
        for row,reference in zip(control['metrics'],state['played_bank']):
            assert sha(row['path'])==row['sha256'] and read(row['path'])['used_model']==reference
            paths.append(Path(row['path']))
        assert read(control['metrics'][-1]['path'])['checkpoint']==control['final_checkpoint']
        catalog=read(cat);q=read(qp)
        assert catalog['context_source']==q['context_source']==source
        root_obs=[r['observation'] for r in catalog['native_observations'] if r['player']==0]
        assert len(root_obs)==169 and all(int(o['hi'])==1 and o['own_history']==[] for o in root_obs)
        queries=[('all-root-classes',dict(context_source=source,observations=root_obs)),
                 ('native-histories',dict(context_source=source,observations=q['observations']))]
        paths.extend((cp,mp,cat,qp,*objects.iterdir(),*Path(__file__).parent.glob('*.py')))
        inputs={str(p):sha(p) for p in paths}
        specification=dict(inputs=inputs,maximum_seconds=LIMIT,chunks=[1,2,8],tolerance=1e-10,
            played_models=state['played_bank'],unplayed_excluded=state['next_model'],
            control_result_sha256=sha(OUT/f'{CONTROL}-result.json'),
            independent_readback_sha256=sha(OUT/f'{REVIEW}-result.json'),
            weight_cases={'training':[[1.,2.],[1.,2.]],'actor-specific-test':[[1.,2.],[4.,9.]]},
            observations=[dict(name=name,count=len(query['observations'])) for name,query in queries],
            scope='Two genuine played models; CUDA composition and own-action averaging only. No 78-model or strength qualification.',
            metadata_limit_bytes=4_000_000,raw_outputs_written=False,production_modified=False)
        assert len(json.dumps(specification).encode())<3_000_000
        atomic_json(rp,specification);registered=True
        policy_args={k:v for k,v in args.items() if k!='context_source'}
        for name,query in queries:
            guard();prepared=prepare_cuda_queries(query,guard=guard)
            original_sha=sha(qp)
            history=histories(query['observations'])
            if name=='native-histories':assert any(history)
            policies=[probabilities(query,model,device='cpu',**policy_args)[0] for model in documents]
            for weight_name,rows in specification['weight_cases'].items():
                weights=np.array(rows,dtype=np.float64)
                expected,reach=average(query,documents,completed_iterations=2,weights_by_player=weights,
                    guard=guard,device='cpu',**policy_args)
                numerator=np.zeros_like(expected);denominator=np.zeros_like(reach)
                for i,o in enumerate(query['observations']):
                    for g,p in enumerate(policies):
                        mass=float(weights[o['actor'],g])
                        for ancestor,action in history[i]:mass*=p[ancestor,action]
                        numerator[i]+=mass*p[i];denominator[i]+=mass
                assert np.all(denominator>0),'Uniform initial policy must provide positive legal reach'
                numerator/=denominator[:,None]
                scalar_error=float(np.max(abs(numerator-expected)))
                scalar_reach_error=float(np.max(abs(denominator-reach)))
                assert max(scalar_error,scalar_reach_error)<1e-10
                for chunk in (1,2,8):
                    guard();bank=BoardRootCudaBank64(documents,weights,completed_iterations=2,
                        models_per_chunk=chunk,guard=guard,**args)
                    got,actual_reach=bank.average_prepared(prepared,guard=guard)
                    error=float(np.max(abs(got-expected)));reach_error=float(np.max(abs(actual_reach-reach)))
                    assert max(error,reach_error)<1e-10
                    wrapper_error=wrapper_reach_error=None
                    if chunk==1:
                        wrapper,wrapper_reach=bank.average(query,guard=guard)
                        wrapper_error=float(np.max(abs(wrapper-got)))
                        wrapper_reach_error=float(np.max(abs(wrapper_reach-actual_reach)))
                        assert max(wrapper_error,wrapper_reach_error)<1e-10
                    cases.append(dict(query=name,weights=weight_name,chunk=chunk,policy_error=error,
                        reach_error=reach_error,scalar_error=scalar_error,scalar_reach_error=scalar_reach_error,
                        wrapper_error=wrapper_error,wrapper_reach_error=wrapper_reach_error))
                    del bank
            assert sha(qp)==original_sha
            del prepared
        for p,h in inputs.items():guard();assert sha(p)==h,p
        result=dict(passed=True,registration_sha256=sha(rp),cases=cases,seconds=time.monotonic()-began,
            gpu_used=True,trained_models=2,full_78_model_bank_qualified=False,accuracy_qualified=False,
            training_performed=False,production_modified=False)
        assert rp.stat().st_size+len(json.dumps(result).encode())<4_000_000
        atomic_json(result_path,result);print(json.dumps(result),flush=True)
    except BaseException as exc:
        if registered:
            atomic_json(failure_path,dict(passed=False,registration_sha256=sha(rp),error=repr(exc),
                completed_cases=cases,seconds=time.monotonic()-began,production_modified=False))
        raise
    finally:
        if acquired:
            assert LOCK.read_text()==str(os.getpid());LOCK.unlink()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run',action='store_true')
    main(parser.parse_args().run)
