"""Paired estimator-noise control using the dense trial's last played policy.

No checkpoint selection by performance, no optimization, no new strength claim.
"""
import json
from pathlib import Path
import subprocess
import time
import numpy as np
import psutil
from loopback_research_validation import idle
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from sampled_physical_checkpoint_v1 import read_object,model_document
from sampled_batch_model_v1 import predict

OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='sampled-physical-allin-learned-control-v1'
STORE=Path('S:/GTOpen-research')/PREFIX
FIXTURE=Path('S:/GTOpen-research/sampled-physical-allin-bridge-control-v1')


def main():
    import torch
    torch.set_num_threads(2);torch.use_deterministic_algorithms(True)
    started=time.monotonic()
    def guard():
        assert idle() and time.monotonic()-started<900
        assert psutil.virtual_memory().available>=20_000_000_000
        assert psutil.disk_usage(str(STORE.parent)).free>=40_000_000_000
    guard()
    priorpath=OUT/'sampled-physical-allin-bridge-control-v1-result.json'
    reviewpath=OUT/'sampled-physical-allin-bridge-control-v1-independent-review.json'
    prior=json.loads(priorpath.read_text());review=json.loads(reviewpath.read_text())
    assert prior['passed'] and review['passed']
    for p,h in review['inputs'].items():assert sha(p)==h,p
    for p,h in prior['artifacts'].items():assert sha(p)==h,p
    training=Path('S:/GTOpen-research/sampled-physical-dense-pilot-v1')
    metrics_path=training/'iteration-0078/metrics.json'
    metrics=json.loads(metrics_path.read_text())
    objects=training/'checkpoint-objects'
    checkpoint=json.loads(read_object(objects,metrics['checkpoint']))
    assert checkpoint['completed_iterations']==78 and len(checkpoint['played_bank'])==78
    ref=checkpoint['played_bank'][-1];assert ref['generation']==77
    model=model_document(objects,ref)
    paths=[Path(__file__),priorpath,reviewpath,metrics_path,objects/metrics['checkpoint']['file'],
        objects/ref['file'],ROOT/'tools/research/sampled_physical_checkpoint_v1.py',
        ROOT/'tools/research/sampled_batch_model_v1.py',
        ROOT/'target/release/examples/hu_sampled_batch_bridge_v2.exe',
        ROOT/'target/release/examples/hu_sampled_allin_bridge_v3.exe']
    reg=dict(inputs={str(p):sha(p) for p in paths},generation=77,replicates=32,
        selection='Last actually played dense-trial generation, fixed before estimator comparison; not the next unplayed model or a checkpoint selected for strength.',
        fixture_source=str(priorpath),fixture_sha256=sha(priorpath),device='cpu',
        torch_version=torch.__version__,maximum_seconds=900,production_modified=False,
        scope='Paired physical board/action-sampling variance on 16 old private-pair fixtures under one fixed learned policy. Measures training-target noise only; no training, fresh strength test, average-bank qualification, or population variance guarantee.')
    regpath=OUT/f'{PREFIX}-registration.json';save(regpath,reg)
    assert not STORE.exists();STORE.mkdir();artifacts={};samples={k:[] for k in ['old_values','new_values','old_advantages','new_advantages']}
    unchanged=0;traversals=0;maxcash=0.
    try:
        for rep in range(32):
            guard();folder=STORE/f'noise-{rep:02}';folder.mkdir()
            source=FIXTURE/f'noise-{rep:02}'
            q=json.loads((source/'queries-v3.json').read_text());obs=q['observations']
            _,prob=predict(obs,model['networks'],'cpu')
            policy=[dict(hi=o['hi'],lo=o['lo'],actor=o['actor'],n=o['n'],probabilities=list(map(float,p))) for o,p in zip(obs,prob)]
            pair=[]
            for version,label,exe in [(2,'old','hu_sampled_batch_bridge_v2'),(3,'new','hu_sampled_allin_bridge_v3')]:
                bp=source/f'batch-v{version}.json';cp=source/'context.json';pp=folder/f'policy-v{version}.json';op=folder/f'updates-v{version}.json'
                doc=dict(format=version,context_source=cp.read_text(),batch_source=bp.read_text(),policies=policy)
                if version==3:doc['terminal_estimator']='conditional-preflop-allin-v1'
                save(pp,doc);guard()
                done=subprocess.run([str(ROOT/f'target/release/examples/{exe}.exe'),'verify',str(cp),str(bp),str(pp),str(op)],
                    cwd=ROOT,capture_output=True,text=True,timeout=45,creationflags=subprocess.CREATE_NO_WINDOW)
                assert done.returncode==0,done.stderr[-2000:]
                for p in [pp,op]:artifacts[str(p)]=sha(p)
                u=json.loads(op.read_text());pair.append(u)
                rv=[v for _,actor,v in u['roots'] if actor==0]
                rr=[v for i,actor,tag,v in u['records'] if actor==0 and tag==4 and int(obs[i]['hi'])==1]
                assert len(rv)==len(rr)==16
                samples[label+'_values'].append((np.asarray(rr)+np.asarray(rv)[:,None]).tolist())
                samples[label+'_advantages'].append(rr)
            old,new=pair
            assert new['verified_cashflow_traversals']==new['verified_query_lookup_traversals']==32
            assert new['maximum_query_lookup_error']==0
            maxcash=max(maxcash,new['maximum_cashflow_error']);traversals+=32
            assert len(old['records'])==len(new['records'])
            for a,b in zip(old['records'],new['records']):
                assert a[:3]==b[:3]
                if obs[a[0]]['phase']!=0 or a[2]<0:assert a==b;unchanged+=1
        sp=STORE/'samples.json';save(sp,samples);artifacts[str(sp)]=sha(sp)
        variances={k:np.asarray(v).var(axis=0,ddof=1).mean(axis=0).tolist() for k,v in samples.items()}
        ratio=sum(variances['new_advantages'])/sum(variances['old_advantages'])
        guard()
        for p,h in reg['inputs'].items():assert sha(p)==h,p
        result=dict(passed=True,registration_sha256=sha(regpath),artifacts=artifacts,
            verified_traversals=traversals,unchanged_postflop_and_opponent_records=unchanged,
            maximum_cashflow_error_bb=maxcash,action_order=['fold','call','raise','jam'],
            variance_bb2=variances,advantage_variance_trace_ratio=ratio,seconds=time.monotonic()-started,
            production_modified=False,accuracy_qualified=False,scope=reg['scope'])
        assert maxcash<1e-9
        save(OUT/f'{PREFIX}-result.json',result)
        print(json.dumps({k:v for k,v in result.items() if k!='artifacts'}))
    except Exception as exc:
        save(OUT/f'{PREFIX}-failure.json',dict(error=str(exc),seconds=time.monotonic()-started));raise


if __name__=='__main__':main()
