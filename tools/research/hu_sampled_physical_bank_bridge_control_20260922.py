"""Saved played models -> streamed average -> independent physical root mixture."""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

import numpy as np

from loopback_research_validation import idle
from sampled_batch_model_v1 import predict
from sampled_physical_checkpoint_v1 import read_object,model_document,verify_bank
from sampled_physical_bank_v1 import average,histories

ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='sampled-physical-bank-bridge-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):
    with p.open('x',encoding='utf-8',newline='\n') as f:f.write(json.dumps(d,separators=(',',':'))+'\n')

def main():
    assert idle();os.environ['CUDA_VISIBLE_DEVICES']=''
    import torch
    torch.set_num_threads(2);torch.use_deterministic_algorithms(True)
    prerequisite=OUT/'sampled-physical-checkpoint-v1-result.json';previous=json.loads(prerequisite.read_text());assert previous['passed']
    store=ROOT/previous['checkpoint_directory'];ref=previous['checkpoint_reference']
    checkpoint=json.loads(read_object(store,ref));verify_bank(store,2,checkpoint['played_bank'],checkpoint['next_model'])
    context=OUT/'bb-context-candidate.json';batch=ROOT/'target/research-sampled/sampled-physical-checkpoint-v1/initial-2/batch.json'
    assert sha(batch)==previous['transcripts'][1]['artifacts']['batch.json']
    exe=ROOT/'target/release/examples/hu_sampled_bank_bridge.exe'
    paths=[Path(__file__),prerequisite,store/ref['file'],context,batch,exe]+[store/r['file'] for r in checkpoint['played_bank']]
    paths += [ROOT/'tools/research'/p for p in ('sampled_physical_bank_v1.py','sampled_batch_model_v1.py',
        'sampled_physical_checkpoint_v1.py','loopback_research_validation.py')]
    paths += [ROOT/'crates/solver/examples'/p for p in ('hu_sampled_bank_bridge.rs',
        'research_sampled/state.rs','research_sampled/poker_reference_v1.rs','research_sampled/observation_v1.rs',
        'research_sampled/policy_bank_v1.rs','research_sampled/batch_queries_v1.rs')]
    frozen={p.relative_to(ROOT).as_posix():sha(p) for p in paths}
    registration=OUT/(PREFIX+'-registration.json')
    save(registration,dict(inputs=frozen,maximum_seconds=180,weights_by_player=[[1,1],[1,1]],
        source='Only played generations 0 and 1 from completed-iteration-2 checkpoint; unused generation 2 excluded.',
        checks='Stream saved parameters; compare own-history average to Rust and full terminal distributions from independent per-player root model draws.',
        tolerance=1e-12,no_gpu=True,scope='Physical bank reader/averaging control. The tiny source models have no strategic qualification.',production_modified=False))
    started=time.monotonic();next_guard=0.
    def guard():
        nonlocal next_guard
        now=time.monotonic()-started
        if now>=next_guard:assert now<180 and idle();next_guard=now+2
    def invoke(mode,data,destination):
        guard();r=subprocess.run([str(exe),mode,str(context),str(batch),str(data),str(destination)],cwd=ROOT,
            timeout=120,capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW)
        assert r.returncode==0,r.stderr[:2000]
    queries_path=OUT/(PREFIX+'-queries.json');invoke('queries','-',queries_path)
    queries=json.loads(queries_path.read_text());weights=[[1,1],[1,1]]
    # Generator keeps only one model pair resident at a time in the real reader.
    def pairs():
        for r in checkpoint['played_bank']:yield model_document(store,r)['networks']
    cpu_rng=torch.get_rng_state().clone();candidate,support=average(queries,pairs(),weights,device='cpu',guard=guard)
    assert torch.equal(cpu_rng,torch.get_rng_state())
    # Materializing the small model-policy bank is ONLY for this independent oracle.
    models=[predict(queries['observations'],nets,'cpu')[1].tolist() for nets in pairs()]
    bank=dict(format=1,context_source=queries['context_source'],batch_source=queries['batch_source'],
        weights_by_player=weights,models=models,average=candidate.tolist(),support=support.tolist())
    bank_path=OUT/(PREFIX+'-policies.json');save(bank_path,bank)
    native_path=OUT/(PREFIX+'-native-result.json');invoke('verify',bank_path,native_path)
    native=json.loads(native_path.read_text());assert native['passed'] and native['naive_probability_average_error']>1e-4
    rejected=[]
    linked=next(i for i,o in enumerate(queries['observations']) if o['own_history'])
    for variant in range(3):
        bad=copy.deepcopy(queries['observations']);link=bad[linked]['own_history'][0]
        if variant==0:link[0]=linked
        elif variant==1:link[1]=link[2]
        else:bad[link[0]]['actor']=1-bad[linked]['actor']
        try:histories(bad)
        except ValueError:rejected.append(variant)
        else:raise AssertionError('Invalid own history accepted')
    for m in ([],list(pairs())+[next(pairs())]):
        try:average(queries,iter(m),weights,device='cpu',guard=guard)
        except ValueError:rejected.append('model count')
        else:raise AssertionError('Invalid model count accepted')
    for name,h in frozen.items():assert sha(ROOT/name)==h,name
    result=dict(passed=True,inputs_verified=len(frozen),native=native,played_generations=[0,1],excluded_next_generation=2,
        visible_own_history_links=sum(len(o['own_history']) for o in queries['observations']),
        caller_cpu_rng_preserved=True,invalid_inputs_rejected=len(rejected),seconds=time.monotonic()-started,
        registration_sha256=sha(registration),artifacts={p.relative_to(ROOT).as_posix():sha(p) for p in (queries_path,bank_path,native_path)},
        physical_poker_convergence_qualified=False,production_modified=False)
    save(OUT/(PREFIX+'-result.json'),result);print(json.dumps(result))

if __name__=='__main__':main()
