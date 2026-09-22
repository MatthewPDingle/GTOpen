"""Qualify physical query export, tensor inference, and sampled-update transport."""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import numpy as np
from sampled_batch_model_v1 import predict,policy_document
from loopback_research_validation import idle

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='sampled-batch-bridge-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,separators=(',',':'))+'\n',encoding='utf-8',newline='\n')

def main():
    assert idle();os.environ['CUDA_VISIBLE_DEVICES']=''
    import torch
    torch.set_num_threads(2);torch.use_deterministic_algorithms(True)
    exe=ROOT/'target/release/examples/hu_sampled_batch_bridge.exe';context=OUT/'bb-context-candidate.json'
    deals=OUT/'sampled-poker-v1-fixture.json';fixture=OUT/'sampled-network-adapter-v1-fixture.json'
    weights=OUT/'sampled-physical-gpu-v1-weights.json';prerequisite=OUT/'sampled-batch-queries-v1-review.json'
    assert json.loads(prerequisite.read_text())['passed']
    paths=[Path(__file__),exe,context,deals,fixture,weights,prerequisite,ROOT/'tools/research/sampled_batch_model_v1.py',ROOT/'tools/research/loopback_research_validation.py']+[ROOT/'crates/solver/examples'/p for p in [
        'hu_sampled_batch_bridge.rs','research_sampled/state.rs','research_sampled/poker_reference_v1.rs',
        'research_sampled/observation_v1.rs','research_sampled/policy_walk_v1.rs','research_sampled/batch_queries_v1.rs']]
    frozen={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in paths}
    reg=OUT/(PREFIX+'-registration.json');assert not reg.exists()
    save(reg,dict(inputs=frozen,maximum_seconds=180,device='cpu',seed=2026092405,query_limit=100000,
        scope='Fixed-data physical batch bridge. Tensor inference on visible rows; no training or new poker accuracy claim.',
        controls='Export -> two frozen player networks -> legal probabilities -> both updater passes. Independent on-demand canonical lookup must match cached traversal exactly.',
        negatives=['stale context','stale batch','reordered rows','negative probability','unnormalized probability','illegal action probability'],
        inference_tolerance=2e-5,no_gpu=True,production_modified=False))
    started=time.monotonic();artifacts=[]
    def path(suffix):return OUT/(PREFIX+'-'+suffix+'.json')
    def invoke(mode,batch,policies,result):
        assert idle() and time.monotonic()-started<180
        return subprocess.run([str(exe),mode,str(context),str(batch),str(policies),str(result)],cwd=ROOT,
            timeout=90,capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW)
    selected=json.loads(fixture.read_text())['deal_indices'];raw=json.loads(deals.read_text())['deals']
    batch=path('batch');save(batch,dict(format=1,batch_id=PREFIX,query_limit=100000,seed=2026092405,deals=[raw[i] for i in selected]));artifacts.append(batch)
    queries_path=path('queries');r=invoke('queries',batch,'-',queries_path);assert r.returncode==0,r.stderr;artifacts.append(queries_path)
    queries=json.loads(queries_path.read_text());networks=json.loads(weights.read_text())['networks']
    before=torch.get_rng_state().clone();scores,p=predict(queries['observations'],networks);assert torch.equal(before,torch.get_rng_state())
    # A different batching/row order must not add cross-hand information.
    order=np.arange(len(scores))[::-1];reverse,_=predict([queries['observations'][i] for i in order],networks)
    row_error=float(np.max(np.abs(reverse-scores[order])));assert row_error<2e-5
    # Compare independent NumPy matrix operations using the same visible features.
    x=np.zeros((len(scores),269),np.float32)
    for i,o in enumerate(queries['observations']):x[i,o['active_features']]=1
    numpy_scores=np.zeros_like(scores)
    for player in (0,1):
        ids=[i for i,o in enumerate(queries['observations']) if o['actor']==player];v=x[ids]
        for layer,shape in enumerate([(64,269),(64,64),(4,64)]):
            w=np.array(networks[player][f'w{layer}'],np.float32).reshape(shape);b=np.array(networks[player][f'b{layer}'],np.float32)
            v=v@w.T+b
            if layer<2:v=np.maximum(v,0)
        numpy_scores[ids]=v
    numpy_error=float(np.max(np.abs(scores-numpy_scores)));assert numpy_error<2e-5
    policy=path('policies');document=policy_document(queries,p);save(policy,document);artifacts.append(policy)
    output=path('updates');r=invoke('verify',batch,policy,output);assert r.returncode==0,r.stderr;artifacts.append(output)
    updates=json.loads(output.read_text());assert updates['verified_traversals']==32 and updates['maximum_reference_error']==0
    assert len(updates['records'])>0
    phases=set();counts=[0,0]
    for i,updater,tag,value in updates['records']:
        o=queries['observations'][i];assert abs(tag)==o['n'];assert o['actor']==(updater if tag>0 else 1-updater)
        assert np.isfinite(value).all() and not any(value[o['n']:]);phases.add(o['phase'])
        if tag>0:counts[updater]+=1
    rejected=[]
    for variant in range(6):
        invalid=copy.deepcopy(document)
        if variant==0:invalid['context']['rake_cap']+=.125
        elif variant==1:invalid['batch']['batch_id']='stale'
        elif variant==2:invalid['policies'][0],invalid['policies'][1]=invalid['policies'][1],invalid['policies'][0]
        elif variant==3:invalid['policies'][0]['probabilities'][0]=-.1
        elif variant==4:invalid['policies'][0]['probabilities'][0]+=.1
        else:
            row=next(r for r in invalid['policies'] if r['n']<4);row['probabilities'][3]=.1
        bad=path(f'reject{variant}');destination=path(f'rejected-output{variant}');save(bad,invalid);artifacts.append(bad)
        r=invoke('walk',batch,bad,destination);assert r.returncode!=0 and not destination.exists();rejected.append(variant)
    assert all(sha(ROOT/name)==h for name,h in frozen.items())
    result=dict(passed=True,inputs_verified=len(frozen),observations=len(scores),raw_queries=queries['raw_queries'],
        verified_traversals=32,update_records=len(updates['records']),advantage_records_by_player=counts,record_phases=sorted(phases),
        maximum_lookup_traversal_error=0,maximum_numpy_score_error=numpy_error,maximum_row_order_score_error=row_error,
        training_rng_preserved=True,malformed_inputs_rejected=len(rejected),seconds=time.monotonic()-started,
        artifacts={p.name:sha(p) for p in artifacts},registration_sha256=sha(reg),
        physical_poker_convergence_qualified=False,production_modified=False)
    save(path('result'),result);print(json.dumps({k:v for k,v in result.items() if k!='artifacts'}))

if __name__=='__main__':main()
