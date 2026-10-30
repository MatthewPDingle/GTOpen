"""Independent card-summary controls; no model fitting or held-out evaluation."""
from itertools import combinations,permutations
import json
from pathlib import Path
import random
import time
import numpy as np
from loopback_research_validation import idle
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from sampled_visible_poker_features_v1 import best_visible_rank,visible_summaries,from_active_features,FEATURE_NAMES,WIDTH
from hu_sampled_physical_dense_btn_jam_diagnosis_20260923 import rank5

OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='sampled-visible-poker-features-v1-control'


def active_for(hole,board):
    cards=list(hole)+list(board)+[None]*(5-len(board));active=[]
    for i,c in enumerate(cards):
        rank,suit=(13,4) if c is None else (c//4,c%4)
        active.extend((i*19+rank,i*19+14+suit))
    phase={0:0,3:1,4:2,5:3}[len(board)]
    active += [133,135+phase,139]
    for i in range(19):active.append(155+i*6+(5 if i<max(0,phase-1) else 0))
    return sorted(active)


def main():
    began=time.monotonic();rng=random.Random(2026092301)
    def guard():assert idle() and time.monotonic()-began<180
    guard()
    oracle_count=0;category_counts=[0]*9;suit_count=0
    for size in (5,6,7):
        for i in range(4096):
            if i%128==0:guard()
            cards=rng.sample(range(52),size)
            actual=best_visible_rank(cards)
            expected=max(rank5(list(c)) for c in combinations(cards,5))
            assert actual==expected,(cards,actual,expected)
            category_counts[actual[0]]+=1;oracle_count+=1
            x=visible_summaries(cards[:2],cards[2:])
            assert np.array_equal(x,from_active_features(active_for(cards[:2],cards[2:])))
            assert x[:9].sum()==1 and x[actual[0]]==1
            assert x.shape==(33,) and WIDTH==33 and len(set(FEATURE_NAMES))==WIDTH
            if i<32:
                for perm in permutations(range(4)):
                    transformed=[c//4*4+perm[c%4] for c in cards]
                    assert np.array_equal(x,visible_summaries(transformed[:2][::-1],transformed[2:][::-1]))
                    suit_count+=1
    # Explicit rare hands, including a wheel straight flush, two trips and three pairs.
    fixtures=[([48,0,4,8,12,45,42],(8,3)),([48,49,50,51,44,40,0],(7,12,11)),
              ([48,49,50,44,45,46,0],(6,12,11)),([48,49,44,45,40,41,0],(2,12,11,10)),
              ([48,40,28,16,4,1,6],(5,12,10,7,4,1))]
    for cards,expected in fixtures:
        assert best_visible_rank(cards)==expected==max(rank5(list(c)) for c in combinations(cards,5))
    for hole in combinations(range(52),2):
        assert not visible_summaries(hole,[]).any()
        assert not from_active_features(active_for(hole,[])).any()
    # Use a completed TRAINING batch only for real native-observation transport parity.
    regpath=OUT/'sampled-physical-dense-pilot-v1-registration.json'
    reg=json.loads(regpath.read_text())
    metricpath=Path(reg['store'])/'iteration-0001/metrics.json'
    metric=json.loads(metricpath.read_text());querypath=metricpath.parent/'batch-00/queries.json'
    assert sha(querypath)==metric['subbatches'][0]['artifacts']['queries.json']
    queries=json.loads(querypath.read_text())
    phase_counts=[0]*4
    for i,o in enumerate(queries['observations']):
        if i%256==0:guard()
        code=int(o['lo']);cards=[(code>>(6*j))&63 for j in range(7)]
        count=(0,3,4,5)[o['phase']]
        assert all(c==63 for c in cards[2+count:])
        direct=visible_summaries(cards[:2],cards[2:2+count])
        assert np.array_equal(direct,from_active_features(o['active_features']))
        if o['phase']:
            assert best_visible_rank(cards[:2+count])==max(rank5(list(c)) for c in combinations(cards[:2+count],5))
        phase_counts[o['phase']]+=1
    malformed=[lambda:visible_summaries([0,0],[1,2,3]),lambda:visible_summaries([0,1],[2,3]),
        lambda:visible_summaries([0,1],[2,3,52]),lambda:visible_summaries([0,1],[2,3,True]),
        lambda:from_active_features([0]*36)]
    # Preserve future card slots but falsely claim the earlier phase: reject leakage.
    for size in (3,4,5):
        row=active_for([0,1],list(range(2,2+size)));phase={3:1,4:2,5:3}[size]
        row[row.index(135+phase)]=135+phase-1
        malformed.append(lambda row=row:from_active_features(row))
    for fn in malformed:
        try:fn()
        except ValueError:pass
        else:raise AssertionError('Accepted invalid visible-card input')
    guard()
    paths=[Path(__file__),ROOT/'tools/research/sampled_visible_poker_features_v1.py',
        ROOT/'tools/research/hu_sampled_physical_dense_btn_jam_diagnosis_20260923.py',regpath,metricpath,querypath]
    result=dict(passed=True,inputs={str(p):sha(p) for p in paths},appended_features=list(FEATURE_NAMES),
        original_width=269,appended_width=WIDTH,prospective_total_width=269+WIDTH,
        random_best_five_reference_cases=oracle_count,random_category_counts=category_counts,
        rare_hand_fixtures=len(fixtures),suit_and_order_invariance_cases=suit_count,
        zero_preflop_private_pairs=1326,real_training_observation_phase_counts=phase_counts,
        malformed_or_future_leak_cases_rejected=len(malformed),seconds=time.monotonic()-began,
        training_launched=False,held_out_data_used=False,production_modified=False,
        scope='Representation correctness only. Summaries are redundant visible-card inputs, not equity or strategic labels. No active model or experiment imports this encoder; no learning or range-quality improvement is established.')
    save(OUT/f'{PREFIX}-result.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ['inputs','appended_features']}))


if __name__=='__main__':main()
