"""Reconstruct each prefix with the original complete-bank CPU constructor.

No individual-model views are used here. Scalar gain reconstruction uses action
advantage times only the probability assigned to the inferior action.
"""
import os
os.environ['OPENBLAS_NUM_THREADS']='2'
os.environ['OMP_NUM_THREADS']='2'
import json
import math
from pathlib import Path
import time
import numpy as np
import psutil
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from hu_exhaustive_btn_response_v2_20260923 import load_models
from reboot_research_idle_v1 import idle

OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='allin-generation-attribution-v1'


def read(p):return json.loads(Path(p).read_text())


def main():
    began=time.monotonic();last=0.
    def guard():
        nonlocal last
        now=time.monotonic();assert now-began<900
        if now-last>=2:
            assert idle() and psutil.virtual_memory().available>=20_000_000_000
            last=now
    guard();rp=OUT/f'{PREFIX}-registration.json';result_path=OUT/f'{PREFIX}-result.json'
    reg,result=read(rp),read(result_path);status=read(OUT/f'{PREFIX}-status.json')
    assert status['state']=='complete' and status['error'] is None and result['passed']
    assert result['registration_sha256']==sha(rp) and result['seconds']<reg['maximum_seconds']
    for p,h in {**reg['inputs'],**result['artifacts']}.items():assert sha(p)==h,p
    source=Path(reg['context']).read_text();catalog=read(reg['catalog'])['native_observations']
    obs=[r['observation'] for r in catalog];assert len(obs)==265 and all(o['own_history']==[] for o in obs)
    index={(r['player'],r['hand_class']):i for i,r in enumerate(catalog)}
    assert len(index)==265
    btn,bb=read(reg['btn_source']),read(reg['bb_source']);checks={};maximum_scalar_error=0.
    assert set(result['candidates'])==set(reg['candidates'])=={'combined_269','visible_302'}
    for name,prefix in reg['candidates'].items():
        guard();item=result['candidates'][name]
        pp=Path(item['policy_artifact']);assert sha(pp)==item['policy_sha256']==result['artifacts'][str(pp)]
        pd=read(pp);assert pd['ordered_catalog_sha256']==sha(reg['catalog'])
        policies=np.asarray(pd['policies']);assert policies.shape==(78,265,4)
        assert np.isfinite(policies).all() and np.min(policies)>=0 and np.max(abs(policies.sum(2)-1))<1e-12
        for i,o in enumerate(obs):assert np.max(abs(policies[:,i,o['n']:]),initial=0)==0
        er=read(OUT/f'{prefix}-evaluation-v1-registration.json')
        documents,CpuBank,_=load_models(name,er,source)
        maximum_prefix_error=0.;records=item['records']
        assert [r['generation'] for r in records]==list(range(78))
        for generation in range(78):
            guard();bank=CpuBank(documents[:generation+1],context_source=source)
            q,support=bank.average(dict(context_source=source,observations=obs),guard=guard)
            assert np.array_equal(support,np.full(265,generation+1.))
            maximum_prefix_error=max(maximum_prefix_error,float(np.max(abs(q-policies[:generation+1].mean(0)))))
            p=policies[generation];bb_gains=[];btn_gains=[];jams=[];call_mass=[];jam_mass=[]
            for row in bb['candidates'][name]['classes']:
                c=row['hand_class'];pi=p[index[(0,c)]];f,j=row['fold_value'],row['jam_value']
                bb_gains.append(row['entry_probability']*((j-f)*pi[0] if j>f else (f-j)*pi[3]))
                jams.append(row['entry_probability']*pi[3])
            for row in btn['candidates'][name]['values']['classes']:
                if row['entry_probability']==0:continue
                pi=p[index[(1,row['hand_class'])]];f,j=row['fold_value_per_entry'],row['call_value_per_entry']
                btn_gains.append((j-f)*pi[0] if j>f else (f-j)*pi[1])
                jam_mass.append(row['jam_probability']);call_mass.append(row['jam_probability']*pi[1])
            expected=dict(bb_gain=math.fsum(bb_gains),btn_gain=math.fsum(btn_gains),
                bb_jam_frequency=math.fsum(jams),btn_call_given_fixed_jam=math.fsum(call_mass)/math.fsum(jam_mass))
            for k,v in expected.items():maximum_scalar_error=max(maximum_scalar_error,abs(records[generation][k]-v))
        assert maximum_prefix_error<1e-12
        assert sorted(g for ids in reg['groups'].values() for g in ids)==list(range(78))
        for label,ids in reg['groups'].items():
            for metric in ('bb_gain','btn_gain'):
                total=math.fsum(records[g][metric] for g in ids)
                maximum_scalar_error=max(maximum_scalar_error,
                    abs(item['groups'][label][metric]['mean']-total/len(ids)),
                    abs(item['groups'][label][metric]['contribution_to_full_average']-total/78))
        for metric,endpoint in [('bb_gain',bb['candidates'][name]['gain_bb_per_entry']),
            ('btn_gain',btn['candidates'][name]['values']['gains_per_entry']['best'])]:
            maximum_scalar_error=max(maximum_scalar_error,abs(math.fsum(r[metric] for r in records)/78-endpoint))
        checks[name]=dict(complete_prefixes_reconstructed=78,catalog_rows_per_prefix=265,
            maximum_prefix_policy_error=maximum_prefix_error)
    for p,h in {**reg['inputs'],**result['artifacts']}.items():assert sha(p)==h,p
    guard();assert maximum_scalar_error<1e-9
    review=dict(passed=True,registration_sha256=sha(rp),result_sha256=sha(result_path),
        reviewer_sha256=sha(Path(__file__)),candidates=checks,maximum_scalar_error_bb=maximum_scalar_error,
        seconds=time.monotonic()-began,production_modified=False,accuracy_qualified=False,
        scope='Every ordered complete-bank prefix reconstructed without model views, plus alternate scalar gain and group-sum identities. Opponents remain fixed final averages; no checkpoint selection or full-game accuracy claim.')
    save(OUT/f'{PREFIX}-independent-review.json',review);print(json.dumps(review))


if __name__=='__main__':main()
