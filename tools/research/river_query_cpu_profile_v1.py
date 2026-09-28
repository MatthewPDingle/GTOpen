"""Profile unchanged CPU policy preparation on four fixed archived exports.

Descriptive timings under cProfile and concurrent study load, not a benchmark.
Checks the recomputed policies against the archived original arrays. No fitting,
new deals, GPU work, or changes to the running scientific experiment.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1',
                  MKL_NUM_THREADS='1', RAYON_NUM_THREADS='1',
                  PYTHONDONTWRITEBYTECODE='1')
import argparse
import cProfile
import gc
import hashlib
import json
from pathlib import Path
import pstats
import subprocess
import sys
import time
import traceback

TOOLS = Path('T:/Dev/GTOpen/tools/research')
sys.path.insert(0, str(TOOLS))
import numpy as np
import psutil
import river_query_reuse_audit_v1 as fixture
from river_policy_batch_v1 import CPUCurrentPolicy
from bounded_parallel_evaluation_archive_v2 import production_available
from preflop_allin_matrix_v1 import AllinMatrix

OUT = fixture.OUT
RESULT = OUT/'river-query-cpu-profile-v1-result.json'
REG = OUT/'river-matched-training-pilot-v1-registration.json'
REG_SHA = '1dec3f979f863c8fafa18a905f897f64c824ba110a7320858795b4fae1e9924b'
CATALOG = Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_model(policy_id, source):
    assert sha(REG) == REG_SHA
    reg = json.loads(REG.read_bytes())
    arm = reg['arms']['A-river']
    metric = json.loads((fixture.FIXTURE/'metrics.json').read_bytes())
    ref = metric['used_model']
    model_path = fixture.FIXTURE.parent/'objects'/ref['file']
    assert ref['generation'] == 78 and sha(model_path) == ref['sha256'] == policy_id
    model = json.loads(model_path.read_bytes())
    config = arm['config']['board_root']
    matrix_path = OUT/'preflop-allin-matrix-control-v1-matrix.json'
    assert sha(matrix_path) == config['matrix_sha256']
    matrix = AllinMatrix(json.loads(matrix_path.read_bytes()), source)
    engine = CPUCurrentPolicy(model, source, catalog_source=CATALOG.read_text(),
        matrix_sha256=config['matrix_sha256'], entry_mass=matrix.btn_mass, root_config=config)
    return engine, model_path


def main(run=False):
    streams, source, policy_id = fixture.selection()
    assert len(streams) == 4
    engine, model_path = load_model(policy_id, source)
    if not run:
        print(json.dumps(dict(ready=True, streams=len(streams), model_generation=78,
                              gpu_used=False, profiles_started=False)))
        return
    assert not RESULT.exists(), 'Preserve completed evidence; use a new version'
    began = time.monotonic()
    process = psutil.Process()
    peak_rss = 0
    def guard():
        nonlocal peak_rss
        assert time.monotonic()-began < 300
        assert production_available(), 'Production has priority'
        assert psutil.virtual_memory().available > 32_000_000_000
        assert psutil.cpu_percent(interval=.2) < 60
        peak_rss = max(peak_rss, process.memory_info().rss)
        assert peak_rss < 2_000_000_000
    source_hashes = {str(Path(__file__)):sha(Path(__file__))}
    for module in list(sys.modules.values()):
        path = getattr(module, '__file__', None)
        if path and Path(path).is_relative_to(TOOLS) and Path(path).suffix == '.py':
            source_hashes[str(Path(path))] = sha(path)
    result = dict(format=1, passed=False, started_unix=time.time(),
        scope='First two chunks of first batch of archived A-river update 79; descriptive cProfile timings under concurrent load.',
        fixture=str(fixture.FIXTURE), metrics_sha256=fixture.METRIC_SHA,
        native_sha256=fixture.NATIVE_SHA, model_sha256=policy_id,
        context_sha256=sha(fixture.CONTEXT), sources=source_hashes,
        gpu_used=False, fitting_run=False, new_deals=0, active_training_changed=False, cases=[])
    metric = json.loads((fixture.FIXTURE/'metrics.json').read_bytes())
    artifacts = metric['subbatches'][0]['artifacts']
    try:
        for name, request, archived in streams:
            guard()
            assert sha(fixture.EXE) == fixture.NATIVE_SHA
            start = time.monotonic()
            completed = subprocess.run([str(fixture.EXE), str(fixture.CONTEXT)], input=request,
                capture_output=True, timeout=60, creationflags=subprocess.CREATE_NO_WINDOW)
            export_seconds = time.monotonic()-start
            assert completed.returncode == archived['code'] == 0
            assert len(completed.stdout) == archived['stdout_bytes'] <= 64_000_000
            assert hashlib.sha256(completed.stdout).hexdigest() == archived['stdout_sha256']
            start = time.monotonic()
            document = json.loads(completed.stdout)
            decode_seconds = time.monotonic()-start
            assert document['context_source'] == source
            assert document['request_source'] == request.decode()
            assert document['queries']['context_source'] == source
            mode = name.rsplit('-', 1)[1]
            relative = Path('conditional')/(name.rsplit('-', 1)[0]+'-policies.npz')
            oracle_path = fixture.FIXTURE/'batch-00'/relative
            assert sha(oracle_path) == artifacts[str(relative)]
            with np.load(oracle_path, allow_pickle=False) as data:
                oracle = data[mode].copy()
            guard()
            profiler = cProfile.Profile()
            start = time.monotonic()
            prepared = profiler.runcall(engine.prepare, document['queries'])
            prepare_seconds = time.monotonic()-start
            start = time.monotonic()
            predicted = profiler.runcall(engine.infer, prepared)
            infer_seconds = time.monotonic()-start
            assert predicted.shape == oracle.shape
            exact = predicted.tobytes() == oracle.tobytes()
            max_error = float(np.max(np.abs(predicted-oracle)))
            support_exact = np.array_equal(predicted > 0, oracle > 0)
            assert max_error < 1e-12 and support_exact
            stats = pstats.Stats(profiler).stats
            rows = [dict(file=k[0], line=k[1], function=k[2], primitive_calls=v[0],
                         calls=v[1], self_seconds=v[2], cumulative_seconds=v[3])
                    for k, v in stats.items()]
            case = dict(name=name, observations=len(predicted), export_seconds=export_seconds,
                decode_seconds=decode_seconds, profiled_prepare_seconds=prepare_seconds,
                profiled_infer_seconds=infer_seconds, exact_policy_bytes=exact,
                maximum_policy_error=max_error, exact_policy_support=support_exact,
                top_self=sorted(rows, key=lambda r:r['self_seconds'], reverse=True)[:20],
                top_cumulative=sorted(rows, key=lambda r:r['cumulative_seconds'], reverse=True)[:20])
            result['cases'].append(case)
            print(json.dumps({k:v for k,v in case.items() if not k.startswith('top_')}), flush=True)
            del document, completed, prepared, predicted, oracle, profiler, stats
            gc.collect()
        for path, expected in source_hashes.items():
            assert sha(path) == expected
        assert sha(model_path) == policy_id
        guard()
        result['passed'] = True
    except Exception as error:
        result.update(error=str(error), traceback=traceback.format_exc())
    result.update(seconds=time.monotonic()-began, finished_unix=time.time(),
                  peak_python_rss_bytes=peak_rss)
    with RESULT.open('x', encoding='utf-8', newline='\n') as handle:
        json.dump(result, handle, indent=2)
        handle.write('\n')
    print(json.dumps(dict(passed=result['passed'], seconds=result['seconds'], result=str(RESULT))), flush=True)
    if not result['passed']:
        raise RuntimeError(result['error'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', action='store_true')
    main(parser.parse_args().run)
