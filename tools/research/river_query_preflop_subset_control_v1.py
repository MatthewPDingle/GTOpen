"""CPU-only exact preparation/policy comparison on a fixed archived full batch."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1',
                  MKL_NUM_THREADS='1', RAYON_NUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1')
import argparse
import copy
import gc
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback
import numpy as np
import psutil

TOOLS = Path('T:/Dev/GTOpen/tools/research')
sys.path.insert(0, str(TOOLS))
import river_query_reuse_audit_v2 as fixture
from river_query_cpu_profile_v1 import load_model
from river_query_preflop_subset_v1 import prepare as candidate
from bounded_parallel_evaluation_archive_v2 import production_available

NAME = 'river-query-preflop-subset-control-v1'
REG = fixture.OUT/(NAME+'-registration.json')
RESULT = fixture.OUT/(NAME+'-result.json')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def assert_same(reference, proposed):
    for key in ('table', 'mask', 'arity'):
        left, right = reference[key], proposed[key]
        assert left.dtype == right.dtype and left.shape == right.shape
        assert left.tobytes() == right.tobytes(), key
    for key in ('features', 'actors', 'legal', 'prior', 'action', 'valid'):
        left, right = getattr(reference['arrays'], key), getattr(proposed['arrays'], key)
        assert left.dtype == right.dtype and left.shape == right.shape
        assert left.tobytes() == right.tobytes(), key
        assert not left.flags.writeable and not right.flags.writeable


def invalid_controls(engine, queries):
    obs = queries['observations']
    target = next(i for i,o in enumerate(obs) if o['phase'] == 3 and o['own_history'])
    selected = sorted({target, *(row[0] for row in obs[target]['own_history'])})
    mapping = {old:new for new,old in enumerate(selected)}
    small = copy.deepcopy(queries)
    small['observations'] = [copy.deepcopy(obs[i]) for i in selected]
    for row in small['observations']:
        row['own_history'] = [[mapping[i], action, n] for i,action,n in row['own_history']]
    at = mapping[target]
    assert_same(engine.prepare(small), candidate(engine, small))
    def feature(row, value):
        row['active_features'][0] = value
    mutations = (
        ('boolean feature', lambda q:feature(q['observations'][at], True)),
        ('float feature', lambda q:feature(q['observations'][at], 1.5)),
        ('out of range feature', lambda q:feature(q['observations'][at], 269)),
        ('duplicate feature', lambda q:feature(q['observations'][at], q['observations'][at]['active_features'][1])),
        ('boolean actor', lambda q:q['observations'][at].update(actor=True)),
        ('invalid actor', lambda q:q['observations'][at].update(actor=2)),
        ('invalid arity', lambda q:q['observations'][at].update(n=5)),
        ('wrong phase', lambda q:q['observations'][at].update(phase=0)),
        ('postflop preflop key', lambda q:q['observations'][at].update(hi='1')),
        ('self history', lambda q:q['observations'][at]['own_history'][0].__setitem__(0, at)),
        ('invalid history action', lambda q:q['observations'][at]['own_history'][0].__setitem__(1, 9)),
        ('wrong context', lambda q:q.update(context_source='{}')),
    )
    for name, mutation in mutations:
        changed = copy.deepcopy(small)
        mutation(changed)
        for prepare in (engine.prepare, lambda q:candidate(engine, q)):
            try:
                prepare(changed)
            except ValueError:
                pass
            else:
                raise AssertionError('Accepted invalid query: '+name)
    return [name for name,_ in mutations]


def main(run=False):
    streams, source, policy_id = fixture.selection()
    assert len(streams) == 38
    engine, model_path = load_model(policy_id, source)
    sources = {str(Path(__file__)):sha(Path(__file__))}
    for module in list(sys.modules.values()):
        path = getattr(module, '__file__', None)
        if path and Path(path).is_relative_to(TOOLS) and Path(path).suffix == '.py':
            sources[str(Path(path))] = sha(path)
    spec = dict(format=1, sources=sources, fixture=str(fixture.FIXTURE),
        metrics_sha256=fixture.METRIC_SHA, native_sha256=fixture.NATIVE_SHA, model_sha256=policy_id,
        streams=[name for name,_,_ in streams], maximum_seconds=300, maximum_own_rss_bytes=2_000_000_000,
        checks='Exact bytes of every prepared array and archived policy, unchanged support, invalid-input rejection.',
        timing='One paired CPU preparation per stream, alternating first; concurrent study load, no cProfile.',
        gpu_used=False, new_deals=0, active_training_changed=False)
    if not run:
        print(json.dumps(dict(ready=True, streams=len(streams), gpu_used=False)))
        return
    assert not REG.exists() and not RESULT.exists()
    began = time.monotonic()
    peak_rss = 0
    def guard():
        nonlocal peak_rss
        assert time.monotonic()-began < 300
        assert production_available() and psutil.virtual_memory().available > 32_000_000_000
        assert psutil.cpu_percent(interval=.2) < 60
        peak_rss = max(peak_rss, psutil.Process().memory_info().rss)
        assert peak_rss < 2_000_000_000
    guard()
    with REG.open('x', encoding='utf-8', newline='\n') as handle:
        json.dump(spec, handle, indent=2); handle.write('\n')
    result = dict(format=1, passed=False, registration_sha256=sha(REG), started_unix=time.time(), cases=[])
    metric = json.loads((fixture.FIXTURE/'metrics.json').read_bytes())
    artifacts = metric['subbatches'][0]['artifacts']
    try:
        for index,(name, request, archived) in enumerate(streams):
            guard()
            assert sha(fixture.EXE) == fixture.NATIVE_SHA
            completed = subprocess.run([str(fixture.EXE),str(fixture.CONTEXT)], input=request,
                capture_output=True, timeout=60, creationflags=subprocess.CREATE_NO_WINDOW)
            assert completed.returncode == archived['code'] == 0
            assert len(completed.stdout) == archived['stdout_bytes'] <= 64_000_000
            assert hashlib.sha256(completed.stdout).hexdigest() == archived['stdout_sha256']
            document = json.loads(completed.stdout)
            assert document['context_source'] == source and document['request_source'] == request.decode()
            queries = document['queries']
            if index == 0:
                result['invalid_controls'] = invalid_controls(engine, queries)
            mode = name.rsplit('-',1)[1]
            relative = Path('conditional')/(name.rsplit('-',1)[0]+'-policies.npz')
            oracle_path = fixture.FIXTURE/'batch-00'/relative
            assert sha(oracle_path) == artifacts[str(relative)]
            with np.load(oracle_path, allow_pickle=False) as data:
                oracle = data[mode].copy()
            order = ('reference','candidate') if index % 2 == 0 else ('candidate','reference')
            prepared = {}; timings = {}
            for label in order:
                start = time.perf_counter()
                prepared[label] = engine.prepare(queries) if label == 'reference' else candidate(engine,queries)
                timings[label] = time.perf_counter()-start
            assert_same(prepared['reference'], prepared['candidate'])
            for label in order:
                predicted = engine.infer(prepared[label])
                assert predicted.shape == oracle.shape and predicted.dtype == oracle.dtype
                assert predicted.tobytes() == oracle.tobytes(), name+' '+label
            row = dict(name=name, observations=len(oracle), first=order[0],
                reference_seconds=timings['reference'], candidate_seconds=timings['candidate'],
                exact_prepared_arrays=True, exact_archived_policy=True)
            result['cases'].append(row)
            if (index+1)%10 == 0:
                print(json.dumps(dict(completed_streams=index+1, total_streams=len(streams))), flush=True)
            del document, completed, queries, prepared, predicted, oracle
            gc.collect()
        for path,expected in sources.items():
            assert sha(path) == expected
        assert sha(model_path) == policy_id
        guard()
        result.update(passed=True, observations=sum(row['observations'] for row in result['cases']),
            reference_seconds=sum(row['reference_seconds'] for row in result['cases']),
            candidate_seconds=sum(row['candidate_seconds'] for row in result['cases']),
            gpu_used=False, active_training_changed=False, accuracy_claim=False,
            next_requirement='Broader models and complete target-generation/update equality before future adoption; active study unchanged.')
    except Exception as error:
        result.update(error=str(error),traceback=traceback.format_exc())
    result.update(seconds=time.monotonic()-began, finished_unix=time.time(), peak_python_rss_bytes=peak_rss)
    with RESULT.open('x',encoding='utf-8',newline='\n') as handle:
        json.dump(result,handle,indent=2);handle.write('\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('cases','invalid_controls','traceback')}), flush=True)
    if not result['passed']:
        raise RuntimeError(result['error'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser();parser.add_argument('--run',action='store_true')
    main(parser.parse_args().run)
