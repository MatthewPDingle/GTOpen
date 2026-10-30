"""Independent small-tree check of the shared-mixture algebra; no poker data."""
import hashlib
import itertools
import json
import math
from pathlib import Path
import random
import time
from paired_policy_mixture_bound_v1 import bound


def nodes(depth=5):
    return [p for d in range(depth) for p in itertools.product((0, 1), repeat=d)]


NODES = nodes()
LEAVES = list(itertools.product((0, 1), repeat=5))


def actor(path):
    return len(path) % 2


def identity(policy):
    return hashlib.sha256(json.dumps([policy[p] for p in NODES], separators=(',', ':')).encode()).hexdigest()


def complete_policy(rng):
    return {p: rng.choice((0., 1., rng.random())) for p in NODES}


def average(models, weights):
    result, zero = {}, 0
    for path in NODES:
        owner = actor(path); numerator, denominator = [], []
        for model, weight in zip(models, weights):
            reach = float(weight)
            for d, action in enumerate(path):
                if actor(path[:d]) == owner:
                    q = model[path[:d]]
                    reach *= q if action == 1 else 1-q
            numerator.append(reach*model[path]); denominator.append(reach)
        mass = math.fsum(denominator)
        result[path] = math.fsum(numerator)/mass if mass else .5
        zero += mass == 0
    return result, zero


def payoff(player0, player1, utilities):
    values = []
    for leaf in LEAVES:
        reach = 1.
        for d, action in enumerate(leaf):
            path = leaf[:d]; p = (player0 if actor(path) == 0 else player1)[path]
            reach *= p if action else 1-p
        values.append(reach*utilities[leaf])
    return math.fsum(values)


def mixed_payoff(player0, weights0, player1, weights1, utilities):
    return math.fsum(w0*w1*payoff(m0, m1, utilities)
        for m0, w0 in zip(player0, weights0) for m1, w1 in zip(player1, weights1))/(sum(weights0)*sum(weights1))


def main():
    started = time.monotonic(); error = 0.; zero = 0; gains = 0
    for seed in range(128):
        rng = random.Random(seed)
        shared = [complete_policy(rng) for _ in range(2)]
        old, new = [*shared, complete_policy(rng)], [*shared, complete_policy(rng)]
        opponent = [complete_policy(rng) for _ in range(3)]
        wa, wb, wo = [1, 2, 3], [2, 3, 5], [4, 1, 2]
        utilities = {leaf: rng.uniform(-5, 5.5) for leaf in LEAVES}
        aa, za = average(old, wa); ab, zb = average(new, wb); op, zo = average(opponent, wo)
        zero += za+zb+zo
        limits = bound([identity(m) for m in old], wa, [identity(m) for m in new], wb,
                       payoff_lower=-5, payoff_upper=5.5)
        for player in (0, 1):
            a = payoff(aa, op, utilities) if player == 0 else payoff(op, aa, utilities)
            b = payoff(ab, op, utilities) if player == 0 else payoff(op, ab, utilities)
            wanted_a = mixed_payoff(old, wa, opponent, wo, utilities) if player == 0 else mixed_payoff(opponent, wo, old, wa, utilities)
            wanted_b = mixed_payoff(new, wb, opponent, wo, utilities) if player == 0 else mixed_payoff(opponent, wo, new, wb, utilities)
            error = max(error, abs(a-wanted_a), abs(b-wanted_b))
            assert abs(b-a) <= limits['absolute_gain_bound']+1e-12
            gains += 1
    assert error < 1e-12 and zero > 0
    ids = [hashlib.sha256(str(i).encode()).hexdigest() for i in range(81)]
    example = bound(ids[:80], list(range(1, 81)), [*ids[:79], ids[80]], list(range(1, 81)),
                    payoff_lower=-200, payoff_upper=200.5)
    assert (example['changed_mass_numerator'], example['changed_mass_denominator']) == (2, 81)
    assert (example['absolute_gain_numerator'], example['absolute_gain_denominator']) == (89, 9)
    identical = bound(ids[:2], [1, 2], ids[:2], [2, 4], payoff_lower=-5, payoff_upper=5)
    assert identical['absolute_gain_bound'] == 0
    split = bound([ids[0], ids[0], ids[1]], [1, 2, 3], ids[:2], [1, 1], payoff_lower=-5, payoff_upper=5)
    assert split['absolute_gain_bound'] == 0
    disjoint = bound(ids[:1], [1], ids[1:2], [1], payoff_lower=-5, payoff_upper=5)
    assert disjoint['absolute_gain_bound'] >= 10
    rejected = 0
    for invalid in ([], [0], [-1], [True], [1.], [1, 2]):
        try: bound(ids[:1], invalid, ids[1:2], [1], payoff_lower=-5, payoff_upper=5)
        except ValueError: rejected += 1
        else: raise AssertionError('Invalid weights accepted')
    assert rejected == 6
    result = dict(passed=True, fixed_seed_trees=128, paired_gains_checked=gains,
        unreachable_rows_checked=zero, maximum_behavioral_vs_exhaustive_mixture_error=error,
        rejected_invalid_weight_cases=rejected, pilot_structural_example=example,
        source_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in
                      (Path(__file__), Path(__file__).with_name('paired_policy_mixture_bound_v1.py'))},
        seconds=time.monotonic()-started, new_poker_deals=0, gpu_used=False,
        current_pilot_intervals_modified=False,
        scope='Algebra and perfect-recall binary toy trees; no new qualification of native poker or neural inference.')
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
