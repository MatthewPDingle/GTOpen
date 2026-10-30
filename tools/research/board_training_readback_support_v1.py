"""CPU-only independent policy/cashflow readback for board-root training.

Uses the shared native tree and feature representation, but not the training
provider, backward board evaluator, ingestion or regret update. Dense forward
cashflows and scalar class-pair sums are intentionally a different calculation.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import hashlib
import json
import math
from pathlib import Path
import subprocess
import time
import numpy as np
import psutil
from weighted_training_readback_parallel_v1 import base_predict
from sampled_physical_deals_v1 import PhysicalDeals
from storage_strategic_common_prior_20260920 import PAIRS, CLASSES
from board_root_components_control_v1 import forward_variable
from board_root_accumulator_v1 import digest
from sampled_physical_root_evaluation_v1 import ROOT, sha
from later_average_support_v1 import OUT
from bounded_parallel_evaluation_archive_v2 import production_available


def regret_policy(values):
    values = np.asarray(values, dtype=float)
    positive = np.maximum(values, 0.)
    total = math.fsum(positive)
    return positive / total if total > 0 else np.eye(len(values))[np.argmax(values)]


def prepare_readback(payload):
    source = payload['context_source']; context = json.loads(source)
    model = json.loads(payload['model_source']); catalog = json.loads(payload['physical_catalog_source'])
    assert catalog['context_source'] == source
    rows = catalog['rows']; obs = [dict(r['observation']) for r in rows]
    indices = {(r['node'], tuple(r['hand'])): i for i, r in enumerate(rows)}
    paths = {}
    def walk(node, path):
        if not context['nodes'][node]['children']: return
        paths[node] = path
        for action, child in enumerate(context['nodes'][node]['children']):
            walk(child, path + [(node, action)])
    walk(0, [])
    for row, o in zip(rows, obs):
        o['own_history'] = [[indices[(n, tuple(row['hand']))], a, len(context['nodes'][n]['children'])]
                            for n, a in paths[row['node']] if context['nodes'][n]['actor'] == o['actor']]
    _, p, _ = base_predict(dict(context_source=source, observations=obs), model, 'cpu')
    mapping = {tuple(h): int(c) for h, c in zip(PAIRS, CLASSES)}
    root = model['board_root_state']; exact = model['exact_btn_state']
    response = context['nodes'][0]['children'][3]
    by_class = {}; seen = {}; error = 0.
    for row, probability in zip(rows, p):
        node = row['node']; c = mapping[tuple(row['hand'])]
        arity = len(context['nodes'][node]['children'])
        if node == 0 and root['completed_updates']:
            probability[:] = regret_policy(root['regret_sums'][c])
        if node == response and exact['conditional_reach_sums'][c] > 0:
            probability[:] = 0.; probability[:2] = regret_policy(exact['regret_sums'][c])
        if node not in by_class:
            by_class[node] = np.zeros((169, arity)); seen[node] = np.zeros(169, dtype=int)
        if seen[node][c]: error = max(error, float(np.max(abs(by_class[node][c] - probability[:arity]))))
        else: by_class[node][c] = probability[:arity]
        seen[node][c] += 1
    assert error < 1e-12 and all(np.all(x > 0) for x in seen.values())
    matrix = json.loads(payload['matrix_source']); mass = np.asarray(matrix['class_mass'])
    showdown = np.asarray(matrix['bb_showdown_entries']); class_mass = mass.sum(1)
    assert np.array_equal(class_mass, payload['root_config']['entry_mass'])
    # Scalar summation deliberately differs from the provider's matrix products.
    scalar = np.zeros((169, 4)); scalar[:, 0] = context['nodes'][1]['leaf']['utilities'][0]
    for b in range(169):
        raise_terms = []; jam_terms = []
        for t in range(169):
            p3, p6, p9, p12 = by_class[3][t], by_class[6][b], by_class[9][b], by_class[12][t]
            raise_terms.append(mass[b,t] * (p3[0]*2.5 - p3[2]*p6[0]*6 - p3[3]*p9[0]*6)
                               + showdown[b,t]*p3[3]*p9[1])
            jam_terms.append(mass[b,t]*p12[0]*2.5 + showdown[b,t]*p12[1])
        scalar[b,2] = math.fsum(raise_terms) / class_mass[b]
        scalar[b,3] = math.fsum(jam_terms) / class_mass[b]
    sampler = PhysicalDeals(source, mode='full_deck', seed=0)
    assert np.max(abs(np.bincount(CLASSES, weights=sampler.first[0], minlength=169)-class_mass)) < 1e-12
    return dict(source=source, context=context, model=model, pre=by_class,
                sampler=sampler, class_mass=class_mass, exact_scalar=scalar,
                maximum_suit_error=error)


def postflop_policy(tree, prepared):
    result = []
    for branch in tree['branches']:
        observations = []; spans = []
        for i, node in enumerate(branch['nodes']):
            if node['kind'] == 0:
                spans.append((i, len(observations), len(node['observations'])))
                observations.extend(node['observations'])
        _, p, _ = base_predict(dict(context_source=prepared['source'], observations=observations),
                               prepared['model'], 'cpu')
        result.append({i: p[start:start+count, :len(branch['nodes'][i]['children'])]
                       for i, start, count in spans})
    return result


def check_draw(payload, request_path, record):
    from threadpoolctl import threadpool_limits
    began = time.monotonic()
    with threadpool_limits(limits=1):
        assert production_available() and psutil.virtual_memory().available > 20_000_000_000
        prepared = prepare_readback(payload); path = Path(request_path)
        request = json.loads(path.read_text()); board = record['board']
        assert len(set(board)) == 5 and board[:3] == sorted(board[:3])
        legal = ~np.isin(PAIRS, board).any(1)
        ids = [np.flatnonzero(legal & (prepared['sampler'].weights[p] > 0)) for p in (0,1)]
        assert request == dict(board=board, hands=[PAIRS[i].tolist() for i in ids])
        raw = subprocess.check_output([str(ROOT/'target/release/examples/hu_fixed_board_tree_v1.exe'),
            str(OUT/'bb-context-candidate.json'), str(path)], timeout=120, creationflags=subprocess.CREATE_NO_WINDOW)
        assert hashlib.sha256(raw).hexdigest() == record['tree_sha256']
        tree = json.loads(raw); del raw
        assert tree['board'] == board and tree['hands'] == request['hands']
        assert record['model_sha256'] == hashlib.sha256(payload['model_source'].encode()).hexdigest()
        assert record['values_sha256'] == digest(record['values'])
        weights = [prepared['sampler'].weights[p,i] for p,i in enumerate(ids)]
        classes = [CLASSES[i] for i in ids]; post = postflop_policy(tree, prepared)
        values = np.zeros((169,4))
        for action, start in ((1,2),(2,3)):
            physical = forward_variable(tree, post, prepared['pre'], prepared['context'], weights, classes, start)
            values[:,action] = np.bincount(classes[0], weights=physical, minlength=169)
        values *= math.comb(52,5) / math.comb(48,5) / prepared['sampler'].masses[0] / prepared['class_mass'][:,None]
        error = float(np.max(abs(values-np.asarray(record['values'])))); assert error < 1e-9
        assert psutil.virtual_memory().available > 20_000_000_000
        return dict(draw_index=record['draw_index'], request_sha256=sha(path),
                    values=values.tolist(), maximum_error=error, seconds=time.monotonic()-began,
                    pid=os.getpid(), rss_bytes=psutil.Process().memory_info().rss)
