"""Independent saved-capture/transport readback for the throughput experiment.

Uses the established scalar native-artifact verifier, not the benchmark's
observation packer or comparator. Does not repeat inference or native poker.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import argparse
import concurrent.futures
import hashlib
import json
import multiprocessing
from pathlib import Path
import statistics
import time
import numpy as np
import psutil
from hu_showdown_complete_evaluation_review_20260926 import verify_batch
from later_average_support_v1 import OUT, read, load_complete_cache
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from bounded_parallel_evaluation_archive_v2 import production_available
from weighted_complete_control_review_20260927 import verify_identities

PREFIX = 'weighted-gpu-throughput-control-v1'
REVIEW = 'weighted-gpu-throughput-readback-v1'
CASES = ('deepcopy32', 'deepcopy64', 'snapshot32', 'snapshot64')
STATE = None


def index_rows(query, policies, reaches):
    """Independent scalar row identities with native-key own-history links."""
    obs = query['observations']; keys = [(o['hi'], o['lo']) for o in obs]
    assert len(keys) == len(set(keys)) and keys
    assert policies.dtype == reaches.dtype == np.dtype('float64')
    assert policies.shape == (4, len(obs), 4) and reaches.shape == (4, len(obs))
    assert np.isfinite(policies).all() and np.isfinite(reaches).all() and (reaches >= 0).all()
    output = {}
    for i, row in enumerate(obs):
        assert set(row) == {'hi', 'lo', 'actor', 'phase', 'n', 'active_features', 'own_history'}
        links = []
        for prior, action, n in row['own_history']:
            assert type(prior) is int and 0 <= prior < len(obs)
            assert n == obs[prior]['n'] and type(action) is int and 0 <= action < n
            assert obs[prior]['actor'] == row['actor']
            links.append((keys[prior], action, n))
        identity = (row['actor'], row['phase'], row['n'], tuple(row['active_features']), tuple(links))
        assert (policies[:, i] >= 0).all() and (policies[:, i, row['n']:] == 0).all()
        assert np.max(abs(policies[:, i].sum(axis=1) - 1)) < 1e-10
        output[keys[i]] = (identity, policies[:, i].copy(), reaches[:, i].copy())
    return output


def compare_rows(reference, candidate):
    assert reference.keys() == candidate.keys(), 'Native key set changed'
    policy = reach = 0.
    for key, (identity, probabilities, support) in reference.items():
        actual, p, r = candidate[key]
        assert actual == identity, 'Observation or prior-action history changed'
        policy = max(policy, float(np.max(abs(p-probabilities))))
        reach = max(reach, float(np.max(abs(r-support))))
    assert policy <= 1e-10 and reach <= 1e-10, 'Policy or own reach changed'
    return policy, reach


class DiskReader:
    def __init__(self, root): self.root = Path(root).resolve()

    def read_bytes(self, path):
        path = Path(path)
        assert path.resolve() == path and path.is_relative_to(self.root)
        assert path.is_file() and path.stat().st_size <= 128*1024**2
        return path.read_bytes()


def read_run(record, store, expected_batches, cache, *, scalar=True):
    folder = store / (record['phase'] + '-' + record['case'])
    assert read(folder / 'comparison.json') == record
    parts = expected_batches if record['batch_size'] == 32 else [dict(format=2,
        batch_id='weighted-gpu-throughput-retained-64-v1', seed=0, query_limit=100000,
        deals=expected_batches[0]['deals']+expected_batches[1]['deals'])]
    expected_files = {str(folder/f'batch-{i}'/name) for i in range(len(parts)) for name in
        ('query-batch.json', 'conditional-batch.json', 'queries.json', 'profiles.json',
         'native.json', 'residuals.json', 'summary.json', 'bank-capture.npz')}
    assert set(record['artifacts']) == expected_files
    for path, digest in record['artifacts'].items(): assert sha(path)==digest, path
    rows = {}; values = []; source = (OUT/'bb-context-candidate.json').read_text()
    repeated_policy = repeated_reach = 0.
    for i, expected in enumerate(parts):
        part = folder/f'batch-{i}'; q = read(part/'queries.json'); summary = read(part/'summary.json')
        assert q['context_source'] == source
        if scalar:
            _, count, digest = verify_batch(DiskReader(store), part, expected, source, cache)
            assert count == len(q['observations']) and digest == sha(part/'summary.json')
        with np.load(part/'bank-capture.npz', allow_pickle=False) as arrays:
            assert set(arrays.files) == {'policies', 'reaches'}
            policies, reaches = arrays['policies'], arrays['reaches']
        assert len(summary['coverage']) == 4
        for bank in range(4):
            assert hashlib.sha256(policies[bank].tobytes()).hexdigest()==summary['coverage'][bank]['probabilities_sha256']
            assert hashlib.sha256(reaches[bank].tobytes()).hexdigest()==summary['coverage'][bank]['support_sha256']
            assert int(np.sum(reaches[bank]==0)) == summary['coverage'][bank]['zero_reach_rows']
        incoming = index_rows(q, policies, reaches)
        shared = incoming.keys() & rows.keys()
        if shared:
            p, r = compare_rows({k: rows[k] for k in shared}, {k: incoming[k] for k in shared})
            repeated_policy = max(repeated_policy, p); repeated_reach = max(repeated_reach, r)
        for key, value in incoming.items(): rows.setdefault(key, value)
        values.extend(summary['values'])
    assert abs(record['duplicate_policy_error']-repeated_policy)<1e-12
    assert abs(record['duplicate_reach_error']-repeated_reach)<1e-12
    values = np.asarray(values); assert values.shape == (64, 2, 4, 2) and np.isfinite(values).all()
    assert record['comparison']['unique_observations'] == len(rows)
    return rows, values


def initialize(store, batches, baseline):
    global STATE
    cache = load_complete_cache()
    reference, values = read_run(baseline, Path(store), batches, cache, scalar=False)
    STATE = Path(store), batches, cache, reference, values


def check_run(record):
    assert production_available() and psutil.virtual_memory().available > 24_000_000_000
    store, batches, cache, reference, values = STATE
    rows, actual_values = read_run(record, store, batches, cache)
    p, r = compare_rows(reference, rows)
    cashflow = float(np.max(abs(values-actual_values))); assert cashflow < 1e-9
    assert abs(record['comparison']['maximum_policy_error']-p)<1e-12
    assert abs(record['comparison']['maximum_reach_error']-r)<1e-12
    assert abs(record['maximum_cashflow_error']-cashflow)<1e-12
    return dict(phase=record['phase'], case=record['case'], rows=len(rows),
                maximum_policy_error=p, maximum_reach_error=r, maximum_cashflow_error=cashflow)


def main(run=False):
    result_path = OUT/f'{PREFIX}-result.json'
    if not run:
        print(json.dumps(dict(ready=result_path.exists(), workers=4, gpu_used=False,
                              required_completed_benchmark=str(result_path), readback_started=False)))
        return
    began = time.monotonic(); last = 0.
    def guard():
        nonlocal last
        assert time.monotonic()-began < 900
        if time.monotonic()-last > 2:
            assert production_available() and psutil.virtual_memory().available > 28_000_000_000
            last = time.monotonic()
    guard(); assert psutil.cpu_percent(interval=1)<50
    rp = OUT/f'{PREFIX}-registration.json'; reg, result = read(rp), read(result_path)
    assert result['passed'] and result['registration_sha256']==sha(rp)
    assert reg['deals']==64 and reg['warmups_per_case']==1 and reg['repeats']==4
    assert reg['cases']==list(CASES)
    for path, digest in reg['inputs'].items(): guard(); assert sha(path)==digest, path
    store = Path(reg['store']); assert store == Path('S:/GTOpen-research')/PREFIX
    verify_identities(read(store/'bank-identities.json'))
    expected = [('warmup', i, CASES[i]) for i in range(4)]
    expected += [(f'repeat-{r+1}', i, CASES[(r+i)%4]) for r in range(4) for i in range(4)]
    assert [(r['phase'],r['order_position'],r['case']) for r in result['runs']] == expected
    assert reg['order']==[[CASES[(r+i)%4] for i in range(4)] for r in range(4)]
    for row in result['runs']:
        assert row['batch_size']==(32 if row['case'].endswith('32') else 64)
        assert 0 < row['seconds_per_64_deals'] < 1800
        assert abs(row['deals_per_second']-64/row['seconds_per_64_deals'])<1e-12
        assert len(row['peaks'])==(2 if row['batch_size']==32 else 1)
        assert all(0 < p['allocated'] <= p['reserved'] <= 24*1024**3 for p in row['peaks'])
    # Independently read the selected historical batch artifacts, not the benchmark input helper.
    selection = read(OUT/'native-query-snapshot-control-v1-registration.json')
    cp = next(Path(p) for p in selection['inputs'] if Path(p).name.startswith('checkpoint-'))
    assert sha(cp)==selection['inputs'][str(cp)]
    from owned_columnar_evaluation_archive_v1 import restore
    batches = []
    for name in ('test-000000', 'test-000032'):
        route=read(cp)['routes'][name]; parent=cp.parent/route['attempt']; manifest=parent/(name+'.manifest.json')
        assert sha(manifest)==route['manifest_sha256']
        members=restore(parent/(name+'.xz'),read(manifest),guard=guard)
        batch=json.loads(members['query-batch.json']); assert len(batch['deals'])==32
        batches.append(batch)
    review_rp=OUT/f'{REVIEW}-registration.json'; assert not review_rp.exists()
    paths=[rp,result_path,store/'bank-identities.json',*Path(__file__).parent.glob('*.py')]
    inputs={str(p):sha(p) for p in paths}
    save(review_rp,dict(inputs=inputs,source_result_sha256=sha(result_path),workers=4,
        maximum_seconds=900,gpu_used=False,scope='All saved captures, native transports, cashflow identities, batch-size equivalence and timing aggregates; no new inference or poker engine.'))
    pool=concurrent.futures.ProcessPoolExecutor(max_workers=4,mp_context=multiprocessing.get_context('spawn'),
        initializer=initialize,initargs=(str(store),batches,result['runs'][0]))
    try:
        futures=[pool.submit(check_run,row) for row in result['runs']]
        checks=[]
        for future in futures:
            while True:
                guard()
                try: checks.append(future.result(timeout=2));break
                except concurrent.futures.TimeoutError: pass
        medians={case:statistics.median(r['seconds_per_64_deals'] for r in result['runs']
            if r['case']==case and r['phase']!='warmup') for case in CASES}
        assert medians==result['median_seconds_per_64_deals']
        assert result['ratios_to_deepcopy32']=={case:value/medians['deepcopy32'] for case,value in medians.items()}
        for p,h in inputs.items():guard();assert sha(p)==h,p
        output=dict(passed=True,registration_sha256=sha(review_rp),source_result_sha256=sha(result_path),
            runs_checked=len(checks),batches_checked=30,checks=checks,median_seconds_per_64_deals=medians,
            seconds=time.monotonic()-began,gpu_used=False,production_modified=False,
            limitation='Independent row mapping and saved-artifact consistency, sharing the existing scalar verifier. No independent model inference or poker engine; excludes archive/end-to-end study timing.')
        save(OUT/f'{REVIEW}-result.json',output);print(json.dumps(output),flush=True)
    except BaseException:
        for child in list(pool._processes.values()):
            if child.is_alive():child.terminate()
        raise
    finally:pool.shutdown(wait=True,cancel_futures=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run',action='store_true')
    main(parser.parse_args().run)
