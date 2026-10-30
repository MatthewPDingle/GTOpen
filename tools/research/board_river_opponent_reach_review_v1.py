"""CPU scalar readback of retained policies and exact finite-range arithmetic."""
import os
os.environ.update(CUDA_VISIBLE_DEVICES='-1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
from concurrent.futures import ProcessPoolExecutor
import itertools
import json
import math
from pathlib import Path
import time
import numpy as np
import psutil
from board_later_fit_holdout_run_v1 import ROOT,OUT,LOCK,OTHER,read,sha,verify
from board_prefix_publication_v1 import atomic_json
from bounded_parallel_evaluation_archive_v2 import production_available

PREFIX='board-river-opponent-reach-v1'
STORE=Path('S:/GTOpen-research')/PREFIX
CONTEXT=OUT/'bb-context-candidate.json'
REG=OUT/(PREFIX+'-registration.json')
RESULT=OUT/(PREFIX+'-result.json')


def independent_entry():
    context=read(CONTEXT);weights=[{},{}]
    for player in (0,1):
        for a,b in itertools.combinations(range(52),2):
            low,high=sorted((a//4,b//4))
            index=14*low if low==high else 13*high+low if a%4==b%4 else 13*low+high
            count=6 if low==high else 4 if a%4==b%4 else 12
            weights[player][a,b]=context['incoming_class_mass'][player][index]/count
        scale=max(weights[player].values())
        weights[player]={pair:0. if value/scale<1e-5 else value/scale for pair,value in weights[player].items()}
    return weights


def check_case(item):
    case_id,expected_hash=item;folder=STORE/'cases'/case_id
    result=read(folder/'result.json');assert sha(folder/'result.json')==expected_hash
    assert result['case']['case_id']==case_id and result['registration_sha256']==sha(REG)
    for field,name in (('request_sha256','request.json'),('export_sha256','export.json'),('policies_sha256','policies.npz')):
        assert result[field]==sha(folder/name)
    doc=read(folder/'export.json');target=doc['target'];obs=doc['queries']['observations'];hero=target['actor'];q=target['query_index']
    assert doc['context_source']==CONTEXT.read_text() and doc['request_source']==(folder/'request.json').read_text()
    entry=independent_entry();visible=set(target['cards']);pairs=list(itertools.combinations(sorted(set(range(52))-visible),2))
    assert pairs==[tuple(x['cards']) for x in doc['pairs']] and len(pairs)==990
    g=doc['geometry'];cost=g['amount_to_call'];pot=g['pot'];rake=g['rake']
    endpoints=(-cost,(pot-cost-rake)/2,pot-rake)
    assert max(abs(a-b) for a,b in zip(endpoints,g['endpoints_loss_tie_win']))<1e-10
    with np.load(folder/'policies.npz',allow_pickle=False) as stored:values={k:stored[k] for k in stored.files}
    max_error=0.;rows=[]
    def close(actual,expected):
        nonlocal max_error
        if expected is None:assert actual is None;return
        assert math.isfinite(actual) and math.isfinite(expected)
        error=abs(actual-expected);max_error=max(max_error,error)
        assert error<1e-9*max(1.,abs(expected)),(actual,expected)
    for bank_index,record in enumerate(result['records']):
        policy=values[f'policy_{bank_index*2}'];conditional=record['conditional']
        for version in (bank_index*2,bank_index*2+1):
            p=values[f'policy_{version}'];assert p.shape==(len(obs),4) and np.isfinite(p).all() and np.all(p>=0)
            for i,o in enumerate(obs):
                close(float(sum(p[i])),1.);assert all(x==0 for x in p[i,o['n']:])
        raw=[];outcomes=[];hero_likelihood=None
        for pair in doc['pairs']:
            own=1.;opponent=1.
            for index,action,arity in pair['path']:
                assert obs[index]['n']==arity and 0<=action<arity
                if obs[index]['actor']==hero:own*=float(policy[index,action])
                else:opponent*=float(policy[index,action])
            if hero_likelihood is None:hero_likelihood=own
            else:assert hero_likelihood==own
            raw.append(entry[1-hero][tuple(pair['cards'])]*opponent)
            outcomes.append(pair['outcome_loss_tie_win'])
        total=math.fsum(raw);prior=math.fsum(entry[1-hero][pair] for pair in pairs)
        hero_entry=entry[hero][tuple(sorted(target['cards'][:2]))]
        on_path=hero_likelihood>0 and hero_entry>0;supported=total>0
        close(conditional['hero_own_likelihood'],hero_likelihood);close(conditional['hero_entry_weight'],hero_entry)
        close(conditional['opponent_posterior_mass'],total);close(conditional['opponent_prior_mass'],prior)
        close(conditional['opponent_history_probability'],None if prior==0 else total/prior)
        assert conditional['supported']==supported and conditional['hero_on_path']==on_path
        assert conditional['supported_opponent_combos']==sum(x>0 for x in raw)
        if supported:
            eq=math.fsum(m*(outcome/2) for m,outcome in zip(raw,outcomes))/total
            delta=math.fsum(m*endpoints[outcome] for m,outcome in zip(raw,outcomes))/total
            ess=total**2/math.fsum(m*m for m in raw)
            close(delta,eq*(pot+cost-rake)-cost)
        else:eq=delta=ess=None
        for key,value in (('equity',eq),('call_minus_fold_bb',delta),('effective_opponent_combos',ess)):close(conditional[key],value)
        for offset,name in ((0,'original'),(1,'bounded')):
            p=list(map(float,values[f'policy_{bank_index*2+offset}'][q]));reported=record[name]
            fold,call=p[:2];mass=fold+call
            # Directly evaluate the two alternatives, with other action mass
            # unchanged. This is independent of the diagnostic vector formula.
            improvement=None if delta is None else max(0.,mass*delta)-call*delta
            for key,value in (('fold_probability',fold),('call_probability',call),('other_action_probability',sum(p[2:])),
                ('fold_call_mass',mass),('call_share_within_fold_call',None if mass==0 else call/mass),
                ('restricted_switch_gain_bb',improvement)):
                close(reported[key],value)
            close(record[name+'_target_own_reach'],float(values[f'own_reach_{bank_index*2+offset}'][q]))
        rows.append(dict(case_id=case_id,bank=record['bank'],actor=hero,pot_band=result['case']['pot_band'],
            pot=pot,cost=cost,supported=supported,on_path=on_path,hero_own_likelihood=hero_likelihood,
            hero_entry_weight=hero_entry,opponent_history_probability=conditional['opponent_history_probability'],
            equity=eq,call_minus_fold_bb=delta,effective_opponent_combos=ess,
            original=record['original'],bounded=record['bounded']))
    return dict(case_id=case_id,maximum_scalar_error=max_error,queries=len(obs),rows=rows)


def describe(rows):
    eligible=[r for r in rows if r['supported'] and r['on_path']]
    result=dict(selected=len(rows),supported=sum(r['supported'] for r in rows),
        on_path_and_supported=len(eligible),off_path_and_supported=sum(r['supported'] and not r['on_path'] for r in rows),
        unsupported=sum(not r['supported'] for r in rows))
    for name,group in (('on_path',eligible),('off_path',[r for r in rows if r['supported'] and not r['on_path']])):
        result[name]=dict(cases=len(group))
        if not group:continue
        gain=[r['original']['restricted_switch_gain_bb'] for r in group]
        result[name].update(call_better=sum(r['call_minus_fold_bb']>0 for r in group),
            fold_better=sum(r['call_minus_fold_bb']<0 for r in group),
            mean_restricted_switch_gain_bb=math.fsum(gain)/len(gain),median_restricted_switch_gain_bb=float(np.median(gain)),
            maximum_restricted_switch_gain_bb=max(gain),
            mean_other_action_probability=math.fsum(r['original']['other_action_probability'] for r in group)/len(group),
            median_effective_opponent_combos=float(np.median([r['effective_opponent_combos'] for r in group])),
            median_opponent_history_probability=float(np.median([r['opponent_history_probability'] for r in group])),
            median_hero_own_likelihood=float(np.median([r['hero_own_likelihood'] for r in group])))
    return result


def main():
    began=time.monotonic();assert not LOCK.exists() and not OTHER.exists();acquired=False
    destination=OUT/(PREFIX+'-independent-review.json');registration=OUT/(PREFIX+'-readback-registration.json')
    assert not destination.exists() and not registration.exists()
    try:
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True;assert production_available() and psutil.virtual_memory().available>24_000_000_000
        result=read(RESULT);assert result['passed'] and result['complete'] and result['cases']==80
        assert result['registration_sha256']==sha(REG);verify(read(REG)['inputs'])
        assert result['bank_identities_sha256']==sha(STORE/'bank-identities.json')
        selected=read(OUT/(PREFIX+'-selected-cases.json'))
        assert list(result['routes'])==[x['case_id'] for x in selected['cases']]
        inputs={str(p):sha(p) for p in (Path(__file__),RESULT,REG,CONTEXT)}
        workers=8 if psutil.cpu_percent(interval=1)<50 else 2
        atomic_json(registration,dict(inputs=inputs,workers=workers,cases=80,maximum_seconds=600,
            scope='Independent scalar reach, entry, equity and payoff readback; shared native poker outcomes, no second poker engine.',
            analysis='Fixed actor/pot/run groups; on-path and off-path separate; no population EV or accuracy claim.'))
        with ProcessPoolExecutor(max_workers=workers) as pool:
            checks=[]
            for check in pool.map(check_case,result['routes'].items()):
                assert time.monotonic()-began<600 and production_available() and not OTHER.exists()
                checks.append(check)
        rows=[row for check in checks for row in check['rows']]
        groups=[]
        for bank in ('A','B'):
            for actor in (0,1):
                for band in ('under10','10to50','50to100','100to200','200plus'):
                    group=[r for r in rows if (r['bank'],r['actor'],r['pot_band'])==(bank,actor,band)]
                    assert len(group)==8;groups.append(dict(bank=bank,actor=actor,pot_band=band,**describe(group)))
        verify(inputs)
        review=dict(passed=True,complete=True,registration_sha256=sha(registration),result_sha256=sha(RESULT),
            cases=80,bank_cases=len(rows),queries=sum(c['queries'] for c in checks),workers=workers,
            maximum_scalar_error=max(c['maximum_scalar_error'] for c in checks),
            summary=describe(rows),by_bank={name:describe([r for r in rows if r['bank']==name]) for name in ('A','B')},
            groups=groups,rows=rows,seconds=time.monotonic()-began,gpu_used=False,production_modified=False,
            scope='Query-balanced selected-case conditional values; not whole-game EV, independent deals or equilibrium accuracy.')
        atomic_json(destination,review)
        print(json.dumps({k:review[k] for k in ('passed','cases','bank_cases','queries','maximum_scalar_error','seconds','summary','by_bank')}),flush=True)
    finally:
        if acquired and LOCK.read_text()==str(os.getpid()):LOCK.unlink()


if __name__=='__main__':main()
