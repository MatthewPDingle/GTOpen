"""Exact-all-in BTN response rows from an already evaluated visible policy.

Returns values per original BB entry; conditional call frequencies must instead
divide by summed BB jam reach. Response selection is a separate operation and
must receive response-training rows only.
"""
import json
import math
from sampled_allin_protocol_v3 import ESTIMATOR,BOARDS
from sampled_physical_root_evaluation_v1 import hand_class


def rows(context,batch,profiles,native,summary,cache):
    assert batch['format']==2 and native['format']==2
    assert native['terminal_estimator']==summary['terminal_estimator']==ESTIMATOR
    assert summary['format']==2 and summary['allin_cache_sha256']==cache.sha256
    labelled=json.loads(profiles['batch_source']);cache.check_batch(labelled)
    assert labelled['deals']==batch['deals'] and labelled['batch_id']==batch['batch_id']
    assert json.loads(profiles['context_source'])==context
    root=context['nodes'][0]
    assert root['actor']==0 and [a['kind'] for a in root['actions']]==['fold','call','raise','jam']
    index=root['children'][3];node=context['nodes'][index]
    assert node['actor']==1 and [a['kind'] for a in node['actions']]==['fold','call']
    folded,called=[context['nodes'][i] for i in node['children']]
    assert folded['leaf']['type']=='fold' and called['leaf']['type']=='showdown'
    assert context['config']['ante']==0
    fold=float(folded['leaf']['utilities'][1]);pot=called['pot']
    rake=pot*context['rake_fraction']
    if context['rake_cap']>0:rake=min(rake,context['rake_cap'])
    baseline=profiles['profiles'][0];assert baseline['name']=='baseline'
    byclass={}
    for p in baseline['policies']:
        if int(p['hi']) != index+1:continue
        assert p['actor']==1 and p['n']==2 and p['probabilities'][2:]==[0.,0.]
        f,c=p['probabilities'][:2]
        assert math.isfinite(f) and math.isfinite(c) and min(f,c)>=0 and abs(f+c-1)<1e-12
        lo=int(p['lo']);hc=hand_class([lo&63,(lo>>6)&63])
        if hc in byclass:assert abs(byclass[hc]-c)<1e-12
        byclass[hc]=c
    jam=[p for p in native['profiles'] if p['name']=='action-3'];assert len(jam)==1
    assert len(jam[0]['deals'])==len(batch['deals'])==len(summary['root_probabilities'])
    result=[];maximum_error=0.
    for i,(deal,label) in enumerate(zip(batch['deals'],cache.labels(batch['deals']))):
        hc=hand_class(deal[2:4]);prob=byclass[hc]
        # Label wins are BB's wins; losses are BTN's wins. Preserve player roles.
        equity=(label['losses']+.5*label['ties'])/BOARDS
        call=-called['invested'][1]+(pot-rake)*equity
        local=fold*(1-prob)+call*prob
        error=abs(local-jam[0]['deals'][i]['values'][1]);assert error<1e-9
        maximum_error=max(maximum_error,error)
        mix=summary['root_probabilities'][i]
        assert len(mix)==4 and all(math.isfinite(x) and x>=0 for x in mix) and abs(sum(mix)-1)<1e-12
        result.append(dict(hand_class=hc,jam_reach=mix[3],baseline_call_probability=prob,
            call_value=call,fold_value=fold,baseline_local_value=local))
    return result,maximum_error


def learn(training_rows,*,minimum_training_deals=16):
    if type(minimum_training_deals) is not int or minimum_training_deals<1:
        raise ValueError('Positive class support threshold required')
    if not training_rows:raise ValueError('Nonempty response-training rows required')
    values=[[] for _ in range(169)];reaches=[[] for _ in range(169)]
    for r in training_rows:
        c=r['hand_class'];reach=r['jam_reach']
        if type(c) is not int or not 0<=c<169 or not math.isfinite(reach) or not 0<=reach<=1:
            raise ValueError('Invalid hand class or jam reach')
        advantage=r['call_value']-r['fold_value']
        if not math.isfinite(advantage):raise ValueError('Finite action values required')
        values[c].append(reach*advantage);reaches[c].append(reach)
    counts=list(map(len,values));sums=list(map(math.fsum,values));mass=list(map(math.fsum,reaches))
    return dict(actions=[int(sums[c]>0) if counts[c]>=minimum_training_deals and mass[c]>0 else -1 for c in range(169)],
        counts=counts,weighted_call_advantage=sums,summed_jam_reach=mass,
        minimum_training_deals=minimum_training_deals,tie_rule='fold',fallback='unchanged baseline')


def differences(response,test_rows):
    result=[]
    for r in test_rows:
        action=response['actions'][r['hand_class']];assert action in (-1,0,1)
        local=r['baseline_local_value'];reach=r['jam_reach']
        selected=local if action<0 else r['call_value'] if action else r['fold_value']
        result.append([reach*(v-local) for v in (selected,r['fold_value'],r['call_value'])])
    return result
