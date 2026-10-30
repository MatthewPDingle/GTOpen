"""Predeclared BTN-vs-jam deviation family on the new candidate's fresh streams.

Selection rules are frozen by training admission; script identity is frozen by evaluation admission before any evaluation draw.
Response selection reads response-training data only; both players otherwise
retain the complete average policy. Independent seven-card payouts are checked
against the existing native pure-jam profile for every deal.
"""
import json
import math
from pathlib import Path
import time
import psutil
from loopback_research_validation import idle
from sampled_physical_root_evaluation_v1 import ROOT,sha,save,hand_class
from sampled_evaluation_intervals_v1 import Plan,PairedEvaluation
from hu_sampled_physical_dense_btn_jam_diagnosis_20260923 import showdown

OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='sampled-physical-hybrid-allin-btn-evaluation-v1'
SOURCE='sampled-physical-hybrid-allin-evaluation-v1'
STORE=Path('S:/GTOpen-research')/PREFIX
SERIES=('trained-response','always-fold','always-call')


def main():
    started=time.monotonic();last=0.
    def guard():
        nonlocal last
        now=time.monotonic()
        if now-last>=2:
            assert now-started<1200 and idle()
            assert psutil.virtual_memory().available>=20_000_000_000
            assert psutil.disk_usage(str(STORE.parent)).free>=40_000_000_000
            last=now
    guard()
    trainpath=OUT/'sampled-physical-hybrid-allin-pilot-v1-registration.json'
    training=json.loads(trainpath.read_text())
    plan=OUT/'SAMPLED-PHYSICAL-HYBRID-ALLIN-PLAN.md'
    assert training['inputs'][str(plan)]==sha(plan)
    paths={s:OUT/f'{SOURCE}-{s}.json' for s in ('registration','result','independent-review','status')}
    reg,result,review,status=[json.loads(paths[s].read_text()) for s in ('registration','result','independent-review','status')]
    assert reg['inputs'][str(Path(__file__))]==sha(Path(__file__))
    assert result['terminal'] and review['passed'] and status['state']=='complete'
    assert review['result_sha256']==sha(paths['result']) and review['registration_sha256']==sha(paths['registration'])
    assert reg['config']==dict(training_deals=8192,evaluation_deals=16384,batch_size=16,minimum_training_deals=16,train_seed=89101,test_seed=89102)
    assert reg['training_registration']==str(trainpath)
    for p,h in training['inputs'].items():assert sha(ROOT/p)==h,p
    context=json.loads(Path(reg['context']).read_text());node=12
    assert context['nodes'][0]['children'][3]==node and context['nodes'][node]['actor']==1
    assert [a['kind'] for a in context['nodes'][node]['actions']]==['fold','call']
    folded=context['nodes'][context['nodes'][node]['children'][0]]
    called=context['nodes'][context['nodes'][node]['children'][1]]
    assert folded['leaf']['type']=='fold' and called['leaf']['type']=='showdown'
    fold=float(folded['leaf']['utilities'][1]);pot=called['pot'];rake=pot*context['rake_fraction']
    if context['rake_cap']>0:rake=min(rake,context['rake_cap'])
    width=2*context['config']['stack']+context['dead_money']
    registration=dict(inputs={str(p):sha(p) for p in [trainpath,Path(__file__),*paths.values()]},
        source=SOURCE,series=SERIES,family_error_probability=.025,paired_bounds=[-width,width],
        predeclared_in_training_sha256=sha(trainpath),minimum_training_deals=16,
        selection='Per-class fold/call chosen from jam-reach-weighted response-training payoffs only; fewer than 16 raw training deals or zero summed reach retains baseline. Ties fold.',
        scope='Fresh, predeclared restricted BTN response to BB jam, measured per original spot entry. Five BB-root comparisons separately use alpha .025, yielding joint error at most .05 across these two within-trial families. No full best-response upper bound or equilibrium certificate.',
        production_modified=False)
    rp=OUT/f'{PREFIX}-registration.json';save(rp,registration)
    assert not STORE.exists();STORE.mkdir();counts=[0]*169;advantages=[0.]*169;reach_sums=[0.]*169
    streams={};hashes={};class_probs={};maxerror=0.;error=None
    try:
        for phase,total in [('train',8192),('test',16384)]:
            rows=[]
            for offset in range(0,total,16):
                guard();folder=Path(reg['store'])/f'{SOURCE}-{phase}-{offset}'
                summarypath=folder/'summary.json';assert sha(summarypath)==result['batch_summary_hashes'][folder.name]
                summary=json.loads(summarypath.read_text());hashes[str(summarypath)]=sha(summarypath);data={}
                for name in ('batch.json','profiles.json','native.json'):
                    p=folder/name;assert sha(p)==summary['artifacts'][name]
                    hashes[str(p)]=sha(p);data[name]=json.loads(p.read_text())
                baseline=data['profiles.json']['profiles'][0];assert baseline['name']=='baseline'
                native={p['name']:p['deals'] for p in data['native.json']['profiles']}
                probabilities={}
                for p in baseline['policies']:
                    if int(p['hi'])!=node+1:continue
                    assert p['actor']==1 and p['n']==2 and p['probabilities'][2:]==[0.,0.]
                    key=int(p['lo']);c=hand_class([key&63,(key>>6)&63]);prob=p['probabilities'][1]
                    assert 0<=prob<=1
                    if c in class_probs:assert abs(class_probs[c]-prob)<1e-12
                    class_probs[c]=prob;probabilities[c]=prob
                for i,deal in enumerate(data['batch.json']['deals']):
                    c=hand_class(deal[2:4]);prob=probabilities[c];winner=showdown(deal)
                    call=-called['invested'][1]+(pot-rake)*(.5 if winner<0 else float(winner==1))
                    local=fold*(1-prob)+call*prob;difference=abs(local-native['action-3'][i]['values'][1])
                    assert difference<1e-9;maxerror=max(maxerror,difference)
                    reach=summary['root_probabilities'][i][3];assert 0<=reach<=1
                    rows.append(dict(hand_class=c,jam_reach=reach,baseline_call_probability=prob,
                        call_value=call,fold_value=fold,baseline_local_value=local))
                    if phase=='train':counts[c]+=1;advantages[c]+=reach*(call-fold);reach_sums[c]+=reach
            assert len(rows)==total;streams[phase]=rows
            if phase=='train':
                response=dict(actions=[int(advantages[c]>0) if counts[c]>=16 and reach_sums[c]>0 else -1 for c in range(169)],
                    counts=counts,weighted_call_advantage=advantages,summed_jam_reach=reach_sums,
                    tie_rule='fold',fallback='unchanged baseline')
                save(STORE/'response.json',response);response_hash=sha(STORE/'response.json')
        assert sha(STORE/'response.json')==response_hash
        plan=Plan(-width,width,SERIES,(16384,),alpha=.025);estimates=[PairedEvaluation(plan,s) for s in SERIES]
        differences=[];applied=0
        for r in streams['test']:
            action=response['actions'][r['hand_class']]
            value=r['baseline_local_value'] if action<0 else r['call_value'] if action else r['fold_value']
            delta=[r['jam_reach']*(v-r['baseline_local_value']) for v in [value,r['fold_value'],r['call_value']]]
            differences.append(delta);applied+=int(action>=0)
            for e,x in zip(estimates,delta):e.add_difference(x)
        total_reach=math.fsum(r['jam_reach'] for r in streams['test'])
        save(STORE/'rows.json',streams);save(STORE/'paired.json',dict(series=SERIES,differences=differences,response_sha256=response_hash))
        result=dict(passed=True,registration_sha256=sha(rp),source_artifacts=hashes,
            artifacts={str(STORE/name):sha(STORE/name) for name in ('rows.json','response.json','paired.json')},
            training_deals=8192,evaluation_deals=16384,independent_showdowns_verified=24576,
            maximum_native_value_error=maxerror,mean_bb_jam_reach=total_reach/16384,
            conditional_btn_call_frequency=math.fsum(r['jam_reach']*r['baseline_call_probability'] for r in streams['test'])/total_reach if total_reach>0 else None,
            intervals={s:e.interval() for s,e in zip(SERIES,estimates)},fallback_test_deals=16384-applied,
            seconds=time.monotonic()-started,production_modified=False,accuracy_qualified=False,scope=registration['scope'])
        for p,h in registration['inputs'].items():assert sha(p)==h,p
        guard();save(OUT/f'{PREFIX}-result.json',result)
        print(json.dumps({k:v for k,v in result.items() if k not in ('artifacts','source_artifacts')}))
    except Exception as exc:error=str(exc);raise
    finally:save(OUT/f'{PREFIX}-status.json',dict(state='stopped' if error else 'complete',error=error,seconds=time.monotonic()-started,production_modified=False))


if __name__=='__main__':main()
