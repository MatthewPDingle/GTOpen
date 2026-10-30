"""Isolated candidate: apply preflop tables only to validated preflop rows.

All visible-array and history validation is unchanged. Postflop key/phase
agreement is checked once here instead of once per preflop table. No live
training caller imports this module.
"""
import numpy as np
from river_query_preparation_vector_v1 import arrays


def prepare(engine, queries):
    if queries['context_source'] != engine.context_source:
        raise ValueError('Current policy context mismatch')
    a = arrays(queries)
    observations = queries['observations']
    table = a.legal.astype(np.float64)
    table /= table.sum(1, keepdims=True)
    mask = np.zeros(len(observations), dtype=bool)
    indices = []
    for index, observation in enumerate(observations):
        preflop = observation['phase'] == 0
        if (int(observation['hi']) < 2**63) != preflop:
            raise ValueError('Query phase disagrees with observation key')
        if preflop:
            indices.append(index)
    if indices:
        indices = np.asarray(indices, dtype=np.int64)
        subset = [observations[index] for index in indices]
        probabilities = table[indices].copy()
        for lookup in engine.tables:
            probabilities, matched = lookup.apply(subset, probabilities)
            mask[indices[np.asarray(matched, dtype=np.int64)]] = True
        table[indices] = probabilities
    return dict(queries=queries, arrays=a, table=table, mask=mask,
                arity=np.asarray([o['n'] for o in observations], dtype=int))
