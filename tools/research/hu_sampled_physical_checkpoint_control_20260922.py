"""Tiny physical learning-loop continuation test, not a strategic pilot."""
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
from sampled_batch_protocol_v2 import policy_document
from sampled_physical_deals_v1 import PhysicalDeals
from sampled_physical_reservoir_v1 import PhysicalReservoir, ingest
from sampled_physical_fit_v1 import fit
from sampled_physical_checkpoint_v1 import (encoded, uniform_networks, write_model,
    model_document, save_checkpoint, restore_checkpoint, read_object, publish)

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='sampled-physical-checkpoint-v1'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def save(p,d):
    with p.open('xb') as f:f.write(encoded(d))


def main():
    assert idle();os.environ['CUDA_VISIBLE_DEVICES']=''
    import torch
    torch.set_num_threads(2);torch.use_deterministic_algorithms(True)
    context_path=OUT/'bb-context-candidate.json'
    exe=ROOT/'target/release/examples/hu_sampled_batch_bridge_v2.exe'
    paths=[Path(__file__),context_path,exe]+[ROOT/'tools/research'/p for p in (
        'sampled_physical_checkpoint_v1.py','sampled_physical_deals_v1.py','sampled_physical_reservoir_v1.py',
        'sampled_physical_fit_v1.py','sampled_batch_model_v1.py','sampled_batch_protocol_v2.py',
        'storage_strategic_common_prior_20260920.py','loopback_research_validation.py')]
    paths += [ROOT/'crates/solver/examples'/p for p in ('hu_sampled_batch_bridge_v2.rs',
        'research_sampled/state.rs','research_sampled/poker_reference_v1.rs','research_sampled/observation_v1.rs',
        'research_sampled/policy_walk_v1.rs','research_sampled/batch_queries_v1.rs')]
    prerequisites=[OUT/p for p in ('sampled-physical-stream-fit-v1-result.json','sampled-physical-deals-v1-result.json')]
    assert all(json.loads(p.read_text())['passed'] for p in prerequisites);paths+=prerequisites
    frozen={p.relative_to(ROOT).as_posix():sha(p) for p in paths}
    config=dict(deals_per_iteration=8,fit_steps=8,fit_seed_base=9301,reservoir_capacity=257,
        sampler_seed=7301,action_seed=8301,reservoir_seeds=[8302,8303],chance='full_deck',
        device='cpu',torch_version=torch.__version__,numpy_version=np.__version__,threads=2,
        architecture=[269,64,64,4],chunk_size=31,learning_rate=.003,iteration_weights='equal')
    registration=OUT/(PREFIX+'-registration.json')
    save(registration,dict(inputs=frozen,config=config,maximum_seconds=180,
        sequence='Two fresh-deal completed iterations, save boundary, compare uninterrupted and restored third iteration byte/state exactly.',
        scope='Three tiny iterations test checkpoint mechanics only. Eight fitting steps and eight deals are not a strategic training budget.',
        negatives=['changed configuration','changed context','include unused next model in played bank','misordered generation','changed object content','escaped object path'],
        no_gpu=True,production_modified=False))
    started=time.monotonic();next_guard=0.
    def guard():
        nonlocal next_guard
        now=time.monotonic()-started
        if now>=next_guard:
            assert now<180 and idle() and psutil.virtual_memory().available>=20_000_000_000
            next_guard=now+2
    work=ROOT/'target/research-sampled'/PREFIX;work.mkdir(parents=True,exist_ok=False)
    store=work/'checkpoint-objects';store.mkdir()
    context=context_path.read_text()
    state=dict(completed_iterations=0,sampler=PhysicalDeals(context,mode='full_deck',seed=7301),
        action_rng=np.random.Generator(np.random.PCG64(8301)),
        reservoirs=[PhysicalReservoir(257,p,8302+p,context) for p in (0,1)],played_bank=[],
        next_model=write_model(store,0,uniform_networks(),[1.,1.]))
    transcripts=[];step_metrics=[]
    def step(s,branch):
        iteration=s['completed_iterations']+1;folder=work/f'{branch}-{iteration}';folder.mkdir()
        batch=dict(format=2,batch_id=f'iteration-{iteration}',query_limit=100000,
            seed=int(s['action_rng'].integers(0,2**63)),deals=s['sampler'].sample(8)['deals'])
        batch_path=folder/'batch.json';save(batch_path,batch)
        queries_path=folder/'queries.json';policy_path=folder/'policies.json';update_path=folder/'updates.json'
        def invoke(mode,policy,path):
            guard();r=subprocess.run([str(exe),mode,str(context_path),str(batch_path),str(policy),str(path)],
                cwd=ROOT,timeout=60,capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW)
            assert r.returncode==0,r.stderr[:1500]
        invoke('queries','-',queries_path);queries=json.loads(queries_path.read_text())
        used=s['next_model'];nets=model_document(store,used)['networks']
        _,probabilities=predict(queries['observations'],nets,'cpu')
        save(policy_path,policy_document(queries,probabilities));invoke('verify',policy_path,update_path)
        updates=json.loads(update_path.read_text())
        assert updates['verified_traversals']==16 and updates['maximum_reference_error']==0
        counts=ingest(queries,updates,s['reservoirs'],iteration)
        nets=[];metrics=[]
        for p,r in enumerate(s['reservoirs']):
            net,metric=fit(r,seed=9301+iteration*200003+p,steps=8,device='cpu',chunk_size=31,guard=guard)
            nets.append(net);metrics.append(metric)
        next_model=write_model(store,iteration,nets,[m['advantage_scale'] for m in metrics])
        s['played_bank'].append(used);s['next_model']=next_model;s['completed_iterations']=iteration
        transcript={p.name:sha(p) for p in (batch_path,queries_path,policy_path,update_path)}
        transcripts.append(dict(branch=branch,iteration=iteration,artifacts=transcript))
        step_metrics.append(dict(branch=branch,iteration=iteration,advantage_records=counts,
            retained=[r.size for r in s['reservoirs']],fits=metrics))
        return transcript
    step(state,'initial');step(state,'initial')
    reference=save_checkpoint(store,completed=2,context_source=context,config=config,
        sampler=state['sampler'],action_rng=state['action_rng'],reservoirs=state['reservoirs'],
        bank=state['played_bank'],current=state['next_model'])
    restored=restore_checkpoint(store,reference,context_source=context,config=config)
    first=step(state,'uninterrupted');second=step(restored,'restored')
    assert first==second and state['next_model']==restored['next_model'] and state['played_bank']==restored['played_bank']
    assert state['sampler'].checkpoint()==restored['sampler'].checkpoint()
    assert state['action_rng'].bit_generator.state==restored['action_rng'].bit_generator.state
    for a,b in zip(state['reservoirs'],restored['reservoirs']):
        assert a.summary()==b.summary() and a.rng.bit_generator.state==b.rng.bit_generator.state
        for name in ('keys','active','arity','values','iterations'):assert np.array_equal(getattr(a,name),getattr(b,name))
    # Averaging includes generations 0,1,2; fitted generation 3 has not been played.
    assert [r['generation'] for r in state['played_bank']]==[0,1,2] and state['next_model']['generation']==3
    negative=[]
    bad_config=dict(config,fit_steps=9)
    operations=[lambda:restore_checkpoint(store,reference,context_source=context,config=bad_config),
                lambda:restore_checkpoint(store,reference,context_source=context+' ',config=config)]
    document=json.loads(read_object(store,reference))
    for variant in (0,1):
        bad=copy.deepcopy(document)
        if variant==0:bad['played_bank'].append(bad['next_model'])
        else:bad['played_bank'][0]['generation']=1
        ref=publish(store,'checkpoint',encoded(bad))
        operations.append(lambda ref=ref:restore_checkpoint(store,ref,context_source=context,config=config))
    operations.append(lambda:read_object(store,dict(reference,sha256='0'*64)))
    operations.append(lambda:read_object(store,dict(reference,file='../'+reference['file'])))
    for i,operation in enumerate(operations):
        try:operation()
        except ValueError:negative.append(i)
        else:raise AssertionError('Malformed checkpoint accepted')
    for name,h in frozen.items():assert sha(ROOT/name)==h,name
    result=dict(passed=True,inputs_verified=len(frozen),verified_physical_traversals=64,
        resumed_next_iteration_artifacts_identical=True,resumed_model_parameters_identical=True,
        resumed_all_rngs_and_reservoirs_identical=True,played_generations=[0,1,2],unused_next_generation=3,
        invalid_checkpoints_rejected=len(negative),checkpoint_reference=reference,
        checkpoint_directory=store.relative_to(ROOT).as_posix(),transcripts=transcripts,steps=step_metrics,
        checkpoint_object_hashes={p.relative_to(ROOT).as_posix():sha(p) for p in store.iterdir()},
        seconds=time.monotonic()-started,registration_sha256=sha(registration),
        physical_poker_convergence_qualified=False,production_modified=False)
    save(OUT/(PREFIX+'-result.json'),result)
    print(json.dumps({k:v for k,v in result.items() if k not in ('checkpoint_object_hashes','steps','transcripts')}))


if __name__=='__main__':main()
