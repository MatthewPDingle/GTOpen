"""Exhaustive public-flop partition qualification, with synthetic parameters.

No scientific deals, native calls, fitting, GPU or actual diagnostic admission.
The public geometry check cannot establish label or player-model accuracy.
"""
import copy
import hashlib
import itertools
import json
from pathlib import Path
import time
import traceback
import psutil
import stack_context_flop_partition_v1 as partition

ROOT = Path('T:/Dev/GTOpen')
OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
NAME = 'stack-context-flop-partition-check-v1'


def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, sort_keys=True, allow_nan=False);stream.write('\n')


def main():
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    attempt, result, failure = (OUT/(NAME+suffix+'.json') for suffix in ('-attempt', '-result', '-failure'))
    assert not any(p.exists() for p in (attempt, result, failure))
    inputs = {str(path):sha(path) for path in (Path(__file__).resolve(), Path(partition.__file__).resolve(),
        OUT/'STACK-CONTEXT-PREDICTION-DIAGNOSTIC-DESIGN.md')}
    save(attempt, dict(inputs=inputs, qualification_only=True, no_scientific_sampling=True,
        synthetic_partition_namespace=True, cpu_priority='below-normal', cpu_workers=1))
    began = time.monotonic(); negative = []
    def reject(label, function):
        try:function()
        except (ValueError, TypeError, KeyError):negative.append(label)
        else:raise AssertionError('Accepted '+label)
    try:
        cfg = partition.config(namespace='qualification-only-not-an-experiment', buckets=16, test_buckets=[1, 5, 9, 13])
        catalogue = partition.population(cfg)
        assert catalogue['canonical_orbit_multiplicities'] == {4:299, 12:1170, 24:286}
        lookup = {}
        for physical in itertools.combinations(range(52), 3):
            lookup[physical] = partition.canonical_flop(physical)
        assert len(lookup) == 22100
        bycanonical = {}
        for physical, key in lookup.items():bycanonical.setdefault(key, []).append(physical)
        # The independently closed suit orbits must exactly match every physical
        # catalogue member and its multiplicity, not just a handful of examples.
        tested = 0; descendants = 0
        for row in catalogue['rows']:
            key = tuple(row['canonical_flop']);orbit = set()
            for suits in itertools.permutations(range(4)):
                physical = tuple(sorted(4*(card//4)+suits[card%4] for card in key))
                assert lookup[physical] == key
                orbit.add(physical);tested += 1
            assert orbit == set(bycanonical[key]) and len(orbit) == row['physical_flops']
            for order in itertools.permutations(key):assert partition.canonical_flop(order) == key
            available = [card for card in range(52) if card not in key]
            for turn, river in ((available[0], available[-1]), (available[-1], available[0])):
                for phase, board in ((1, list(key)), (2, [*key, turn]), (3, [*key, turn, river])):
                    assert partition.visible_partition(board, phase=phase, document=cfg) == row['split']
                    descendants += 1
        assert tested == 1755*24 and descendants == 1755*6
        # Equal weighting over canonical flop classes would distort full-deck
        # probabilities. Check both conditional denominators against actual
        # physical flop counts and all orbit multiplicities.
        for split in ('fit', 'test'):
            expected = sum(len(bycanonical[tuple(r['canonical_flop'])]) for r in catalogue['rows'] if r['split'] == split)
            assert catalogue['physical_population_by_split'][split] == expected
            assert abs(sum(r['physical_flops']/expected for r in catalogue['rows'] if r['split'] == split)-1) < 1e-12
        assert cfg == partition.config(namespace=cfg['namespace'], buckets=16, test_buckets=[13, 9, 5, 1])
        damaged = copy.deepcopy(cfg);damaged['namespace'] = 'changed'
        reject('configuration substitution', lambda:partition.validate(damaged))
        damaged = copy.deepcopy(cfg);damaged['future_cards_used'] = True
        reject('future-card split', lambda:partition.validate(damaged))
        damaged = copy.deepcopy(cfg);damaged['unregistered_rule'] = True
        reject('unknown configuration field', lambda:partition.validate(damaged))
        for label, cards in (('missing flop card', [0, 4]), ('future card in flop', [0, 4, 8, 12]),
            ('duplicate physical card', [0, 0, 4]), ('invalid card', [0, 4, 52]),
            ('floating card', [0, 4., 8]), ('boolean card', [True, 4, 8])):
            reject(label, lambda cards=cards:partition.canonical_flop(cards))
        reject('hidden flop as preflop holdout', lambda:partition.visible_partition([0, 4, 8], phase=0, document=cfg))
        reject('wrong public street length', lambda:partition.visible_partition([0, 4, 8, 12, 16], phase=2, document=cfg))
        reject('boolean street', lambda:partition.visible_partition([0, 4, 8], phase=True, document=cfg))
        reject('noncanonical assignment', lambda:partition.assignment([8, 4, 0], cfg))
        reject('duplicate test bucket', lambda:partition.config(namespace='x', buckets=4, test_buckets=[1, 1]))
        reject('test-only population', lambda:partition.config(namespace='x', buckets=2, test_buckets=[0, 1]))
        reject('fit-only population', lambda:partition.config(namespace='x', buckets=2, test_buckets=[]))
        reject('implicit namespace', lambda:partition.config(namespace='', buckets=4, test_buckets=[1]))
        for path, identity in inputs.items():assert sha(path) == identity
        answer = dict(complete=True, passed=True, seconds=time.monotonic()-began, inputs=inputs,
            exhaustive_physical_flops=22100, canonical_flops=1755, closed_suit_maps=tested,
            all_card_orders_checked=True, visible_street_descendants_checked=descendants,
            orbit_multiplicities=catalogue['canonical_orbit_multiplicities'],
            physical_population_by_split=catalogue['physical_population_by_split'],
            conditional_physical_weights_verified=True, catalogue_sha256=catalogue['sha256'],
            negative_cases=negative, synthetic_partition_configuration=True,
            actual_diagnostic_split_registered=False, actual_diagnostic_complete=False,
            scientific_deals=0, native_calls=0, fits=0, gpu=False, production_modified=False)
        save(result, answer)
        print(json.dumps(dict(passed=True, seconds=answer['seconds'], physical_flops=22100,
            canonical_flops=1755, negative_cases=len(negative), scientific_work=False)), flush=True)
    except BaseException as error:
        save(failure, dict(complete=False, passed=False, error=repr(error), traceback=traceback.format_exc(),
            preserve_evidence=True, automatic_retry_allowed=False));raise


if __name__ == '__main__':main()
