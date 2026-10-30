"""Physical replay -> bounded full-gradient fit -> engine inference control."""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

import numpy as np
import psutil

from loopback_research_validation import idle
from sampled_batch_model_v1 import predict
from sampled_physical_reservoir_v1 import PhysicalReservoir, ingest
from sampled_physical_fit_v1 import grouped_rows, fresh_network, objective, fit

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'sampled-physical-stream-fit-v1'


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def save(p, value):
    with p.open('x', encoding='utf-8', newline='\n') as f:
        f.write(json.dumps(value, separators=(',', ':'))+'\n')


def main():
    assert idle()
    os.environ['CUDA_VISIBLE_DEVICES'] = ''
    import torch
    torch.set_num_threads(2); torch.use_deterministic_algorithms(True)
    executable = ROOT/'target/release/examples/hu_sampled_physical_fit_control.exe'
    paths = [Path(__file__), executable] + [ROOT/'tools/research'/p for p in
        ('sampled_physical_fit_v1.py', 'sampled_physical_reservoir_v1.py',
         'sampled_batch_model_v1.py', 'loopback_research_validation.py')] + [OUT/p for p in
        ('sampled-physical-reservoir-v1-result.json', 'sampled-batch-bridge-v2-queries.json',
         'sampled-batch-bridge-v2-updates.json', 'bb-context-candidate.json')]
    paths += [ROOT/'crates/solver/examples'/p for p in ('hu_sampled_physical_fit_control.rs',
        'research_sampled/state.rs', 'research_sampled/poker_reference_v1.rs',
        'research_sampled/observation_v1.rs', 'research_sampled/network_v1.rs',
        'research_sampled/policy_walk_v1.rs')]
    assert json.loads(paths[6].read_text())['passed']
    frozen = {p.relative_to(ROOT).as_posix(): sha(p) for p in paths}
    registration = OUT/(PREFIX+'-registration.json')
    save(registration, dict(inputs=frozen, maximum_seconds=180, reservoir_capacity=257,
        reservoir_seeds=[3301,3302], fit_seeds=[4301,4302], steps=64, chunk_size=31,
        device='cpu', learning_rate=.003, repeated_fixture_batches=3,
        checks='Per-visit vs grouped/chunked gradients; within-observation variance identity; chunk-size invariance; fixed-data fit loss; Rust reload scores and legal probabilities; unchanged reservoir and caller RNG.',
        tolerances=dict(double_gradient=1e-10,variance_identity=1e-10,rust_scores=2e-5,rust_policy=1e-4),
        scope='Bounded physical fitting integration only. Repeated fixture is not fresh self-play or validation data.',
        no_gpu=True, production_modified=False))
    started = time.monotonic(); next_guard = 0.
    def guard():
        nonlocal next_guard
        elapsed = time.monotonic()-started
        if elapsed >= next_guard:
            assert elapsed < 180 and idle() and psutil.virtual_memory().available >= 20_000_000_000
            next_guard = elapsed+2
    queries, updates = [json.loads(paths[i].read_text()) for i in (7,8)]
    context = queries['context_source']
    reservoirs = [PhysicalReservoir(257,p,3301+p,context) for p in (0,1)]
    for iteration in (1,2,3): ingest(queries,updates,reservoirs,iteration)
    def reservoir_digest(r):
        payload = b''.join(getattr(r,k).tobytes() for k in ('keys','active','arity','values','iterations'))
        return hashlib.sha256(payload+json.dumps(r.rng.bit_generator.state,sort_keys=True).encode()).hexdigest()
    original = [reservoir_digest(r) for r in reservoirs]
    metrics = []; networks = []; cpu_rng = torch.get_rng_state().clone()
    for player, r in enumerate(reservoirs):
        guard(); grouped = grouped_rows(r); size=r.size
        model=fresh_network(4301+player).double()
        dense=np.zeros((size,269),np.float64)
        dense[np.arange(size)[:,None],r.active[:size]]=1
        mask=np.arange(4)[None,:]<r.arity[:size,None]
        targets=r.values[:size]/grouped['scale']
        raw=((model(torch.from_numpy(dense))-torch.from_numpy(targets)).square()*torch.from_numpy(mask)).sum()/int(mask.sum())
        raw.backward(); expected=[p.grad.clone() for p in model.parameters()]
        model.zero_grad(set_to_none=True)
        chunked=objective(model,grouped,31,guard,backward=True)
        chunk_gradient=[p.grad.clone() for p in model.parameters()]
        gradient_error=max(float((p.grad-e).abs().max()) for p,e in zip(model.parameters(),expected))
        variance_error=abs(float(raw.detach())-chunked-grouped['variance'])
        model.zero_grad(set_to_none=True)
        one_chunk=objective(model,grouped,100000,guard,backward=True)
        chunk_error=max(float((p.grad-e).abs().max()) for p,e in zip(model.parameters(),chunk_gradient))
        assert max(gradient_error,variance_error,chunk_error,abs(one_chunk-chunked))<1e-10
        net, detail=fit(r,seed=4301+player,steps=64,device='cpu',chunk_size=31,guard=guard)
        assert detail['normalized_grouped_loss_after']<detail['normalized_grouped_loss_before']
        detail.update(maximum_full_visit_gradient_error=gradient_error,maximum_chunk_gradient_error=chunk_error,
                      variance_decomposition_error=variance_error)
        networks.append(net);metrics.append(detail)
    assert torch.equal(cpu_rng,torch.get_rng_state())
    assert original==[reservoir_digest(r) for r in reservoirs]
    weights=OUT/(PREFIX+'-weights.json')
    save(weights,dict(networks=networks,advantage_scales=[m['advantage_scale'] for m in metrics],
        scope='Normalized signed-advantage outputs; positive player scale cancels in legal regret matching. Fixed-data fit only.'))
    destination=OUT/(PREFIX+'-engine-inference.json');guard()
    result=subprocess.run([str(executable),'infer',str(paths[9]),str(paths[7]),str(weights),str(destination)],
        cwd=ROOT,timeout=60,capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW)
    assert result.returncode==0,result.stderr[:2000]
    scores,policy=predict(queries['observations'],networks)
    rows=json.loads(destination.read_text())['rows']
    score_error=float(np.max(np.abs(scores-np.array([r['scores'] for r in rows]))))
    policy_error=float(np.max(np.abs(policy-np.array([r['policy'] for r in rows]))))
    assert score_error<2e-5 and policy_error<1e-4
    # Fail closed for an empty reservoir and contradictory duplicates.
    rejected=[]
    try: grouped_rows(PhysicalReservoir(17,0,1,context))
    except ValueError: rejected.append('empty')
    else: raise AssertionError('Empty fit accepted')
    bad=copy.deepcopy(reservoirs[1])
    _,indices,inverse,counts=np.unique(bad.keys[:bad.size],axis=0,return_index=True,return_inverse=True,return_counts=True)
    group=int(np.flatnonzero(counts>1)[0]);same=np.flatnonzero(inverse==group)
    bad.arity[same[-1]]=2 if bad.arity[same[0]]!=2 else 3
    try: grouped_rows(bad)
    except ValueError: rejected.append('inconsistent canonical key')
    else: raise AssertionError('Contradictory duplicate accepted')
    for name,h in frozen.items(): assert sha(ROOT/name)==h,name
    final=dict(passed=True,inputs_verified=len(frozen),fits=metrics,observations_checked=len(rows),
        maximum_rust_score_error=score_error,maximum_rust_policy_error=policy_error,
        caller_cpu_rng_preserved=True,reservoirs_preserved=True,invalid_inputs_rejected=rejected,
        seconds=time.monotonic()-started,registration_sha256=sha(registration),
        artifacts={p.relative_to(ROOT).as_posix():sha(p) for p in (weights,destination)},
        physical_poker_convergence_qualified=False,production_modified=False)
    save(OUT/(PREFIX+'-result.json'),final);print(json.dumps(final))


if __name__=='__main__':main()
