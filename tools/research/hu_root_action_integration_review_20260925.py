"""Standard-library readback of saved-policy action integration control."""
import hashlib
import json
import math
from pathlib import Path
import statistics
import time

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='root-action-integration-v1'


def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def values(doc,queries):
    records=doc['records'];positions=[]
    for i,r in enumerate(records):
        o=queries['observations'][r[0]]
        if o['phase']==0 and o['hi']=='1':positions.append(i)
    assert len(positions)==len(doc['roots'])==128
    result=[]
    for k,position in enumerate(positions):
        root=doc['roots'][k];assert root[:2]==[k//2,k%2]
        r=records[position]
        if root[1]==0:
            assert r[1:3]==[0,4]
            result.append([root[2]+v for v in r[3]])
    assert len(result)==64
    return result


def main():
    start=time.monotonic();maximum=0.
    def close(a,b,tol=1e-9):
        nonlocal maximum
        error=abs(a-b);assert math.isfinite(error) and error<tol
        maximum=max(maximum,error)
    def guard():assert time.monotonic()-start<900
    rp,pp=[OUT/f'{PREFIX}-{s}.json' for s in ('registration','result')]
    reg,result=read(rp),read(pp)
    assert result['passed'] and result['registration_sha256']==sha(rp)
    assert len(reg['fixtures'])==len(result['fixtures'])==8
    for p,h in {**reg['inputs'],**result['artifacts']}.items():guard();assert sha(p)==h,p
    count=0
    for fi,(fixture,reported) in enumerate(zip(reg['fixtures'],result['fixtures'])):
        guard();folder=Path(reg['store'])/f'fixture-{fi:02d}';source=Path(fixture['source'])
        original_batch=read(source/'batch.json');original_p=read(source/'policies.json')
        q=read(source/'queries.json');transport=read(folder/'profiles.json');full=read(folder/'full-values.json')
        assert transport['format']==1 and transport['context_source']==original_p['context_source']
        assert transport['batch_source']==original_p['batch_source']==(source/'batch.json').read_text()
        assert transport['profiles'][0]['policies']==original_p['policies']
        assert len(transport['profiles'])==len(full['profiles'])==5
        for a in range(4):
            for i,row in enumerate(transport['profiles'][a+1]['policies']):
                old=original_p['policies'][i];o=q['observations'][i]
                expected=dict(old)
                if o['phase']==0 and o['hi']=='1':expected['probabilities']=[float(k==a) for k in range(4)]
                assert row==expected
        assert full['maximum_forward_cashflow_error']<1e-10 and full['maximum_conservation_error']<1e-10
        exact=[[full['profiles'][a+1]['deals'][d]['values'][0] for a in range(4)] for d in range(64)]
        corrected=read(source/'derived-targets.json')['bb_root_corrections']
        original=values(read(source/'updates.json'),q)
        for d,row in enumerate(corrected):
            for a in range(3):close(original[d][a],row['advantages'][a]+row['derived_root_value'])
            p=original_p['policies'][row['query']]['probabilities']
            close(full['profiles'][0]['deals'][d]['values'][0],math.fsum(x*y for x,y in zip(exact[d],p)))
            close(exact[d][0],-1)
        errors=[]
        assert fixture['seeds']==[358501+1000*fi+r for r in range(16)]
        for ri,seed in enumerate(fixture['seeds']):
            guard();part=folder/f'repeat-{ri:02d}'
            batch=read(part/'batch.json');policy=read(part/'policies.json')
            assert batch==dict(original_batch,seed=seed,batch_id=f'{PREFIX}-fixture-{fi}-repeat-{ri}')
            assert policy==dict(original_p,batch_source=(part/'batch.json').read_text())
            actual=values(read(part/'updates.json'),q)
            row=[]
            for d in range(64):
                call=actual[d][1]-exact[d][1];raise_=actual[d][2]-exact[d][2]
                row.append([call,raise_,call-raise_])
            errors.append(row);count+=64
        for a in range(3):
            per_deal=[[rep[d][a] for rep in errors] for d in range(64)]
            variance=statistics.mean(statistics.variance(x) for x in per_deal)
            mean=statistics.mean(statistics.mean(x) for x in per_deal)
            rms=math.sqrt(statistics.mean(statistics.mean(x)**2 for x in per_deal))
            close(variance,reported['conditional_action_noise_variance'][a],1e-8)
            close(mean,reported['pooled_mean_error'][a])
            close(rms,reported['rms_per_deal_mean_error'][a])
    assert count==8192
    output=dict(passed=True,registration_sha256=sha(rp),result_sha256=sha(pp),reader_sha256=sha(Path(__file__)),
        fixtures=8,action_seed_deals=count,physical_deals=512,maximum_scalar_error=maximum,
        seconds=time.monotonic()-start,production_modified=False,accuracy_qualified=False,
        scope='Transport/card/policy preservation, raw root values, full-action mixtures and conditional sample variances reconstructed. Does not independently implement native poker traversal or neural inference.')
    path=OUT/f'{PREFIX}-independent-review.json';assert not path.exists()
    path.write_text(json.dumps(output,separators=(',',':'))+'\n',encoding='utf-8',newline='\n')
    print(output)


if __name__=='__main__':main()
