"""Prepare bank-independent visible-query arrays once for a crossed comparison.

CPU preparation only; not connected to any live or production policy runtime.
Consumers must treat the input queries and returned arrays as immutable for the
duration of their comparison. Model-dependent tables are intentionally absent.
"""
from dataclasses import dataclass

import numpy as np

from sampled_physical_bank_v1 import histories
from sampled_visible_features_bulk_v1 import features as visible_features


@dataclass(frozen=True)
class SharedQueryArrays:
    features: np.ndarray
    actors: np.ndarray
    legal: np.ndarray
    prior: np.ndarray
    action: np.ndarray
    valid: np.ndarray


def prepare(queries):
    observations = queries['observations']
    if not observations:
        raise ValueError('Nonempty query batch required')
    history = histories(observations)
    x = visible_features(observations).astype(np.float64)
    actors = np.empty(len(observations), np.int64)
    mask = np.zeros((len(observations), 4), dtype=bool)
    depth = max(map(len, history), default=0)
    prior = np.zeros((len(observations), depth), np.int64)
    action = np.zeros_like(prior)
    valid = np.zeros_like(prior, dtype=bool)
    for i, o in enumerate(observations):
        active, n, actor = o['active_features'], o['n'], o['actor']
        if (len(active) != 36 or len(set(active)) != 36
                or any(type(j) is not int or not 0 <= j < 269 for j in active)):
            raise ValueError('Invalid visible feature row')
        if type(actor) is not int or type(n) is not int or actor not in (0, 1) or n not in (2, 3, 4):
            raise ValueError('Invalid actor or legal menu')
        x[i, active] = 1
        actors[i] = actor
        mask[i, :n] = True
        for j, (index, a) in enumerate(history[i]):
            prior[i, j], action[i, j], valid[i, j] = index, a, True
    arrays = (x, actors, mask, prior, action, valid)
    for array in arrays:
        array.flags.writeable = False
    return SharedQueryArrays(*arrays)
