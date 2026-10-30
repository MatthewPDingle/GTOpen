"""Exact rational finite-game oracle for external sampling and average policy.

This is a correctness control, not a poker trainer or a convergence benchmark.
All random tapes are enumerated; no Monte Carlo confidence claims are made.
"""
from collections import defaultdict
from fractions import Fraction as F
import hashlib
from itertools import permutations, product
import json
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'sampled-updates-oracle-v1'
# Full public histories are represented by unique node IDs. Board is hidden
# preflop; the opponent's private card is never part of an information-set key.
ACTOR = {0:0, 2:1, 3:0, 5:1, 6:1, 7:0, 8:0}
CHILD = {0:(1,2,5), 2:(10,3), 3:(11,12), 5:(13,6,8),
         6:(14,7), 7:(15,16), 8:(17,18)}
POST = {2,3,6,7}
# Terminal: player contributions, winner for folds (None for showdown).
TERMINAL = {1:((1,2),1), 10:((2,2),None), 11:((2,5),1),
            12:((5,5),None), 13:((6,2),0), 14:((6,6),None),
            15:((6,9),1), 16:((9,9),None), 17:((6,10),1),
            18:((10,10),None)}


def key(node, deal):
    return (node, deal[ACTOR[node]], deal[2] if node in POST else -1)


def distribution(round_id, info):
    node, hand, board = info
    n = len(CHILD[node])
    values = [1+(node*3+hand*5+(board+1)*2+a*7+round_id*(a+1)*3)%11
              for a in range(n)]
    if round_id == 0 and node == 0 and hand == 1:
        values = [5,5,0]  # Later own nodes must still receive regret updates.
    if round_id == 0 and node == 5 and hand == 2:
        values = [1,0,0]
    return tuple(F(v,sum(values)) for v in values)


def payoff(node, deal, rake):
    invested, winner = TERMINAL[node]
    pot = sum(invested)+F(1,2)
    if winner is not None:
        return tuple((pot if p == winner else 0)-invested[p] for p in range(2))
    strength = [(deal[p]+deal[2])%3 for p in range(2)]
    wins = [F(1,2) if strength[0] == strength[1] else F(strength[p] > strength[1-p])
            for p in range(2)]
    fee = min(pot/F(20),F(1,2)) if rake else F(0)
    values = tuple(w*(pot-fee)-i for w,i in zip(wins,invested))
    assert sum(values) == F(1,2)-fee
    return values


def add(target, info, values, scale=F(1)):
    for a,value in enumerate(values):
        target[info,a] += scale*value


def main():
    started = time.monotonic()
    registration_path = OUT/(PREFIX+'-registration.json')
    result_path = OUT/(PREFIX+'-result.json')
    assert not registration_path.exists() and not result_path.exists()
    script_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    registration = dict(script_sha256=script_hash, created_at_unix=time.time(),
        purpose='Exact update/averaging identities only; prerequisite to a sampled GPU trainer.',
        support='24 distinct deals: 4-card toy deck, one card per player, one public card. Seven decision nodes with early folds, postflop calls and an all-in.',
        arithmetic='fractions.Fraction; no tolerance or statistical estimate',
        policy_rounds=2, utility_modes=['dead money, no rake','dead money, action-dependent rake'],
        required_controls=['zero own reach and re-entry','rare private hand','hidden-information key isolation',
            'double opponent-reach weighting rejected','double chance weighting rejected',
            'updater-pass naive average rejected','root-only averaging does not suffice'],
        averages='Accumulate sigma at sampled-opponent nodes, during the other player update. Expectation = fixed chance marginal * own reach * sigma. Normalize cumulative sums within each information set.',
        limits='Not physical poker, no full-game memory/convergence/runtime claim; no nonlinear CFR+ equivalence claim.')
    registration_path.write_text(json.dumps(registration,indent=2)+'\n',encoding='utf-8',newline='\n')
    deals = list(permutations(range(4),3))
    raw = {d:F([7,3,2,1][d[0]],[1,1,1,1000][d[0]])*
           F([2,5,1,3][d[1]])*F([1,4,2,3][d[2]]) for d in deals}
    z = sum(raw.values()); chance = {d:w/z for d,w in raw.items()}
    assert len(chance)==24 and sum(chance.values())==1
    infos = {key(n,d) for n in ACTOR for d in deals}
    q = {i:sum(prob for d,prob in chance.items() if key(i[0],d)==i) for i in infos}
    assert all(x>0 for x in q.values())
    # Explicit imperfect-information controls: same preflop key across boards
    # and opponent cards, but distinct postflop keys after the board is seen.
    assert key(0,(1,2,0))==key(0,(1,3,2))
    assert key(3,(1,2,0))!=key(3,(1,3,2))
    assert payoff(1,(1,2,0),True)==payoff(1,(1,3,2),True)
    scenarios=[]
    for rake in [False,True]:
        average_reference = defaultdict(F); average_sample = defaultdict(F)
        naive_average = defaultdict(F); zero_witnesses=[]; rounds=[]
        for round_id in range(2):
            sigma = {i:distribution(round_id,i) for i in infos}
            reference = defaultdict(F); own_average = {}; own_reach={}
            # Reference fully traverses all actions and sums hidden histories.
            for deal,prob in chance.items():
                def full(node, reach):
                    if node not in ACTOR:
                        return payoff(node,deal,rake)
                    p=ACTOR[node]; info=key(node,deal); s=sigma[info]
                    if info in own_reach:
                        assert own_reach[info]==reach[p]
                    own_reach[info]=reach[p]
                    own_average[info]=tuple(reach[p]*x for x in s)
                    children=[]
                    for a,c in enumerate(CHILD[node]):
                        r=list(reach);r[p]*=s[a]
                        children.append(full(c,tuple(r)))
                    value=tuple(sum(s[a]*v[k] for a,v in enumerate(children)) for k in range(2))
                    add(reference,info,[v[p]-value[p] for v in children],prob*reach[1-p])
                    return value
                full(0,(F(1),F(1)))
            for info,values in own_average.items():
                add(average_reference,info,values)
            expected=defaultdict(F); avg=defaultdict(F)
            doubled_opp=defaultdict(F); doubled_chance=defaultdict(F)
            wrong_avg=defaultdict(F); tapes=0
            # Candidate fixes one complete chance deal and one independently
            # sampled pure action at each opponent information set. Enumerating
            # all tapes exactly computes the expectation of a single traversal.
            for player in range(2):
                opp_nodes=[n for n,p in ACTOR.items() if p!=player]
                for deal,prob in chance.items():
                    tape_total=F(0)
                    for choices in product(*(range(len(CHILD[n])) for n in opp_nodes)):
                        tape=dict(zip(opp_nodes,choices)); tape_prob=F(1)
                        for n,a in tape.items():tape_prob*=sigma[key(n,deal)][a]
                        tape_total+=tape_prob
                        if tape_prob==0:continue
                        tapes+=1; weight=prob*tape_prob
                        def sampled(node, opponent_reach):
                            if node not in ACTOR:return payoff(node,deal,rake)[player]
                            p=ACTOR[node];info=key(node,deal);s=sigma[info]
                            if p!=player:
                                add(avg,info,s,weight)
                                a=tape[node]
                                return sampled(CHILD[node][a],opponent_reach*s[a])
                            values=[sampled(c,opponent_reach) for c in CHILD[node]]
                            value=sum(a*b for a,b in zip(s,values))
                            delta=[v-value for v in values]
                            add(expected,info,delta,weight)
                            add(doubled_opp,info,delta,weight*opponent_reach)
                            add(doubled_chance,info,delta,weight*prob)
                            add(wrong_avg,info,s,weight)
                            return value
                        sampled(0,F(1))
                    assert tape_total==1
            keys=set(reference)|set(expected)
            assert all(reference[k]==expected[k] for k in keys)
            assert any(reference[k]!=doubled_opp[k] for k in keys)
            assert any(reference[k]!=doubled_chance[k] for k in keys)
            for info,values in own_average.items():
                for a,value in enumerate(values):
                    assert avg[info,a]==q[info]*value
                    average_sample[info,a]+=avg[info,a]
                    naive_average[info,a]+=wrong_avg[info,a]
                if own_reach[info]==0 and any(reference[info,a]!=0 for a in range(len(values))):
                    zero_witnesses.append(info)
            rounds.append(dict(round=round_id,enumerated_nonzero_tapes=tapes,
                exact_regret_entries=len(keys),exact_average_entries=len(avg),
                max_regret_error=0,max_average_error_after_chance_scale=0,
                zero_own_reach_nonzero_regret_infos=sum(own_reach[i]==0 and
                    any(reference[i,a]!=0 for a in range(len(sigma[i]))) for i in infos)))
        assert zero_witnesses
        # Fixed Q(I) cancels ONLY after accumulation across rounds. A naive
        # average collected on the updating player's pass generally does not.
        naive_differences=[]
        for info in infos:
            n=len(CHILD[info[0]])
            den=sum(average_reference[info,a] for a in range(n))
            sd=sum(average_sample[info,a] for a in range(n))
            nd=sum(naive_average[info,a] for a in range(n))
            assert den>0 and sd>0 and nd>0
            for a in range(n):
                target=average_reference[info,a]/den
                assert target==average_sample[info,a]/sd
                naive_differences.append(abs(target-naive_average[info,a]/nd))
        assert max(naive_differences)>F(1,100)
        for info in zero_witnesses:
            # Round 1 has re-entry; the correct cumulative average is its policy.
            n=len(CHILD[info[0]]);den=sum(average_sample[info,a] for a in range(n))
            assert tuple(average_sample[info,a]/den for a in range(n))==distribution(1,info)
        scenarios.append(dict(rake=rake,rounds=rounds,zero_reach_witness_count=len(zero_witnesses),
            naive_average_max_probability_error=float(max(naive_differences)),
            normalized_two_round_average_exact=True,zero_reach_reentry_exact=True))
    assert hashlib.sha256(Path(__file__).read_bytes()).hexdigest()==script_hash
    result=dict(passed=True,scenarios=scenarios,distinct_infosets=len(infos),
        minimum_chance_infoset_mass=float(min(q.values())),chance_deals=len(deals),
        exact_rational_checks=True,production_modified=False,gpu_used=False,trainer_qualified=False,
        registration_sha256=hashlib.sha256(registration_path.read_bytes()).hexdigest(),
        seconds=time.monotonic()-started,
        next_gate='GPU batch update/reduction and exact perfect-recall sparse keys; then actual wide-geometry memory, throughput and independent convergence tests.')
    result_path.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
