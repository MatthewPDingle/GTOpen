"""Check the new cached bank against retained full-average evidence, without fitting."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
                  CUBLAS_WORKSPACE_CONFIG=':4096:8', PYTHONDONTWRITEBYTECODE='1')
import copy
import hashlib
import json
from pathlib import Path
import sys
import time
import traceback
ROOT = Path('T:/Dev/GTOpen')
sys.path.insert(1, str(ROOT / 'tools/research'))
import numpy as np
import psutil
import torch
import stack_context_full_policy_v1 as full
import stack_context_policy_v1 as base
import stack_context_relative_policy_v1 as relative
from stack_context_inputs_v1 import Registry
from stack_context_relative_inputs_v1 import Registry as RelativeRegistry
from stack_context_played_bank_v1 import PlayedBank
from board_root_accumulator_v1 import BoardRootRegrets
from exact_btn_regret_accumulator_v1 import ExactBtnRegrets
from river_matched_training_pilot_v1 import OUT, LOCK, OTHER, available, production_available

HERE = Path(__file__).resolve().parent
NAME = 'stack-context-played-bank-check-v1'
REG, ATTEMPT, RESULT, FAILURE = (HERE / (NAME + x + '.json') for x in
                                ('-registration', '-attempt', '-result', '-failure'))
OLD = Path('S:/GTOpen-research/stack-context-full-control-v1')
GEOMETRY = Path('S:/GTOpen-research/stack-geometry-control-v1')
QUERIES = Path('S:/GTOpen-research/stack-context-model-control-v1')
DEPTHS = (20, 40, 60, 100, 150, 200, 400)


def read(path):
    return json.loads(Path(path).read_bytes())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, sort_keys=True, separators=(',', ':'), allow_nan=False)
        stream.write('\n')


def main():
    if any(p.exists() for p in (REG, ATTEMPT, RESULT, FAILURE, LOCK, OTHER)):
        raise ValueError('Existing attempt or research owner')
    ready, probe = available()
    if not ready:
        print(json.dumps(dict(deferred=True, probe=probe))); return
    old_reg = read(OUT / 'stack-context-full-control-v1-registration.json')
    old_result = read(OUT / 'stack-context-full-control-v1-result.json')
    if not old_result['complete'] or not old_result['passed']:
        raise ValueError('Passed full-model control required')
    paths = {Path(__file__).resolve(), HERE / 'stack_context_played_bank_v1.py',
             OUT / 'stack-context-full-control-v1-registration.json',
             OUT / 'stack-context-full-control-v1-result.json'}
    entries = []
    for depth in DEPTHS:
        context = GEOMETRY / 'fixtures' / f'stack-{depth}-context.json'
        public = GEOMETRY / f'stack-{depth}-public.json'
        query = QUERIES / f'stack-{depth}-queries.json'
        for p in (context, public, query):
            if sha(p) != old_reg['inputs'][str(p)]:
                raise ValueError('Retained geometry/query changed')
            paths.add(p)
        entries.append(dict(name=f'{depth}bb', split='heldout' if depth in (60,150) else 'fit',
                            context_source=context.read_text(), public_document=read(public)))
    for width in (362, 387):
        for p in [OLD / f'{width}-fixture.json', *[OLD / f'{width}-{d}-comparison.npz' for d in DEPTHS]]:
            if sha(p) != old_result['artifacts'][str(p)]:
                raise ValueError('Retained model/reference changed')
            paths.add(p)
    for module in list(sys.modules.values()):
        p = getattr(module, '__file__', None)
        if p and Path(p).is_relative_to(ROOT) and Path(p).suffix == '.py':
            paths.add(Path(p))
    identities = {str(p): sha(p) for p in paths}
    with LOCK.open('x') as stream:
        stream.write(str(os.getpid()))
    began = time.monotonic()
    try:
        save(REG, dict(inputs=identities, maximum_seconds=600, maximum_cuda_bytes=1_000_000_000,
             maximum_new_bytes=2_000_000, new_native_calls=False, fitting=False,
             policy_tolerance=1e-10, reach_tolerance=1e-10,
             reference='Previously authenticated CPU averages on native queries with synthetic routing models'))
        save(ATTEMPT, dict(pid=os.getpid(), process_created=psutil.Process().create_time(), registration_sha256=sha(REG)))
        torch.set_num_threads(1)
        torch.use_deterministic_algorithms(True)
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        torch.cuda.set_per_process_memory_fraction(1_000_000_000 / torch.cuda.get_device_properties(0).total_memory)
        def guard():
            if (time.monotonic() - began > 600 or OTHER.exists() or not production_available()
                    or psutil.virtual_memory().available < 24_000_000_000
                    or torch.cuda.memory_reserved() > 1_000_000_000):
                raise RuntimeError('Cached-bank check resource bound')
        records = []
        negatives = []
        for width, kind, api in ((362, Registry, base), (387, RelativeRegistry, relative)):
            registry = kind(entries)
            fixture = read(OLD / f'{width}-fixture.json')
            if fixture['registry'] != registry.manifest:
                raise ValueError('Retained registry changed')
            resources, model = fixture['resources'], fixture['model']
            initial = copy.deepcopy(model)
            initial['generation'] = 0
            initial['shared'] = api.initial(registry)
            for key, state in initial['local_states'].items():
                cfg = dict(resources[key]['root_config'])
                cfg.pop('chance')
                state['board_root_state'] = BoardRootRegrets(**cfg).document()
                state['exact_btn_state'] = ExactBtnRegrets(key, resources[key]['entry_mass']).document()
            full.validate(initial, registry, resources)
            documents = [initial, model]
            for depth, entry in zip(DEPTHS, entries):
                key = hashlib.sha256(entry['context_source'].encode()).hexdigest()
                queries = read(QUERIES / f'stack-{depth}-queries.json')
                with np.load(OLD / f'{width}-{depth}-comparison.npz') as arrays:
                    expected, reach = arrays['average_cpu'], arrays['reach_cpu']
                for device in ('cpu', 'cuda'):
                    guard()
                    started = time.monotonic()
                    bank = PlayedBank(documents, registry, context_sha256=key, resources=resources,
                        weights_by_player=[[1., 2.], [3., 4.]], completed_cycles=2, device=device, guard=guard)
                    encodings = [0, 0]
                    for i, engine in enumerate(bank.engines):
                        original = engine._features
                        def counted(obs, i=i, original=original):
                            encodings[i] += 1
                            return original(obs)
                        engine._features = counted
                    probability, support = bank.average(queries, guard=guard)
                    error = float(np.max(abs(probability - expected)))
                    reach_error = float(np.max(abs(support - reach)))
                    if error > 1e-10 or reach_error > 1e-10 or encodings != [1, 0]:
                        raise ValueError('Cached complete average differs or repeats feature preparation')
                    records.append(dict(width=width, depth=depth, device=device, rows=len(expected),
                        maximum_policy_error=error, maximum_reach_error=reach_error,
                        feature_encodings=encodings, seconds=time.monotonic()-started))
                print(json.dumps(dict(width=width, depth=depth, cached_average_passed=True)), flush=True)
            def reject(label, fn):
                try:
                    fn()
                except (ValueError, KeyError):
                    negatives.append(dict(width=width, case=label))
                else:
                    raise ValueError('Accepted ' + label)
            args = dict(registry=registry, context_sha256=key, resources=resources,
                        weights_by_player=[[1., 2.], [3., 4.]], completed_cycles=2, device='cpu', guard=guard)
            reject('reordered_generations', lambda: PlayedBank(documents[::-1], **args))
            reject('extra_unplayed_generation', lambda: PlayedBank(documents, **dict(args, completed_cycles=1)))
            reject('zero_weight', lambda: PlayedBank(documents, **dict(args, weights_by_player=[[0., 2.], [3., 4.]])))
            missing = copy.deepcopy(queries)
            del missing['observations'][0]['own_history']
            reject('missing_native_history', lambda: bank.average(missing, guard=guard))
            wrong = dict(queries, context_source=entries[0]['context_source'])
            reject('different_context', lambda: bank.average(wrong, guard=guard))
        for path, expected_hash in identities.items():
            if sha(path) != expected_hash:
                raise ValueError('Qualification input changed')
        save(RESULT, dict(complete=True, passed=True, registration_sha256=sha(REG), records=records,
             negative_controls=negatives, seconds=time.monotonic()-began,
             peak_cuda_reserved_bytes=torch.cuda.max_memory_reserved(), training=False, accuracy_qualified=False,
             scope='Cached average agrees with retained reference; no fresh native labels, training, or policy-quality claim.'))
    except BaseException as error:
        save(FAILURE, dict(error=repr(error), traceback=traceback.format_exc(), retry_allowed=False))
        raise
    finally:
        if LOCK.exists() and LOCK.read_text().strip() == str(os.getpid()):
            LOCK.unlink()


if __name__ == '__main__':
    main()
