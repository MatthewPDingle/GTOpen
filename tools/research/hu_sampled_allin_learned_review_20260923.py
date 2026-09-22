"""Independent readback of the learned-policy conditional-all-in noise control."""
import json
from pathlib import Path
import numpy as np
from loopback_research_validation import idle
from sampled_physical_root_evaluation_v1 import ROOT,sha,save

OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='sampled-physical-allin-learned-control-v1'
STORE=Path('S:/GTOpen-research')/PREFIX
FIXTURE=Path('S:/GTOpen-research/sampled-physical-allin-bridge-control-v1')


def main():
    assert idle()
    rp=OUT/f'{PREFIX}-registration.json';zp=OUT/f'{PREFIX}-result.json'
    reg=json.loads(rp.read_text());result=json.loads(zp.read_text())
    assert result['passed'] and result['registration_sha256']==sha(rp)
    for p,h in {**reg['inputs'],**result['artifacts']}.items():assert sha(p)==h,p
    cp=next(Path(p) for p in reg['inputs'] if Path(p).name.startswith('checkpoint-'))
    checkpoint=json.loads(cp.read_text());assert checkpoint['completed_iterations']==78
    last=checkpoint['played_bank'][-1];assert last['generation']==reg['generation']==77
    mp=cp.parent/last['file'];assert sha(mp)==last['sha256'] and str(mp) in reg['inputs']
    model=json.loads(mp.read_text());assert model['generation']==77
    original=OUT/'bb-context-candidate.json'
    assert sha(original)==checkpoint['context_sha256']
    samples={k:[] for k in ['old_values','new_values','old_advantages','new_advantages']}
    unchanged=0;maxcash=0.;maxpolicy=0.
    # Independent float64 forward pass on the first 16 visible rows of every
    # batch. No hole cards, future cards, or conditional equity enter its inputs.
    def infer(o):
        net=model['networks'][o['actor']];x=np.zeros(269)
        x[o['active_features']]=1.
        for i,(nout,nin) in enumerate([(64,269),(64,64),(4,64)]):
            x=np.asarray(net[f'w{i}']).reshape(nout,nin)@x+np.asarray(net[f'b{i}'])
            if i<2:x=np.maximum(x,0.)
        n=o['n'];p=np.zeros(4);p[:n]=np.maximum(x[:n],0.)
        if p.sum()>0:p/=p.sum()
        else:p[np.argmax(x[:n])]=1.
        return p
    for rep in range(32):
        assert idle();folder=STORE/f'noise-{rep:02}';source=FIXTURE/f'noise-{rep:02}'
        q=json.loads((source/'queries-v3.json').read_text());obs=q['observations']
        assert json.loads((source/'context.json').read_text())==json.loads(original.read_text())
        p2=json.loads((folder/'policy-v2.json').read_text());p3=json.loads((folder/'policy-v3.json').read_text())
        assert p2['policies']==p3['policies']
        assert p2['batch_source']==(source/'batch-v2.json').read_text()
        assert p3['batch_source']==(source/'batch-v3.json').read_text()
        for o,p in zip(obs[:16],p3['policies'][:16]):
            assert (o['hi'],o['lo'])==(p['hi'],p['lo'])
            maxpolicy=max(maxpolicy,float(np.max(np.abs(infer(o)-p['probabilities']))))
        old=json.loads((folder/'updates-v2.json').read_text());new=json.loads((folder/'updates-v3.json').read_text())
        assert new['verified_cashflow_traversals']==new['verified_query_lookup_traversals']==32
        assert new['maximum_query_lookup_error']==0
        maxcash=max(maxcash,new['maximum_cashflow_error'])
        assert len(old['records'])==len(new['records'])
        for a,b in zip(old['records'],new['records']):
            assert a[:3]==b[:3]
            if obs[a[0]]['phase']!=0 or a[2]<0:assert a==b;unchanged+=1
        for label,u in [('old',old),('new',new)]:
            rv=[v for _,actor,v in u['roots'] if actor==0]
            rr=[v for i,actor,tag,v in u['records'] if actor==0 and tag==4 and int(obs[i]['hi'])==1]
            assert len(rv)==len(rr)==16
            samples[label+'_values'].append((np.asarray(rr)+np.asarray(rv)[:,None]).tolist())
            samples[label+'_advantages'].append(rr)
    assert json.loads((STORE/'samples.json').read_text())==samples
    for k,v in samples.items():
        x=np.asarray(v);variance=np.mean(np.sum((x-x.mean(axis=0))**2,axis=0)/31,axis=0)
        assert np.max(np.abs(variance-result['variance_bb2'][k]))<1e-9
    assert unchanged==result['unchanged_postflop_and_opponent_records']
    assert maxcash==result['maximum_cashflow_error_bb']<1e-9 and maxpolicy<1e-4
    ratio=sum(result['variance_bb2']['new_advantages'])/sum(result['variance_bb2']['old_advantages'])
    assert ratio==result['advantage_variance_trace_ratio']
    report=dict(passed=True,inputs={str(p):sha(p) for p in [Path(__file__),rp,zp]},
        reconstructed_fixture_deals=512,verified_traversals=1024,unchanged_records=unchanged,
        independently_checked_policy_rows=512,maximum_float64_policy_difference=maxpolicy,
        advantage_variance_trace_ratio=ratio,production_modified=False,accuracy_qualified=False,
        scope='Reconstructed all paired noise summaries and checked fixed last-played-model identity; independent float64 inference spot-checks 512 visible rows. No board enumeration, new training or poker-strength evaluation.')
    save(OUT/f'{PREFIX}-independent-review.json',report);print(json.dumps(report))


if __name__=='__main__':main()
