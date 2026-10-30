"""Synthetic weighted-objective and exact-resume control; no poker training."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',CUBLAS_WORKSPACE_CONFIG=':4096:8')
import copy
import json
from pathlib import Path
import subprocess
import time
import numpy as np
import psutil
from later_average_support_v1 import OUT,read
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from sampled_physical_reservoir_v1 import PhysicalReservoir
from sampled_physical_fit_v1 import grouped_rows as old_grouped
from weighted_physical_reservoir_v1 import WeightedPhysicalReservoir,ARRAYS
from weighted_visible_objective_v1 import grouped_rows,PreparedWeightedObjective
from sampled_visible_initialization_v1 import fresh_visible_network
from sampled_visible_features_bulk_v1 import features
from showdown_root_trajectory_20260927 import safe_read_only_resources

PREFIX='weighted-learning-control-v1'
LOCK=ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER=ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock'


def equal(a,b):
    return a.seen==b.seen and a.rng.bit_generator.state==b.rng.bit_generator.state and all(
        np.array_equal(getattr(a,k),getattr(b,k)) for k in ARRAYS)


def main():
    import torch
    torch.set_num_threads(2);torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    start=time.monotonic();last=0.
    def guard():
        nonlocal last
        assert time.monotonic()-start<180 and psutil.virtual_memory().available>20_000_000_000
        if time.monotonic()-last>2:assert safe_read_only_resources();last=time.monotonic()
    guard();assert psutil.cpu_percent(interval=1)<70
    path=Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')
    context_path=OUT/'bb-context-candidate.json';context=context_path.read_text()
    observations=[copy.deepcopy(r['observation']) for r in read(path)['native_observations'] if r['player']==0][:12]
    assert len(observations)==12
    for i,o in enumerate(observations):o['n']=2+i%3
    # Menus and advantage values are deliberately synthetic numerical fixtures.
    # Their visible card/history features come from previously inspected catalog rows.
    paths=[path,context_path,*Path(__file__).parent.glob('*.py'),OUT/'WEIGHTED-LEARNING-CONTROL-PLAN.md']
    bindings={str(p):sha(p) for p in paths}
    rp=OUT/f'{PREFIX}-registration.json'
    save(rp,dict(inputs=bindings,capacity=37,visits=120,network_seed=9272001,
        gradient_tolerance=1e-10,parameter_cuda_tolerance=1e-4,optimizer_steps=8,
        maximum_seconds=180,fixture='Synthetic varying targets, weights and menus on 12 existing visible observations.',
        training=False,production_modified=False))
    weighted=WeightedPhysicalReservoir(37,0,9272001,context)
    unit=WeightedPhysicalReservoir(37,0,9272001,context)
    old=PhysicalReservoir(37,0,9272001,context)
    rows=[]
    for i in range(120):
        o=observations[i%12];values=[float(((i+3)*(a+2))%23-11) if a<o['n'] else 0. for a in range(4)]
        w=(.375,.75,1.,1.625)[(i//12)%4];rows.append((o,values,1+i//40,w))
    for i,(o,v,it,w) in enumerate(rows):
        weighted.add(o,v,it,deal_weight=w);unit.add(o,v,it,deal_weight=1.);old.add(o,v,it)
        if i==59:
            checkpoint=OUT/f'{PREFIX}-checkpoint.npz';weighted.save(checkpoint)
            resumed=WeightedPhysicalReservoir.load(checkpoint,context)
            assert equal(weighted,resumed)
        elif i>59:resumed.add(o,v,it,deal_weight=w)
    assert equal(weighted,resumed)
    assert unit.seen==old.seen and unit.rng.bit_generator.state==old.rng.bit_generator.state
    assert all(np.array_equal(getattr(unit,k),getattr(old,k)) for k in ARRAYS if k!='deal_weights')
    gu=grouped_rows(unit);go=old_grouped(old)
    for k in ('active','arity','counts','targets'):assert np.allclose(gu[k],go[k],rtol=0,atol=1e-14)
    for k in ('scale','denominator','variance'):assert abs(gu[k]-go[k])<1e-14
    g=grouped_rows(weighted)
    net=fresh_visible_network(9272001).double()
    reference=copy.deepcopy(net)
    prepared=PreparedWeightedObjective(g,'cpu',dtype=torch.float64,guard=guard)
    grouped_loss=prepared.objective(net,5,guard,backward=True)
    n=weighted.size
    x=torch.tensor(features([dict(active_features=r.tolist()) for r in weighted.active[:n]]),dtype=torch.float64)
    target=torch.tensor(weighted.values[:n]/g['scale'],dtype=torch.float64)
    legal=np.arange(4)[None,:]<weighted.arity[:n,None]
    w=torch.tensor(legal*weighted.deal_weights[:n,None],dtype=torch.float64)
    direct=((reference(x)-target).square()*w).sum()/w.sum();direct.backward()
    loss_error=abs(float(direct.detach())-(grouped_loss+g['variance']))
    gradient_error=max(float((a.grad-b.grad).abs().max()) for a,b in zip(net.parameters(),reference.parameters()))
    assert loss_error<1e-12 and gradient_error<1e-10
    rejected=0
    for bad in (0.,-1.,float('nan'),float('inf'),65537.,True,'1'):
        before=copy.deepcopy(weighted)
        try:weighted.add(*rows[0][:3],deal_weight=bad)
        except ValueError:rejected+=1
        else:raise AssertionError('Invalid weight accepted')
        assert equal(before,weighted)
    try:PhysicalReservoir.load(checkpoint,context)
    except ValueError:rejected+=1
    else:raise AssertionError('Old reader accepted weighted checkpoint')
    plain=OUT/f'{PREFIX}-unweighted-checkpoint.npz';old.save(plain)
    try:WeightedPhysicalReservoir.load(plain,context)
    except ValueError:rejected+=1
    else:raise AssertionError('Weighted reader accepted old checkpoint')
    try:WeightedPhysicalReservoir.load(checkpoint,context+' ')
    except ValueError:rejected+=1
    else:raise AssertionError('Changed context accepted')
    # A damaged retained weight must be caught even after deserialization.
    corrupt=copy.deepcopy(weighted);corrupt.deal_weights[0]=0
    try:grouped_rows(corrupt)
    except ValueError:rejected+=1
    else:raise AssertionError('Bad retained weight accepted')
    gpu=dict(executed=False,reason='Busy or unavailable GPU; CPU control remains valid')
    acquired=False
    try:
        if torch.cuda.is_available() and not LOCK.exists() and not OTHER.exists():
            status=subprocess.run(['nvidia-smi','--query-gpu=utilization.gpu,memory.free','--format=csv,noheader,nounits'],
                capture_output=True,text=True,timeout=5,creationflags=subprocess.CREATE_NO_WINDOW)
            if status.returncode==0:
                utilization,free=[float(s.strip()) for s in status.stdout.strip().splitlines()[0].split(',')]
                if utilization<20 and free>4000:
                    with LOCK.open('x') as f:f.write(str(os.getpid()))
                    acquired=True;guard()
                    cpu=fresh_visible_network(9272002)
                    cuda=copy.deepcopy(cpu).cuda()
                    pc=PreparedWeightedObjective(g,'cpu',dtype=torch.float32,guard=guard)
                    pg=PreparedWeightedObjective(g,'cuda',dtype=torch.float32,guard=guard)
                    oc=torch.optim.Adam(cpu.parameters(),lr=.003);og=torch.optim.Adam(cuda.parameters(),lr=.003)
                    for _ in range(8):
                        guard();oc.zero_grad();og.zero_grad()
                        pc.objective(cpu,5,guard,backward=True);pg.objective(cuda,5,guard,backward=True)
                        oc.step();og.step()
                    error=max(float((a-b.cpu()).detach().abs().max()) for a,b in zip(cpu.parameters(),cuda.parameters()))
                    assert error<1e-4
                    gpu=dict(executed=True,steps=8,maximum_parameter_error=error,device=torch.cuda.get_device_name())
    finally:
        if acquired:
            assert LOCK.read_text()==str(os.getpid());LOCK.unlink()
    for p,h in bindings.items():assert sha(p)==h
    save(OUT/f'{PREFIX}-result.json',dict(passed=True,registration_sha256=sha(rp),
        source_weight_retention_and_resume_exact=True,unit_weight_legacy_equivalence=True,
        maximum_cpu_gradient_error=gradient_error,loss_plus_variance_error=loss_error,
        negative_controls_rejected=rejected,gpu=gpu,seconds=time.monotonic()-start,
        artifacts={str(p):sha(p) for p in (checkpoint,plain)},
        training_qualified=False,poker_strength_claim=False,production_modified=False))
    print(json.dumps(dict(passed=True,gradient_error=gradient_error,loss_error=loss_error,gpu=gpu)),flush=True)


if __name__=='__main__':main()
