"""Read back bridge controls without importing their producer or rerunning training."""
import json
from pathlib import Path
import subprocess
import numpy as np
from loopback_research_validation import idle
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from hu_sampled_physical_dense_btn_jam_diagnosis_20260923 import showdown

OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='sampled-physical-allin-bridge-control-v1'
STORE=Path('S:/GTOpen-research')/PREFIX


def main():
    assert idle()
    rp=OUT/f'{PREFIX}-registration.json';zp=OUT/f'{PREFIX}-result.json'
    reg=json.loads(rp.read_text());result=json.loads(zp.read_text())
    assert result['passed'] and result['registration_sha256']==sha(rp)
    for p,h in {**reg['inputs'],**result['artifacts']}.items():assert sha(p)==h,p
    exact=json.loads(Path('S:/GTOpen-research/sampled-physical-allin-board-control-v1/native.json').read_text())[:16]
    all_samples={k:[] for k in ['old_action_values','new_action_values','old_regrets','new_regrets']}
    unchanged=0;traversals=0;maxcash=0.;maxdegenerate=0.;forcederror=0.
    names=[f'payout-{j}-{k}' for j in range(4) for k in range(3)]
    names += [f'observed-outcome-{j}' for j in range(4)]
    names += [f'noise-{j:02}' for j in range(32)]
    for name in names:
        assert idle()
        folder=STORE/name
        def read(s):return json.loads((folder/s).read_text())
        b=read('batch-v3.json');q=read('queries-v3.json');q2=read('queries-v2.json')
        a=read('updates-v2.json');z=read('updates-v3.json');c=read('context.json')
        assert q['observations']==q2['observations'] and q['raw_queries']==q2['raw_queries']
        assert q['batch_source']==(folder/'batch-v3.json').read_text()
        assert q2['batch_source']==(folder/'batch-v2.json').read_text()
        assert read('policy-v3.json')['policies']==read('policy-v2.json')['policies']
        assert b['deals']==read('batch-v2.json')['deals']
        for i,(deal,row) in enumerate(zip(b['deals'],b['allin_counts'])):
            assert len(deal)==len(set(deal))==9 and row['private_cards']==deal[:4]
            assert row['boards']==row['wins']+row['ties']+row['losses']==1712304
            if name.startswith('observed-outcome'):
                w=showdown(deal)
                assert [row[k] for k in ['wins','ties','losses']]==[1712304*int(w==j) for j in [0,-1,1]]
            else:
                assert row['private_cards']==exact[i]['private_cards']
                assert all(row[k]==exact[i][k] for k in ['wins','ties','losses'])
        assert z['verified_cashflow_traversals']==z['verified_query_lookup_traversals']==32
        assert z['maximum_query_lookup_error']==0
        maxcash=max(maxcash,z['maximum_cashflow_error']);traversals+=32
        assert len(a['records'])==len(z['records'])
        for old,new in zip(a['records'],z['records']):
            assert old[:3]==new[:3]
            if q['observations'][old[0]]['phase']!=0 or old[2]<0:
                assert old==new;unchanged+=1
            if name.startswith('observed-outcome'):
                maxdegenerate=max(maxdegenerate,max(abs(x-y) for x,y in zip(old[3],new[3])))
        if name.startswith('observed-outcome'):
            for old,new in zip(a['roots'],z['roots']):
                assert old[:2]==new[:2];maxdegenerate=max(maxdegenerate,abs(old[2]-new[2]))
        def roots(u):
            values=[v for _,p,v in u['roots'] if p==0]
            regrets=[r for i,p,n,r in u['records'] if p==0 and n==4 and int(q['observations'][i]['hi'])==1]
            assert len(values)==len(regrets)==16
            return np.asarray(regrets)+np.asarray(values)[:,None],np.asarray(regrets)
        if name.startswith('payout') and name.endswith('-2'):
            values,_=roots(z);node=c['nodes'][14]
            rake=node['pot']*c['rake_fraction']
            if c['rake_cap']>0:rake=min(rake,c['rake_cap'])
            for i,row in enumerate(b['allin_counts']):
                expected=(row['wins']+.5*row['ties'])/1712304*(node['pot']-rake)-node['invested'][0]
                forcederror=max(forcederror,abs(values[i,3]-expected))
        if name.startswith('noise'):
            for label,u in [('old',a),('new',z)]:
                values,regrets=roots(u)
                all_samples[label+'_action_values'].append(values.tolist())
                all_samples[label+'_regrets'].append(regrets.tolist())
    assert json.loads((STORE/'samples.json').read_text())==all_samples
    for label in ['old','new']:
        for suffix,outkey in [('action_values','action'),('regrets','advantage')]:
            x=np.asarray(all_samples[label+'_'+suffix])
            v=np.mean(np.sum((x-x.mean(axis=0))**2,axis=0)/31,axis=0)
            assert np.max(np.abs(v-result[f'{label}_{outkey}_variance_bb2']))<1e-9
    assert unchanged==result['unchanged_postflop_and_opponent_records']
    assert traversals==result['verified_traversals']==1536
    assert maxdegenerate==result['maximum_observed_outcome_error_bb']<1e-9
    assert maxcash==result['maximum_cashflow_error_bb']<1e-9
    assert forcederror==result['maximum_forced_jam_cashflow_error_bb']<1e-9
    # Repeat malformed-input rejection against the frozen native executables.
    reviewdir=STORE/'independent-review';reviewdir.mkdir()
    cp=STORE/'noise-31/context.json';rejections=0
    exe=ROOT/'target/release/examples/hu_sampled_allin_bridge_v3.exe'
    for i in range(9):
        assert idle();output=reviewdir/f'bad-{i}.json'
        done=subprocess.run([str(exe),'verify',str(cp),str(STORE/f'bad-{i}-batch.json'),
            str(STORE/f'bad-{i}-policy.json'),str(output)],cwd=ROOT,capture_output=True,
            timeout=45,creationflags=subprocess.CREATE_NO_WINDOW)
        assert done.returncode!=0 and not output.exists();rejections+=1
    output=reviewdir/'legacy.json'
    done=subprocess.run([str(ROOT/'target/release/examples/hu_sampled_batch_bridge_v2.exe'),
        'queries',str(cp),str(STORE/'noise-31/batch-v3.json'),'-',str(output)],cwd=ROOT,
        capture_output=True,timeout=45,creationflags=subprocess.CREATE_NO_WINDOW)
    assert done.returncode!=0 and not output.exists();rejections+=1
    assert rejections==result['rejected_inputs']==10
    old=sum(result['old_advantage_variance_bb2']);new=sum(result['new_advantage_variance_bb2'])
    report=dict(passed=True,inputs={str(p):sha(p) for p in [Path(__file__),rp,zp]},
        verified_traversals=traversals,unchanged_records=unchanged,repeated_rejections=rejections,
        reconstructed_noise_fixture_deals=512,uniform_fixture_advantage_variance_trace_ratio=new/old,
        maximum_cashflow_error_bb=maxcash,maximum_observed_outcome_error_bb=maxdegenerate,
        production_modified=False,accuracy_qualified=False,
        scope='Readback reconstructs all recorded paired controls and variance summaries and repeats ten input rejections. It does not independently enumerate exact boards or claim lower variance under trained policies or improved range accuracy.')
    save(OUT/f'{PREFIX}-independent-review.json',report);print(json.dumps(report))


if __name__=='__main__':main()
