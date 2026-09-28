"""Visible-history posterior and fixed-size conditional river sample mean."""
import copy
import hashlib
import itertools
import math
import numpy as np

SAMPLES = 64


def subset(queries, indices):
    rows = queries['observations']; wanted = set(map(int, indices)); todo = list(wanted)
    while todo:
        i = todo.pop()
        if not 0 <= i < len(rows): raise ValueError('Invalid query index')
        for prior, _, _ in rows[i]['own_history']:
            if prior not in wanted: wanted.add(prior); todo.append(prior)
    ids = np.array(sorted(wanted), dtype=np.int64)
    mapping = {int(i): j for j, i in enumerate(ids)}; selected = []
    for i in ids:
        row = copy.deepcopy(rows[int(i)])
        row['own_history'] = [[mapping[j], a, n] for j, a, n in row['own_history']]
        selected.append(row)
    return dict(queries, observations=selected), ids


def history_indices(batch):
    indices = set()
    for doc in batch['targets']:
        indices.add(doc['target']['query_index'])
        for pair in doc['pairs']: indices.update(i for i, _, _ in pair['path'])
    return indices


def posterior(doc, rows, p, entry):
    target = doc['target']; hero = target['actor']; mass = []; own = []
    expected = list(itertools.combinations([c for c in range(52) if c not in target['cards']], 2))
    if len(expected) != 990 or [tuple(x['cards']) for x in doc['pairs']] != expected:
        raise ValueError('Complete ordered compatible opponent pairs required')
    for pair in doc['pairs']:
        w = entry[1-hero][tuple(pair['cards'])]; my = 1.
        if not math.isfinite(w) or w < 0: raise ValueError('Invalid entry mass')
        for i, a, n in pair['path']:
            if rows[i]['n'] != n or not 0 <= a < n: raise ValueError('Invalid action history')
            x = float(p[i, a])
            if not math.isfinite(x) or not 0 <= x <= 1: raise ValueError('Invalid history probability')
            if rows[i]['actor'] == hero: my *= x
            else: w *= x
        mass.append(w); own.append(my)
    if max(own)-min(own) > 1e-12: raise ValueError('Own reach depends on hidden cards')
    total = math.fsum(mass)
    if not math.isfinite(total) or total <= 0: raise ValueError('Unsupported opponent posterior')
    return np.asarray(mass)/total, total, own[0]


def draw(probabilities, identity, *, stream='native-plan'):
    if (np.shape(probabilities) != (990,) or not np.isfinite(probabilities).all()
            or np.any(probabilities < 0) or abs(float(sum(probabilities))-1) > 1e-12):
        raise ValueError('Normalized full posterior required')
    seed = int.from_bytes(hashlib.sha256(('river-posterior64-v1|'+stream+'|'+identity).encode()).digest()[:16], 'little')
    return np.random.Generator(np.random.PCG64(seed)).choice(990, SAMPLES, replace=True, p=probabilities)


def future_indices(doc, draws):
    if np.shape(draws) != (SAMPLES,) or any(type(i) not in (int, np.int64) or not 0 <= i < 990 for i in draws):
        raise ValueError('Exactly 64 valid opponent-pair draws required')
    indices = set()
    for i in np.unique(draws):
        pair = doc['pairs'][int(i)]
        for node in doc['nodes'][pair['node_start']:pair['root']+1]:
            if node['kind'] == 'decision': indices.add(node['query_index'])
    return indices


def sampled_target(doc, p, draws):
    future_indices(doc, draws)  # validate sample size and identity domain
    n = doc['target']['n']; sigma = p[doc['target']['query_index'], :n]
    if not np.isfinite(sigma).all() or abs(float(sum(sigma))-1) > 1e-12:
        raise ValueError('Invalid current target policy')
    vectors = {}
    for i in np.unique(draws):
        pair = doc['pairs'][int(i)]; values = {}
        for index in range(pair['node_start'], pair['root']+1):
            node = doc['nodes'][index]
            if node['kind'] != 'decision': values[index] = node['payoff']
            else:
                probs = p[node['query_index'], :len(node['children'])]
                if not np.isfinite(probs).all() or np.any(probs < 0) or abs(float(sum(probs))-1) > 1e-12:
                    raise ValueError('Missing or invalid selected future policy')
                values[index] = math.fsum(float(w)*values[c] for w, c in zip(probs, node['children']))
        vectors[int(i)] = [values[c] for c in doc['nodes'][pair['root']]['children']]
    # Repeated draws retain their multiplicity. No posterior or source weight
    # is multiplied into a value already sampled from the posterior.
    q = np.array([math.fsum(vectors[int(i)][a] for i in draws)/SAMPLES for a in range(n)])
    value = math.fsum(float(x*y) for x, y in zip(sigma, q))
    return dict(action_values=q, value=value, regrets=q-value)
