"""One fixed held-out scoring stage, only after all 48 paired fits are frozen."""
import os
os.environ.update(CUDA_VISIBLE_DEVICES='-1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
from concurrent.futures import ProcessPoolExecutor
import argparse
import math
from pathlib import Path
import time
import traceback
import numpy as np
import psutil
from board_river_deal_coverage_common_v1 import ROOT,OUT,STORE,PREFIX,PLAN,LOCK,OTHER,MODEL_SEEDS,read,sha,verify
from board_prefix_publication_v1 import atomic_json
from sampled_visible_features_bulk_v1 import features
from bounded_parallel_evaluation_archive_v2 import production_available
from board_study_storage_v1 import measure

ARMS=('dense-exact','broad-exact','dense-sample16','broad-sample16')
CONTROL=OUT/(PREFIX+'-evaluation-control.json')
REG=OUT/(PREFIX+'-evaluation-registration.json')
RESULT=OUT/(PREFIX+'-evaluation.json')
SHAPES={'0.weight':(64,302),'0.bias':(64,),'2.weight':(64,64),'2.bias':(64,),'4.weight':(4,64),'4.bias':(4,)}


def forward(x,weights):
    x=np.asarray(x,dtype=np.float64);assert x.ndim==2 and x.shape[1]==302 and np.isfinite(x).all()
    assert set(weights)==set(SHAPES)
    for key,shape in SHAPES.items():assert weights[key].shape==shape and np.isfinite(weights[key]).all()
    y=x
    for layer in ('0','2','4'):
        y=y@weights[layer+'.weight'].astype(np.float64).T+weights[layer+'.bias'].astype(np.float64)
        if layer!='4':y=np.maximum(y,0.)
    return (y[:,1]-y[:,0])*400.5


def metrics(predicted,target,original):
    predicted=np.asarray(predicted,dtype=np.float64);target=np.asarray(target,dtype=np.float64)
    original=np.asarray(original,dtype=np.float64)
    assert predicted.shape==target.shape and predicted.ndim==1 and len(target)>0
    assert original.shape==(len(target),4) and np.isfinite(predicted).all() and np.isfinite(target).all()
    assert np.isfinite(original).all() and np.all(original>=0) and np.max(abs(original.sum(1)-1))<1e-12
    cost=np.maximum(target,0)-target*(np.where(predicted>0,1.,np.where(predicted==0,.5,0.)))
    assert np.min(cost)>=-1e-10
    agreement=np.where(target==0,1.,np.where(predicted==0,.5,(np.sign(predicted)==np.sign(target)).astype(float)))
    fc=original[:,:2].sum(1);original_cost=fc*np.maximum(target,0)-original[:,1]*target
    result=dict(rows=len(target),mse_bb2=float(np.mean((predicted-target)**2)),
        fold_call_decision_cost_bb=float(np.mean(cost)),directional_agreement=float(np.mean(agreement)),
        mean_signed_error_bb=float(np.mean(predicted-target)),zero_value_mse_bb2=float(np.mean(target**2)),
        zero_value_decision_cost_bb=float(np.mean(abs(target))*.5),
        original_restricted_fold_call_cost_bb=float(np.mean(original_cost)),original_mean_fold_call_mass=float(np.mean(fc)))
    # Independent scalar payoff reconstruction catches sign, tie and mass errors.
    n=len(target);scalars=dict(
        mse_bb2=math.fsum((float(p)-float(t))**2 for p,t in zip(predicted,target))/n,
        fold_call_decision_cost_bb=math.fsum(abs(float(t))*(.5 if p==0 else 1. if (p<0<t or p>0>t) else 0.) for p,t in zip(predicted,target))/n,
        directional_agreement=math.fsum(1. if t==0 else .5 if p==0 else float((p>0)==(t>0)) for p,t in zip(predicted,target))/n,
        mean_signed_error_bb=math.fsum(float(p)-float(t) for p,t in zip(predicted,target))/n,
        original_restricted_fold_call_cost_bb=math.fsum(float(row[0])*float(t) if t>0 else -float(row[1])*float(t) for row,t in zip(original,target))/n)
    for key,value in scalars.items():assert abs(value-result[key])<1e-10*max(1.,abs(value))
    return result


def control():
    assert not CONTROL.exists()
    source=Path('S:/GTOpen-research/board-river-opponent-reach-v1/control/case-000-export.json')
    inputs={str(p):sha(p) for p in (Path(__file__),PLAN,source,ROOT/'tools/research/sampled_visible_features_bulk_v1.py')}
    result=metrics([1,1,-5,0],[2,-3,0,4],np.full((4,4),.25))
    for key,want in (('mse_bb2',14.5),('fold_call_decision_cost_bb',1.25),('directional_agreement',.625),
        ('mean_signed_error_bb',-1.5),('zero_value_mse_bb2',7.25),('zero_value_decision_cost_bb',1.125),
        ('original_restricted_fold_call_cost_bb',.5625)):
        assert abs(result[key]-want)<1e-12,(key,result[key],want)
    obs=read(source)['queries']['observations'][:97];x=features(obs);rng=np.random.default_rng(9289914)
    weights={k:rng.normal(0,.03,size=shape).astype(np.float32) for k,shape in SHAPES.items()}
    actual=forward(x,weights)
    import torch
    torch.set_num_threads(1);y=torch.tensor(x,dtype=torch.float64)
    for layer in ('0','2','4'):
        y=torch.nn.functional.linear(y,torch.tensor(weights[layer+'.weight'],dtype=torch.float64),
            torch.tensor(weights[layer+'.bias'],dtype=torch.float64))
        if layer!='4':y=torch.relu(y)
    expected=(y[:,1]-y[:,0]).numpy()*400.5
    error=float(np.max(abs(actual-expected)));assert error<1e-10
    rowwise=np.array([forward(row[None,:],weights)[0] for row in x]);rowerror=float(np.max(abs(actual-rowwise)))
    assert rowerror<1e-10 and not torch.cuda.is_initialized();verify(inputs)
    proof=dict(passed=True,inputs=inputs,hand_calculated_metrics=True,maximum_numpy_torch_forward_error_bb=error,
        maximum_batch_row_forward_error_bb=rowerror,examples=len(x),gpu_initialized=False,final_evaluation_read=False)
    atomic_json(CONTROL,proof);print({k:v for k,v in proof.items() if k!='inputs'},flush=True)


def evaluate_one(item):
    record,dataset_path,registration_sha=item;name=record['name'];model=STORE/'fits'/(name+'.npz')
    assert sha(model)==record['model_sha256'] and record['steps']==512 and record['scale']==400.5
    with np.load(model,allow_pickle=False) as z:weights={k:z[k] for k in z.files}
    bank=record['bank'];actor=record['actor']
    with np.load(dataset_path,allow_pickle=False) as z:
        mask=z['evaluation']&(z['actor']==actor)&z['supported'][:,bank]
        assert mask.any();active=z['active'][mask];target=z['delta'][mask,bank];original=z['original_policy'][mask,bank]
        case_ids=z['case_ids'][mask];deal=z['deal'][mask];pot=z['pot'][mask]
        share=z['initial_share'][mask,bank];onpath=z['on_path'][mask,bank]
    assert not set(case_ids.tolist())&set(record['case_ids']) and np.all(deal>=192)
    x=features([dict(active_features=a.tolist()) for a in active]);predicted=forward(x,weights)
    import torch
    torch.set_num_threads(1);independent=torch.tensor(x,dtype=torch.float64)
    for layer in ('0','2','4'):
        independent=torch.nn.functional.linear(independent,torch.tensor(weights[layer+'.weight'],dtype=torch.float64),
            torch.tensor(weights[layer+'.bias'],dtype=torch.float64))
        if layer!='4':independent=torch.relu(independent)
    reference=(independent[:,1]-independent[:,0]).numpy()*400.5
    inference_error=float(np.max(abs(predicted-reference)))
    assert inference_error<1e-7 and not torch.cuda.is_initialized()
    masks=[('all',np.ones(len(target),dtype=bool)),('initialization_only',abs(share-1)<1e-12),
        ('later_generations_contribute',abs(share-1)>=1e-12),('no_hero_mixture_support',~np.isfinite(share)),
        ('hero_on_path',onpath),('hero_off_path',~onpath)]
    for band,low,high in (('under10',0,10),('10to50',10,50),('50to100',50,100),('100to200',100,200),('200plus',200,np.inf)):
        masks.append((band,(pot>=low)&(pot<high)))
    scored={key:(metrics(predicted[m],target[m],original[m]) if m.any() else dict(rows=0)) for key,m in masks}
    retained=dict(predicted_bb=predicted,exact_bb=target,original_policy=original,case_ids=case_ids,deal=deal,pot=pot,
        initial_share=share,hero_on_path=onpath)
    dest=STORE/'evaluation'/(name+'.npz')
    if dest.exists():
        with np.load(dest,allow_pickle=False) as z:
            assert set(z.files)==set(retained)
            for key in retained:
                assert np.array_equal(z[key],retained[key]) if retained[key].dtype.kind=='U' else np.array_equal(z[key],retained[key],equal_nan=True)
    else:
        with dest.open('xb') as f:np.savez_compressed(f,**retained);f.flush();os.fsync(f.fileno())
    return dict(name=name,bank=bank,actor=actor,repetition=record['repetition'],arm=record['arm'],groups=scored,
        predictions_sha256=sha(dest),model_sha256=sha(model),registration_sha256=registration_sha,
        maximum_numpy_torch_prediction_difference_bb=inference_error)


def aggregate(rows):
    out={}
    for arm in ARMS:
        chosen=[r['groups']['all'] for r in rows if r['arm']==arm];assert chosen
        out[arm]={key:math.fsum(r[key] for r in chosen)/len(chosen) for key in chosen[0] if key!='rows'}
        out[arm]['models']=len(chosen);out[arm]['rows_per_model']=[r['rows'] for r in chosen]
    return out


def evaluate(resume):
    began=time.monotonic();assert not RESULT.exists() and not LOCK.exists() and not OTHER.exists();acquired=False
    try:
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True;assert production_available() and psutil.virtual_memory().available>24_000_000_000
        proof=read(CONTROL);assert proof['passed'];verify(proof['inputs'])
        frozen_path=OUT/(PREFIX+'-frozen-models.json');frozen=read(frozen_path);fit_reg=OUT/(PREFIX+'-fit-registration.json')
        assert frozen['passed'] and frozen['complete'] and not frozen['final_evaluation_scored']
        assert frozen['registration_sha256']==sha(fit_reg);verify(read(fit_reg)['inputs'])
        dataset=STORE/'combined-dataset.npz';assert sha(dataset)==frozen['dataset_sha256']
        expected={(b,a,r,arm) for b in (0,1) for a in (0,1) for r in range(3) for arm in ARMS}
        records=frozen['models'];assert len(records)==48 and {(r['bank'],r['actor'],r['repetition'],r['arm']) for r in records}==expected
        for r in records:
            assert r['seed']==MODEL_SEEDS[r['repetition']] and r['steps']==512 and r['scale']==400.5
            assert r['name']==f"bank-{r['bank']}-player-{r['actor']}-repeat-{r['repetition']}-{r['arm']}"
        sources=[Path(__file__),PLAN,CONTROL,frozen_path,fit_reg,dataset,
            ROOT/'tools/research/sampled_visible_features_bulk_v1.py',ROOT/'tools/research/sampled_visible_poker_features_v1.py']
        hashes={str(p):sha(p) for p in sources}
        workers=8 if psutil.cpu_percent(interval=1)<50 else 2
        before=measure(STORE);assert before['logical_bytes']+32_000_000<2_000_000_000
        if resume:assert read(REG)['inputs']==hashes
        else:
            assert not REG.exists() and not (STORE/'evaluation').exists()
            atomic_json(REG,dict(inputs=hashes,workers=workers,models=48,maximum_seconds=600,
                aggregation='Equal means across paired repetitions and actors; by-bank checks retained.',
                heldout_scoring_after_all_models_frozen=True,created_unix=time.time(),production_modified=False))
            (STORE/'evaluation').mkdir()
        rows=[];last=0.
        with ProcessPoolExecutor(max_workers=workers) as pool:
            for row in pool.map(evaluate_one,((r,str(dataset),sha(REG)) for r in records)):
                assert time.monotonic()-began<600
                if time.monotonic()-last>2:
                    assert production_available() and not OTHER.exists();last=time.monotonic()
                rows.append(row)
        overall=aggregate(rows);bybank={str(b):aggregate([r for r in rows if r['bank']==b]) for b in (0,1)}
        checks={'equal_effective_actor_pot_counts':frozen['equal_effective_actor_pot_counts']}
        gates={}
        for gate,other in (('coverage','dense-exact'),('target','broad-sample16')):
            local={}
            for metric in ('mse_bb2','fold_call_decision_cost_bb'):
                local[f'{gate}_aggregate_{metric}']=overall['broad-exact'][metric]<overall[other][metric]
            for bank in ('0','1'):
                local[f'{gate}_bank_{bank}_cost']=bybank[bank]['broad-exact']['fold_call_decision_cost_bb']<=bybank[bank][other]['fold_call_decision_cost_bb']
            checks.update(local);gates[gate]=all(local.values()) and frozen['equal_effective_actor_pot_counts']
        verify(hashes)
        storage=measure(STORE);assert storage['logical_bytes']<2_000_000_000
        result=dict(passed=True,complete=True,registration_sha256=sha(REG),rows=rows,aggregate=overall,by_bank=bybank,
            advancement_checks=checks,gates=gates,qualifies_for_separate_estimator_integration=all(checks.values()),
            statistical_confirmation=False,production_qualified=False,whole_game_EV_measured=False,
            maximum_numpy_torch_prediction_difference_bb=max(r['maximum_numpy_torch_prediction_difference_bb'] for r in rows),
            storage=storage,seconds=time.monotonic()-began,workers=workers,gpu_used=False,production_modified=False)
        atomic_json(RESULT,result);print({k:result[k] for k in ('complete','aggregate','advancement_checks','seconds')},flush=True)
    finally:
        if acquired and LOCK.read_text()==str(os.getpid()):LOCK.unlink()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--mode',choices=('control','evaluate'),required=True)
    parser.add_argument('--resume',action='store_true');args=parser.parse_args();assert not args.resume or args.mode=='evaluate'
    try:
        if args.mode=='control':control()
        else:evaluate(args.resume)
    except Exception as e:
        atomic_json(OUT/(PREFIX+'-evaluation-failure-'+str(time.time_ns())+'.json'),dict(error=repr(e),traceback=traceback.format_exc()));raise
