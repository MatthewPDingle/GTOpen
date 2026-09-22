"""Qualify bounded per-visit replay storage using the physical bridge fixture."""
import copy
import hashlib
import itertools
import json
from pathlib import Path
import time

import numpy as np

from loopback_research_validation import idle
from sampled_physical_reservoir_v1 import PhysicalReservoir, ingest

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'sampled-physical-reservoir-v1'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(p, value):
    with p.open('x', encoding='utf-8', newline='\n') as f:
        f.write(json.dumps(value, indent=2)+'\n')


def equal(a, b):
    assert a.summary() == b.summary()
    assert a.rng.bit_generator.state == b.rng.bit_generator.state
    for name in ('keys', 'active', 'arity', 'values', 'iterations'):
        assert np.array_equal(getattr(a, name), getattr(b, name)), name


def main():
    assert idle()
    paths = [Path(__file__), ROOT/'tools/research/sampled_physical_reservoir_v1.py',
             ROOT/'tools/research/loopback_research_validation.py'] + [OUT/p for p in
             ('sampled-batch-bridge-v2-queries.json', 'sampled-batch-bridge-v2-updates.json',
              'sampled-batch-bridge-v2-result.json', 'sampled-batch-bridge-v2-review.json')]
    result_source = json.loads(paths[-2].read_text())
    assert result_source['passed'] and json.loads(paths[-1].read_text())['passed']
    for p in paths[3:5]:
        assert result_source['artifacts'][p.relative_to(ROOT).as_posix()] == sha(p)
    frozen = {p.relative_to(ROOT).as_posix(): sha(p) for p in paths}
    registration = OUT/(PREFIX+'-registration.json')
    save(registration, dict(inputs=frozen, maximum_seconds=120, capacity=17, seeds=[2101, 2102],
        algorithm='Algorithm R: uniform reservoir of actual positive-tag visits; equal ordinary-CFR iteration weights.',
        checks=['independent slot oracle', 'split versus whole ingestion', 'save/resume RNG and rows',
                'duplicate visits retained', 'late invalid record leaves state unchanged',
                'exhaustive 5-visit capacity-2 inclusion law', 'fixed payload after repeated ingestion'],
        scope='Physical replay-storage correctness only; no training, no GPU work, no poker accuracy claim.',
        production_modified=False))
    began = time.monotonic()
    queries, updates = [json.loads(p.read_text()) for p in paths[3:5]]
    context = queries['context_source']
    def pair(capacity=17):
        return [PhysicalReservoir(capacity, p, 2101+p, context) for p in (0, 1)]
    whole, split = pair(), pair()
    counts = ingest(queries, updates, whole, 1)
    for start in range(0, len(updates['records']), 37):
        chunk = dict(updates, records=updates['records'][start:start+37])
        ingest(queries, chunk, split, 1)
    for a, b in zip(whole, split): equal(a, b)
    # Independent simple Algorithm-R oracle: retained source indices plus RNG state.
    source_records = []
    for player in (0, 1):
        records = [r for r in updates['records'] if r[1] == player and r[2] > 0]
        source_records.append(records)
        rng = np.random.default_rng(2101+player); retained = list(range(min(17, len(records))))
        for j in range(17, len(records)):
            slot = int(rng.integers(j+1))
            if slot < 17: retained[slot] = j
        r = whole[player]
        assert len(records) == r.seen and rng.bit_generator.state == r.rng.bit_generator.state
        for slot, j in enumerate(retained):
            index, updater, tag, values = records[j]; o = queries['observations'][index]
            assert r.keys[slot].tolist() == [int(o['hi']), int(o['lo'])]
            assert r.active[slot].tolist() == sorted(o['active_features'])
            assert r.arity[slot] == tag and r.values[slot].tolist() == values and r.iterations[slot] == 1
    # Saved random state must permit exact continuation, not merely equal distributions.
    checkpoint_dir = ROOT/'target/research-sampled'/PREFIX
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    checkpoints = [checkpoint_dir/f'player{p}.npz' for p in (0, 1)]
    for r, path in zip(whole, checkpoints): r.save(path)
    resumed = [PhysicalReservoir.load(path, context) for path in checkpoints]
    for iteration in range(2, 8):
        assert idle() and time.monotonic()-began < 120
        ingest(queries, updates, whole, iteration)
        ingest(queries, updates, resumed, iteration)
    for a, b in zip(whole, resumed): equal(a, b)
    # A large enough buffer retains every repeated visit, including identical keys/targets.
    duplicates = pair(4096)
    for iteration in (1, 2, 3): ingest(queries, updates, duplicates, iteration)
    for player, r in enumerate(duplicates):
        n = counts[player]
        assert r.size == 3*n and np.array_equal(r.keys[:n], r.keys[n:2*n])
        assert np.array_equal(r.values[:n], r.values[2*n:3*n])
        assert r.iterations[:r.size].tolist() == [i for i in (1, 2, 3) for _ in range(n)]
    rejected = []
    for variant in range(6):
        bad = copy.deepcopy(updates)
        if variant == 0: bad['batch_id'] = 'stale'
        elif variant == 1: bad['policies_frozen_across_updater_passes'] = False
        elif variant == 2: bad['records'][-1][3][0] = float('nan')
        elif variant == 3: bad['records'][-1][1] = 2
        elif variant == 4: bad['records'][-1][2] = 0
        else: bad['records'][-1][0] = len(queries['observations'])
        try:
            ingest(queries, bad, whole, 8)
        except ValueError:
            rejected.append(variant)
        else: raise AssertionError('Invalid transport accepted')
        for a, b in zip(whole, resumed): equal(a, b)
    try: PhysicalReservoir.load(checkpoints[0], context+' ')
    except ValueError: rejected.append('stale checkpoint context')
    else: raise AssertionError('Wrong checkpoint context accepted')
    # Enumerate all 3*4*5 equally likely RNG sequences. Every 2-of-5 subset must
    # appear six times. This proves the small inclusion law without a noisy test.
    o = queries['observations'][source_records[0][0][0]]
    class Draws:
        def __init__(self, sequence): self.sequence = iter(sequence)
        def integers(self, high):
            value = next(self.sequence); assert 0 <= value < high; return value
    subsets = {}
    for sequence in itertools.product(range(3), range(4), range(5)):
        r = PhysicalReservoir(2, 0, 0, context); r.rng = Draws(sequence)
        for iteration in range(1, 6): r.add(o, [0, 0, 0, 0], iteration)
        key = tuple(sorted(r.iterations.tolist())); subsets[key] = subsets.get(key, 0)+1
    assert len(subsets) == 10 and set(subsets.values()) == {6}
    for name, expected in frozen.items(): assert sha(ROOT/name) == expected, name
    result = dict(passed=True, inputs_verified=len(frozen), advantage_visits_by_player=counts,
        streaming_summaries=[r.summary() for r in whole], exact_resume=True,
        full_vs_split_identical=True, independent_slot_oracle_identical=True,
        exhaustive_equal_probability_subsets=len(subsets), outcomes_per_subset=6,
        rejected_inputs=len(rejected), rejection_preserved_rows_counters_and_rng=True,
        duplicate_visits_preserved=True, seconds=time.monotonic()-began,
        checkpoint_artifacts={p.relative_to(ROOT).as_posix(): sha(p) for p in checkpoints},
        registration_sha256=sha(registration), physical_poker_convergence_qualified=False,
        production_modified=False)
    save(OUT/(PREFIX+'-result.json'), result)
    print(json.dumps(result))


if __name__ == '__main__': main()
