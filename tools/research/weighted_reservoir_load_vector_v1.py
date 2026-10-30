"""Isolated bulk validation for the existing weighted reservoir archive format.

Returns the original reservoir type and preserves array order and bytes. Existing
loaders and registered studies remain unchanged. Full checkpoint checks still
belong to the caller.
"""
import json
import numpy as np
from weighted_physical_reservoir_v1 import WeightedPhysicalReservoir, ARRAYS, METHOD


def load(path, context_source):
    with np.load(path, allow_pickle=False) as data:
        if set(data.files) != set(ARRAYS) | {'metadata'}:
            raise ValueError('Explicit weighted checkpoint arrays required')
        m = json.loads(str(data['metadata']))
        if (m.get('format') != 2 or m.get('method') != METHOD
                or type(m.get('seen')) is not int or not 0 <= m['seen'] < 2**63):
            raise ValueError('Unsupported weighted checkpoint')
        result = WeightedPhysicalReservoir(m['capacity'], m['player'], 0, context_source)
        if result.context_sha256 != m['context_sha256']:
            raise ValueError('Changed context')
        size = min(m['seen'], m['capacity'])
        for name in ARRAYS:
            target, source = getattr(result, name), data[name]
            if source.dtype != target.dtype or source.shape != target[:size].shape:
                raise ValueError('Checkpoint array mismatch')
            target[:size] = source
        # Exact integer dtypes and constructor checks already establish key bounds,
        # feature integer types and the actor. Sorting below validates uniqueness;
        # it does not alter the stored feature order (the original load preserves it).
        for start in range(0, size, 8192):
            end = min(start+8192, size)
            active = result.active[start:end]
            ordered = np.sort(active, axis=1)
            if np.any(active >= 269) or np.any(ordered[:, 1:] == ordered[:, :-1]):
                raise ValueError('Invalid visible feature row')
            arity = result.arity[start:end]
            if np.any((arity < 2) | (arity > 4)):
                raise ValueError('Invalid actor or legal menu')
            values = result.values[start:end]
            if (not np.isfinite(values).all()
                    or np.any((np.arange(4)[None, :] >= arity[:, None]) & (values != 0))):
                raise ValueError('Invalid signed advantage values')
            weights = result.deal_weights[start:end]
            if not np.isfinite(weights).all() or np.any((weights <= 0) | (weights > 65536)):
                raise ValueError('Positive bounded importance weight required')
            if np.any(result.iterations[start:end] == 0):
                raise ValueError('Missing iteration')
        result.rng.bit_generator.state = m['rng']
        result.seen = m['seen']
        return result
