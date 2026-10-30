"""Plan residual-test precision using an already inspected complete old sample.

No new draws, policy fitting/selection, current training output, GPU work or
fresh confidence claim. Centres use only that old study's training sample.
"""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
import json
import math
from pathlib import Path
import time
import numpy as np
import psutil
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from reboot_research_idle_v1 import idle
from root_residual_evaluation_v1 import prepare,residuals

OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='root-residual-diagnostic-v1'
SOURCE='sampled-physical-hybrid-allin-evaluation-v1'


def read(p):return json.loads(Path(p).read_text())


def radius(n,variance,width):
    log=math.log(4*5/.025)
    return math.sqrt(2*variance*log/n)+7*width*log/(3*(n-1))


def projected_count(variance,width,target):
    lo,hi=2,2
    while radius(hi,variance,width)>target and hi<100_000_000:hi*=2
    if hi>=100_000_000:return None
    while lo<hi:
        mid=(lo+hi)//2
        if radius(mid,variance,width)<=target:hi=mid
        else:lo=mid+1
    return lo


def main():
    start=time.monotonic();last=0.
    def guard():
        nonlocal last
        now=time.monotonic();assert now-start<600
        if now-last>2:
            assert idle() and psutil.virtual_memory().available>=20_000_000_000
            last=now
    guard();inputs={}
    def admit(prefix):
        rp,pp,ap=[OUT/f'{prefix}-{s}.json' for s in ('registration','result','independent-review')]
        r,p,a=map(read,(rp,pp,ap))
        assert a['passed'] and a['registration_sha256']==p['registration_sha256']==sha(rp)
        assert a['result_sha256']==sha(pp)
        inputs.update({str(x):sha(x) for x in (rp,pp,ap)});return r,p,a
    sr,sp,sa=admit(SOURCE);br,bp,ba=admit('bb-fold-jam-response-v3')
    er,ep,ea=admit('exhaustive-btn-response-v2')
    assert br['source_result']==str(OUT/'exhaustive-btn-response-v2-result.json')
    assert er['candidates']['combined_269']=='sampled-physical-hybrid-allin'
    policy_path=Path(ep['candidates']['combined_269']['policy_artifact']);policy=read(policy_path)
    assert sha(policy_path)==ep['candidates']['combined_269']['policy_sha256']
    assert policy['checkpoint']==sr['checkpoint']==sp['checkpoint']
    baseline=np.asarray(policy['root_probabilities'])
    exact_rows=bp['candidates']['combined_269']['classes']
    assert np.max(abs(np.array([r['baseline'] for r in exact_rows])-baseline))<1e-12
    mass=np.array([r['entry_probability'] for r in exact_rows])
    folds=mass*np.array([r['fold_value'] for r in exact_rows]);jams=mass*np.array([r['jam_value'] for r in exact_rows])
    store=Path(sr['store']);response_path=store/'response.json';response=read(response_path)
    assert sha(response_path)==sp['response_sha256']
    assert sr['config']['training_deals']==8192 and sr['config']['evaluation_deals']==16384
    for p in (Path(__file__),ROOT/'tools/research/root_residual_evaluation_v1.py',policy_path,response_path,
              Path(sr['context']),OUT/'root-residual-control-v1-registration.json',OUT/'root-residual-control-v1-result.json'):
        inputs[str(p)]=sha(p)
    control=read(OUT/'root-residual-control-v1-result.json')
    assert control['passed'] and control['registration_sha256']==sha(OUT/'root-residual-control-v1-registration.json')
    data={}
    for phase,count in [('train',8192),('test',16384)]:
        classes=[];values=[];base=[]
        for offset in range(0,count,16):
            guard();folder=store/f'{SOURCE}-{phase}-{offset}';path=folder/'summary.json';s=read(path)
            assert sha(path)==sp['batch_summary_hashes'][folder.name]
            assert len(s['classes'])==16
            assert np.max(abs(np.asarray(s['root_probabilities'])-baseline[s['classes']]))<1e-10
            classes.extend(s['classes']);values.extend(s['action_values']);base.extend(s['baseline_values'])
            inputs[str(path)]=sha(path)
        data[phase]=(np.asarray(classes),np.asarray(values),np.asarray(base))
    rp=OUT/f'{PREFIX}-registration.json'
    reg=dict(inputs=inputs,source=SOURCE,old_training_deals=8192,old_test_deals=16384,
        comparisons=sr['comparisons'],maximum_seconds=600,gpu_used=False,production_modified=False,
        scope='Post-hoc estimator/resource diagnostic on all old inspected deals with the original frozen responder. No new confidence intervals, policy choice or current-study access.')
    save(rp,reg)
    context=read(sr['context']);lower=-context['config']['stack'];upper=context['config']['stack']+context['dead_money']
    alternatives={};fitted=baseline.copy();actions=response['actions']
    for c,a in enumerate(actions):
        if a>=0:fitted[c]=np.eye(4)[a]
    alternatives['trained-response']=fitted
    for a,name in enumerate(('fold','call','raise','jam')):alternatives['always-'+name]=np.tile(np.eye(4)[a],(169,1))
    assert set(alternatives)==set(sr['comparisons'])
    train_c,train_q,_=data['train'];test_c,test_q,test_b=data['test'];records={};maximum_replay_error=0.
    for name,rho in alternatives.items():
        raw=np.sum(rho[test_c]*test_q,axis=1)-test_b
        old=sp['intervals'][name]
        maximum_replay_error=max(maximum_replay_error,abs(float(raw.mean())-old['mean']),abs(float(raw.var(ddof=1))-old['sample_variance']))
        versions={}
        for centred in (False,True):
            p=prepare(baseline,rho,mass,folds,jams,training_classes=train_c,training_actions=train_q,
                      centre=centred,lower=lower,upper=upper)
            r=residuals(p,test_c,test_q);mean=p['total_offset']+float(r.mean());var=float(r.var(ddof=1))
            # A separately formed scalar residual must agree for every test deal.
            delta=rho-baseline;centre=p['centre']
            scalar=[math.fsum([delta[c,1]*q[1],delta[c,2]*q[2],-centre[c]]) for c,q in zip(test_c,test_q)]
            assert np.max(abs(r-scalar))<1e-10
            width=p['residual_upper']-p['residual_lower']
            versions['centred' if centred else 'uncentred']=dict(prepared=p,descriptive_mean=mean,
                sample_variance=var,variance_ratio_to_original=var/float(raw.var(ddof=1)),
                hypothetical_radius_at_old_count=radius(len(r),var,width),
                hypothetical_deals_for_radius={str(t):projected_count(var,width,t) for t in (.5,.25,.1)},
                actual_residual_extrema=[float(r.min()),float(r.max())])
        records[name]=dict(original_mean=float(raw.mean()),original_sample_variance=float(raw.var(ddof=1)),versions=versions)
    assert maximum_replay_error<1e-8
    for p,h in inputs.items():assert sha(p)==h,p
    guard();result=dict(passed=True,registration_sha256=sha(rp),maximum_original_statistic_error=maximum_replay_error,
        comparisons=records,seconds=time.monotonic()-start,production_modified=False,gpu_used=False,
        accuracy_qualified=False,scope=reg['scope'],
        planning_caveat='Hypothetical counts assume the inspected variance persists under a future frozen policy and independent sample. They are neither achieved intervals nor an adopted budget.')
    save(OUT/f'{PREFIX}-result.json',result)
    print(json.dumps({k:{v:{f:x[f] for f in ('descriptive_mean','sample_variance','variance_ratio_to_original','hypothetical_deals_for_radius')} for v,x in r['versions'].items()} for k,r in records.items()}))


if __name__=='__main__':main()
