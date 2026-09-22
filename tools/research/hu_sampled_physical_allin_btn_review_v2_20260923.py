"""Read back predeclared BTN decisions and independently reconstruct intervals."""
import json
import math
from pathlib import Path
import time
import psutil
from loopback_research_validation import idle
from sampled_physical_root_evaluation_v1 import ROOT,sha,save

OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='sampled-physical-allin-btn-evaluation-v2'
STORE=Path('S:/GTOpen-research')/PREFIX


def main():
    started=time.monotonic()
    def guard():
        assert idle() and time.monotonic()-started<600
        assert psutil.virtual_memory().available>=20_000_000_000
    guard();paths={s:OUT/f'{PREFIX}-{s}.json' for s in ('registration','result','status')}
    reg,result,status=[json.loads(paths[s].read_text()) for s in ('registration','result','status')]
    assert status['state']=='complete' and status['error'] is None and result['passed']
    assert result['registration_sha256']==sha(paths['registration'])
    for p,h in {**reg['inputs'],**result['artifacts'],**result['source_artifacts']}.items():guard();assert sha(p)==h,p
    training_path=OUT/'sampled-physical-allin-pilot-v1-registration.json'
    training=json.loads(training_path.read_text());assert sha(training_path)==reg['predeclared_in_training_sha256']
    for source in ['hu_sampled_physical_allin_btn_evaluation_20260923.py','hu_sampled_physical_allin_btn_review_20260923.py']:
        p=ROOT/'tools/research'/source;assert training['inputs'][str(p)]==sha(p)
    source_reg=json.loads((OUT/'sampled-physical-allin-evaluation-v2-registration.json').read_text())
    assert source_reg['inputs'][str(Path(__file__))]==sha(Path(__file__))
    rows=json.loads((STORE/'rows.json').read_text());response=json.loads((STORE/'response.json').read_text())
    paired=json.loads((STORE/'paired.json').read_text());assert paired['response_sha256']==sha(STORE/'response.json')
    assert len(rows['train'])==8192 and len(rows['test'])==16384
    counts=[0]*169;sums=[[] for _ in range(169)];reaches=[[] for _ in range(169)]
    for r in rows['train']:
        c=r['hand_class'];counts[c]+=1;sums[c].append(r['jam_reach']*(r['call_value']-r['fold_value']));reaches[c].append(r['jam_reach'])
    advantages=[math.fsum(s) for s in sums];reach_sums=[math.fsum(s) for s in reaches]
    choices=[int(advantages[c]>0) if counts[c]>=16 and reach_sums[c]>0 else -1 for c in range(169)]
    assert choices==response['actions'] and counts==response['counts']
    for expected,actual in [(advantages,response['weighted_call_advantage']),(reach_sums,response['summed_jam_reach'])]:
        assert all(math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-8) for a,b in zip(expected,actual))
    rebuilt=[];fallback=0
    for r in rows['train']+rows['test']:
        assert r['call_value'] in (-200.,-.75,198.5) and r['fold_value']==-2.
        assert 0<=r['jam_reach']<=1 and 0<=r['baseline_call_probability']<=1
        assert math.isclose(-2+(r['call_value']+2)*r['baseline_call_probability'],r['baseline_local_value'],abs_tol=1e-12)
    for r in rows['test']:
        a=choices[r['hand_class']];fallback+=int(a<0)
        chosen=r['baseline_local_value'] if a<0 else r['call_value'] if a else r['fold_value']
        rebuilt.append([r['jam_reach']*(v-r['baseline_local_value']) for v in [chosen,r['fold_value'],r['call_value']]])
    assert rebuilt==paired['differences'] and paired['series']==reg['series']==['trained-response','always-fold','always-call']
    assert fallback==result['fallback_test_deals']
    assert reg['family_error_probability']==.025 and reg['paired_bounds']==[-400.5,400.5]
    intervals={}
    for index,name in enumerate(reg['series']):
        xs=[r[index] for r in rebuilt];n=len(xs);mean=math.fsum(xs)/n
        variance=math.fsum((x-mean)**2 for x in xs)/(n-1)
        log=math.log(4*3/.025);radius=math.sqrt(2*variance*log/n)+7*801*log/(3*(n-1))
        expected=dict(count=n,mean=mean,sample_variance=variance,radius=radius,
            lower=max(-400.5,mean-radius),upper=min(400.5,mean+radius),family_error_probability=.025,bounds_best_response_above=False)
        actual=result['intervals'][name];assert set(actual)==set(expected)
        for k,v in expected.items():
            if isinstance(v,float):assert math.isclose(v,actual[k],abs_tol=1e-10,rel_tol=2e-12),(name,k)
            else:assert v==actual[k]
        intervals[name]=expected
    reach=math.fsum(r['jam_reach'] for r in rows['test'])
    assert math.isclose(reach/16384,result['mean_bb_jam_reach'],abs_tol=1e-12)
    if reach>0:
        call=math.fsum(r['jam_reach']*r['baseline_call_probability'] for r in rows['test'])/reach
        assert math.isclose(call,result['conditional_btn_call_frequency'],abs_tol=1e-12)
    else:assert result['conditional_btn_call_frequency'] is None
    guard();report=dict(passed=True,inputs={str(p):sha(p) for p in [Path(__file__),*paths.values()]},
        source_artifacts_verified=len(result['source_artifacts']),training_response_reconstructed=True,
        paired_differences_reconstructed=16384*3,intervals_reconstructed=intervals,
        predeclared_training_registration_sha256=sha(training_path),seconds=time.monotonic()-started,
        accuracy_qualified=False,production_modified=False,
        scope='Complete independent arithmetic readback of the predeclared second-player response family. Original showdown enumeration/native traversal not rerun. No full best-response bound.')
    save(OUT/f'{PREFIX}-independent-review.json',report);print(json.dumps(report))


if __name__=='__main__':main()
