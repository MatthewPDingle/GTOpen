"""Post-hoc location of residual error in completed CPU/GPU finite policies."""
import hashlib
import json
from pathlib import Path
import time

from hu_sampled_convergence_fixture_20260922 import evaluate
from loopback_research_validation import idle

ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='sampled-neural-residual-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):
    with p.open('x',encoding='utf-8',newline='\n') as f:f.write(json.dumps(d,indent=2)+'\n')


def restricted_response(data, policy, case, player, allowed):
    """Optimize only selected public nodes, grouping hidden states before acting."""
    chance=data['probabilities'];infos=data['deal_infos'];offset=data['offsets']
    actors=data['actors'];children=data['children'];arity=data['arity'];utilities=data['cases'][case]['utilities']
    def p(d,n,a):return policy[offset[infos[d][n]]+a]
    reach=[[0.]*19 for _ in chance]
    for d,q in enumerate(chance):reach[d][0]=q
    for n in range(19):
        if not arity[n]:continue
        for d in range(24):
            for a in range(arity[n]):
                reach[d][children[n][a]]=reach[d][n]*(1. if actors[n]==player and n in allowed else p(d,n,a))
    values=[[0.]*19 for _ in chance];chosen={}
    for n in reversed(range(19)):
        if not arity[n]:
            for d in range(24):values[d][n]=utilities[d][n][player]
        elif actors[n]==player and n in allowed:
            groups={}
            for d in range(24):groups.setdefault(infos[d][n],[]).append(d)
            for info,ds in groups.items():
                action_values=[sum(reach[d][n]*values[d][children[n][a]] for d in ds) for a in range(arity[n])]
                action=max(range(arity[n]),key=action_values.__getitem__);chosen[info]=action
                for d in ds:values[d][n]=values[d][children[n][action]]
        else:
            for d in range(24):values[d][n]=sum(p(d,n,a)*values[d][children[n][a]] for a in range(arity[n]))
    value=sum(q*values[d][0] for d,q in enumerate(chance))
    # Independent evaluation of the explicit resulting behavioral policy.
    explicit=list(policy)
    for info,action in chosen.items():
        a,b=offset[info:info+2];explicit[a:b]=[float(i==action) for i in range(b-a)]
    independent=evaluate(data,explicit,case)['ev'][player]
    assert abs(value-independent)<1e-11
    return value


def local_deviations(data, policy, case, player):
    chance=data['probabilities'];infos=data['deal_infos'];offset=data['offsets']
    actors=data['actors'];children=data['children'];arity=data['arity'];utilities=data['cases'][case]['utilities']
    def p(d,n,a):return policy[offset[infos[d][n]]+a]
    reach=[[0.]*19 for _ in chance];values=[[0.]*19 for _ in chance]
    for d,q in enumerate(chance):reach[d][0]=q
    for n in range(19):
        if arity[n]:
            for d in range(24):
                for a in range(arity[n]):reach[d][children[n][a]]=reach[d][n]*p(d,n,a)
    for n in reversed(range(19)):
        for d in range(24):
            values[d][n]=(sum(p(d,n,a)*values[d][children[n][a]] for a in range(arity[n]))
                          if arity[n] else utilities[d][n][player])
    base=sum(q*values[d][0] for d,q in enumerate(chance));rows=[]
    for info,(node,card,board) in enumerate(data['information_keys']):
        if actors[node]!=player:continue
        ds=[d for d in range(24) if infos[d][node]==info]
        mass=sum(reach[d][node] for d in ds)
        q=[sum(reach[d][node]*values[d][children[node][a]] for d in ds) for a in range(arity[node])]
        start,end=offset[info:info+2];mix=policy[start:end]
        selected=max(range(arity[node]),key=q.__getitem__)
        gain=q[selected]-sum(a*b for a,b in zip(q,mix))
        altered=list(policy);altered[start:end]=[float(a==selected) for a in range(arity[node])]
        independent=evaluate(data,altered,case)['ev'][player]-base
        assert abs(independent-gain)<1e-11 and gain>=-1e-11
        rows.append(dict(information_id=info,node=node,own_card=card,public_card=board,
            entry_probability=mass,policy=mix,best_single_action=selected,
            action_values_conditional=[v/mass for v in q] if mass else None,
            single_information_deviation_gain=gain))
    return sorted(rows,key=lambda r:r['single_information_deviation_gain'],reverse=True)


def main():
    assert idle()
    fixture=OUT/'sampled-convergence-v1-fixture.json'
    cases=[OUT/f'sampled-neural-mean-{device}-v1-case0-seed17.json' for device in ('cpu','gpu')]
    paths=[Path(__file__),fixture,*cases]+[ROOT/'tools/research'/p for p in (
        'hu_sampled_convergence_fixture_20260922.py','hu_sampled_updates_oracle_20260922.py','loopback_research_validation.py')]
    frozen={p.relative_to(ROOT).as_posix():sha(p) for p in paths};reg=OUT/(PREFIX+'-registration.json')
    save(reg,dict(inputs=frozen,maximum_seconds=120,
        scope='Post-hoc diagnostic of two completed finite no-rake seed-17 runs. Not an independent acceptance test or physical-poker diagnosis.',
        methods='Exact restricted best response: repair public-card nodes, add later preflop nodes, then root; independent explicit-policy checks. Separately measure one-information-set deviations with all other behavior fixed.',
        decomposition_order=[[2,3,6,7],[2,3,5,6,7,8],[0,2,3,5,6,7,8]],
        no_training=True,no_gpu=True,production_modified=False))
    started=time.monotonic();data=json.loads(fixture.read_text());results=[]
    all_nodes={n for n,a in enumerate(data['arity']) if a}
    stages=[('public_card_decisions',{2,3,6,7}),('add_later_preflop',{2,3,5,6,7,8}),('add_root',all_nodes)]
    for device,path in zip(('cpu','gpu'),cases):
        result=json.loads(path.read_text());assert result['terminal'];last=result['checkpoints'][-1]
        policy=last['average_policy'];ev=evaluate(data,policy,0);assert abs(ev['gap']-last['evaluation']['gap'])<1e-12
        players=[]
        for player in (0,1):
            base=restricted_response(data,policy,0,player,set());assert abs(base-ev['ev'][player])<1e-11
            current=base;decomposition=[]
            for label,nodes in stages:
                value=restricted_response(data,policy,0,player,nodes);assert value>=current-1e-11
                decomposition.append(dict(stage=label,additional_gain=value-current));current=value
            assert abs(current-ev['best_response'][player])<1e-11
            local=local_deviations(data,policy,0,player)
            players.append(dict(player=player,full_best_response_gain=current-base,decomposition=decomposition,
                local_deviations=local,largest_single_information_gain=local[0]['single_information_deviation_gain']))
        assert abs(sum(p['full_best_response_gain'] for p in players)-ev['gap'])<1e-11
        results.append(dict(device=device,iteration=last['iteration'],gap=ev['gap'],players=players))
        assert idle() and time.monotonic()-started<120
    for name,h in frozen.items():assert sha(ROOT/name)==h,name
    final=dict(passed=True,inputs_verified=len(frozen),runs=results,seconds=time.monotonic()-started,
        registration_sha256=sha(reg),warning='Single-information gains overlap and must not be summed. The sequential decomposition is order-dependent.',
        physical_poker_convergence_qualified=False,production_modified=False)
    save(OUT/(PREFIX+'-result.json'),final)
    print(json.dumps([dict(device=r['device'],gap=r['gap'],players=[dict(player=p['player'],gain=p['full_best_response_gain'],
        decomposition=p['decomposition'],top=p['local_deviations'][:3]) for p in r['players']]) for r in results],indent=2))

if __name__=='__main__':main()
