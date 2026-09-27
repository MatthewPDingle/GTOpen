"""Exact rational small-deck check of a proposed change in integration order.

This is a synthetic chance/utility fixture, not a poker solve or production
evaluator. It proves only the implemented finite probability identities.
"""
from fractions import Fraction as F
import hashlib
from itertools import combinations
import json
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'board-first-chance-identity-control-v1'
CARDS = tuple(range(8))
HANDS = list(combinations(CARDS, 2))
BOARDS = HANDS


def weights(mode, hand, player):
    if mode == 'uniform':
        return 1
    if mode == 'restricted' and (sum(hand)+player) % 3 == 0:
        return 0
    return 1 + ((hand[0]+1)*(hand[1]+2)*(player+2)) % 13


def utility(h, v, board):
    # Deliberately asymmetric bounded values, unrelated to hold'em hand ranks.
    # This is terminal arithmetic, not a policy that sees hidden cards.
    call = F(sum(h)-sum(v)) + F(len(set(board)&{(x+1)%8 for x in h}), 3)
    raise_value = 2*call + F(sum(board)-7, 2) + F(h[0]*v[1]-h[1]*v[0], 5)
    return [F(-1), call, raise_value, raise_value-call]


def fixture(mode, proposal):
    pairs = [(h,v) for h in HANDS for v in HANDS if not set(h)&set(v)]
    raw = {(h,v):weights(mode,h,0)*weights(mode,v,1) for h,v in pairs}
    total = sum(raw.values())
    joint = {hv:F(w,total) for hv,w in raw.items()}
    hero_mass = {h:sum((p for (x,v),p in joint.items() if x==h),F(0)) for h in HANDS}
    board_q_raw = {b:(1 if proposal=='uniform' else 1+(sum(b)%5)) for b in BOARDS}
    board_q = {b:F(w,sum(board_q_raw.values())) for b,w in board_q_raw.items()}
    expected = [F(0)]*4
    second = [F(0)]*4
    conditional = {h:[F(0)]*4 for h in HANDS}
    physical_outcomes = 0
    # Private-first reference: enumerate the original conditional board law.
    for (h,v),p in joint.items():
        remaining = [c for c in CARDS if c not in h and c not in v]
        boards = list(combinations(remaining,2))
        assert len(boards)==6
        for b in boards:
            physical_outcomes += 1
            values = utility(h,v,b)
            for a,u in enumerate(values):
                expected[a] += p*F(1,len(boards))*u
                second[a] += p*F(1,len(boards))*u*u
                conditional[h][a] += p*F(1,len(boards))*u
    for h in HANDS:
        if hero_mass[h]:
            conditional[h] = [x/hero_mass[h] for x in conditional[h]]

    reconstructed = [F(0)]*4
    proposed_second = [F(0)]*4
    marginal_second = [F(0)]*4
    naive = [F(0)]*4
    conditional_reconstructed = {h:[F(0)]*4 for h in HANDS}
    marginal_sum = F(0)
    # Board-first candidate: independently enumerate compatible private pairs.
    for b in BOARDS:
        remaining = [c for c in CARDS if c not in b]
        sums = [F(0)]*4
        mass = F(0)
        by_hero = {h:[F(0)]*4 for h in HANDS}
        for h in combinations(remaining,2):
            for v in combinations([c for c in remaining if c not in h],2):
                p = F(raw[(h,v)],total)*F(1,6)
                mass += p
                for a,u in enumerate(utility(h,v,b)):
                    sums[a] += p*u
                    by_hero[h][a] += p*u
        marginal_sum += mass
        for a in range(4):
            estimate = sums[a]/board_q[b]
            reconstructed[a] += board_q[b]*estimate
            proposed_second[a] += board_q[b]*estimate*estimate
            if mass:
                marginal_second[a] += sums[a]*sums[a]/mass
                naive[a] += board_q[b]*sums[a]/mass
        for h in HANDS:
            if hero_mass[h]:
                for a in range(4):
                    estimate = by_hero[h][a]/board_q[b]/hero_mass[h]
                    conditional_reconstructed[h][a] += board_q[b]*estimate
    assert marginal_sum == 1 and reconstructed == expected
    assert conditional_reconstructed == conditional
    direct_variance = [s-m*m for s,m in zip(second,expected)]
    marginal_variance = [s-m*m for s,m in zip(marginal_second,expected)]
    proposed_variance = [s-m*m for s,m in zip(proposed_second,expected)]
    assert all(0<=v<=original for v,original in zip(marginal_variance,direct_variance))
    assert all(v>=0 for v in proposed_variance)
    naive_error = max(abs(a-b) for a,b in zip(naive,expected))
    if mode!='uniform' or proposal!='uniform':
        assert naive_error>0, 'Negative control must expose the lost board marginal'
    return dict(mode=mode,proposal=proposal,physical_outcomes=physical_outcomes,
        positive_hero_hands=sum(bool(x) for x in hero_mass.values()),
        exact_rational_global_and_conditional_means_equal=True,
        true_board_marginal_variance_never_larger=True,
        naive_board_normalization_maximum_bias=float(naive_error),
        mean=[float(x) for x in expected],
        direct_variance=[float(x) for x in direct_variance],
        true_board_marginal_variance=[float(x) for x in marginal_variance],
        proposal_importance_variance=[float(x) for x in proposed_variance])


def main():
    start=time.monotonic()
    result=[fixture(mode,proposal) for mode in ('uniform','weighted','restricted')
            for proposal in ('uniform','nonuniform')]
    output=dict(passed=True,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        fixtures=result,seconds=time.monotonic()-start,exact_arithmetic=True,
        gpu_used=False,training_changed=False,production_modified=False,
        scope='Synthetic 8-card, 2-card-board chance identities only. Not a poker engine, performance result, learned baseline, CFR implementation, or range accuracy result.')
    with (OUT/f'{PREFIX}-result.json').open('x',encoding='utf-8') as stream:
        json.dump(output,stream,separators=(',',':'),allow_nan=False)
    print(json.dumps(output),flush=True)


if __name__=='__main__':
    main()
