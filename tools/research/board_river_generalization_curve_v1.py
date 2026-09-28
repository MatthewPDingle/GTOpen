"""Nested learning curves inside the original training partition only."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',
    CUBLAS_WORKSPACE_CONFIG=':4096:8',PYTHONDONTWRITEBYTECODE='1')
import hashlib
import math
from pathlib import Path
import time
import traceback
import numpy as np
from board_river_target_common_v1 import ROOT,OUT,STORE,PREFIX,LOCK,OTHER,read,sha,verify
from board_river_target_collect_v1 import Guard
from board_river_target_fit_v1 import loss
from board_prefix_publication_v1 import atomic_json
from board_later_fit_holdout_train_v1 import configure
from sampled_visible_initialization_v1 import fresh_visible_network
from sampled_visible_features_bulk_v1 import features
from board_study_storage_v1 import measure

NAME='board-river-generalization-curve-v1'
DEST=STORE/'generalization-curve-v1'
PLAN=OUT/'BOARD-RIVER-GENERALIZATION-CURVE-PLAN.md'
REG=OUT/(NAME+'-registration.json')
RESULT=OUT/(NAME+'-result.json')
COUNTS=(8,16,32,48)
SEEDS=(9289951,9289952,9289953)


def prediction(x,weights):
    import torch
    y=x.astype(np.float64);independent=torch.tensor(y,dtype=torch.float64)
    for layer in ('0','2','4'):
        w=weights[layer+'.weight'].astype(np.float64);b=weights[layer+'.bias'].astype(np.float64)
        y=y@w.T+b;independent=torch.nn.functional.linear(independent,torch.tensor(w),torch.tensor(b))
        if layer!='4':y=np.maximum(y,0);independent=torch.relu(independent)
    actual=(y[:,1]-y[:,0])*400.5;reference=(independent[:,1]-independent[:,0]).numpy()*400.5
    error=float(np.max(abs(actual-reference)));assert error<1e-7
    return actual,error


def metrics(p,t):
    p=np.asarray(p);t=np.asarray(t);assert len(t)>0 and p.shape==t.shape and np.isfinite(p).all() and np.isfinite(t).all()
    cost=np.maximum(t,0)-t*np.where(p>0,1,np.where(p==0,.5,0))
    scalar=math.fsum(abs(float(y))*(.5 if x==0 else float(x*y<0)) for x,y in zip(p,t))/len(t)
    assert abs(scalar-float(np.mean(cost)))<1e-10
    return dict(rows=len(t),mse_bb2=float(np.mean((p-t)**2)),decision_cost_bb=scalar,
        direction_agreement=float(np.mean(np.where(t==0,1,np.where(p==0,.5,(p*t>0).astype(float))))),
        signed_bias_bb=float(np.mean(p-t)),zero_mse_bb2=float(np.mean(t*t)))


def main():
    import torch
    began=time.monotonic();assert not LOCK.exists() and not OTHER.exists() and not REG.exists() and not DEST.exists()
    acquired=False
    try:
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True;configure();torch.use_deterministic_algorithms(True);guard=Guard();guard.limit=300;guard()
        control_path=OUT/(PREFIX+'-fit-control.json');control=read(control_path);assert control['passed'];verify(control['inputs'])
        proof_path=OUT/(PREFIX+'-readback.json');proof=read(proof_path);dataset=Path(proof['dataset'])
        assert proof['passed'] and proof['complete'] and sha(dataset)==proof['dataset_sha256']
        assert read(OUT/(PREFIX+'-pipeline.json'))['complete']
        inputs={str(p):sha(p) for p in (Path(__file__),PLAN,control_path,proof_path,dataset,
            ROOT/'tools/research/board_river_target_fit_v1.py',ROOT/'tools/research/sampled_visible_initialization_v1.py',
            ROOT/'tools/research/sampled_visible_features_bulk_v1.py')}
        order=sorted(range(64),key=lambda d:hashlib.sha256(f'9289941|{d}'.encode()).digest())
        fit_deals=order[:48];validation_deals=order[48:];assert not set(fit_deals)&set(validation_deals)
        with np.load(dataset,allow_pickle=False) as z:
            original_train=~z['evaluation'];assert np.all(z['deal'][original_train]<64)
            data={key:z[key][original_train] for key in ('active','actor','deal','case_ids','delta','supported')}
        assert len(data['deal'])==1152 and set(data['deal'])==set(range(64)) and np.all(data['supported'])
        x=features([dict(active_features=a.tolist()) for a in data['active']]);assert len(x)==1152
        size=measure(STORE,guard);assert size['logical_bytes']+20_000_000<2_000_000_000
        atomic_json(REG,dict(inputs=inputs,fit_deals=fit_deals,validation_deals=validation_deals,nested_counts=COUNTS,
            seeds=SEEDS,models=48,original_final_evaluation_reused=False,exploratory_development_only=True,
            maximum_added_bytes=20_000_000,maximum_seconds=300,created_unix=time.time()));DEST.mkdir()
        rows=[];max_error=0.
        for bank in (0,1):
            for actor in (0,1):
                vm=(data['actor']==actor)&np.isin(data['deal'],validation_deals);assert int(vm.sum())==144
                for repeat,seed in enumerate(SEEDS):
                    for count in COUNTS:
                        guard();tm=(data['actor']==actor)&np.isin(data['deal'],fit_deals[:count]);assert int(tm.sum())==count*9
                        assert not np.any(tm&vm)
                        a=torch.tensor(x[tm],device='cuda');b=torch.tensor(data['delta'][tm,bank]/400.5,dtype=torch.float32,device='cuda')
                        model=fresh_visible_network(seed).cuda();optimizer=torch.optim.Adam(model.parameters(),lr=.003)
                        for step in range(512):
                            guard();optimizer.zero_grad(set_to_none=True);value=loss(model,a,b)
                            assert bool(torch.isfinite(value));value.backward();optimizer.step()
                        weights={k:v.detach().cpu().numpy().copy() for k,v in model.state_dict().items()}
                        pred,error=prediction(x[tm|vm],weights);max_error=max(max_error,error)
                        used=np.flatnonzero(tm|vm);inside=tm[used];truth=data['delta'][used,bank]
                        name=f'bank-{bank}-actor-{actor}-repeat-{repeat}-deals-{count}'
                        path=DEST/(name+'.npz');assert not path.exists()
                        retained=dict(**weights,predicted_bb=pred,exact_bb=truth,is_training=inside,
                            case_ids=data['case_ids'][used],deals=data['deal'][used])
                        with path.open('xb') as f:np.savez_compressed(f,**retained);f.flush();os.fsync(f.fileno())
                        row=dict(name=name,bank=bank,actor=actor,repetition=repeat,seed=seed,training_deals=count,
                            training=metrics(pred[inside],truth[inside]),validation=metrics(pred[~inside],truth[~inside]),
                            artifact_sha256=sha(path),numpy_torch_max_error_bb=error)
                        rows.append(row);print(dict(models=len(rows),seconds=time.monotonic()-began),flush=True)
        verify(inputs);size=measure(DEST,guard);assert size['logical_bytes']<20_000_000
        aggregate={}
        for count in COUNTS:
            chosen=[r for r in rows if r['training_deals']==count];assert len(chosen)==12
            aggregate[str(count)]={split:{key:math.fsum(r[split][key] for r in chosen)/12 for key in chosen[0][split] if key!='rows'}
                for split in ('training','validation')}
        result=dict(passed=True,complete=True,registration_sha256=sha(REG),rows=rows,aggregate=aggregate,
            maximum_numpy_torch_error_bb=max_error,storage=size,seconds=time.monotonic()-began,
            original_final_evaluation_reused=False,production_qualified=False,exploratory_development_only=True)
        atomic_json(RESULT,result);print(dict(complete=True,aggregate=aggregate,seconds=result['seconds']),flush=True)
    except Exception as e:
        atomic_json(OUT/(NAME+'-failure.json'),dict(error=repr(e),traceback=traceback.format_exc()));raise
    finally:
        if acquired and LOCK.read_text()==str(os.getpid()):LOCK.unlink()


if __name__=='__main__':main()
