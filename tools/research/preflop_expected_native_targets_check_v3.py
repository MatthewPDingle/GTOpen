"""Bounded software integration: uniform model, synthetic values, native topology.

No scientific models, fitting, scientific deals, CUDA or production mutations.
Native exports use only two test holdings/player and are retained independently.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
    CUDA_VISIBLE_DEVICES='-1', PYTHONDONTWRITEBYTECODE='1')
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback

import numpy as np
import psutil

TOOLS = Path(r'T:\Dev\GTOpen\tools\research')
sys.path.append(str(TOOLS))
from preflop_expected_native_targets_v1 import (FrozenExpectedTargets, FrozenAllPreflopPolicy,
    canonical_card_keys, physical_class_mass)
from preflop_expected_regret_accumulator_v1 import PreflopExpectedRegrets
from stack_context_preflop_expected_components_v2 import PreflopExpectedComponents
from stack_context_inputs_v1 import Registry, digest as text_sha
import stack_context_policy_v1 as shared
import stack_context_full_policy_v1 as full
from board_root_accumulator_v1 import BoardRootRegrets, CHANCE, digest
from exact_btn_regret_accumulator_v1 import ExactBtnRegrets
from sampled_physical_deals_v1 import PhysicalDeals
from stack_context_board_targets_v1 import preflop_policy, policy_rows
from stack_context_teacher_path_v1 import card_key
from storage_strategic_common_prior_20260920 import PAIRS, CLASSES

import argparse
_parser = argparse.ArgumentParser()
_parser.add_argument('--evidence-dir', type=Path, required=True)
_parser.add_argument('--result', type=Path, required=True)
_args = _parser.parse_args()
STAGE = _args.evidence_dir.resolve()
RESULT = _args.result.resolve()
POPULATION = Path(r'S:\GTOpen-research\stack-context-population-v1')
OUT = TOOLS.parents[1]/'research/preflop-evolution/blind-defense-20260922'
INPUTS = {}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    INPUTS[str(path)] = sha(path)
    return Path(path).read_text(encoding='utf-8')


def write(path, value):
    with Path(path).open('x', encoding='utf-8') as f:
        json.dump(value, f, indent=2, allow_nan=False)


def matrix_source(source):
    c = json.loads(source); sampler = PhysicalDeals(source, mode='full_deck', seed=0)
    w = sampler.weights
    allowed = ((PAIRS[:, None, 0] != PAIRS[None, :, 0]) & (PAIRS[:, None, 0] != PAIRS[None, :, 1])
        & (PAIRS[:, None, 1] != PAIRS[None, :, 0]) & (PAIRS[:, None, 1] != PAIRS[None, :, 1]))
    joint = allowed*w[0, :, None]*w[1, None, :]
    total = float(joint.sum()); joint /= total
    keys = CLASSES[:, None]*169+CLASSES[None, :]
    def group(x):
        return np.bincount(keys.ravel(), weights=x.ravel(), minlength=169**2).reshape(169, 169)
    mass = group(joint)
    raw, normalizer = physical_class_mass(w)
    assert np.max(abs(raw/normalizer-mass)) < 1e-12
    root = c['nodes'][0]; jam = c['nodes'][root['children'][3]]
    folded, called = [c['nodes'][i] for i in jam['children']]
    rake = min(called['pot']*c['rake_fraction'], c['rake_cap'])
    strengths = PAIRS.sum(1)
    win = (strengths[:, None] > strengths[None, :])+.5*(strengths[:, None] == strengths[None, :])
    bb = group(joint*(-called['invested'][0]+(called['pot']-rake)*win))
    btn = group(joint*(-called['invested'][1]+(called['pot']-rake)*(1-win)))
    d = dict(format=1, context_sha256=text_sha(source), class_mass=mass.tolist(),
        bb_showdown_entries=bb.tolist(), btn_showdown_entries=btn.tolist(),
        bb_fold=c['nodes'][root['children'][0]]['leaf']['utilities'][0],
        bb_uncontested=folded['leaf']['utilities'][0], btn_fold=folded['leaf']['utilities'][1],
        conserved_showdown_total=called['pot']-sum(called['invested'])-rake,
        canonical_population_rows=0, scope='Synthetic strengths, original entry law; software control only')
    return json.dumps(d, sort_keys=True, separators=(',', ':')), mass


def native_template(depth, board, context_source):
    exe = TOOLS.parents[1]/'target/release/examples/hu_fixed_board_tree_v1.exe'
    proof_path = OUT/'stack-context-native-adapters-v1-cpu-tests.json'
    proof = json.loads(read(proof_path))
    assert proof['passed'] and sha(exe) == proof['inputs'][str(exe)]
    INPUTS[str(exe)] = sha(exe)
    context_path = POPULATION/f'stack-{depth}'/'context.json'
    assert context_path.read_text(encoding='utf-8') == context_source
    live = PAIRS[~np.isin(PAIRS, board).any(1)]
    request = dict(board=board, hands=[live[:2].tolist(), live[5:7].tolist()])
    stem = STAGE/f'preflop-native-software-template-stack-{depth}'
    req, started, result, tree = [Path(str(stem)+s) for s in ('-request.json', '-started.json', '-result.json', '-tree.json')]
    if result.exists():
        saved = json.loads(read(result))
        assert saved['executable_sha256'] == sha(exe) and saved['context_sha256'] == text_sha(context_source)
        assert saved['request_sha256'] == sha(req) and json.loads(req.read_bytes()) == request
        assert saved['tree_sha256'] == sha(tree) and saved['exit_code'] == 0
        return json.loads(read(tree)), request
    assert not started.exists() and not tree.exists() and not req.exists()
    assert psutil.virtual_memory().available > 20_000_000_000
    write(req, request)
    write(started, dict(executable_sha256=sha(exe), context_sha256=text_sha(context_source),
        request_sha256=sha(req), maximum_seconds=60, native_export_only=True, scientific_attempt=False))
    done = subprocess.run([str(exe), str(context_path), str(req)], capture_output=True,
        timeout=60, creationflags=subprocess.CREATE_NO_WINDOW)
    assert done.returncode == 0, done.stderr.decode(errors='replace')[-1000:]
    with tree.open('xb') as f: f.write(done.stdout)
    saved = dict(executable_sha256=sha(exe), context_sha256=text_sha(context_source),
        request_sha256=sha(req), tree_sha256=sha(tree), exit_code=done.returncode,
        native_export_only=True, scientific_attempt=False, bytes=len(done.stdout))
    write(result, saved)
    for p in (req, started, result, tree): INPUTS[str(p)] = sha(p)
    return json.loads(done.stdout), request


def observation(hi, lo, actor, phase, n):
    cards = [(lo >> (6*i)) & 63 for i in range(7)]
    active = []
    for i, c in enumerate(cards):
        active.extend((19*i+(13 if c == 63 else c//4), 19*i+14+(4 if c == 63 else c % 4)))
    h = (int(hi) & ((1 << 63)-1)) >> 4; history = []
    while h > 1: history.append(h & 7); h >>= 3
    history.reverse()
    active.extend((133+actor, 135+phase, 139+(int(hi) & 15)))
    active.extend(155+6*i+(history[i] if i < len(history) else 0) for i in range(19))
    return dict(hi=hi, lo=str(lo), actor=actor, phase=phase, n=n, active_features=active)


def widen(template, request, full_request):
    tree = copy.deepcopy(template); hands = np.asarray(full_request['hands'][0])
    tree['hands'] = full_request['hands']
    # Native topology/cashflows are retained; strengths are deliberately synthetic.
    ranks = (hands.sum(1)*7+(hands[:, 1]-hands[:, 0]) % 5).tolist()
    tree['ranks'] = [ranks, ranks.copy()]
    cache = {}; native_rows = 0; scalar_keys = 0
    for branch in tree['branches']:
        for node in branch['nodes']:
            if node['kind'] != 0: continue
            old = node['observations']; actor = node['actor']; phase = node['street']+1
            small_keys = canonical_card_keys(np.asarray(request['hands'][actor]), request['board'], actor, phase)
            for o, lo in zip(old, small_keys):
                assert o == observation(o['hi'], int(lo), actor, phase, len(node['children']))
                native_rows += 1
            key = (actor, phase)
            if key not in cache:
                cache[key] = canonical_card_keys(hands, request['board'], actor, phase)
                for j in range(0, len(hands), 37):
                    assert str(int(cache[key][j])) == card_key(hands[j].tolist(), request['board'][:(0, 3, 4, 5)[phase]], actor)
                    scalar_keys += 1
            node['observations'] = [observation(old[0]['hi'], int(lo), actor, phase, len(node['children'])) for lo in cache[key]]
    return tree, native_rows, scalar_keys


def main():
    began = time.monotonic(); entries = []; cases = []; resources = {}; locals_ = {}
    for depth in (20, 200):
        folder = POPULATION/f'stack-{depth}'
        source = read(folder/'context.json'); key = text_sha(source)
        public = json.loads(read(folder/'public.json')); catalog = read(folder/'initial-catalog.json')
        physical = read(folder/'physical-catalog.json'); ms, mass = matrix_source(source)
        config = dict(context_sha256=key, matrix_sha256=text_sha(ms), entry_mass=mass.sum(1).tolist(),
            physical_budget=169, boards_per_generation=1, board_seed=depth+17, chance=CHANCE)
        resources[key] = dict(catalog_source=catalog, matrix_sha256=text_sha(ms),
            entry_mass=mass.sum(0).tolist(), root_config=config)
        root = BoardRootRegrets(**{k:v for k, v in config.items() if k != 'chance'}); exact = ExactBtnRegrets(key, mass.sum(0))
        locals_[key] = full.local_document(catalog_source=catalog, matrix_sha256=text_sha(ms),
            root_config=config, root=root, exact=exact)
        entries.append(dict(name=f'{depth}bb', split='fit', context_source=source, public_document=public))
        state = PreflopExpectedRegrets(context_source=source, matrix_source=ms,
            generation_scale=169, boards_per_generation=1, board_seed=depth+17)
        cases.append(dict(depth=depth, source=source, key=key, physical=physical, matrix=ms, state=state))
    registry = Registry(entries)
    model = full.model(registry, shared.initial(registry), locals_, resources)
    model_source = json.dumps(model, sort_keys=True, separators=(',', ':'))
    results = []; rejected = []
    for case in cases:
        state = case['state']; snapshot = state.document()
        kwargs = dict(state=state, model_source=model_source, registry=registry, resources=resources,
            physical_catalog_source=case['physical'], expected_physical_catalog_sha256=text_sha(case['physical']),
            matrix_source=case['matrix'])
        targets = FrozenExpectedTargets(**kwargs); pre = targets.played_preflop()
        catalog_pre, error = preflop_policy(json.loads(case['physical']), state.context, targets.policy)
        assert error == 0 and all(np.array_equal(catalog_pre[i], pre[i]) for i in pre)
        altered = {i:p.copy() for i, p in pre.items()}
        for i, p in altered.items():
            raw = 1+(np.arange(169)[:, None]+np.arange(p.shape[1])[None, :]+i) % 7
            altered[i] = raw/raw.sum(1)[:, None]
        overlay = FrozenAllPreflopPolicy(targets._base, altered, state.context, state.matrix)
        got, error = preflop_policy(json.loads(case['physical']), state.context, overlay)
        assert error == 0 and all(np.array_equal(got[i], altered[i]) for i in got)
        plan = state.plan(); board = plan['boards'][0]; request, ids = targets.request(board)
        assert len(ids) == 1081 and any(np.any(w[ids] == 0) for w in targets._sampler.weights)
        template, small_request = native_template(case['depth'], board, case['source'])
        tree, native_rows, scalar_keys = widen(template, small_request, request)
        post = policy_rows(tree, targets._base)
        wrapped_post = policy_rows(tree, overlay)
        assert all(np.array_equal(p[i], q[i]) for p, q in zip(post, wrapped_post) for i in p)
        expected = PreflopExpectedComponents(state.context, state.matrix, pre).board(tree, post,
            [w[ids] for w in targets._sampler.weights], [CLASSES[ids], CLASSES[ids]], targets._sampler.masses[0])
        raw = json.dumps(tree, separators=(',', ':')).encode(); tree_sha = hashlib.sha256(raw).hexdigest()
        record = targets.draw_record(raw, expected_tree_sha256=tree_sha, draw_index=0)
        maximum = max(float(np.max(abs(np.asarray(record['values'][str(i)])-expected[i]['q']))) for i in pre)
        assert maximum == 0 and state.document() == snapshot
        evidence = targets.generation_evidence(state, plan, [record])
        assert state.document() == snapshot
        restored = PreflopExpectedRegrets.restore(snapshot, context_source=case['source'],
            matrix_source=case['matrix'], expected_config=state.config)
        state.step(plan, evidence, played_policy=pre); restored.step(plan, evidence, played_policy=pre)
        assert state.document() == restored.document()
        def refuse(label, operation):
            before = state.document()
            try: operation()
            except (ValueError, KeyError, TypeError, IndexError): pass
            else: raise AssertionError('Accepted invalid '+label)
            assert state.document() == before
            rejected.append(f"{case['depth']}bb:{label}")
        refuse('advanced-parent', lambda:targets.generation_evidence(state, plan, [record]))
        refuse('tree-identity', lambda:targets.draw_record(raw, expected_tree_sha256='0'*64, draw_index=0))
        refuse('missing-record', lambda:targets.generation_evidence(restored, plan, []))
        for label, change in [
            ('wrong-board', lambda t:t.update(board=[0, 1, 2, 3, 4])),
            ('missing-hand', lambda t:t['hands'][0].pop()),
            ('missing-rank', lambda t:t['ranks'][0].pop()),
            ('foreign-hand-row', lambda t:t['branches'][0]['nodes'][0]['observations'].reverse()),
            ('wrong-actor', lambda t:t['branches'][0]['nodes'][0]['observations'][0].update(actor=1)),
            ('invented-history', lambda t:t['branches'][0]['nodes'][0]['observations'][0].update(own_history=[])),
            ('wrong-prefix', lambda t:t['branches'][0]['nodes'][0]['observations'][0].update(lo='0'))]:
            bad = copy.deepcopy(tree); change(bad); encoded = json.dumps(bad, separators=(',', ':')).encode()
            refuse(label, lambda encoded=encoded:targets.draw_record(encoded,
                expected_tree_sha256=hashlib.sha256(encoded).hexdigest(), draw_index=0))
        results.append(dict(stack=case['depth'], decision_nodes=len(pre), complete_private_hands=1081,
            native_prefix_rows_checked=native_rows, independent_scalar_card_keys_checked=scalar_keys,
            target_transport_maximum_error=maximum, preflop_overlay_exact=True, postflop_policy_unchanged=True,
            complete_update_and_restore_exact=True, bytes_of_synthetic_widened_tree=len(raw)))
    for module in list(sys.modules.values()):
        path = getattr(module, '__file__', None)
        if path and Path(path).suffix == '.py' and (Path(path).is_relative_to(TOOLS.parents[1]) or Path(path).parent == STAGE):
            INPUTS[str(Path(path).resolve())] = sha(path)
    INPUTS[str(Path(__file__).resolve())] = sha(__file__)
    result = dict(passed=True, seconds=time.monotonic()-began, cases=results, refused_cases=rejected,
        inputs=INPUTS, initial_uniform_362_input_model=True, synthetic_strengths=True,
        native_topology_export_only=True, scientific_model_inference=False, scientific_training=False,
        scientific_attempt=False, gpu_used=False, production_modified=False,
        native_worker_cycle_integration_qualified=False, accuracy_qualified=False)
    path = RESULT
    write(path, result)
    print(json.dumps({k:v for k, v in result.items() if k != 'inputs'}, indent=2))


if __name__ == '__main__':
    try:
        main()
    except Exception:
        failure = RESULT.with_name(RESULT.stem+'-failure.json')
        if not failure.exists():
            write(failure, dict(error=traceback.format_exc(), source_sha256=sha(__file__),
                provider_sha256=sha(TOOLS/'preflop_expected_native_targets_v1.py'),
                scientific_attempt=False, production_modified=False))
        raise
