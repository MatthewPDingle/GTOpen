"""CPU-only equivalence controls on existing two-model routing fixtures.

No fitting, deals, native executable, CUDA, scientific result inspection or
changes to the live study. This is not actual 64-generation qualification.
"""
import os
os.environ.update(CUDA_VISIBLE_DEVICES='-1', OPENBLAS_NUM_THREADS='1',
                  OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
                  PYTHONDONTWRITEBYTECODE='1')
import copy
import hashlib
import json
from pathlib import Path
import sys
import time
import traceback
import numpy as np
import psutil
import torch
from threadpoolctl import threadpool_limits
import stack_context_full_policy_v1 as full
import stack_context_policy_v1 as base
import stack_context_relative_policy_v1 as relative
from stack_context_inputs_v1 import Registry
from stack_context_relative_inputs_v1 import Registry as RelativeRegistry
from stack_context_played_bank_v1 import PlayedBank as Original
from stack_context_played_bank_routed_v1 import PlayedBank as Candidate
from board_root_accumulator_v1 import BoardRootRegrets
from exact_btn_regret_accumulator_v1 import ExactBtnRegrets
from river_matched_training_pilot_v1 import production_available

ROOT = Path('T:/Dev/GTOpen')
OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
OLD = Path('S:/GTOpen-research/stack-context-full-control-v1')
GEOMETRY = Path('S:/GTOpen-research/stack-geometry-control-v1')
QUERIES = Path('S:/GTOpen-research/stack-context-model-control-v1')
DEPTHS = (20, 40, 60, 100, 150, 200, 400)
NAME = 'stack-context-played-bank-routed-check-v1'


def read(path):
    return json.loads(Path(path).read_bytes())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, sort_keys=True, allow_nan=False)
        stream.write('\n')


def main():
    attempt, result, failure = (OUT/(NAME+s+'.json')
                                for s in ('-attempt', '-result', '-failure'))
    if any(p.exists() for p in (attempt, result, failure)):
        raise ValueError('Preserve prior implementation-check evidence')
    if (psutil.cpu_percent(interval=.2) > 50
            or psutil.virtual_memory().available < 28_000_000_000
            or not production_available()):
        print(json.dumps(dict(deferred=True, started=False))); return
    torch.set_num_threads(1)
    limits = threadpool_limits(limits=1)
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    original_reg = read(OUT/'stack-context-full-control-v1-registration.json')
    original_result = read(OUT/'stack-context-full-control-v1-result.json')
    if not original_result['complete'] or not original_result['passed']:
        raise ValueError('Passed retained fixture controls required')
    inputs = {str(p): sha(p) for p in
              (OUT/'stack-context-full-control-v1-registration.json',
               OUT/'stack-context-full-control-v1-result.json')}
    entries = []
    for depth in DEPTHS:
        context = GEOMETRY/'fixtures'/f'stack-{depth}-context.json'
        public = GEOMETRY/f'stack-{depth}-public.json'
        query = QUERIES/f'stack-{depth}-queries.json'
        for path in (context, public, query):
            if sha(path) != original_reg['inputs'][str(path)]:
                raise ValueError('Retained context/query identity changed')
            inputs[str(path)] = sha(path)
        entries.append(dict(name=f'{depth}bb', split='heldout' if depth in (60,150) else 'fit',
                            context_source=context.read_text(), public_document=read(public)))
    for width in (362,387):
        for path in (OLD/f'{width}-fixture.json',
                     *(OLD/f'{width}-{depth}-comparison.npz' for depth in DEPTHS)):
            if sha(path) != original_result['artifacts'][str(path)]:
                raise ValueError('Retained fixture/reference identity changed')
            inputs[str(path)] = sha(path)
    for module in list(sys.modules.values()):
        path = getattr(module, '__file__', None)
        if path and Path(path).is_relative_to(ROOT) and Path(path).suffix == '.py':
            inputs[str(Path(path))] = sha(path)
    inputs[str(Path(__file__).resolve())] = sha(__file__)
    save(attempt, dict(inputs=inputs, pid=os.getpid(), process_created=psutil.Process().create_time(),
                      maximum_seconds=300, math_threads=1, scientific_training=False,
                      new_deals=False, native_execution=False, gpu_used=False,
                      current_study_sources_modified=False, production_modified=False))
    started = time.monotonic(); cases = []; negatives = []

    def guard():
        if (time.monotonic()-started > 300
                or psutil.virtual_memory().available < 24_000_000_000
                or not production_available()):
            raise RuntimeError('CPU implementation check resource/time bound')

    def both_reject(label, banks, query):
        for bank in banks:
            try:
                bank.average(query, guard=guard)
            except (ValueError, KeyError, TypeError):
                pass
            else:
                raise AssertionError('Invalid query accepted: '+label)
        negatives.append(label)

    try:
        for width, kind, api in ((362,Registry,base),(387,RelativeRegistry,relative)):
            fixture = read(OLD/f'{width}-fixture.json'); registry = kind(entries)
            if fixture['registry'] != registry.manifest:
                raise ValueError('Fixture registry changed')
            resources, model = fixture['resources'], fixture['model']
            initial = copy.deepcopy(model); initial['generation'] = 0
            initial['shared'] = api.initial(registry)
            for key, state in initial['local_states'].items():
                config = dict(resources[key]['root_config']); config.pop('chance')
                state['board_root_state'] = BoardRootRegrets(**config).document()
                state['exact_btn_state'] = ExactBtnRegrets(key,resources[key]['entry_mass']).document()
            full.validate(initial,registry,resources)
            for depth, entry in zip(DEPTHS,entries):
                guard(); query = read(QUERIES/f'stack-{depth}-queries.json')
                args = dict(context_sha256=hashlib.sha256(entry['context_source'].encode()).hexdigest(),
                            resources=resources, weights_by_player=[[1.,2.],[3.,4.]],
                            completed_cycles=2, device='cpu', guard=guard)
                banks = [cls([initial,model],registry,**args) for cls in (Original,Candidate)]
                work = [[],[]]
                for implementation, bank in enumerate(banks):
                    for generation, engine in enumerate(bank.engines):
                        for overlay in engine.tables:
                            original = overlay.apply
                            def counted(rows,p,original=original,generation=generation,implementation=implementation):
                                work[implementation].append(dict(generation=generation,rows=len(rows),
                                    postflop_rows=sum(row['phase']>0 for row in rows)))
                                return original(rows,p)
                            overlay.apply = counted
                p, reach = banks[0].average(query,guard=guard)
                q, support = banks[1].average(query,guard=guard)
                if not np.array_equal(p,q) or not np.array_equal(reach,support):
                    raise AssertionError('Original and routed played averages differ')
                with np.load(OLD/f'{width}-{depth}-comparison.npz',allow_pickle=False) as arrays:
                    policy_error = float(np.max(abs(q-arrays['average_cpu'])))
                    reach_error = float(np.max(abs(support-arrays['reach_cpu'])))
                if policy_error > 1e-10 or reach_error > 1e-10:
                    raise AssertionError('Retained independent reference differs')
                if any(row['postflop_rows'] for row in work[1] if row['generation'] == 1):
                    raise AssertionError('Repeated generation checks still receive postflop rows')
                cases.append(dict(width=width,depth=depth,rows=len(p),
                    zero_reach_rows=int(np.sum(support==0)),maximum_probability_error=0.,
                    maximum_reach_error=0.,maximum_retained_probability_error=policy_error,
                    maximum_retained_reach_error=reach_error,overlay_work=work))
                for field,value in [('actor',2),('actor',True),('phase',1),('n',0),
                                    ('n',5),('hi','01'),('lo','bad')]:
                    bad=copy.deepcopy(query);bad['observations'][0][field]=value
                    both_reject(f'{width}/{depth}/{field}/{value}',banks,bad)
                bad=copy.deepcopy(query);bad['observations'][0].pop('own_history')
                both_reject(f'{width}/{depth}/missing-history',banks,bad)
                bad=copy.deepcopy(query);bad['observations'][0]['own_history']=[[0,0,0]]
                both_reject(f'{width}/{depth}/self-ancestor',banks,bad)
                both_reject(f'{width}/{depth}/wrong-context',banks,dict(query,context_source=query['context_source']+' '))
                both_reject(f'{width}/{depth}/empty',banks,dict(query,observations=[]))
        guard()
        for path, expected in inputs.items():
            if sha(path) != expected: raise ValueError('Implementation-check input changed')
        if torch.cuda.is_initialized(): raise AssertionError('Unexpected CUDA initialization')
        answer = dict(complete=True,passed=True,seconds=time.monotonic()-started,inputs=inputs,
            cases=cases,negative_cases=negatives,math_threads=1,cuda_initialized=False,
            scope='Two-model synthetic routing fixtures at seven depths and two input widths; exact original CPU agreement',
            actual_64_generation_banks_qualified=False,cuda_qualified=False,
            full_runtime_speedup_measured=False,scientific_training=False,new_deals=False,
            native_execution=False,installed_in_registered_study=False,production_modified=False)
        save(result,answer)
        print(json.dumps(dict(passed=True,cases=len(cases),negative_cases=len(negatives),
                              seconds=answer['seconds'],cuda_initialized=False)))
    except BaseException as error:
        save(failure,dict(error=repr(error),traceback=traceback.format_exc(),
                         preserve_evidence=True,automatic_retry_allowed=False))
        raise


if __name__ == '__main__':
    main()
