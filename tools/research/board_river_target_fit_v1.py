"""Paired fixed-budget contrast regressors; evaluation is a separate later stage."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',
    CUBLAS_WORKSPACE_CONFIG=':4096:8',PYTHONDONTWRITEBYTECODE='1')
import argparse
import json
from pathlib import Path
import time
import traceback
import numpy as np
from board_river_target_common_v1 import *
from board_river_target_collect_v1 import Guard
from board_prefix_publication_v1 import atomic_json
from board_later_fit_holdout_train_v1 import configure
from sampled_visible_initialization_v1 import fresh_visible_network
from sampled_visible_features_bulk_v1 import features
from board_study_storage_v1 import measure

SCALE=400.5
STEPS=512
ARMS=('exact','sample1','sample16')
CONTROL=OUT/(PREFIX+'-fit-control.json')
REG=OUT/(PREFIX+'-fit-registration.json')
FROZEN=OUT/(PREFIX+'-frozen-models.json')


def loss(model,x,y):
    prediction=model(x);delta=prediction[:,1]-prediction[:,0]
    return ((delta-y)**2).mean()


def source_hashes():
    files=[Path(__file__),PLAN,ROOT/'tools/research/board_river_target_common_v1.py',
        ROOT/'tools/research/board_river_target_collect_v1.py',ROOT/'tools/research/board_river_bounds_pilot_support_v2.py',
        ROOT/'tools/research/sampled_visible_initialization_v1.py',ROOT/'tools/research/sampled_physical_fit_v1.py',
        ROOT/'tools/research/sampled_visible_features_bulk_v1.py',ROOT/'tools/research/sampled_visible_poker_features_v1.py']
    return {str(p):sha(p) for p in files}


def control(guard):
    import torch
    assert not CONTROL.exists();hashes=source_hashes()
    source=Path('S:/GTOpen-research/board-river-opponent-reach-v1/control/case-000-export.json')
    hashes[str(source)]=sha(source);obs=read(source)['queries']['observations'][:97]
    x=features(obs);y=np.linspace(-.8,.9,len(x),dtype=np.float32)
    # Analytic output derivative independently checks both signs and scaling.
    z=torch.tensor([[.2,.7,4.,-8.],[-.3,.1,-2.,9.]],dtype=torch.float64,requires_grad=True)
    targets=torch.tensor([.9,-.4],dtype=torch.float64)
    objective=((z[:,1]-z[:,0]-targets)**2).mean();objective.backward()
    expected=np.zeros((2,4));residual=z.detach().numpy()[:,1]-z.detach().numpy()[:,0]-targets.numpy()
    expected[:,1]=residual;expected[:,0]=-residual
    assert np.max(abs(z.grad.numpy()-expected))<1e-12
    states=[];losses=[];gradients=[]
    for device in ('cpu','cuda'):
        guard();model=fresh_visible_network(MODEL_SEEDS[0]).to(device)
        a=torch.tensor(x,device=device);b=torch.tensor(y,device=device);optimizer=torch.optim.Adam(model.parameters(),lr=.003)
        for _ in range(8):
            optimizer.zero_grad(set_to_none=True);value=loss(model,a,b);value.backward();optimizer.step()
        optimizer.zero_grad(set_to_none=True);value=loss(model,a,b);value.backward()
        states.append({k:v.detach().cpu().numpy().copy() for k,v in model.state_dict().items()})
        losses.append(float(value.detach().cpu()));gradients.append([p.grad.detach().cpu().numpy().copy() for p in model.parameters()])
    pd=max(float(np.max(abs(states[0][k]-states[1][k]))) for k in states[0])
    gd=max(float(np.max(abs(a-b))) for a,b in zip(*gradients))
    assert pd<1e-5 and gd<1e-5 and abs(losses[0]-losses[1])<1e-5,(pd,gd,losses)
    verify(hashes);proof=dict(passed=True,inputs=hashes,examples=len(x),steps=8,analytic_output_gradient=True,
        maximum_cpu_gpu_parameter_difference=pd,maximum_cpu_gpu_gradient_difference=gd,
        cpu_gpu_loss_difference=abs(losses[0]-losses[1]),final_evaluation_read=False)
    atomic_json(CONTROL,proof);print(json.dumps({k:v for k,v in proof.items() if k!='inputs'}),flush=True)


def fit(guard,resume):
    import torch
    assert not FROZEN.exists();control_result=read(CONTROL);assert control_result['passed'];verify(control_result['inputs'])
    hashes=source_hashes();proof_path=OUT/(PREFIX+'-readback.json');proof=read(proof_path)
    assert proof['passed'] and proof['complete'];dataset=Path(proof['dataset']);assert sha(dataset)==proof['dataset_sha256']
    hashes.update({str(p):sha(p) for p in (CONTROL,proof_path,dataset)})
    storage=measure(STORE,guard);assert storage['logical_bytes']+32_000_000<LIMIT
    if resume:assert read(REG)['inputs']==hashes
    else:
        assert not REG.exists() and not (STORE/'fits').exists()
        atomic_json(REG,dict(inputs=hashes,arms=ARMS,model_seeds=MODEL_SEEDS,steps=STEPS,scale=SCALE,
            optimizer='full-batch Adam 0.003',loss='equal-row squared output1-minus-output0 contrast error',
            models=36,heldout_scoring='After all models frozen; separate evaluation stage.',
            created_unix=time.time(),production_modified=False));(STORE/'fits').mkdir()
    # Only training rows enter feature preparation or targets. Evaluation rows
    # remain unused here; the fixed partition and its hash are already public.
    with np.load(dataset,allow_pickle=False) as z:
        training=~z['evaluation'];active=z['active'][training];actors=z['actor'][training]
        support=z['supported'][training];exact=z['delta'][training]
        sampled={name:z[name][training] for name in ('sample1','sample16')}
        case_ids=z['case_ids'][training]
    x=features([dict(active_features=a.tolist()) for a in active]);records=[];started=time.monotonic()
    for bank in (0,1):
        for actor in (0,1):
            mask=(actors==actor)&support[:,bank];assert mask.any()
            a=torch.tensor(x[mask],device='cuda');reference=exact[mask,bank]
            for repeat,seed in enumerate(MODEL_SEEDS):
                for arm in ARMS:
                    guard();name=f'bank-{bank}-player-{actor}-repeat-{repeat}-{arm}'
                    mp=STORE/'fits'/(name+'.npz');rp=STORE/'fits'/(name+'.json')
                    if rp.exists():
                        record=read(rp);assert record['registration_sha256']==sha(REG) and record['model_sha256']==sha(mp)
                        records.append(record);continue
                    assert not mp.exists(),'Incomplete model marker; preserve and inspect before resuming'
                    target=reference if arm=='exact' else sampled[arm][mask,bank,repeat]
                    assert np.isfinite(target).all();b=torch.tensor(target/SCALE,dtype=torch.float32,device='cuda')
                    model=fresh_visible_network(seed).cuda();optimizer=torch.optim.Adam(model.parameters(),lr=.003)
                    began=time.monotonic()
                    for _ in range(STEPS):
                        guard();optimizer.zero_grad(set_to_none=True);value=loss(model,a,b)
                        assert bool(torch.isfinite(value));value.backward();optimizer.step()
                    with torch.no_grad():
                        score=model(a);predicted=(score[:,1]-score[:,0]).cpu().numpy().astype(np.float64)*SCALE
                    assert np.isfinite(predicted).all()
                    weights={k:v.detach().cpu().numpy().copy() for k,v in model.state_dict().items()}
                    with mp.open('xb') as f:np.savez_compressed(f,**weights);f.flush();os.fsync(f.fileno())
                    record=dict(name=name,bank=bank,actor=actor,repetition=repeat,seed=seed,arm=arm,steps=STEPS,
                        examples=int(mask.sum()),case_ids=case_ids[mask].tolist(),scale=SCALE,
                        training_label_mse_bb2=float(np.mean((predicted-target)**2)),
                        training_exact_mse_bb2=float(np.mean((predicted-reference)**2)),
                        model_sha256=sha(mp),registration_sha256=sha(REG),seconds=time.monotonic()-began)
                    atomic_json(rp,record);records.append(record)
                    print(json.dumps(dict(frozen_models=len(records),total_models=36,seconds=time.monotonic()-started)),flush=True)
    assert len(records)==36;verify(hashes);storage=measure(STORE,guard);assert storage['logical_bytes']<LIMIT
    frozen=dict(passed=True,complete=True,registration_sha256=sha(REG),models=records,dataset_sha256=sha(dataset),
        final_evaluation_scored=False,production_modified=False,storage=storage,seconds=time.monotonic()-started,
        peak_cuda_allocated_bytes=torch.cuda.max_memory_allocated(),peak_cuda_reserved_bytes=torch.cuda.max_memory_reserved())
    atomic_json(FROZEN,frozen);print(json.dumps(dict(models_frozen=36,final_evaluation_scored=False)),flush=True)


def main(mode,resume):
    assert not LOCK.exists() and not OTHER.exists();acquired=False
    try:
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True
        import torch
        configure();torch.use_deterministic_algorithms(True);guard=Guard();guard.limit=3600;guard()
        if mode=='control':control(guard)
        else:fit(guard,resume)
    except Exception as e:
        path=OUT/(PREFIX+'-fit-failure-'+str(time.time_ns())+'.json')
        atomic_json(path,dict(error=repr(e),traceback=traceback.format_exc()));raise
    finally:
        if acquired and LOCK.read_text()==str(os.getpid()):LOCK.unlink()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--mode',choices=('control','fit'),required=True)
    parser.add_argument('--resume',action='store_true');args=parser.parse_args();assert not args.resume or args.mode=='fit';main(args.mode,args.resume)
