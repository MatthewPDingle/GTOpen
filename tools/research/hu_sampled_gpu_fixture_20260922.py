"""Export exact-reference fixtures for frozen sampled GPU batches."""
from collections import defaultdict
from fractions import Fraction as F
import hashlib
from itertools import permutations, product
import json
from pathlib import Path
from hu_sampled_updates_oracle_20260922 import ACTOR, CHILD, TERMINAL, key, distribution, payoff

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'


def main():
    destination=OUT/'sampled-gpu-batch-v1-fixture.json'
    assert not destination.exists()
    oracle=OUT/'sampled-updates-oracle-v1-result.json'
    assert json.loads(oracle.read_text())['passed']
    deals=list(permutations(range(4),3))
    raw={d:F([7,3,2,1][d[0]],[1,1,1,1000][d[0]])*F([2,5,1,3][d[1]])*F([1,4,2,3][d[2]]) for d in deals}
    z=sum(raw.values());chance={d:w/z for d,w in raw.items()}
    infos=sorted({key(n,d) for n in ACTOR for d in deals});ids={k:i for i,k in enumerate(infos)}
    assert len(ids)==60
    offsets=[0]
    for i in infos:offsets.append(offsets[-1]+len(CHILD[i[0]]))
    states=offsets[-1];nn=19;arity=[len(CHILD.get(n,())) for n in range(nn)]
    actors=[ACTOR.get(n,-1) for n in range(nn)]
    children=[CHILD.get(n,())+(0,)*(3-arity[n]) for n in range(nn)]
    cases=[]
    for rake in [False,True]:
        regret=[F((i%7)-3,10) for i in range(states)];average=[F(0)]*states
        initial=list(regret);rounds=[]
        for t in range(2):
            policy={i:distribution(t,i) for i in infos};delta=defaultdict(F);ownavg={}
            for deal,prob in chance.items():
                def full(n,reach):
                    if n not in ACTOR:return payoff(n,deal,rake)
                    p=ACTOR[n];info=key(n,deal);s=policy[info];vs=[]
                    ownavg[info]=[reach[p]*v for v in s]
                    for a,c in enumerate(CHILD[n]):
                        r=list(reach);r[p]*=s[a];vs.append(full(c,r))
                    v=[sum(s[a]*vs[a][p] for a in range(len(s))) for p in range(2)]
                    for a,u in enumerate(vs):delta[info,a]+=prob*reach[1-p]*(u[p]-v[p])
                    return v
                full(0,[F(1),F(1)])
            sigma=[float(x) for i in infos for x in policy[i]]
            expected_delta=[];expected_avg=[]
            for i in infos:
                q=sum(prob for d,prob in chance.items() if key(i[0],d)==i)
                for a in range(len(policy[i])):
                    expected_delta.append(delta[i,a]);expected_avg.append(q*ownavg[i][a])
            regret=[r+d for r,d in zip(regret,expected_delta)]
            average=[r+d for r,d in zip(average,expected_avg)]
            next_sigma=[];normalized_avg=[]
            for j,i in enumerate(infos):
                r=regret[offsets[j]:offsets[j+1]];positive=[max(x,F(0)) for x in r];total=sum(positive)
                next_sigma.extend(float(v/total if total else F(1,len(r))) for v in positive)
                av=average[offsets[j]:offsets[j+1]];total=sum(av)
                normalized_avg.extend(float(v/total if total else F(1,len(r))) for v in av)
            samples=[]
            for player in range(2):
                opp=[n for n,p in ACTOR.items() if p!=player]
                for deal,prob in chance.items():
                    for actions in product(*(range(arity[n]) for n in opp)):
                        tape=dict(zip(opp,actions));w=prob
                        for n,a in tape.items():w*=policy[key(n,deal)][a]
                        if not w:continue
                        samples.append(dict(player=player,weight=float(w),
                            infos=[ids[key(n,deal)] if n in ACTOR else -1 for n in range(nn)],
                            choice=[tape.get(n,0) for n in range(nn)],
                            utilities=[float(payoff(n,deal,rake)[player]) if n in TERMINAL else 0. for n in range(nn)]))
            # CSR groups duplicate information sets, retaining every occurrence
            # in deterministic sample/node order. No lossy hash key is used.
            occurrences=[[] for _ in infos]
            for s,sample in enumerate(samples):
                for n,i in enumerate(sample['infos']):
                    if i>=0:occurrences[i].append(s*nn+n)
            csr=[0];entries=[]
            for occ in occurrences:entries.extend(occ);csr.append(len(entries))
            assert len(entries)==len(samples)*len(ACTOR)
            assert len(entries)==len(set(entries))
            rounds.append(dict(policy=sigma,samples=samples,csr_offsets=csr,csr_entries=entries,
                expected_delta=list(map(float,expected_delta)),expected_average_increment=list(map(float,expected_avg)),
                expected_regret=list(map(float,regret)),expected_average=list(map(float,average)),
                expected_next_policy=next_sigma,expected_normalized_average=normalized_avg))
        cases.append(dict(rake=rake,initial_regret=list(map(float,initial)),rounds=rounds))
    inputs=[Path(__file__),ROOT/'tools/research/hu_sampled_updates_oracle_20260922.py',oracle]
    result=dict(node_count=nn,arity=arity,actors=actors,children=children,information_keys=infos,
        action_offsets=offsets,cases=cases,scope='Finite-control batches only, complete external-sampling tapes. f64 GPU reference; not poker training.',
        inputs_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs})
    destination.write_text(json.dumps(result,separators=(',',':'))+'\n',encoding='utf-8',newline='\n')
    print('Fixture:',destination.stat().st_size,'bytes;',len(infos),'information sets;',states,'action entries')


if __name__=='__main__':main()
