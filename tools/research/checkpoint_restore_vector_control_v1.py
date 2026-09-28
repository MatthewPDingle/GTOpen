"""Historical CPU-only parity checks for bulk reservoir validation and restore."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1',
                  MKL_NUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1')
import argparse
import ast
import copy
import gc
import hashlib
import inspect
import io
import json
from pathlib import Path
import sys
import time
import traceback
import numpy as np
import psutil
import board_training_checkpoint_v1 as original_checkpoint
import board_checkpoint_restore_vector_v1 as vector_checkpoint
from weighted_physical_reservoir_v1 import WeightedPhysicalReservoir, ARRAYS, METHOD
from weighted_reservoir_load_vector_v1 import load as vector_load
from board_training_pipeline_control_v1 import compare_states
from bounded_parallel_evaluation_archive_v2 import production_available
from preflop_allin_matrix_v1 import AllinMatrix
from board_prefix_publication_v1 import atomic_json

ROOT = Path('T:/Dev/GTOpen')
TOOLS = ROOT/'tools/research'
OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
NAME = 'checkpoint-restore-vector-control-v1'
REG = OUT/(NAME+'-registration.json')
RESULT = OUT/(NAME+'-result.json')
PARENT_REG = OUT/'river-matched-training-pilot-v1-registration.json'
PARENT_RESULT = OUT/'river-matched-training-pilot-v1-result.json'
REVIEW = OUT/'river-matched-training-pilot-v1-independent-review-v2.json'


def read(path): return json.loads(Path(path).read_bytes())
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def equal_reservoirs(a, b):
    assert type(a) is type(b) is WeightedPhysicalReservoir
    assert a.summary() == b.summary() and a.rng.bit_generator.state == b.rng.bit_generator.state
    for key in ARRAYS:
        x, y = getattr(a, key), getattr(b, key)
        assert x.shape == y.shape and x.dtype == y.dtype and x.tobytes() == y.tobytes(), key


def archive(metadata, arrays):
    stream = io.BytesIO()
    np.savez(stream, metadata=np.array(json.dumps(metadata)), **arrays)
    return stream.getvalue()


def synthetic(source):
    rng = np.random.default_rng(9297101)
    size = 512
    arity = rng.integers(2, 5, size=size, dtype=np.uint8)
    values = rng.normal(size=(size, 4))
    values[np.arange(4)[None, :] >= arity[:, None]] = -0.0
    arrays = dict(keys=rng.integers(0, 2**64-1, size=(size, 2), dtype=np.uint64),
        active=np.stack([rng.choice(269, 36, replace=False) for _ in range(size)]).astype(np.uint16),
        arity=arity, values=values, iterations=np.arange(1, size+1, dtype=np.uint64),
        deal_weights=np.exp(rng.uniform(-20, 10, size)))
    arrays['keys'][0] = np.iinfo(np.uint64).max
    arrays['iterations'][0] = np.iinfo(np.uint64).max
    arrays['deal_weights'][0:2] = [np.nextafter(0., 1.), 65536.]
    m = dict(format=2, method=METHOD, capacity=size+3, player=0, seen=size,
        context_sha256=hashlib.sha256(source.encode()).hexdigest(), rng=copy.deepcopy(rng.bit_generator.state))
    valid = [('mixed-unsorted-and-boundaries', m, arrays)]
    empty = {k:v[:0].copy() for k,v in arrays.items()}
    valid += [('empty', dict(m, seen=0), empty),
              ('other-player-full', dict(m, player=1, capacity=size, seen=size+100), arrays)]
    for name, meta, data in valid:
        payload = archive(meta, data)
        equal_reservoirs(WeightedPhysicalReservoir.load(io.BytesIO(payload), source),
                         vector_load(io.BytesIO(payload), source))
    cases = []
    def change_array(name, key, operation):
        data = {k:v.copy() for k,v in arrays.items()}
        operation(data)
        cases.append((name, copy.deepcopy(m), data))
    for key in ARRAYS:
        change_array(key+'-dtype', key, lambda d, k=key: d.__setitem__(k, d[k].astype(np.float32)))
        change_array(key+'-shape', key, lambda d, k=key: d.__setitem__(k, d[k][:-1]))
    edits = [('feature-duplicate', 'active', lambda a:a.__setitem__((0, 0), a[0, 1])),
             ('feature-outside', 'active', lambda a:a.__setitem__((0, 0), 269)),
             ('arity-low', 'arity', lambda a:a.__setitem__(0, 1)),
             ('arity-high', 'arity', lambda a:a.__setitem__(0, 5)),
             ('target-nan', 'values', lambda a:a.__setitem__((0, 0), np.nan)),
             ('target-inf', 'values', lambda a:a.__setitem__((0, 0), np.inf)),
             ('iteration-zero', 'iterations', lambda a:a.__setitem__(0, 0))]
    for name, key, edit in edits:
        change_array(name, key, lambda d, k=key, fn=edit:fn(d[k]))
    for value in (0., -1., 65537., np.inf, np.nan):
        change_array('weight-'+str(value), 'deal_weights',
                     lambda d, v=value:d['deal_weights'].__setitem__(0, v))
    change_array('padding-nonzero', 'values', lambda d:(d['arity'].__setitem__(0, 2), d['values'].__setitem__((0, 3), 1.)))
    change_array('missing-array', 'keys', lambda d:d.pop('keys'))
    change_array('extra-array', 'keys', lambda d:d.__setitem__('extra', np.array([1])))
    for key, value in [('format', 1), ('method', 'other'), ('seen', True), ('seen', -1),
                       ('seen', 2**63), ('capacity', 0), ('player', 2),
                       ('context_sha256', 'wrong'), ('rng', {})]:
        cases.append(('metadata-'+key+'-'+str(value), dict(m, **{key:value}), arrays))
    for name, meta, data in cases:
        payload = archive(meta, data)
        for loader in (WeightedPhysicalReservoir.load, vector_load):
            try: loader(io.BytesIO(payload), source)
            except (ValueError, TypeError, KeyError, OverflowError): pass
            else: raise AssertionError('Accepted malformed archive: '+name)
    return dict(valid_archives=len(valid), valid_rows=sum(min(x[1]['seen'], x[1]['capacity']) for x in valid),
                rejected_archives=len(cases), invalid_cases=[x[0] for x in cases])


def specification():
    original = inspect.getsource(original_checkpoint.restore_checkpoint)
    expected = original.replace('WeightedPhysicalReservoir.load(', 'load_reservoir(')
    assert ast.dump(ast.parse(expected)) == ast.dump(ast.parse(inspect.getsource(vector_checkpoint.restore_checkpoint)))
    assert sha(PARENT_REG) == '1dec3f979f863c8fafa18a905f897f64c824ba110a7320858795b4fae1e9924b'
    parent, result, review = read(PARENT_REG), read(PARENT_RESULT), read(REVIEW)
    assert result['passed'] and result['complete'] and result['registration_sha256'] == sha(PARENT_REG)
    assert review['passed'] and review['source_result_sha256'] == sha(PARENT_RESULT)
    paths = [PARENT_REG, PARENT_RESULT, REVIEW, Path(__file__),
             OUT/'bb-context-candidate.json', OUT/'preflop-allin-matrix-control-v1-matrix.json',
             Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')]
    cases = []
    for name in ('A-baseline', 'A-river', 'B-baseline', 'B-river'):
        folder = Path(parent['store'])/name
        pp = folder/'progress.json'; p = read(pp)
        r = next(r for r in result['training'] if r['arm'] == name)
        assert p['completed'] == r['completed'] == 80 and p['checkpoint'] == r['checkpoint']
        path = folder/'objects'/p['checkpoint']['file']; assert sha(path) == p['checkpoint']['sha256']
        doc = read(path)
        paths += [pp, path]
        paths += [folder/'objects'/ref['file'] for ref in [*doc['reservoirs'], *doc['played_bank'], doc['next_model']]]
        cases.append(dict(arm=name, objects=str(folder/'objects'), checkpoint=p['checkpoint'],
                          config=parent['arms'][name]['config'], reservoirs=doc['reservoirs']))
    for module in tuple(sys.modules.values()):
        file = getattr(module, '__file__', None)
        if file and Path(file).is_relative_to(TOOLS) and Path(file).suffix == '.py': paths.append(Path(file))
    return dict(format=1, inputs={str(p):sha(p) for p in paths}, cases=cases,
        maximum_seconds=1200, maximum_own_rss_bytes=3_000_000_000, gpu_used=False,
        training_run=False, new_deals=0, active_training_changed=False,
        equality='Exact complete restored states, full allocated array bytes and RNG state; valid and invalid archive checks.',
        timing='One pair per fixture/checkpoint, alternating first implementation, under concurrent load; descriptive only.')


def main(run=False):
    spec = specification()
    if not run:
        print(json.dumps(dict(ready=True, checkpoints=len(spec['cases']), gpu_started=False)))
        return
    assert not REG.exists() and not RESULT.exists()
    began = time.monotonic(); process = psutil.Process()
    def guard():
        assert time.monotonic()-began < 1200
        assert production_available() and psutil.virtual_memory().available > 32_000_000_000
        assert psutil.cpu_percent(interval=.2) < 60 and process.memory_info().rss < 3_000_000_000
    guard(); atomic_json(REG, spec)
    result = dict(passed=False, registration_sha256=sha(REG), started_unix=time.time(),
        gpu_used=False, training_run=False, new_deals=0, active_training_changed=False,
        reservoir_cases=[], checkpoint_cases=[], timing_note=spec['timing'])
    source = (OUT/'bb-context-candidate.json').read_text()
    matrix_path = OUT/'preflop-allin-matrix-control-v1-matrix.json'
    matrix = AllinMatrix(read(matrix_path), source)
    catalog = Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json').read_text()
    try:
        result['synthetic'] = synthetic(source)
        for i, case in enumerate(spec['cases']):
            for player, ref in enumerate(case['reservoirs']):
                guard(); path = Path(case['objects'])/ref['file']; assert sha(path) == ref['sha256']
                loaders = [('reference', WeightedPhysicalReservoir.load), ('vector', vector_load)]
                if (i*2+player) % 2: loaders.reverse()
                values, timings = {}, {}
                for name, loader in loaders:
                    start=time.monotonic(); values[name]=loader(path, source); timings[name]=time.monotonic()-start
                equal_reservoirs(values['reference'], values['vector'])
                row = dict(arm=case['arm'], player=player, rows=values['reference'].size,
                    exact_arrays_and_rng_state=True, seconds=timings, first=loaders[0][0])
                result['reservoir_cases'].append(row); print(json.dumps(row), flush=True)
                del values; gc.collect()
            guard()
            args = dict(context_source=source, catalog_source=catalog, matrix_sha256=sha(matrix_path),
                        entry_mass=matrix.btn_mass, root_config=case['config']['board_root'])
            loaders = [('reference', original_checkpoint.restore_checkpoint), ('vector', vector_checkpoint.restore_checkpoint)]
            if i % 2: loaders.reverse()
            states, timings = {}, {}
            for name, loader in loaders:
                guard(); start=time.monotonic()
                states[name]=loader(case['objects'], case['checkpoint'], case['config'], **args)
                timings[name]=time.monotonic()-start
            compare_states(states['reference'], states['vector'])
            for a, b in zip(states['reference']['reservoirs'], states['vector']['reservoirs']): equal_reservoirs(a, b)
            row = dict(arm=case['arm'], exact_complete_state=True, seconds=timings, first=loaders[0][0])
            result['checkpoint_cases'].append(row); print(json.dumps(row), flush=True)
            del states; gc.collect()
        guard()
        for path, digest in spec['inputs'].items(): assert sha(path) == digest, path
        result['passed'] = True
        result['next_requirement'] = 'Isolated restore candidate only. Future runner integration must preserve all guards and be qualified before adoption. No change to the active registered experiment.'
    except BaseException as error:
        result.update(error=repr(error), traceback=traceback.format_exc())
        raise
    finally:
        result['seconds'] = time.monotonic()-began
        result['finished_unix'] = time.time()
        atomic_json(RESULT, result)
        print(json.dumps(dict(passed=result['passed'], result=str(RESULT))), flush=True)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--run', action='store_true')
    main(parser.parse_args().run)
