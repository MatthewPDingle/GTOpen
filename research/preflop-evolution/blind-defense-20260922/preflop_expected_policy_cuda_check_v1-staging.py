"""Bounded synthetic CPU/CUDA parity, both declared input representations."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
                  PYTHONDONTWRITEBYTECODE='1')
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback
import numpy as np
import psutil
import torch

TOOLS = Path(r'T:\Dev\GTOpen\tools\research')
OUT = TOOLS.parents[1]/'research/preflop-evolution/blind-defense-20260922'
POP = Path(r'S:\GTOpen-research\stack-context-population-v1')
sys.path.append(str(TOOLS))
from bounded_parallel_evaluation_archive_v2 import production_available
from sampled_physical_deals_v1 import PhysicalDeals
from preflop_expected_native_targets_v1 import physical_class_mass, text_sha
from preflop_expected_regret_accumulator_v1 import PreflopExpectedRegrets, TARGET
from stack_context_preflop_expected_components_v2 import PreflopExpectedComponents
from board_root_accumulator_v1 import digest
from stack_context_inputs_v1 import Registry
from stack_context_relative_inputs_v1 import Registry as RelativeRegistry
from stack_context_board_targets_v1 import preflop_policy
import stack_context_policy_v1 as base
import stack_context_relative_policy_v1 as relative
import preflop_expected_policy_v1 as new

INPUTS = {}

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):
    INPUTS[str(Path(path).resolve())] = sha(path)
    return Path(path).read_text(encoding='utf-8')

def guard():
    if not production_available() or psutil.virtual_memory().available < 20_000_000_000:
        raise RuntimeError('Yield to active production or RAM pressure')
    free, total = torch.cuda.mem_get_info()
    if free < 2_000_000_000: raise RuntimeError('Insufficient GPU reserve')
    raw = subprocess.check_output(['nvidia-smi', '--query-gpu=utilization.gpu', '--format=csv,noheader,nounits'])
    if max(int(v) for v in raw.decode().split()) > 35:
        raise RuntimeError('Yield to heavier GPU work')
    return dict(available_ram=psutil.virtual_memory().available, free_gpu_bytes=free, total_gpu_bytes=total)

def synthetic_matrix(source):
    c = json.loads(source); sampler = PhysicalDeals(source, mode='full_deck', seed=0)
    raw, total = physical_class_mass(sampler.weights); mass = raw/total
    root = c['nodes'][0]; jam = c['nodes'][root['children'][3]]
    fold, call = [c['nodes'][i] for i in jam['children']]
    rake = min(call['pot']*c['rake_fraction'], c['rake_cap'])
    net = call['pot']-rake
    value = dict(format=1, context_sha256=text_sha(source), class_mass=mass.tolist(),
        bb_showdown_entries=(mass*(-call['invested'][0]+.5*net)).tolist(),
        btn_showdown_entries=(mass*(-call['invested'][1]+.5*net)).tolist(),
        bb_fold=c['nodes'][root['children'][0]]['leaf']['utilities'][0],
        bb_uncontested=fold['leaf']['utilities'][0], btn_fold=fold['leaf']['utilities'][1],
        conserved_showdown_total=net-sum(call['invested']), canonical_population_rows=0,
        scope='Synthetic all-tied strengths for inference software check only')
    return json.dumps(value, sort_keys=True, separators=(',', ':'))

def main(output):
    torch.set_num_threads(1)
    torch.backends.cuda.matmul.allow_tf32 = False; torch.backends.cudnn.allow_tf32 = False
    admission = guard(); began = time.monotonic()
    torch.cuda.reset_peak_memory_stats()
    entries = []; sources = {}
    for depth in (20, 200):
        folder = POP/f'stack-{depth}'; source = read(folder/'context.json'); key = text_sha(source)
        entries.append(dict(name=f'{depth}bb', split='fit', context_source=source,
                            public_document=json.loads(read(folder/'public.json'))))
        sources[depth] = dict(source=source, key=key, matrix=synthetic_matrix(source),
            physical=read(folder/'physical-catalog.json'))
    results = []
    for registry_class, api in ((Registry, base), (RelativeRegistry, relative)):
        guard(); registry = registry_class(entries); states = {}; resources = {}
        for depth, case in sources.items():
            state = PreflopExpectedRegrets(context_source=case['source'], matrix_source=case['matrix'],
                generation_scale=169, boards_per_generation=1, board_seed=depth+17)
            states[case['key']] = state
            resources[case['key']] = dict(physical_catalog_source=case['physical'],
                physical_catalog_sha256=text_sha(case['physical']), matrix_source=case['matrix'], expected_config=state.config)
        initial = new.model(registry, api.initial(registry), states, resources)
        initial_source = json.dumps(initial, sort_keys=True, separators=(',', ':'))
        for key, state in states.items():
            engine = new.ExpectedPolicy(initial, registry, context_sha256=key, resources=resources)
            p = engine.played_preflop(); exact = PreflopExpectedComponents(state.context, state.matrix, p).exact()
            plan = state.plan(); values = state.encoded({i:np.zeros_like(x) for i, x in p.items()})
            record = dict(draw_index=0, board=plan['boards'][0], model_sha256=text_sha(initial_source),
                tree_sha256='a'*64, policy_recipe_sha256='b'*64, values=values, values_sha256=digest(values))
            evidence = dict(format=1, method=TARGET, generation=0, plan_sha256=digest(plan),
                context_sha256=key, matrix_sha256=state.config['matrix_sha256'], model_sha256=text_sha(initial_source),
                played_policy_sha256=digest(state.encoded(p)),
                exact_terms_sha256=digest(state.encoded({i:r['q'] for i, r in exact.items()})), draws=[record])
            state.step(plan, evidence, played_policy=p)
        rng = np.random.Generator(np.random.PCG64(73191))
        nets = api.uniform_networks()
        for net in nets:
            for name in ('w0', 'w1', 'w2'): net[name] = rng.normal(0, .001, len(net[name])).tolist()
            net['b0'] = rng.uniform(.01, .02, 64).tolist(); net['b1'] = rng.uniform(.01, .02, 64).tolist()
            net['b2'] = [.25, .5, 1., 2.]
        shared = api.model(registry, generation=1, networks=nets,
                           preflop_tables={k:[None, None] for k in registry.fit_contexts})
        value = new.model(registry, shared, states, resources)
        for depth, case in sources.items():
            guard(); key = case['key']
            cpu = new.ExpectedPolicy(value, registry, context_sha256=key, resources=resources)
            gpu = new.ExpectedPolicy(value, registry, context_sha256=key, resources=resources, device='cuda')
            c, _ = preflop_policy(json.loads(case['physical']), states[key].context, cpu)
            g, _ = preflop_policy(json.loads(case['physical']), states[key].context, gpu)
            pre_error = max(float(np.max(abs(c[i]-g[i]))) for i in c)
            # The saved export has actual native visible prefixes at every street.
            path = OUT/f'preflop-native-software-template-stack-{depth}-tree.json'
            tree = json.loads(read(path))
            observations = [o for b in tree['branches'] for n in b['nodes'] if n['kind'] == 0 for o in n['observations']]
            pc = cpu.score_rows(case['source'], observations); pg = gpu.score_rows(case['source'], observations)
            post_error = float(np.max(abs(pc-pg)))
            assert pre_error <= 1e-12 and post_error <= 1e-12
            assert {o['phase'] for o in observations} == {1, 2, 3}
            results.append(dict(input_width=cpu.width, stack=depth, preflop_nodes=len(c),
                postflop_rows=len(observations), phases=[1, 2, 3], preflop_maximum_error=pre_error,
                postflop_maximum_error=post_error))
            del cpu, gpu
    torch.cuda.synchronize()
    for module in list(sys.modules.values()):
        path = getattr(module, '__file__', None)
        if path and Path(path).suffix == '.py' and (Path(path).is_relative_to(TOOLS.parents[1])
                or Path(path).parent == Path(__file__).parent): INPUTS[str(Path(path).resolve())] = sha(path)
    INPUTS[str(Path(__file__).resolve())] = sha(__file__)
    result = dict(passed=True, seconds=time.monotonic()-began, cases=results, inputs=INPUTS,
        admission=admission, torch_version=torch.__version__, cuda_version=torch.version.cuda,
        device=torch.cuda.get_device_name(), peak_cuda_allocated_bytes=torch.cuda.max_memory_allocated(),
        process_rss_bytes=psutil.Process().memory_info().rss,
        synthetic_strengths=True, synthetic_networks=True, no_new_native_invocation=True,
        scientific_attempt=False, scientific_training=False, scientific_model_inference=False,
        gpu_used=True, production_modified=False, accuracy_qualified=False,
        performance_benchmark=False)
    with output.open('x', encoding='utf-8') as f: json.dump(result, f, indent=2, allow_nan=False)
    print(json.dumps({k:v for k, v in result.items() if k != 'inputs'}, indent=2))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--result', type=Path, required=True)
    args = parser.parse_args()
    try: main(args.result)
    except Exception:
        with args.result.with_name(args.result.stem+'-failure.json').open('x', encoding='utf-8') as f:
            json.dump(dict(error=traceback.format_exc(), inputs=INPUTS, source_sha256=sha(__file__),
                           scientific_attempt=False, production_modified=False), f, indent=2)
        raise
