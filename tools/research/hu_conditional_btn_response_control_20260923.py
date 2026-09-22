"""Conditional BTN payoff/selection controls on existing repeated-board fixtures."""
import copy
import json
import math
from pathlib import Path
import time
import psutil
from loopback_research_validation import idle
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from sampled_allin_protocol_v3 import AllinCache
from sampled_conditional_btn_response_v1 import rows,learn,differences

OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='sampled-conditional-btn-response-control-v1'


def main():
    began=time.monotonic()
    def guard():
        assert time.monotonic()-began<300 and idle()
        assert psutil.virtual_memory().available>=20_000_000_000
    guard()
    source=OUT/'sampled-conditional-root-pipeline-control-v1-result.json'
    prior=json.loads(source.read_text());assert prior['passed'] and prior['complete_deals']==256
    cp=OUT/'bb-context-candidate.json';context=json.loads(cp.read_text())
    cr=OUT/'sampled-physical-allin-training-cache-v1-independent-review.json'
    cache=AllinCache.from_review(cr)
    paths=[Path(__file__),source,cp,cr,ROOT/'tools/research/sampled_conditional_btn_response_v1.py']
    reg=dict(inputs={str(p):sha(p) for p in paths},scope='Old repeated-board fixtures only: conditional BTN values, player orientation, response-training support and original-entry weighting. No independent strategic evidence or new chance stream.',production_modified=False)
    rp=OUT/f'{PREFIX}-registration.json';save(rp,reg)
    batches=[];artifacts={};maximum_error=0.
    for record in prior['records']:
        guard();sp=Path(record['summary_path']);assert sha(sp)==record['summary_sha256']
        summary=json.loads(sp.read_text());artifacts[str(sp)]=sha(sp)
        for name,h in summary['artifacts'].items():
            p=sp.parent/name;assert sha(p)==h;artifacts[str(p)]=h
        batch=json.loads((sp.parent/'query-batch.json').read_text())
        profile=json.loads((sp.parent/'profiles.json').read_text())
        native=json.loads((sp.parent/'native.json').read_text())
        values,error=rows(context,batch,profile,native,summary,cache)
        maximum_error=max(maximum_error,error);batches.append(values)
        # Independent fixed-context payout expression, preserving BTN ownership.
        for d,r,label in zip(batch['deals'],values,cache.labels(batch['deals'])):
            expected=-200+398.5*(1-(label['wins']+.5*label['ties'])/1712304)
            assert math.isclose(expected,r['call_value'],abs_tol=1e-10) and r['fold_value']==-2
    assert len(batches)==16 and all(len(b)==16 for b in batches)
    assert all(b==batches[0] for b in batches), 'Preflop all-in values must not depend on sampled runout'
    training=[r for b in batches[:8] for r in b];testing=[r for b in batches[8:] for r in b]
    response=learn(training,minimum_training_deals=4)
    independent=[]
    for c in range(169):
        rs=[r for r in training if r['hand_class']==c]
        mass=sum(r['jam_reach'] for r in rs)
        gain=math.fsum(r['jam_reach']*(r['call_value']-r['fold_value']) for r in rs)
        independent.append(-1 if len(rs)<4 or mass==0 else int(gain>0))
    assert response['actions']==independent
    delta=differences(response,testing)
    for r,d in zip(testing,delta):
        choice=independent[r['hand_class']]
        value=r['baseline_local_value'] if choice<0 else (r['fold_value'],r['call_value'])[choice]
        assert d[0]==r['jam_reach']*(value-r['baseline_local_value'])
        assert d[1]==r['jam_reach']*(r['fold_value']-r['baseline_local_value'])
        assert d[2]==r['jam_reach']*(r['call_value']-r['baseline_local_value'])
    def case(c,reach,gain):return dict(hand_class=c,jam_reach=reach,call_value=gain,fold_value=0.,baseline_local_value=.5*gain,baseline_call_probability=.5)
    fixtures=[case(0,.01,100),case(0,1,-2),case(1,1,1),case(1,1,-1),
        case(2,0,10),case(2,0,10),case(3,1,10),case(4,.1,10),case(4,.1,10)]
    fixed=learn(fixtures,minimum_training_deals=2)
    assert fixed['actions'][:5]==[0,0,-1,-1,1]
    assert differences(fixed,[fixtures[-1]])==[[.5,-.5,.5]]
    snapshot=copy.deepcopy(response);differences(response,testing);assert response==snapshot
    rejected=0
    for data,minimum in (([],16),(fixtures,0),([case(169,1,1)],1),([case(0,2,1)],1),([case(0,1,float('nan'))],1)):
        try:learn(data,minimum_training_deals=minimum)
        except ValueError:rejected+=1
        else:raise AssertionError('Invalid response-training data accepted')
    for p,h in {**reg['inputs'],**artifacts}.items():assert sha(p)==h,p
    result=dict(passed=True,registration_sha256=sha(rp),existing_deals_checked=256,
        maximum_native_value_error=maximum_error,runout_invariance=True,
        exact_BTN_orientation=True,training_only_selection_reconstructed=True,
        original_entry_weighting_checked=True,default_support_threshold=16,
        synthetic_weighting_tie_zero_reach_sparse_and_call_cases=5,
        invalid_cases_rejected=rejected,artifacts=artifacts,seconds=time.monotonic()-began,
        production_modified=False,accuracy_qualified=False)
    save(OUT/f'{PREFIX}-result.json',result)
    print(json.dumps({k:v for k,v in result.items() if k!='artifacts'}))


if __name__=='__main__':main()
