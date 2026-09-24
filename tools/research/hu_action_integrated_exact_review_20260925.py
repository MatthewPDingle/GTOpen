"""Reconstruct four endpoint pairings with scalar outcome-wise chip accounting."""
import os
os.environ['OPENBLAS_NUM_THREADS']='2'
os.environ['OMP_NUM_THREADS']='2'
import math
from pathlib import Path
import sys
import time
import numpy as np
import psutil
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from reboot_research_idle_v1 import idle
from later_average_support_v1 import OUT,read,weights,load_complete_cache
from hu_action_integrated_exact_20260925 import load_bank,bank_args
from action_integrated_policy_v1 import ActionIntegratedCpuBank64


def classify(cards):
    a,b=cards;h,l=max(a//4,b//4),min(a//4,b//4)
    return h*13+l if h==l or a%4==b%4 else l*13+h


def main():
    assert len(sys.argv)==2 and sys.argv[1] in ('first','replication')
    trial=sys.argv[1];control=False
    prefix=f'action-integrated-{trial}-exact-v1'
    rp,pp,sp=[OUT/f'{prefix}-{s}.json' for s in ('registration','result','status')]
    reg,result,status=map(read,(rp,pp,sp));start=time.monotonic();last=0.
    def guard():
        nonlocal last
        now=time.monotonic();assert now-start<1200
        if now-last>2:
            assert idle() and psutil.virtual_memory().available>=20_000_000_000
            last=now
    guard()
    assert result['passed'] and result['registration_sha256']==sha(rp)
    assert status['state']=='complete' and status['error'] is None and result['seconds']<1200
    assert reg['control_only']==result['control_only']==control and reg['trial']==trial
    assert reg['count']==(2 if control else 78)
    for p,h in {**reg['inputs'],**result['artifacts']}.items():assert sha(p)==h,p
    source=(OUT/'bb-context-candidate.json').read_text();context=read(OUT/'bb-context-candidate.json')
    population=read(reg['population']);cache=load_complete_cache()
    assert len(population['rows'])==len(cache.rows)==47478 and population['physical_pairs']==776650
    assert abs(math.fsum(r['probability'] for r in population['rows'])-1)<1e-12
    assert len({tuple(r['private_cards']) for r in population['rows']})==47478
    tr,ta=read(reg['training_registration']),read(reg['training_review'])
    models=load_bank(tr,ta,source,reg['count']);policies={};policy_errors={}
    train_result=read(OUT/(Path(tr['store']).name+'-result.json'))
    catalog=read(reg['catalog'])['native_observations']
    for kind in ('equal','linear'):
        ppath=Path(reg['store'])/f'{kind}-policy.json';policy=read(ppath)
        assert result['artifacts'][str(ppath)]==sha(ppath)
        assert policy['weights']==weights(kind,reg['count']).tolist()
        assert policy['checkpoint']==train_result['final_checkpoint'] and policy['played_generations']==list(range(reg['count']))
        assert policy['excluded_generation']==reg['count'] and policy['schedule']==kind
        bank=ActionIntegratedCpuBank64(models,completed_iterations=reg['count'],weights_by_player=weights(kind,reg['count']),**bank_args(source))
        actual,reach=bank.average(dict(context_source=source,observations=[r['observation'] for r in catalog]),guard=guard)
        assert np.array_equal(reach,np.full(265,sum(policy['weights'][0])))
        pe=0.
        for row,p in zip(catalog,actual):
            c=row['hand_class'];call=policy['btn_call_probabilities'][c]
            expected=policy['root_probabilities'][c] if row['player']==0 else [1-call,call,0,0]
            pe=max(pe,float(np.max(abs(p-expected))))
        assert pe<1e-12;policies[kind]=policy;policy_errors[kind]=pe
    root=context['nodes'][0];jam=context['nodes'][root['children'][3]]
    folded,showdown=[context['nodes'][i] for i in jam['children']]
    bb_fold=context['nodes'][root['children'][0]]['leaf']['utilities'][0]
    btn_fold=folded['leaf']['utilities'][1];bb_win=folded['leaf']['utilities'][0]
    rake=showdown['pot']*context['rake_fraction']
    if context['rake_cap']>0:rake=min(rake,context['rake_cap'])
    net=showdown['pot']-rake;costs=showdown['invested']
    expected_pairs={f'{b}/{t}' for b in ('equal','linear') for t in ('equal','linear')}
    assert set(result['pairings'])==set(reg['pairings'])==expected_pairs
    maximum_error=0.;conservation=0.;checks={}
    for name,values in result['pairings'].items():
        bb_kind,btn_kind=name.split('/');bp=policies[bb_kind]['root_probabilities'];tp=policies[btn_kind]['btn_call_probabilities']
        bm=[[] for _ in range(169)];bj=[[] for _ in range(169)]
        tm=[[] for _ in range(169)];trc=[[] for _ in range(169)];tc=[[] for _ in range(169)]
        for i,r in enumerate(population['rows']):
            if i%2048==0:guard()
            cards=r['private_cards'];b,t=classify(cards[:2]),classify(cards[2:]);m=r['probability']
            label=cache.rows[tuple(cards)];n=label['boards']
            assert n==1712304 and label['wins']+label['ties']+label['losses']==n
            bpay=(label['wins']*(net-costs[0])+label['ties']*(net/2-costs[0])-label['losses']*costs[0])/n
            tpay=(label['losses']*(net-costs[1])+label['ties']*(net/2-costs[1])-label['wins']*costs[1])/n
            conservation=max(conservation,abs(bpay+tpay-(showdown['pot']-sum(costs)-rake)))
            bm[b].append(m);bj[b].append(m*((1-tp[t])*bb_win+tp[t]*bpay))
            tm[t].append(m);trc[t].append(m*bp[b][3]);tc[t].append(m*bp[b][3]*tpay)
        bg=[];tg=[]
        assert [r['hand_class'] for r in values['bb_classes']]==list(range(169))
        assert [r['hand_class'] for r in values['btn']['classes']]==list(range(169))
        for c in range(169):
            m,j=math.fsum(bm[c]),math.fsum(bj[c]);f=m*bb_fold;baseline=bp[c]
            gain=(j-f)*baseline[0] if j>f else (f-j)*baseline[3]
            row=values['bb_classes'][c];response=row['response']
            assert row['baseline']==baseline and response[1:3]==baseline[1:3]
            assert min(response)>=0 and abs(sum(response)-1)<1e-12
            assert abs(response[0]+response[3]-baseline[0]-baseline[3])<1e-12
            actual_gain=(response[0]-baseline[0])*f+(response[3]-baseline[3])*j
            for a,b in [(gain,row['gain_per_entry']),(gain,actual_gain),(m,row['entry_probability']),
                        (f,row['fold_value_per_entry']),(j,row['jam_value_per_entry'])]:maximum_error=max(maximum_error,abs(a-b))
            bg.append(gain)
            entry,reach,call=math.fsum(tm[c]),math.fsum(trc[c]),math.fsum(tc[c]);fold=reach*btn_fold
            base=0. if not entry else (1-tp[c])*fold+tp[c]*call
            best=max(fold,call);gain=best-base;tg.append(gain)
            row=values['btn']['classes'][c]
            expected=dict(entry_probability=entry,jam_probability=reach,fold_value_per_entry=fold,
                call_value_per_entry=call,baseline_value_per_entry=base,best_value_per_entry=best,gain_per_entry=gain)
            for k,v in expected.items():maximum_error=max(maximum_error,abs(v-row[k]))
            assert row['baseline_call_probability']==(tp[c] if entry else None)
            if abs(call-fold)>1e-10:assert row['best_action']==int(call>fold)
            if reach==0:assert row['best_action']==-1
        btotal,ttotal=math.fsum(bg),math.fsum(tg)
        maximum_error=max(maximum_error,abs(btotal-values['bb_gain']),abs(ttotal-values['btn_gain']))
        assert btotal>=-1e-10 and ttotal>=-1e-10
        checks[name]=dict(bb_gain=btotal,btn_gain=ttotal,bb_classes=169,btn_classes=169)
    assert maximum_error<1e-9 and conservation<1e-9
    expected_old='root-retained-exact-v1' if trial=='first' else 'root-retained-replication-exact-v1'
    assert reg['old_prefix']==expected_old
    old=read(OUT/f'{expected_old}-result.json')
    b={k:old['pairings']['linear/linear'][k] for k in ('bb_gain','btn_gain')}
    assert b==reg['baseline']
    n=checks['linear/linear']
    differences={k:float(n[k]-b[k]) for k in ('bb_gain','btn_gain')}
    assert not reg['quality_screen_applied'] and not result['quality_screen_applied']
    for k,v in differences.items():assert abs(v-result['differences_from_previous'][k])<1e-10
    for p,h in {**reg['inputs'],**result['artifacts']}.items():assert sha(p)==h,p
    guard();review=dict(passed=True,registration_sha256=sha(rp),result_sha256=sha(pp),
        reviewer_sha256=sha(Path(__file__)),maximum_scalar_error_bb=maximum_error,
        maximum_cashflow_conservation_error_bb=conservation,policy_errors=policy_errors,pairings=checks,
        seconds=time.monotonic()-start,control_only=control,production_modified=False,accuracy_qualified=False)
    save(OUT/f'{prefix}-independent-review.json',review);print(review)


if __name__=='__main__':main()
