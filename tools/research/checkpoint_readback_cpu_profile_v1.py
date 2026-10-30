"""Profile an unchanged archived checkpoint restore; no training or GPU work.

One descriptive cProfile observation under concurrent study load. This does not
measure an optimization, isolated throughput or the active study's overhead.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1',
                  MKL_NUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1')
import argparse
import cProfile
import hashlib
import json
from pathlib import Path
import pstats
import sys
import time
import traceback

TOOLS = Path('T:/Dev/GTOpen/tools/research')
sys.path.insert(0, str(TOOLS))
import psutil
import board_training_checkpoint_v1 as checkpoint
from preflop_allin_matrix_v1 import AllinMatrix
from bounded_parallel_evaluation_archive_v2 import production_available

OUT = Path('T:/Dev/GTOpen/research/preflop-evolution/blind-defense-20260922')
STORE = Path('S:/GTOpen-research/weighted-complete-river-training-pilot-v1')
REG = OUT/'river-matched-training-pilot-v1-registration.json'
REG_SHA = '1dec3f979f863c8fafa18a905f897f64c824ba110a7320858795b4fae1e9924b'
PARENT_RESULT = OUT/'river-matched-training-pilot-v1-result.json'
REVIEW = OUT/'river-matched-training-pilot-v1-independent-review-v2.json'
CONTEXT = OUT/'bb-context-candidate.json'
MATRIX = OUT/'preflop-allin-matrix-control-v1-matrix.json'
CATALOG = Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')
RESULT = OUT/'checkpoint-readback-cpu-profile-v1-result.json'
CHECKPOINT_SHA = '86981a66fb99f3d25aa7c8f27b7b3d990ab201cec50fb2807b91e471bc973663'


def read(path):
    return json.loads(Path(path).read_bytes())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main(run=False):
    assert sha(REG) == REG_SHA
    reg, parent, review = read(REG), read(PARENT_RESULT), read(REVIEW)
    assert parent['passed'] and parent['complete'] and parent['registration_sha256'] == REG_SHA
    assert review['passed'] and review['source_result_sha256'] == sha(PARENT_RESULT)
    arm = reg['arms']['A-baseline']
    recorded = next(row for row in parent['training'] if row['arm'] == 'A-baseline')
    progress_path = STORE/'A-baseline/progress.json'
    progress = read(progress_path)
    assert progress['completed'] == recorded['completed'] == 80
    ref = progress['checkpoint']
    assert ref == recorded['checkpoint'] and ref['sha256'] == CHECKPOINT_SHA
    objects = STORE/'A-baseline/objects'
    checkpoint_path = objects/ref['file']
    assert sha(checkpoint_path) == CHECKPOINT_SHA
    doc = read(checkpoint_path)
    source = CONTEXT.read_text()
    config = arm['config']
    assert doc['config'] == config
    assert sha(MATRIX) == config['board_root']['matrix_sha256']
    matrix = AllinMatrix(read(MATRIX), source)
    args = dict(context_source=source, catalog_source=CATALOG.read_text(),
        matrix_sha256=sha(MATRIX), entry_mass=matrix.btn_mass, root_config=config['board_root'])
    assert sha(CONTEXT) == doc['context_sha256'] and sha(CATALOG) == doc['catalog_sha256']
    if not run:
        print(json.dumps(dict(ready=True, source_boundary=80, gpu_started=False, restore_started=False)))
        return
    assert not RESULT.exists(), 'Preserve prior evidence; use a new version'
    started = time.monotonic()
    process = psutil.Process()
    def guard():
        assert time.monotonic()-started < 600
        assert production_available(), 'Production has priority'
        assert psutil.cpu_percent(interval=.2) < 60
        assert psutil.virtual_memory().available > 32_000_000_000
        assert process.memory_info().rss < 3_000_000_000
    guard()
    paths = [Path(__file__), REG, PARENT_RESULT, REVIEW, progress_path,
             checkpoint_path, CONTEXT, MATRIX, CATALOG]
    paths += [objects/r['file'] for r in [*doc['reservoirs'], *doc['played_bank'], doc['next_model']]]
    for module in tuple(sys.modules.values()):
        file = getattr(module, '__file__', None)
        if file and Path(file).is_relative_to(TOOLS) and Path(file).suffix == '.py':
            paths.append(Path(file))
    identities = {str(path):sha(path) for path in paths}
    result = dict(format=1, passed=False, started_unix=time.time(),
        scope='Unchanged complete A-baseline parent-80 checkpoint restore under cProfile and concurrent load.',
        inputs=identities, gpu_used=False, training_run=False, new_deals=0,
        source_boundary=80, checkpoint=ref, active_training_changed=False,
        timing_note='Single profiled observation, not an isolated benchmark or measured speedup. RSS sampled before/after only.')
    try:
        guard()
        result['rss_before_bytes'] = process.memory_info().rss
        profiler = cProfile.Profile()
        begin = time.monotonic()
        state = profiler.runcall(checkpoint.restore_checkpoint, objects, ref, config, **args)
        result['restore_seconds'] = time.monotonic()-begin
        assert state['completed_iterations'] == 80 and state['next_model'] == doc['next_model']
        assert state['played_bank'] == doc['played_bank']
        result['reservoir_rows'] = [r.size for r in state['reservoirs']]
        result['rss_after_bytes'] = process.memory_info().rss
        rows = []
        for (file, line, function), (primitive, calls, own, cumulative, _) in pstats.Stats(profiler).stats.items():
            rows.append(dict(file=file, line=line, function=function, primitive_calls=primitive,
                calls=calls, own_seconds=own, cumulative_seconds=cumulative))
        result['top_cumulative'] = sorted(rows, key=lambda row:row['cumulative_seconds'], reverse=True)[:30]
        result['top_self'] = sorted(rows, key=lambda row:row['own_seconds'], reverse=True)[:20]
        guard()
        for path, digest in identities.items():
            assert sha(path) == digest, path
        result['passed'] = True
    except BaseException as error:
        result.update(error=repr(error), traceback=traceback.format_exc())
        raise
    finally:
        result['seconds_including_input_checks'] = time.monotonic()-started
        result['finished_unix'] = time.time()
        data = json.dumps(result, separators=(',', ':'), allow_nan=False)+'\n'
        assert len(data.encode()) < 100_000
        with RESULT.open('x', encoding='utf-8', newline='\n') as stream:
            stream.write(data)
        print(json.dumps(dict(passed=result['passed'], result=str(RESULT),
            restore_seconds=result.get('restore_seconds'), reservoir_rows=result.get('reservoir_rows'))), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', action='store_true')
    main(parser.parse_args().run)
