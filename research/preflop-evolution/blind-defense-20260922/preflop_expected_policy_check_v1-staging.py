"""CPU software controls for typed all-node policy; no fitting or science run."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
                  CUDA_VISIBLE_DEVICES='-1', PYTHONDONTWRITEBYTECODE='1')
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import time
import traceback

import numpy as np

TOOLS = Path(r'T:\Dev\GTOpen\tools\research')
OUT = TOOLS.parents[1]/'research/preflop-evolution/blind-defense-20260922'
POP = Path(r'S:\GTOpen-research\stack-context-population-v1')
sys.path.append(str(TOOLS))
import preflop_expected_policy_v1 as new
from preflop_expected_native_targets_v2 import FrozenExpectedTargets
from preflop_expected_native_targets_v1 import FrozenExpectedTargets as LegacyTransport
from preflop_expected_regret_accumulator_v1 import PreflopExpectedRegrets
from preflop_expected_regret_accumulator_check_v1 import evidence
from board_root_accumulator_v1 import BoardRootRegrets, CHANCE
from exact_btn_regret_accumulator_v1 import ExactBtnRegrets
from stack_context_inputs_v1 import Registry, digest as text_sha
import stack_context_policy_v1 as shared
import stack_context_full_policy_v1 as full
from stack_context_board_targets_v1 import policy_rows, preflop_policy

INPUTS = {}

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read(path):
    INPUTS[str(Path(path).resolve())] = sha(path)
    return Path(path).read_text(encoding='utf-8')

def queries(physical, context):
    rows = json.loads(physical)['rows']
    obs = [copy.deepcopy(row['observation']) for row in rows]
    index = {(row['node'], tuple(row['hand'])):i for i, row in enumerate(rows)}
    ancestors = {}
    def walk(i, path):
        if not context['nodes'][i]['children']: return
        ancestors[i] = path
        for a, child in enumerate(context['nodes'][i]['children']): walk(child, path+[(i, a)])
    walk(0, [])
    for row, o in zip(rows, obs):
        o['own_history'] = [[index[(n, tuple(row['hand']))], a, len(context['nodes'][n]['children'])]
            for n, a in ancestors[row['node']] if context['nodes'][n]['actor'] == o['actor']]
    return dict(context_source=json.loads(physical)['context_source'], observations=obs)

def main(output):
    began = time.monotonic()
    helper_path = OUT/'preflop_expected_native_targets_check_v2-staging.py'
    read(helper_path)
    spec = importlib.util.spec_from_file_location('retained_native_control', helper_path)
    helper = importlib.util.module_from_spec(spec); spec.loader.exec_module(helper)
    entries = []; cases = {}; states = {}; resources = {}; legacy_resources = {}; legacy_local = {}
    for depth, split in ((20, 'fit'), (200, 'fit'), (60, 'heldout')):
        folder = POP/f'stack-{depth}'
        source = read(folder/'context.json'); key = text_sha(source)
        entries.append(dict(name=f'{depth}bb', split=split, context_source=source,
                            public_document=json.loads(read(folder/'public.json'))))
        physical = read(folder/'physical-catalog.json')
        cases[depth] = dict(key=key, source=source, physical=physical)
        if split != 'fit': continue
        ms, mass = helper.matrix_source(source)
        state = PreflopExpectedRegrets(context_source=source, matrix_source=ms,
            generation_scale=169, boards_per_generation=1, board_seed=depth+17)
        states[key] = state
        resources[key] = dict(physical_catalog_source=physical,
            physical_catalog_sha256=text_sha(physical), matrix_source=ms, expected_config=state.config)
        catalog = read(folder/'initial-catalog.json')
        config = dict(context_sha256=key, matrix_sha256=text_sha(ms), entry_mass=mass.sum(1).tolist(),
            physical_budget=169, boards_per_generation=1, board_seed=depth+17, chance=CHANCE)
        legacy_resources[key] = dict(catalog_source=catalog, matrix_sha256=text_sha(ms),
            entry_mass=mass.sum(0).tolist(), root_config=config)
        root = BoardRootRegrets(**{k:v for k, v in config.items() if k != 'chance'})
        legacy_local[key] = full.local_document(catalog_source=catalog, matrix_sha256=text_sha(ms),
            root_config=config, root=root, exact=ExactBtnRegrets(key, mass.sum(0)))
    registry = Registry(entries)
    shared0 = shared.initial(registry)
    initial = new.model(registry, shared0, states, resources)
    legacy = full.model(registry, shared0, legacy_local, legacy_resources)
    initial_sha = hashlib.sha256(json.dumps(initial, sort_keys=True).encode()).hexdigest()
    rejected = []
    def refuse(label, operation):
        try: operation()
        except (ValueError, KeyError, TypeError, IndexError): pass
        else: raise AssertionError('Accepted invalid '+label)
        assert hashlib.sha256(json.dumps(initial, sort_keys=True).encode()).hexdigest() == initial_sha
        rejected.append(label)
    result_cases = []; native_parity = None
    for depth in (20, 200):
        case = cases[depth]; key = case['key']; state = states[key]
        engine = new.ExpectedPolicy(initial, registry, context_sha256=key, resources=resources)
        q = queries(case['physical'], state.context)
        prepared = engine.prepare(q); p = engine.infer(prepared)
        assert prepared['mask'].all() and np.max(abs(p.sum(1)-1)) < 1e-12
        got, suit = preflop_policy(json.loads(case['physical']), state.context, engine)
        pre = engine.played_preflop()
        assert suit == 0 and all(np.array_equal(got[i], pre[i]) for i in pre)
        model_source = json.dumps(initial, sort_keys=True, separators=(',', ':'))
        targets = FrozenExpectedTargets(state=state, model_source=model_source,
                                        registry=registry, resources=resources)
        if depth == 20:
            # Reuse the preserved native software export; never invoke another job.
            assert (OUT/'preflop-native-software-template-stack-20-result.json').exists()
            board = state.plan()['boards'][0]
            template, small = helper.native_template(depth, board, case['source'])
            request, _ = targets.request(board)
            tree, native_rows, scalar_keys = helper.widen(template, small, request)
            old = LegacyTransport(state=state, model_source=json.dumps(legacy, sort_keys=True, separators=(',', ':')),
                registry=registry, resources=legacy_resources, physical_catalog_source=case['physical'],
                expected_physical_catalog_sha256=text_sha(case['physical']), matrix_source=resources[key]['matrix_source'])
            rows = policy_rows(tree, engine); before = policy_rows(tree, old.policy)
            assert all(np.array_equal(a[i], b[i]) for a, b in zip(rows, before) for i in a)
            raw = json.dumps(tree, separators=(',', ':')).encode(); identity = hashlib.sha256(raw).hexdigest()
            record = targets.draw_record(raw, expected_tree_sha256=identity, draw_index=0)
            old_record = old.draw_record(raw, expected_tree_sha256=identity, draw_index=0)
            assert record['values'] == old_record['values']
            complete = targets.generation_evidence(state, state.plan(), [record])
            assert complete['model_sha256'] == text_sha(model_source)
            refuse('missing-board-record-at-current-parent',
                   lambda:targets.generation_evidence(state, state.plan(), []))
            bad = copy.deepcopy(tree)
            first = bad['branches'][0]['nodes'][0]['observations'][0]['active_features']
            first[first.index(19*5+13)] = 19*5
            first[first.index(19*5+14+4)] = 19*5+14
            bad_raw = json.dumps(bad, separators=(',', ':')).encode()
            refuse('future-card-features', lambda:targets.draw_record(bad_raw,
                expected_tree_sha256=hashlib.sha256(bad_raw).hexdigest(), draw_index=0))
            native_parity = dict(native_prefix_rows_checked=native_rows,
                independent_scalar_card_keys_checked=scalar_keys, all_node_values_exact=True,
                postflop_probabilities_bit_identical=True, no_new_native_invocation=True)
        plan, target, _ = evidence(state, pre)
        target['model_sha256'] = text_sha(model_source)
        for draw in target['draws']: draw['model_sha256'] = text_sha(model_source)
        state.step(plan, target, played_policy=pre)
        result_cases.append(dict(stack=depth, physical_preflop_rows=len(q['observations']),
            decision_nodes=len(pre), all_preflop_rows_overridden=True))
    nets = shared.uniform_networks()
    for net in nets: net['b2'] = [.25, .5, 1., 2.]
    shared1 = shared.model(registry, generation=1, networks=nets,
                           preflop_tables={k:[None, None] for k in registry.fit_contexts})
    advanced = new.model(registry, shared1, states, resources)
    for depth in (20, 200):
        case = cases[depth]; key = case['key']; state = states[key]
        engine = new.ExpectedPolicy(advanced, registry, context_sha256=key, resources=resources)
        actual, _ = preflop_policy(json.loads(case['physical']), state.context, engine)
        fallback = {i:np.tile(np.array([.25, .5, 1., 2.])[:state.specs[i]['arity']], (169, 1)) for i in state.nodes}
        for p in fallback.values(): p /= p.sum(1)[:, None]
        wanted = state.probabilities(fallback)
        assert all(np.array_equal(actual[i], wanted[i]) for i in actual)
        assert any(np.any(abs(p-fallback[i]) > 1e-8) for i, p in actual.items())
        q = queries(case['physical'], state.context)
        mixture, support = new.average([initial, advanced], registry, q, context_sha256=key,
            resources=resources, completed_cycles=2, weights_by_player=[[1, 2], [1, 2]])
        probabilities = [new.predict(v, registry, q, context_sha256=key, resources=resources)[0]
                         for v in (initial, advanced)]
        manual = np.zeros_like(mixture); manual_mass = np.zeros(len(mixture))
        for i, o in enumerate(q['observations']):
            for generation, p in enumerate(probabilities):
                reach = float(generation+1)
                for parent, action, _ in o['own_history']: reach *= p[parent, action]
                manual[i] += reach*p[i]; manual_mass[i] += reach
            if manual_mass[i]: manual[i] /= manual_mass[i]
            else: manual[i, :o['n']] = 1/o['n']
        assert np.max(abs(mixture-manual)) < 1e-12 and np.array_equal(support, manual_mass)
    held = cases[60]
    engine = new.ExpectedPolicy(advanced, registry, context_sha256=held['key'], resources=resources)
    q = queries(held['physical'], json.loads(held['source']))
    p = engine.prepare(q)
    assert not p['mask'].any() and engine._state is None
    refuse('heldout-owned-state', engine.played_preflop)
    for label, mutate in (
        ('legacy-policy-type', lambda v:v.update(policy_type=full.TYPE)),
        ('legacy-overlay-order', lambda v:v.update(override_order=full.ORDER)),
        ('missing-fitting-state', lambda v:v['local_states'].pop(registry.fit_contexts[0])),
        ('detached-generation', lambda v:v.update(generation=1)),
        ('changed-catalog-id', lambda v:v['local_states'][registry.fit_contexts[0]].update(physical_catalog_sha256='0'*64)),
        ('changed-state-seal', lambda v:v['local_states'][registry.fit_contexts[0]]['cumulative_state'].update(state_sha256='0'*64))):
        bad = copy.deepcopy(initial); mutate(bad)
        refuse(label, lambda bad=bad:new.validate(bad, registry, resources))
    bad_resources = copy.deepcopy(resources)
    bad_resources[registry.fit_contexts[0]]['physical_catalog_source'] += ' '
    refuse('changed-resource-catalog', lambda:new.validate(initial, registry, bad_resources))
    bad = copy.deepcopy(initial); bad['local_states'][held['key']] = next(iter(bad['local_states'].values()))
    refuse('heldout-local-state-in-model', lambda:new.validate(bad, registry, resources))
    refuse('partial-joint-generation', lambda:new.model(registry, shared0, states, resources))
    key = cases[20]['key']; q = queries(cases[20]['physical'], states[key].context)
    refuse('unplayed-model-in-average', lambda:new.average([initial, advanced], registry, q,
        context_sha256=key, resources=resources, completed_cycles=1, weights_by_player=[[1, 2], [1, 2]]))
    refuse('reordered-bank', lambda:new.average([advanced, initial], registry, q,
        context_sha256=key, resources=resources, completed_cycles=2, weights_by_player=[[1, 2], [1, 2]]))
    with tempfile.TemporaryDirectory(prefix='expected-policy-control-', dir=Path(__file__).parent) as folder:
        ref = new.write_model(folder, advanced, registry, resources)
        restored = new.read_model(folder, ref, registry, resources)
        assert restored == advanced
        refuse('wrong-model-ref-generation', lambda:new.read_model(folder, dict(ref, generation=0), registry, resources))
    for module in list(sys.modules.values()):
        path = getattr(module, '__file__', None)
        if path and Path(path).suffix == '.py' and (Path(path).is_relative_to(TOOLS.parents[1])
                or Path(path).parent == Path(__file__).parent): INPUTS[str(Path(path).resolve())] = sha(path)
    INPUTS[str(Path(__file__).resolve())] = sha(__file__)
    result = dict(passed=True, seconds=time.monotonic()-began, cases=result_cases,
        native_transport_parity=native_parity, refused_cases=rejected,
        all_node_state_overrides_shared_preflop=True, heldout_network_only=True,
        own_history_average_independent_loop_parity=True, content_addressed_model_roundtrip_exact=True,
        inputs=INPUTS, scientific_attempt=False, scientific_training=False,
        scientific_model_inference=False, gpu_used=False, production_modified=False,
        cycle_checkpoint_integration_qualified=False, accuracy_qualified=False)
    with output.open('x', encoding='utf-8') as f: json.dump(result, f, indent=2, allow_nan=False)
    print(json.dumps({k:v for k, v in result.items() if k != 'inputs'}, indent=2))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--result', type=Path, required=True)
    args = parser.parse_args()
    try: main(args.result)
    except Exception:
        failure = args.result.with_name(args.result.stem+'-failure.json')
        with failure.open('x', encoding='utf-8') as f:
            json.dump(dict(error=traceback.format_exc(), source_sha256=sha(__file__),
                inputs=INPUTS, scientific_attempt=False, production_modified=False), f, indent=2)
        raise
