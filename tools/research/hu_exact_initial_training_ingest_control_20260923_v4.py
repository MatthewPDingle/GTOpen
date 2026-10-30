"""CPU-only ingestion control on immutable old native traces, not new training."""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
import copy
import json
import math
import time
from pathlib import Path
import numpy as np
import psutil
from later_average_support_v1 import OUT, read, load_complete_cache
from sampled_physical_root_evaluation_v1 import ROOT, sha, save, hand_class
from sampled_physical_reservoir_v1 import PhysicalReservoir
from sampled_allin_protocol_v3 import AllinCache, ingest as original_ingest
from exact_initial_training_ingest_v2 import InitialTargets, ingest, digest
from reboot_research_idle_v1 import idle

PREFIX = 'exact-initial-training-ingest-control-v4'
GENERATIONS = (0, 25, 51, 77)
CAPACITY = 97  # Deliberately fill/replace repeatedly to exercise selection RNGs.


def state_digest(reservoirs):
    import hashlib
    h = hashlib.sha256()
    for r in reservoirs:
        h.update(str(r.seen).encode())
        h.update(json.dumps(r.rng.bit_generator.state, sort_keys=True).encode())
        for name in ('keys', 'active', 'arity', 'values', 'iterations'):
            h.update(getattr(r, name).tobytes())
    return h.hexdigest()


def main():
    started = time.monotonic()
    def guard():
        assert idle() and psutil.virtual_memory().available > 20_000_000_000
        assert time.monotonic()-started < 600
    guard()
    rp = OUT/f'{PREFIX}-registration.json'
    assert not rp.exists(), 'Preserve previous attempts'
    inputs = {}
    def admit(path):
        path = Path(path); inputs[str(path)] = sha(path); return read(path)
    old_rp = OUT/'initial-allin-trace-diagnostic-v1-registration.json'
    old_reg, old_result = admit(old_rp), admit(OUT/'initial-allin-trace-diagnostic-v1-result.json')
    assert old_result['passed'] and old_result['registration_sha256'] == sha(old_rp)
    for path, h in old_reg['inputs'].items():
        assert sha(path) == h, path
        inputs[path] = h
    generations = read(next(p for p in inputs if Path(p).name == 'visible_302-generation-policies.json'))['policies']
    catalog = read(next(p for p in inputs if Path(p).name == 'native-preflop-catalog.json'))['native_observations']
    source = (OUT/'bb-context-candidate.json').read_text()
    matrix_path = OUT/'preflop-allin-matrix-control-v1-matrix.json'
    matrix_source = matrix_path.read_text()
    matrix = admit(matrix_path)
    batches = sorted({Path(p).parent for p in inputs if Path(p).name == 'updates.json'})
    assert len(batches) == 32
    complete_cache = load_complete_cache()
    historical_review = OUT/'sampled-physical-allin-training-cache-v1-independent-review.json'
    historical = admit(historical_review)
    cache = AllinCache.from_review(historical_review)
    inputs[historical['cache_artifact']] = cache.sha256
    assert all(complete_cache.rows[k] == row for k,row in cache.rows.items())
    for name in ('complete-private-allin-cache-v2-registration.json',
                 'complete-private-allin-cache-v2-result.json',
                 'complete-private-allin-cache-v2-independent-review.json'):
        admit(OUT/name)
    for path in (Path(__file__), ROOT/'tools/research/exact_initial_training_ingest_v2.py',
                 ROOT/'tools/research/sampled_allin_protocol_v3.py',
                 ROOT/'tools/research/sampled_physical_reservoir_v1.py',
                 ROOT/'tools/research/sampled_physical_preflop_table_v1.py',
                 ROOT/'tools/research/later_average_support_v1.py'):
        inputs[str(path)] = sha(path)
    save(rp, dict(inputs=inputs, generations=list(GENERATIONS), batches=len(batches), capacity=CAPACITY,
        maximum_seconds=600, exact_cache_sha256=cache.sha256,
        scope='Independent action-value recentering and complete insertion/RNG parity on old immutable traces. CPU only; no new training, GPU or active candidate access.',
        production_modified=False, gpu_used=False))
    try:
        base = [PhysicalReservoir(CAPACITY, p, 290701+p, source) for p in range(2)]
        corrected, oracle = copy.deepcopy(base), copy.deepcopy(base)
        maximum = 0.; witnesses = 0; counts_total = [0, 0]; per_generation = {}
        rejection_cases = []
        for g in GENERATIONS:
            root = np.zeros((169, 4)); calls = np.zeros(169)
            for item, row in zip(catalog, generations[g]):
                if item['player'] == 0: root[item['hand_class']] = row
                else: calls[item['hand_class']] = row[1]
            targets = InitialTargets(matrix_source, source, root, calls,
                matrix_sha256=sha(matrix_path), generation=g)
            # Independent scalar summation, not AllinMatrix.evaluate/bb_correction.
            exact_jam = [math.fsum(m*(1-c)*matrix['bb_uncontested']+b*c for m,b,c in
                zip(matrix['class_mass'][h], matrix['bb_showdown_entries'][h], calls)) /
                math.fsum(matrix['class_mass'][h]) for h in range(169)]
            gen_witnesses = 0
            for folder in batches:
                if int(folder.parent.name.split('-')[1])-1 != g: continue
                guard()
                queries, updates, policies = [read(folder/f'{name}.json') for name in ('queries','updates','policies')]
                raw_hashes = [digest(x) for x in (queries, updates, policies)]
                expected_counts = original_ingest(queries, updates, base, g+1, cache)
                counts, audit = ingest(queries, updates, policies, corrected, g+1, cache, targets, guard=guard)
                assert counts == expected_counts
                by_record = {w['record']:w for w in audit['bb_root_corrections']}
                for index, (qi, player, tag, v) in enumerate(updates['records']):
                    if tag <= 0: continue
                    o = queries['observations'][qi]
                    expected = np.asarray(v, dtype=float)
                    if index in by_record:
                        w = by_record[index]; h = w['hand_class']
                        # Reconstruct native Qa from the separately recorded root value.
                        q = expected + updates['roots'][2*w['deal']][2]
                        q[3] = exact_jam[h]
                        probability = np.asarray(policies['policies'][qi]['probabilities'])
                        mean = math.fsum(float(a*b) for a,b in zip(q, probability))
                        expected = q-mean
                        maximum = max(maximum, float(np.max(abs(expected-w['advantages']))),
                                      abs(mean-w['derived_root_value']))
                        assert np.max(abs(expected-w['advantages'])) < 1e-9
                        witnesses += 1; gen_witnesses += 1
                    oracle[player].add(o, expected, g+1)
                for p in range(2):
                    a,b,c = base[p],corrected[p],oracle[p]
                    assert a.seen == b.seen == c.seen
                    assert a.rng.bit_generator.state == b.rng.bit_generator.state == c.rng.bit_generator.state
                    for name in ('keys','active','arity','iterations'):
                        assert np.array_equal(getattr(a,name),getattr(b,name))
                        assert np.array_equal(getattr(b,name),getattr(c,name))
                    assert np.max(abs(b.values-c.values)) < 1e-9
                    untouched = np.ones(b.size, dtype=bool) if p == 1 else b.keys[:b.size,0] != 1
                    assert np.array_equal(a.values[:a.size][untouched], b.values[:b.size][untouched])
                    counts_total[p] += counts[p]
                assert raw_hashes == [digest(x) for x in (queries, updates, policies)]
                if not rejection_cases:
                    def reject(label, q=queries, u=updates, pol=policies, it=g+1, t=targets):
                        before = state_digest(corrected)
                        try: ingest(q,u,pol,corrected,it,cache,t)
                        except (ValueError, KeyError, TypeError, IndexError): pass
                        else: raise AssertionError('Did not reject '+label)
                        assert before == state_digest(corrected), label
                        rejection_cases.append(label)
                    bad = copy.deepcopy(updates); bad['roots'][-2][2] += 1
                    reject('late native root value mismatch', u=bad)
                    bad = copy.deepcopy(updates); bad['records'][-1][3][0] = float('nan')
                    reject('late nonfinite native record', u=bad)
                    bad = copy.deepcopy(updates); bad['roots'][-1][0] += 1
                    reject('late native root ordering mismatch', u=bad)
                    bad = copy.deepcopy(policies); bad['policies'][0]['probabilities'] = [.1,.2,.3,.4]
                    reject('current played initial policy mismatch', pol=bad)
                    reject('wrong played generation', it=g+2)
                    bad = copy.deepcopy(updates)
                    negative = next(r for r in reversed(bad['records']) if r[2] < 0)
                    chosen = int(np.argmin(negative[3][:abs(negative[2])]))
                    negative[3][:] = [1. if i == chosen else 0. for i in range(4)]
                    reject('opponent record policy mismatch', u=bad)
                    try: InitialTargets(matrix_source,source,root,calls,matrix_sha256='0'*64,generation=g)
                    except ValueError: rejection_cases.append('matrix identity mismatch')
                    else: raise AssertionError('Wrong matrix accepted')
            assert gen_witnesses == 512
            per_generation[str(g)] = gen_witnesses
        assert witnesses == 2048 and len(rejection_cases) == 7
        for path,h in inputs.items(): assert sha(path) == h, path
        guard()
        result = dict(passed=True, registration_sha256=sha(rp), seconds=time.monotonic()-started,
            bb_root_witnesses=witnesses, roots_by_generation=per_generation,
            insertion_counts=counts_total, reservoir_capacity=CAPACITY,
            maximum_independent_reconstruction_error=maximum, rejected_without_mutation=rejection_cases,
            original_inputs_unchanged=True, nonroot_and_btn_targets_unchanged=True,
            selection_rngs_and_metadata_identical=True, gpu_used=False, production_modified=False,
            limitation='Arithmetic and ingestion control only. No fresh training, CUDA runtime qualification or poker-strength claim.')
        save(OUT/f'{PREFIX}-result.json', result)
        print(json.dumps(result))
    except BaseException as exc:
        save(OUT/f'{PREFIX}-result.json', dict(passed=False, registration_sha256=sha(rp),
            seconds=time.monotonic()-started, error=repr(exc), production_modified=False, gpu_used=False))
        raise


if __name__ == '__main__': main()
