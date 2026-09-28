"""Exploratory board-relative error decomposition; no final-test data or fitting."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',
                  CUBLAS_WORKSPACE_CONFIG=':4096:8',PYTHONDONTWRITEBYTECODE='1')
import argparse
import gc
import json
from pathlib import Path
import random
import sys
import time
import traceback
import uuid
import numpy as np
import torch
import river_matched_training_pilot_v1 as pilot
from global_research_inventory_v3 import measure
from stack_price_learning_data_v2 import public_factors
from stack_price_learning_fit_v1 import Dataset,load_models,scores,probabilities,PRICE_EDGES,CATEGORIES
from sampled_visible_poker_features_v1 import best_visible_rank

ROOT=pilot.ROOT;OUT=pilot.OUT;NAME='stack-board-error-diagnosis-v1'
SOURCE=Path('S:/GTOpen-research/stack-board-training-budget-v1')
GEOMETRY=Path('S:/GTOpen-research/stack-geometry-control-v1')
STORE=Path('S:/GTOpen-research')/NAME
REG=OUT/(NAME+'-registration.json');RESULT=OUT/(NAME+'-result.json')
read=pilot.read;sha=pilot.sha;write=pilot.atomic_json
RELATIONS=('plays_board','same_category_better_kickers','improves_category')
RULES=('original_positive_scores','largest_predicted_legal_value','exact_zero_fold')

def specification():
    rp=OUT/'stack-board-training-budget-v1-registration.json';reg=read(rp)
    selection=SOURCE/'frozen-selection.json';chosen=read(selection)
    review=OUT/'stack-board-training-budget-v1-readback-v1.json'
    assert read(review)['passed'] and chosen['registration_sha256']==sha(rp)
    candidates=[c for c in chosen['candidates'] if c['arm']=='long'];assert len(candidates)==2
    sampled=sorted(random.Random(9296800).sample(range(512),32))
    boards=[b for b in reg['reused_training_boards'] if b['index'] in sampled]
    for b in reg['boards']:
        if b['split']=='validation':
            p=SOURCE/f"board-{b['index']}.npz"
            boards.append(dict(**b,file=str(p),sha256=sha(p)))
    assert len(boards)==64 and all(b['split'] in ('fit','validation') for b in boards)
    proof=OUT/'global-research-inventory-v3-control-v2.json'
    inventory_reg=OUT/'global-research-inventory-v3-registration-v2.json'
    assert read(proof)['passed'] and read(proof)['registration_sha256']==sha(inventory_reg)
    pilot.verify(read(inventory_reg)['inputs'])
    paths=[Path(__file__),OUT/'STACK-BOARD-ERROR-DIAGNOSIS-PLAN.md',rp,selection,review,proof,inventory_reg]
    paths.extend(Path(b['file']) for b in boards)
    paths.extend(Path(c['selected']['weights']['file']) for c in candidates)
    paths.extend(GEOMETRY/f'stack-{d}-public.json' for d in reg['fitting_depths'])
    for mod in list(sys.modules.values()):
        p=getattr(mod,'__file__',None)
        if p and Path(p).is_relative_to(ROOT) and Path(p).suffix=='.py':paths.append(Path(p))
    return dict(inputs={str(p):sha(p) for p in paths},boards=boards,candidates=candidates,
        fitting_subset_seed=9296800,fitting_indices=sampled,depths=reg['fitting_depths'],
        rules=list(RULES),relations=list(RELATIONS),maximum_seconds=1800,maximum_new_bytes=32_000_000,
        reserve_bytes=32_000_000,scope='Exploratory existing fit/validation data; not an accuracy qualification.',
        test_boards_used=False,heldout_depths_used=False,new_training=False,new_boards=False,production_modified=False)

def load(ref):
    assert sha(ref['file'])==ref['sha256']
    with np.load(ref['file'],allow_pickle=False) as z:
        features=z['features'].copy();counts=z['counts'].copy();hands=z['hands'].copy()
    board=list(ref['board']);base=best_visible_rank(board)
    ranks=[best_visible_rank(list(map(int,h))+board) for h in hands]
    assert all(r>=base for r in ranks)
    relation=np.asarray([0 if r==base else 1 if r[0]==base[0] else 2 for r in ranks],dtype=np.int8)
    return dict(features=features,counts=counts,relation=relation,board_category=base[0])

def analyze(candidate,refs,loaded,contexts,guard):
    model=load_models(candidate['selected']['weights'],candidate['seed'],362);model.eval()
    splits=[]
    for split in ('fit','validation'):
        ids=[i for i,b in enumerate(refs) if b['split']==split]
        boards=[loaded[i] for i in ids];data=Dataset(boards,contexts);nc=len(data.card_np)
        board_ids=np.repeat([refs[i]['index'] for i in ids],1081)
        relations=np.concatenate([b['relation'] for b in boards])
        board_categories=np.repeat([b['board_category'] for b in boards],1081)
        records=[]
        with torch.no_grad():
            for ci,context in enumerate(contexts):
                guard();offset=int(data.offsets[ci]);ns=int(data.lengths[ci]);n=ns*nc
                raw=np.empty((n,2),np.float32)
                for lo in range(0,n,16384):
                    guard();idx=torch.arange(lo,min(n,lo+16384),device='cuda')
                    x,actors,_=data.assemble(offset+idx//nc,idx%nc,362)
                    raw[lo:lo+len(idx)]=scores(model,x,actors)[:,:2].cpu().numpy()
                e=data.economics_np[offset:offset+ns];stack=float(context['stack'])
                delta=(e[:,1,None]*data.equity_np-e[:,2,None]).reshape(-1)
                p=probabilities(raw);choices=(p,(raw[:,1]>raw[:,0]).astype(float),(raw[:,1]>0).astype(float))
                loss=[np.where(delta>0,(1-a)*delta,a*(-delta)) for a in choices]
                fold=raw[:,0].astype(float);call=raw[:,1].astype(float);target=delta/stack
                implied=(call.reshape(ns,nc)*stack+e[:,2,None])/e[:,1,None]
                eq_error=((implied-data.equity_np)**2).reshape(-1);outside=abs(delta)>1e-4*stack
                def summary(mask):
                    count=int(np.count_nonzero(mask))
                    if not count:return dict(rows=0)
                    v=outside[mask]
                    return dict(rows=count,fold_score_rms=float(np.sqrt(np.mean(fold[mask]**2))),
                        call_score_rms=float(np.sqrt(np.mean((call[mask]-target[mask])**2))),
                        implied_equity_rmse=float(np.sqrt(eq_error[mask].mean())),
                        rules=[dict(name=name,mean_regret_bb=float(l[mask].mean()),
                            mean_regret_stack_fraction=float(l[mask].mean()/stack),
                            maximum_regret_bb=float(l[mask].max()),
                            majority_mistake_rate=float((((a[mask]>=.5)!=(delta[mask]>0))&v).sum()/v.sum()) if v.any() else None)
                            for name,l,a in zip(RULES,loss,choices)])
                record=dict(stack=stack,**summary(np.ones(n,dtype=bool)))
                for name,labels,values in (
                    ('boards',np.tile(board_ids,ns),[refs[i]['index'] for i in ids]),
                    ('relations',np.tile(relations,ns),list(range(3))),
                    ('board_categories',np.tile(board_categories,ns),list(range(9))),
                    ('hand_categories',np.tile(data.category_np,ns),list(range(9))),
                    ('actors',np.repeat(e[:,3],nc),[0,1]),
                    ('price_bands',np.repeat(np.searchsorted(PRICE_EDGES,e[:,4],side='right')-1,nc),list(range(6)))):
                    record[name]=[dict(index=int(v),**summary(labels==v)) for v in values]
                    assert sum(row['rows'] for row in record[name])==n
                records.append(record)
            splits.append(dict(split=split,contexts=records,
                rules=[dict(name=name,context_balanced_mean_regret_stack_fraction=float(np.mean([c['rules'][ri]['mean_regret_stack_fraction'] for c in records]))) for ri,name in enumerate(RULES)]))
        del data;gc.collect();torch.cuda.empty_cache()
    del model;gc.collect();torch.cuda.empty_cache()
    return dict(seed=candidate['seed'],selected_step=candidate['selected']['step'],splits=splits)

def main(run):
    spec=specification()
    if not run:
        print(json.dumps(dict(preflight_passed=True,boards=64,candidates=2,new_training=False,gpu_started=False)));return
    assert not any(p.exists() for p in (REG,RESULT,STORE))
    ready,probe=pilot.available();assert ready,'Other work takes priority'
    start=time.monotonic()
    with pilot.LOCK.open('x') as f:f.write(str(os.getpid()))
    try:
        inventory=measure();allocated=sum(r['allocated_file_bytes'] for r in inventory)
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
        guard();contexts=[public_factors(read(GEOMETRY/f'stack-{d}-public.json')) for d in spec['depths']]
        loaded=[load(b) for b in spec['boards']];records=[]
        for c in spec['candidates']:
            guard();pilot.status('diagnosing',seed=c['seed'])
            r=analyze(c,spec['boards'],loaded,contexts,guard);records.append(r)
            write(STORE/f"seed-{c['seed']}.json",r)
            print(json.dumps(dict(seed=c['seed'],summaries=[dict(split=s['split'],rules=s['rules']) for s in r['splits']])),flush=True)
        maximum=0.
        for c,r in zip(spec['candidates'],records):
            for old,new in zip(c['selected']['validation']['contexts'],r['splits'][1]['contexts']):
                error=abs(old['mean_regret_bb']-new['rules'][0]['mean_regret_bb']);maximum=max(maximum,error)
                assert error<1e-4,(c['seed'],old['stack'],error)
        pilot.verify(spec['inputs']);guard()
        result=dict(passed=True,registration_sha256=sha(REG),records=records,
            maximum_original_validation_replay_error_bb=maximum,seconds=time.monotonic()-start,
            storage=pilot.study_measure(STORE),peak_cuda_allocated_bytes=torch.cuda.max_memory_allocated(),
            artifacts={str(p):sha(p) for p in STORE.rglob('*') if p.is_file()},
            test_boards_used=False,heldout_depths_used=False,new_training=False,new_boards=False,
            full_preflop_accuracy_qualified=False,production_modified=False)
        write(RESULT,result);print(json.dumps({k:v for k,v in result.items() if k not in ('records','artifacts')}),flush=True)
    except BaseException as error:
        write(OUT/(NAME+'-interruption-'+uuid.uuid4().hex[:8]+'.json'),dict(error=repr(error),traceback=traceback.format_exc()))
        raise
    finally:
        assert pilot.LOCK.read_text()==str(os.getpid());pilot.LOCK.unlink()

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run',action='store_true');main(parser.parse_args().run)
