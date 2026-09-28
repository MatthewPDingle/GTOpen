"""Deal-level sensitivity, without changing any primary advancement gate."""
import os
os.environ.update(CUDA_VISIBLE_DEVICES='-1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
import argparse
from collections import Counter
import json
from pathlib import Path
import time
import numpy as np
from board_river_deal_coverage_common_v1 import ROOT,OUT,STORE,PREFIX,PLAN,read,sha,verify
from board_prefix_publication_v1 import atomic_json

REG=OUT/(PREFIX+'-robustness-registration.json')
RESULT=OUT/(PREFIX+'-robustness.json')
SUPPLEMENT=OUT/'BOARD-RIVER-DEAL-COVERAGE-ROBUSTNESS-PLAN.md'
METRICS=('mse_bb2','fold_call_decision_cost_bb')


def average(rows,metric,*,only=None,omit=None):
    values=[]
    for row in rows:
        mask=np.ones(len(row['deal']),dtype=bool)
        if only is not None:mask &= row['deal']==only
        if omit is not None:mask &= row['deal']!=omit
        assert mask.any();values.append(float(row[metric][mask].mean()))
    assert values
    return float(np.mean(values))


def compare(candidate,reference):
    deals=sorted(set(candidate[0]['deal'].tolist()))
    assert len(deals)>1 and all(set(r['deal'].tolist())==set(deals) for r in candidate+reference)
    assert len(candidate)==len(reference)
    output={}
    for metric in METRICS:
        primary=average(reference,metric)-average(candidate,metric)
        per=[average(reference,metric,only=d)-average(candidate,metric,only=d) for d in deals]
        leave=[average(reference,metric,omit=d)-average(candidate,metric,omit=d) for d in deals]
        output[metric]=dict(primary_improvement=primary,deals_favoring_candidate=sum(x>0 for x in per),
            deals_tied=sum(x==0 for x in per),deals=len(deals),per_deal_median=float(np.median(per)),
            per_deal_min=min(per),per_deal_max=max(per),leave_one_out_min=min(leave),leave_one_out_max=max(leave),
            per_deal=[dict(deal=d,improvement=x) for d,x in zip(deals,per)],
            leave_one_out=[dict(omitted_deal=d,improvement=x) for d,x in zip(deals,leave)])
    return output


def controls():
    candidate=[dict(deal=np.array([0,1,2,3]),**{k:np.ones(4) for k in METRICS}) for _ in range(2)]
    reference=[dict(deal=np.array([0,1,2,3]),**{k:np.array([0.,2.,4.,2.]) for k in METRICS}) for _ in range(2)]
    for metric,value in compare(candidate,reference).items():
        assert value['primary_improvement']==1 and value['deals_favoring_candidate']==3
        assert value['per_deal_median']==1 and value['per_deal_min']==-1 and value['per_deal_max']==3
        assert abs(value['leave_one_out_min']-1/3)<1e-12 and abs(value['leave_one_out_max']-5/3)<1e-12
    # Unequal state counts must use each model's remaining-state mean.
    one=[dict(deal=np.array([0,0,1,2]),**{k:np.array([0.,2.,4.,6.]) for k in METRICS})]
    assert average(one,'mse_bb2')==3 and average(one,'mse_bb2',omit=0)==5
    assert average(one,'mse_bb2',only=0)==1
    return dict(passed=True,hand_calculated_deal_differences=True,leave_one_out_recomputed=True,unequal_count_weighting=True)


def register():
    assert not REG.exists() and not (OUT/(PREFIX+'-evaluation.json')).exists()
    paths=[Path(__file__),SUPPLEMENT,PLAN,OUT/(PREFIX+'-selection.json')]
    hashes={str(p):sha(p) for p in paths};control=controls()
    atomic_json(REG,dict(inputs=hashes,control=control,registered_before_final_scoring=True,
        comparisons=['broad-exact vs dense-exact','broad-exact vs broad-sample16'],
        maximum_seconds=60,maximum_new_bytes=1_000_000,changes_primary_gates=False,created_unix=time.time()))
    print(json.dumps(dict(registered=True,control=control)),flush=True)


def analyze():
    started=time.monotonic();assert not RESULT.exists();registration=read(REG);verify(registration['inputs'])
    ep=OUT/(PREFIX+'-evaluation.json');rp=OUT/(PREFIX+'-report-readback.json')
    evaluation=read(ep);report=read(rp);assert evaluation['passed'] and evaluation['complete'] and report['passed'] and report['complete']
    assert report['inputs'][str(ep)]==sha(ep)
    verify(read(OUT/(PREFIX+'-evaluation-registration.json'))['inputs'])
    inputs={str(p):sha(p) for p in (REG,ep,rp)};data=[];maximum=0.
    for record in evaluation['rows']:
        path=STORE/'evaluation'/(record['name']+'.npz');assert sha(path)==record['predictions_sha256'];inputs[str(path)]=sha(path)
        with np.load(path,allow_pickle=False) as z:
            p=z['predicted_bb'];t=z['exact_bb'];deal=z['deal']
            assert set(deal.tolist())==set(range(192,224))
            mse=(p-t)**2;cost=np.where(p==0,abs(t)/2,np.where(p*t<0,abs(t),0.))
            row=dict(arm=record['arm'],name=record['name'],deal=deal,mse_bb2=mse,fold_call_decision_cost_bb=cost)
            for key in METRICS:
                error=abs(float(row[key].mean())-record['groups']['all'][key]);maximum=max(maximum,error);assert error<1e-8
            data.append(row)
    assert len(data)==48
    for arm in ('dense-exact','broad-exact','dense-sample16','broad-sample16'):
        selected=[r for r in data if r['arm']==arm];assert len(selected)==12
        for key in METRICS:
            error=abs(average(selected,key)-evaluation['aggregate'][arm][key]);maximum=max(maximum,error);assert error<1e-8
    candidate=[r for r in data if r['arm']=='broad-exact']
    comparisons={ref:compare(candidate,[r for r in data if r['arm']==ref]) for ref in ('dense-exact','broad-sample16')}
    balanced=all(len(set(Counter(row['deal'].tolist()).values()))==1 for row in data)
    verify(inputs);verify(registration['inputs']);assert time.monotonic()-started<60
    result=dict(passed=True,complete=True,registration_sha256=sha(REG),inputs=inputs,comparisons=comparisons,
        equal_states_per_deal_within_models=balanced,maximum_primary_metric_reconstruction_error=maximum,
        original_gates=evaluation['gates'],changes_primary_gates=False,statistical_confirmation=False,
        production_qualified=False,seconds=time.monotonic()-started)
    atomic_json(RESULT,result)
    lines=[]
    for ref,metrics in comparisons.items():
        for key,value in metrics.items():
            lines.append(f"| {ref} | {key} | {value['primary_improvement']:.4f} | {value['deals_favoring_candidate']}/32 | {value['per_deal_median']:.4f} | {value['leave_one_out_min']:.4f} to {value['leave_one_out_max']:.4f} |")
    text=f'''# Deal-level robustness of the coverage comparison

This supplemental analysis was registered before final scoring. It changes no
training, data, primary metric or advancement gate. Positive differences favor
broad-exact. The original gates remain: {evaluation['gates']}.

| Reference arm | Metric | Full evaluation difference | Deals favoring broad-exact | Median deal difference | Leave-one-deal-out difference range |
|---|---|---:|---:|---:|---:|
{chr(10).join(lines)}

Each omission removes the physical deal from every bank/actor/repetition and
recomputes each model's mean over remaining states before averaging models.
The range shows sensitivity to single deals. It is not a confidence interval,
significance test or full-game EV result. A fragile result stays fragile even
if the descriptive primary gate passes; a failed gate remains failed.

Equal state counts per deal within every model: {balanced}. If false, the
per-deal summaries have different weighting from the primary model/state mean.
All saved predictions and primary metrics were reconciled, maximum discrepancy
{maximum:.3g}. Full per-deal and omission records are in `{PREFIX}-robustness.json`.

Costs are per selected river decision, not bb per dealt hand or demonstrated
preflop-range improvement. No settings were chosen from these diagnostics.
'''
    path=OUT/'BOARD-RIVER-DEAL-COVERAGE-ROBUSTNESS.md';assert not path.exists()
    with path.open('x',encoding='utf-8',newline='\n') as f:f.write(text)
    assert RESULT.stat().st_size+path.stat().st_size<1_000_000
    print(json.dumps(dict(complete=True,comparisons=comparisons,seconds=time.monotonic()-started)),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--mode',choices=('register','analyze'),required=True)
    args=parser.parse_args();register() if args.mode=='register' else analyze()
