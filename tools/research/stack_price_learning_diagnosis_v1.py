"""Exploratory train/validation-only error decomposition of frozen price models."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',
                  CUBLAS_WORKSPACE_CONFIG=':4096:8',PYTHONDONTWRITEBYTECODE='1')
import gc
import hashlib
import json
from pathlib import Path
import sys
import time
import traceback
import numpy as np
import torch
import river_matched_training_pilot_v1 as pilot
from stack_price_learning_data_v2 import public_factors
from stack_price_learning_fit_v1 import Dataset,load_models,scores,probabilities

ROOT=pilot.ROOT;OUT=pilot.OUT;NAME='stack-price-learning-diagnosis-v1'
ORIGINAL=Path('S:/GTOpen-research/stack-price-learning-v2')
GEOMETRY=Path('S:/GTOpen-research/stack-geometry-control-v1')
STORE=Path('S:/GTOpen-research')/NAME
REG=OUT/(NAME+'-registration.json');RESULT=OUT/(NAME+'-result.json')
read=pilot.read;sha=pilot.sha;write=pilot.atomic_json

def specification():
    source_reg=OUT/'stack-price-learning-v2-registration.json'
    registered=read(source_reg);selection=ORIGINAL/'frozen-selection.json';chosen=read(selection)
    assert chosen['registration_sha256']==sha(source_reg)
    review=OUT/'stack-price-learning-v2-readback-v1.json';assert read(review)['passed']
    # Selection was frozen previously. Do not read held-out contexts or test-board files.
    tasks=[b for b in registered['boards'] if b['split'] in ('fit','validation')]
    assert len(tasks)==32 and all(b['index']<32 for b in tasks)
    paths=[Path(__file__),source_reg,selection,review]
    paths.extend(ORIGINAL/f"board-{b['index']}.npz" for b in tasks)
    paths.extend(Path(c['selected']['weights']['file']) for c in chosen['candidates'])
    paths.extend(GEOMETRY/f'stack-{d}-public.json' for d in registered['fitting_depths'])
    for m in list(sys.modules.values()):
        p=getattr(m,'__file__',None)
        if p and Path(p).is_relative_to(ROOT) and Path(p).suffix=='.py':paths.append(Path(p))
    return dict(inputs={str(p):sha(p) for p in paths},boards=tasks,candidates=chosen['candidates'],
        depths=registered['fitting_depths'],source_registration_sha256=sha(source_reg),
        scope='Exploratory error diagnosis after the failed learning gate; not a new validation or promoted policy.',
        rules=['original_positive_score_matching','largest_predicted_legal_value','exact_zero_fold_then_predicted_call'],
        metrics=['actual_mixed_policy_regret','legal_value_mse','fold_score_rms','call_score_rms',
                 'implied_equity_rmse','majority_mistake_rate_outside_registered_band'],
        fit_checkpoint_selection=False,new_training=False,new_boards=False,
        test_boards_used=False,heldout_depths_used=False,production_modified=False,
        maximum_seconds=1800,maximum_new_bytes=32_000_000)

def analyze(candidate,boards,contexts,guard):
    width=candidate['width'];seed=candidate['seed']
    model=load_models(candidate['selected']['weights'],seed,width);model.eval()
    split_records=[]
    for split in ('fit','validation'):
        selected=[b for b in boards if b['split']==split]
        data=Dataset([b['data'] for b in selected],contexts)
        nc=len(data.card_np);records=[]
        with torch.no_grad():
            for ci,context in enumerate(contexts):
                offset=int(data.offsets[ci]);ns=int(data.lengths[ci]);n=ns*nc
                raw=np.empty((n,2),dtype=np.float32)
                for lo in range(0,n,16384):
                    guard();idx=torch.arange(lo,min(n,lo+16384),device='cuda')
                    x,actor,_=data.assemble(offset+idx//nc,idx%nc,width)
                    raw[lo:lo+len(idx)]=scores(model,x,actor)[:,:2].cpu().numpy()
                e=data.economics_np[offset:offset+ns];stack=float(context['stack'])
                delta=(e[:,1,None]*data.equity_np-e[:,2,None]).reshape(-1)
                p=probabilities(raw);greedy=(raw[:,1]>raw[:,0]).astype(np.float64)
                anchor=(raw[:,1]>0).astype(np.float64)
                target=delta/stack;fold=raw[:,0].astype(np.float64);call=raw[:,1].astype(np.float64)
                implied=(call.reshape(ns,nc)*stack+e[:,2,None])/e[:,1,None]
                equity_squared_error=((implied-data.equity_np)**2).reshape(-1)
                losses=[np.where(delta>0,(1-a)*delta,a*(-delta)) for a in (p,greedy,anchor)]
                outside=abs(delta)>1e-4*stack
                def summary(mask):
                    v=outside[mask]
                    return dict(rows=int(mask.sum()),
                        fold_score_rms=float(np.sqrt(np.mean(fold[mask]**2))),
                        call_score_rms=float(np.sqrt(np.mean((call[mask]-target[mask])**2))),
                        mean_legal_value_mse=float(np.mean((fold[mask]**2+(call[mask]-target[mask])**2)/2)),
                        implied_equity_rmse=float(np.sqrt(equity_squared_error[mask].mean())),
                        rules=[dict(name=name,mean_regret_bb=float(loss[mask].mean()),
                            mean_regret_stack_fraction=float(loss[mask].mean()/stack),
                            majority_mistake_rate=float((((a[mask]>=.5)!=(delta[mask]>0))&v).sum()/v.sum()) if v.any() else None)
                            for name,loss,a in zip(('original_positive_score_matching','largest_predicted_legal_value','exact_zero_fold_then_predicted_call'),losses,(p,greedy,anchor))])
                record=dict(stack=stack,**summary(np.ones(n,dtype=bool)))
                board_ids=np.tile(np.repeat([b['index'] for b in selected],1081),ns)
                record['boards']=[dict(index=b['index'],**summary(board_ids==b['index'])) for b in selected]
                records.append(record)
        split_records.append(dict(split=split,contexts=records,
            rules=[dict(name=name,context_balanced_mean_regret_stack_fraction=float(np.mean([c['rules'][ri]['mean_regret_stack_fraction'] for c in records])))
                   for ri,name in enumerate(('original_positive_score_matching','largest_predicted_legal_value','exact_zero_fold_then_predicted_call'))]))
        del data;gc.collect();torch.cuda.empty_cache()
    del model;gc.collect();torch.cuda.empty_cache()
    return dict(seed=seed,width=width,splits=split_records)

def main():
    spec=specification()
    assert not any(p.exists() for p in (REG,RESULT,STORE))
    ready,probe=pilot.available();assert ready,'Other work takes priority'
    start=time.monotonic()
    with pilot.LOCK.open('x') as f:f.write(str(os.getpid()))
    try:
        inventory=pilot.global_measure();allocated=sum(r['allocated_file_bytes'] for r in inventory)
        assert allocated+64_000_000<=pilot.GLOBAL_LIMIT
        write(REG,spec);pilot.create(STORE);write(STORE/'admission.json',dict(inventory=inventory,allocated_bytes=allocated,gpu=probe))
        pilot.STORE=STORE;pilot.LIMIT=32_000_000;pilot.STATUS=OUT/(NAME+'-status.json')
        torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
        torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
        torch.cuda.set_per_process_memory_fraction(pilot.CUDA_BUDGET_BYTES/torch.cuda.get_device_properties(0).total_memory)
        resource=pilot.Guard()
        def guard():
            assert time.monotonic()-start<1800
            resource()
        contexts=[public_factors(read(GEOMETRY/f'stack-{d}-public.json')) for d in spec['depths']]
        boards=[]
        for b in spec['boards']:
            with np.load(ORIGINAL/f"board-{b['index']}.npz",allow_pickle=False) as d:
                boards.append(dict(**b,data=dict(features=d['features'].copy(),counts=d['counts'].copy())))
        records=[]
        for candidate in spec['candidates']:
            guard();pilot.status('diagnosing',seed=candidate['seed'],width=candidate['width'])
            record=analyze(candidate,boards,contexts,guard);records.append(record)
            write(STORE/f"diagnosis-{candidate['seed']}-{candidate['width']}.json",record)
            print(json.dumps(dict(seed=candidate['seed'],width=candidate['width'],
                summaries=[dict(split=s['split'],rules=s['rules']) for s in record['splits']])),flush=True)
        pilot.verify(spec['inputs']);guard()
        # The registered validation means must replay unchanged under the original rule.
        maximum=0.
        for candidate,record in zip(spec['candidates'],records):
            for old,new in zip(candidate['selected']['validation']['contexts'],record['splits'][1]['contexts']):
                error=abs(old['mean_regret_bb']-new['rules'][0]['mean_regret_bb']);maximum=max(maximum,error)
                assert error<1e-4,(candidate['seed'],candidate['width'],old['stack'],error)
        result=dict(passed=True,registration_sha256=sha(REG),records=records,
            maximum_original_validation_replay_error_bb=maximum,seconds=time.monotonic()-start,
            storage=pilot.study_measure(STORE),peak_cuda_allocated_bytes=torch.cuda.max_memory_allocated(),
            artifacts={str(p):sha(p) for p in STORE.rglob('*') if p.is_file()},
            test_boards_used=False,heldout_depths_used=False,new_training=False,production_modified=False,
            scientific_status='Exploratory error decomposition only; original learning failure remains unchanged.')
        write(RESULT,result);print(json.dumps({k:v for k,v in result.items() if k not in ('records','artifacts')}),flush=True)
    except BaseException as error:
        write(OUT/(NAME+'-interruption.json'),dict(complete=False,error=repr(error),traceback=traceback.format_exc()))
        raise
    finally:
        assert pilot.LOCK.read_text()==str(os.getpid());pilot.LOCK.unlink()

if __name__=='__main__':main()
