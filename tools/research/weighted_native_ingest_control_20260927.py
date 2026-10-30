"""Exercise weighted ingestion on real native traversals, without fitting a model."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
import argparse
import copy
import json
from pathlib import Path
import subprocess
import time
import numpy as np
import psutil
from later_average_support_v1 import OUT, read, load_complete_cache
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from class_stratified_physical_deals_v1 import ClassStratifiedDeals
from weighted_deal_binding_v1 import DealWeightGeneration
from weighted_physical_reservoir_v1 import WeightedPhysicalReservoir, ARRAYS
from sampled_physical_reservoir_v1 import PhysicalReservoir
from sampled_allin_protocol_v3 import policy_document
from exact_initial_training_ingest_v2 import InitialTargets, digest
from later_action_training_ingest_v1 import ingest as old_ingest
from weighted_later_action_ingest_v1 import ingest

PREFIX = 'weighted-native-ingest-control-v1'


def fingerprint(reservoirs):
    import hashlib
    h = hashlib.sha256()
    for r in reservoirs:
        h.update(str(r.seen).encode()); h.update(json.dumps(r.rng.bit_generator.state, sort_keys=True).encode())
        for name in ARRAYS: h.update(getattr(r,name).tobytes())
    return h.hexdigest()


def main(publish=False):
    started = time.monotonic()
    def guard():
        if time.monotonic()-started > 180 or psutil.virtual_memory().available < 20_000_000_000:
            raise RuntimeError('Time or host memory limit reached')
    guard(); assert psutil.cpu_percent(interval=1) < 70
    cp = OUT/'bb-context-candidate.json'; source = cp.read_text()
    mp = OUT/'preflop-allin-matrix-control-v1-matrix.json'; matrix_source = mp.read_text()
    executable = ROOT/'target/release/examples/hu_sampled_allin_bridge_v3.exe'
    trace_executable = ROOT/'target/release/examples/hu_sampled_action_trace_v2.exe'
    paths = [cp, mp, executable, trace_executable, *Path(__file__).parent.glob('*.py'),
        OUT/'WEIGHTED-NATIVE-INGEST-CONTROL-PLAN.md']
    inputs = {str(p):sha(p) for p in paths}
    store = Path('T:/GTOpen-research')/(PREFIX if publish else PREFIX+'-dev-'+str(time.time_ns()))
    store.mkdir(exist_ok=False)
    registration = OUT/f'{PREFIX}-registration.json'
    if publish:
        save(registration, dict(inputs=inputs, store=str(store), full_generation=512, native_slice=32,
            capacity=97, seed=9274001, maximum_seconds=180, maximum_bytes=64*1024**2,
            trained_model=False, production_modified=False))
    cache = load_complete_cache(); guard()
    sample = ClassStratifiedDeals(source, seed=9274001).sample(512)
    generation = DealWeightGeneration(sample, source)
    save(store/'source-generation.json', sample)
    batch = cache.batch(dict(format=2, batch_id=PREFIX, query_limit=500000, seed=9274002,
        deals=sample['deals'][:32]))
    bp = store/'batch.json'; qp = store/'queries.json'; pp = store/'policies.json'
    up = store/'updates.json'; tp = store/'trace.json'; save(bp,batch)
    def invoke(exe, args):
        guard()
        p = subprocess.run([str(exe), *map(str,args)], capture_output=True, text=True,
            timeout=min(90, max(1, 180-(time.monotonic()-started))), creationflags=subprocess.CREATE_NO_WINDOW)
        if p.returncode: raise RuntimeError(p.stderr[-2000:])
        guard()
    invoke(executable, ['queries', cp, bp, '-', qp]); queries = read(qp)
    probabilities = np.array([[1./o['n'] if a < o['n'] else 0. for a in range(4)] for o in queries['observations']])
    policy = policy_document(queries, probabilities); save(pp, policy)
    invoke(executable, ['verify', cp, bp, pp, up]); updates = read(up)
    invoke(trace_executable, [cp, bp, pp, tp]); trace = read(tp)
    targets = InitialTargets(matrix_source, source, np.full((169,4),.25), np.full(169,.5),
        matrix_sha256=sha(mp), generation=0)
    weighted = [WeightedPhysicalReservoir(97,p,9274100+p,source) for p in (0,1)]
    oracle = copy.deepcopy(weighted)
    plain = [PhysicalReservoir(97,p,9274100+p,source) for p in (0,1)]
    immutable = [digest(x) for x in (queries,updates,policy,trace)]
    counts, ia, la, wa = ingest(queries,updates,policy,weighted,1,cache,targets,trace,
        generation=generation,start=0,guard=guard)
    oc, oi, ol = old_ingest(queries,updates,policy,plain,1,cache,targets,trace,guard=guard)
    assert counts == oc and ia == oi and la == ol
    # Independent source mapping comes from the native trace's explicit deal
    # field, rather than the new adapter's traversal-header mapping.
    target_map = {r['record']:r for r in trace['conditional_targets']}
    initial_map = {r['record']:r['advantages'] for r in ia['bb_root_corrections']}
    phases = set(); visited_deals = set()
    for index,(qi,player,n,values) in enumerate(updates['records']):
        if n <= 0: continue
        o = queries['observations'][qi]; t = target_map[index]
        assert t['query'] == qi and t['updater'] == player
        value = t['advantages'] if o['phase'] else initial_map.get(index, values)
        oracle[player].add(o,value,1,deal_weight=sample['deal_weights'][t['deal']])
        phases.add(o['phase']); visited_deals.add(t['deal'])
    assert phases == {0,1,2,3} and visited_deals == set(range(32))
    error = 0.
    for w,o,p in zip(weighted,oracle,plain):
        assert w.seen == o.seen == p.seen and w.seen > w.capacity
        assert w.rng.bit_generator.state == o.rng.bit_generator.state == p.rng.bit_generator.state
        for name in ('keys','active','arity','iterations'):
            assert np.array_equal(getattr(w,name),getattr(o,name)) and np.array_equal(getattr(w,name),getattr(p,name))
        assert np.array_equal(w.values,p.values) and np.array_equal(w.deal_weights,o.deal_weights)
        error = max(error,float(np.max(abs(w.values-o.values))))
    assert error < 1e-10
    assert immutable == [digest(x) for x in (queries,updates,policy,trace)]
    rejected = []
    def reject(label, q=queries, t=trace, offset=0, rs=weighted):
        before = fingerprint(weighted)
        try: ingest(q,updates,policy,rs,1,cache,targets,t,generation=generation,start=offset,guard=guard)
        except (ValueError,TypeError,KeyError): pass
        else: raise AssertionError('Invalid input accepted: '+label)
        assert before == fingerprint(weighted); rejected.append(label)
    reject('wrong source offset',offset=32)
    reject('unweighted reservoirs',rs=plain)
    bad = copy.deepcopy(queries); b = json.loads(bad['batch_source']); b['deals'].reverse(); bad['batch_source'] = json.dumps(b)
    reject('reordered native physical deals',q=bad)
    bad = copy.deepcopy(trace); bad['conditional_targets'][-1]['deal'] += 1
    reject('late target moved between deals',t=bad)
    bad = copy.deepcopy(trace); bad['conditional_targets'][-1]['advantages'][0] += 1
    reject('late target changed',t=bad)
    save(store/'weight-audit.json',wa)
    for p,h in inputs.items(): assert sha(p) == h,p
    artifacts = {str(p):sha(p) for p in store.iterdir() if p.is_file()}
    bytes_written = sum(Path(p).stat().st_size for p in artifacts)
    assert bytes_written < 64*1024**2
    result = dict(passed=True, native_deals=32, visits=counts, phases=sorted(phases),
        weights_match_native_trace_exactly=True, unchanged_targets_and_reservoir_rng=True,
        maximum_independent_target_error=error, negative_controls=rejected,
        artifacts=artifacts, bytes_written=bytes_written, seconds=time.monotonic()-started,
        full_training_qualified=False, trained_model=False, poker_strength_claim=False, production_modified=False)
    if publish:
        result['registration_sha256'] = sha(registration); save(OUT/f'{PREFIX}-result.json',result)
    print(json.dumps(result),flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--publish',action='store_true')
    main(parser.parse_args().publish)
