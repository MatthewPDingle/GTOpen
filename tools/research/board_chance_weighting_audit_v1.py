"""Exhaustive small-deck audit of board-first importance weighting.

This checks a probability identity, not poker strength or trained predictions.
It uses two separate enumeration orders and includes an order-dependent payoff.
"""
from collections import defaultdict
import hashlib
import itertools
import json
import math
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'board-chance-weighting-audit-v1'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def runouts(cards):
    for five in itertools.combinations(cards, 5):
        for flop in itertools.combinations(five, 3):
            last = tuple(c for c in five if c not in flop)
            yield flop + last
            yield flop + last[::-1]


def payoff(hero, opponent, board):
    # Intentionally varies with both players' cards, flop, turn and river.
    # Values are synthetic; no hand ranking or poker engine is used.
    a, b = hero; c, d = opponent
    return (7*a-3*b+2*c-d+sum(board[:3])+4*board[3]-5*board[4],
            (a+c+board[3])*(b+d+board[4])-3*sum(board[:3]))


def main():
    began = time.monotonic()
    destination = OUT / f'{PREFIX}-result.json'
    assert not destination.exists()
    paths = [Path(__file__), ROOT / 'tools/research/board_root_components_v1.py',
             ROOT / 'tools/research/board_training_targets_v1.py',
             ROOT / 'tools/research/board_root_accumulator_v1.py']
    inputs = {str(p): sha(p) for p in paths}
    deck = tuple(range(10))
    hands = tuple(itertools.combinations(deck, 2))
    hero_weight = {h: 1+((3*h[0]+7*h[1]) % 13) for h in hands}
    other_weight = {h: 1+((11*h[0]+h[1]) % 17) for h in hands}
    hand_class = {h: (h[0]+2*h[1]) % 7 for h in hands}
    pairs = [(a, b, hero_weight[a]*other_weight[b]) for a in hands for b in hands
             if not set(a).intersection(b)]
    total = math.fsum(w for _, _, w in pairs)
    mass = [math.fsum(w for a, _, w in pairs if hand_class[a] == c)/total for c in range(7)]
    assert min(mass) > 0 and abs(math.fsum(mass)-1) < 1e-14
    conditional_count = math.comb(6, 3)*3*2
    public_count = math.comb(10, 3)*7*6
    direct, proposal, wrong_normalized, no_correction = [defaultdict(list) for _ in range(4)]
    direct_worlds = proposal_worlds = 0
    for hero, opponent, weight in pairs:
        remaining = tuple(c for c in deck if c not in hero and c not in opponent)
        boards = tuple(runouts(remaining))
        assert len(boards) == conditional_count
        c = hand_class[hero]
        probability = weight/total/mass[c]/conditional_count
        for board in boards:
            direct_worlds += 1
            for action, value in enumerate(payoff(hero, opponent, board)):
                direct[c, action].append(probability*value)
    ratio = math.comb(10, 5)/math.comb(6, 5)
    assert ratio == public_count/conditional_count
    boards = tuple(runouts(deck))
    assert len(boards) == public_count and len(set(boards)) == public_count
    for board in boards:
        legal = [(a, b, w) for a, b, w in pairs if not set(board).intersection((*a, *b))]
        surviving_mass = math.fsum(w for _, _, w in legal)/total
        assert surviving_mass > 0
        for hero, opponent, weight in legal:
            proposal_worlds += 1
            c = hand_class[hero]
            raw_mass = weight/total/mass[c]/public_count
            for action, value in enumerate(payoff(hero, opponent, board)):
                proposal[c, action].append(raw_mass*ratio*value)
                no_correction[c, action].append(raw_mass*value)
                wrong_normalized[c, action].append(raw_mass/surviving_mass*value)
    assert direct_worlds == proposal_worlds == 151200
    expected = {k: math.fsum(v) for k, v in direct.items()}
    actual = {k: math.fsum(v) for k, v in proposal.items()}
    error = max(abs(expected[k]-actual[k]) for k in expected)
    omitted_error = max(abs(expected[k]-math.fsum(no_correction[k])) for k in expected)
    renormalized_error = max(abs(expected[k]-math.fsum(wrong_normalized[k])) for k in expected)
    assert error < 1e-10 and omitted_error > 1 and renormalized_error > .01
    # Flop sorting leaves 20 turn/river orderings per five-card set, at both
    # the 52-card proposal and 48-card conditional law, so this factor cancels.
    full_ratio = math.comb(52, 5)/math.comb(48, 5)
    ordered_ratio = (math.comb(52, 3)*49*48)/(math.comb(48, 3)*45*44)
    assert full_ratio == ordered_ratio
    for p, h in inputs.items():
        assert sha(p) == h, p
    result = dict(passed=True, inputs=inputs, seconds=time.monotonic()-began,
        private_pairs=len(pairs), public_runouts=public_count, runouts_per_private_pair=conditional_count,
        worlds_each_order=direct_worlds, classes=7, actions=2, nonuniform_private_weights=True,
        maximum_weighted_identity_error=error, omitted_correction_error=omitted_error,
        per_board_renormalization_error=renormalized_error, miniature_chance_ratio=ratio,
        full_deck_chance_ratio=full_ratio, ordered_and_unordered_ratios_equal=True,
        native_poker_outputs_tested=False, trained_policies_tested=False, gpu_used=False,
        fresh_study_deals_drawn=0, production_modified=False,
        scope='Independent exhaustive probability-law audit on a ten-card toy deck; supports the weighting identity, not learned range accuracy.')
    with destination.open('x', encoding='utf-8') as f:
        json.dump(result, f, sort_keys=True); f.write('\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'inputs'}), flush=True)


if __name__ == '__main__':
    main()
