"""Finite imperfect-information convergence control and independent evaluator."""
from fractions import Fraction as F
from itertools import permutations
from pathlib import Path
import hashlib
import json
from hu_sampled_updates_oracle_20260922 import ACTOR,CHILD,TERMINAL,key,payoff

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'

def evaluate(data,policy,case):
    """Exact finite chance sum; choose BR actions after grouping hidden states."""
    chance=data['probabilities'];infos=data['deal_infos'];offset=data['offsets']
    utilities=data['cases'][case]['utilities'];actors=data['actors'];children=data['children'];arity=data['arity']
    def p(d,n,a):return policy[offset[infos[d][n]]+a]
    def profile(player,override=None):
        values=[[0.]*19 for _ in chance]
        for n in reversed(range(19)):
            for d in range(24):
                if not arity[n]:values[d][n]=utilities[d][n][player]
                elif override is not None and actors[n]==player:values[d][n]=values[d][children[n][override[infos[d][n]]]]
                else:values[d][n]=sum(p(d,n,a)*values[d][children[n][a]] for a in range(arity[n]))
        return sum(q*values[d][0] for d,q in enumerate(chance))
    ev=[profile(player) for player in range(2)];br=[];cheat=[]
    for player in range(2):
        reach=[[0.]*19 for _ in chance]
        for d,q in enumerate(chance):reach[d][0]=q
        for n in range(19):
            if not arity[n]:continue
            for d in range(24):
                for a in range(arity[n]):reach[d][children[n][a]]=reach[d][n]*(1 if actors[n]==player else p(d,n,a))
        values=[[0.]*19 for _ in chance];chosen={}
        cheating=[[0.]*19 for _ in chance]
        for n in reversed(range(19)):
            if not arity[n]:
                for d in range(24):values[d][n]=cheating[d][n]=utilities[d][n][player]
            elif actors[n]==player:
                groups={}
                for d in range(24):groups.setdefault(infos[d][n],[]).append(d)
                for info,ds in groups.items():
                    q=[sum(reach[d][n]*values[d][children[n][a]] for d in ds) for a in range(arity[n])]
                    action=max(range(arity[n]),key=lambda a:q[a]);chosen[info]=action
                    for d in ds:values[d][n]=values[d][children[n][action]]
                for d in range(24):cheating[d][n]=max(cheating[d][children[n][a]] for a in range(arity[n]))
            else:
                for d in range(24):
                    values[d][n]=sum(p(d,n,a)*values[d][children[n][a]] for a in range(arity[n]))
                    cheating[d][n]=sum(p(d,n,a)*cheating[d][children[n][a]] for a in range(arity[n]))
        value=sum(q*values[d][0] for d,q in enumerate(chance));assert abs(value-profile(player,chosen))<1e-11
        br.append(value);cheat.append(sum(q*cheating[d][0] for d,q in enumerate(chance)))
        assert value>=ev[player]-1e-11 and cheat[-1]>=value-1e-11
    return {'ev':ev,'best_response':br,'gap':sum(b-a for a,b in zip(ev,br)),'clairvoyant_gap':sum(b-a for a,b in zip(ev,cheat))}

def main():
    out=OUT/'sampled-convergence-v1-fixture.json';assert not out.exists()
    deals=list(permutations(range(4),3));raw=[F([7,3,2,1][d[0]],[1,1,1,1000][d[0]])*F([2,5,1,3][d[1]])*F([1,4,2,3][d[2]]) for d in deals]
    z=sum(raw);prob=[float(w/z) for w in raw];infos=sorted({key(n,d) for n in ACTOR for d in deals});ids={i:k for k,i in enumerate(infos)}
    offsets=[0]
    for i in infos:offsets.append(offsets[-1]+len(CHILD[i[0]]))
    data={'deals':deals,'probabilities':prob,'information_keys':infos,'offsets':offsets,
        'deal_infos':[[ids[key(n,d)] if n in ACTOR else -1 for n in range(19)] for d in deals],
        'actors':[ACTOR.get(n,-1) for n in range(19)],'arity':[len(CHILD.get(n,())) for n in range(19)],
        'children':[list(CHILD.get(n,()))+[0]*(3-len(CHILD.get(n,()))) for n in range(19)],
        'cases':[{'rake':rake,'utilities':[[list(map(float,payoff(n,d,rake))) if n in TERMINAL else [0.,0.] for n in range(19)] for d in deals]} for rake in [False,True]],
        'scope':'Existing 4-card nonphysical finite oracle game. Convergence implementation control only; not BB ranges or full poker feasibility.'}
    uniform=[1/len(CHILD[i[0]]) for i in infos for _ in CHILD[i[0]]]
    control=[evaluate(data,uniform,c) for c in range(2)]
    assert abs(sum(control[0]['ev'])-.5)<1e-12
    assert all(c['clairvoyant_gap']>c['gap']+.01 for c in control)
    data['uniform_evaluation']=control
    paths=[Path(__file__),ROOT/'tools/research/hu_sampled_updates_oracle_20260922.py']
    data['inputs']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    out.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'information_sets':len(infos),'action_entries':offsets[-1],'uniform':control}))

if __name__=='__main__':main()
