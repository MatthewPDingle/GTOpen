"""Bounded per-visit physical-poker advantage storage, ordinary CFR weights.

Only visible features enter training. Keys and iteration labels are audit metadata.
Algorithm R samples visits uniformly; duplicate observations remain separate visits.
This module never stores a global information-set dictionary or average policy.
"""
import copy
import hashlib
import json
from pathlib import Path

import numpy as np


def checked_row(observation, values):
    active = observation['active_features']
    if (len(active) != 36 or len(set(active)) != 36
            or any(type(i) is not int or not 0 <= i < 269 for i in active)):
        raise ValueError('Invalid visible feature row')
    actor, n = observation['actor'], observation['n']
    if type(actor) is not int or actor not in (0, 1) or type(n) is not int or n not in (2, 3, 4):
        raise ValueError('Invalid actor or legal menu')
    keys = tuple(int(observation[k]) for k in ('hi', 'lo'))
    if any(not 0 <= k < 2**64 for k in keys):
        raise ValueError('Invalid observation key')
    target = np.asarray(values, dtype=np.float64)
    if target.shape != (4,) or not np.isfinite(target).all() or np.any(target[n:]):
        raise ValueError('Invalid signed advantage values')
    return keys, np.asarray(sorted(active), dtype=np.uint16), n, target


class PhysicalReservoir:
    """Fixed allocation; independent RNG from deal sampling and model fitting."""
    def __init__(self, capacity, player, seed, context_source):
        if type(capacity) is not int or not 1 <= capacity <= 2**24:
            raise ValueError('Explicit bounded capacity required')
        if type(player) is not int or player not in (0, 1):
            raise ValueError('Invalid player')
        if not isinstance(context_source, str) or not context_source:
            raise ValueError('Original game context required')
        self.capacity, self.player = capacity, player
        self.context_sha256 = hashlib.sha256(context_source.encode('utf-8')).hexdigest()
        self.rng = np.random.default_rng(seed)
        self.seen = 0
        self.keys = np.zeros((capacity, 2), dtype=np.uint64)
        self.active = np.zeros((capacity, 36), dtype=np.uint16)
        self.arity = np.zeros(capacity, dtype=np.uint8)
        self.values = np.zeros((capacity, 4), dtype=np.float64)
        self.iterations = np.zeros(capacity, dtype=np.uint64)

    @property
    def size(self):
        return min(self.seen, self.capacity)

    def add(self, observation, values, iteration):
        if observation['actor'] != self.player:
            raise ValueError('Wrong player for reservoir')
        if type(iteration) is not int or not 1 <= iteration < 2**64:
            raise ValueError('Positive iteration metadata required')
        row = checked_row(observation, values)
        self._insert(row, iteration)

    def _insert(self, row, iteration):
        # One chance per visit; never collapse repeated hand/history observations.
        if self.seen >= 2**63-1:
            raise OverflowError('Visit counter exhausted')
        self.seen += 1
        slot = self.seen-1 if self.seen <= self.capacity else int(self.rng.integers(self.seen))
        if slot < self.capacity:
            self.keys[slot], self.active[slot], self.arity[slot], self.values[slot] = row
            self.iterations[slot] = iteration

    def summary(self):
        return dict(player=self.player, capacity=self.capacity, seen=self.seen, retained=self.size,
                    allocated_payload_bytes=sum(a.nbytes for a in
                        (self.keys, self.active, self.arity, self.values, self.iterations)),
                    context_sha256=self.context_sha256)

    def save(self, path):
        # New checkpoint only. Caller publishes its hash after successful return.
        metadata = dict(format=1, capacity=self.capacity, player=self.player, seen=self.seen,
                        context_sha256=self.context_sha256, rng=copy.deepcopy(self.rng.bit_generator.state))
        with Path(path).open('xb') as f:
            np.savez(f, metadata=np.array(json.dumps(metadata)), **{
                k: getattr(self, k)[:self.size] for k in ('keys', 'active', 'arity', 'values', 'iterations')})

    @classmethod
    def load(cls, path, context_source):
        with np.load(path, allow_pickle=False) as saved:
            m = json.loads(str(saved['metadata']))
            if m['format'] != 1 or type(m['seen']) is not int or not 0 <= m['seen'] < 2**63:
                raise ValueError('Invalid reservoir checkpoint')
            result = cls(m['capacity'], m['player'], 0, context_source)
            if result.context_sha256 != m['context_sha256']:
                raise ValueError('Checkpoint belongs to a different game')
            size = min(m['seen'], m['capacity'])
            for name in ('keys', 'active', 'arity', 'values', 'iterations'):
                target, source = getattr(result, name), saved[name]
                if source.shape != target[:size].shape or source.dtype != target.dtype:
                    raise ValueError('Checkpoint shape or type mismatch')
                target[:size] = source
            for i in range(size):
                checked_row(dict(hi=str(result.keys[i, 0]), lo=str(result.keys[i, 1]),
                                 actor=result.player, n=int(result.arity[i]),
                                 active_features=result.active[i].astype(int).tolist()), result.values[i])
                if result.iterations[i] == 0:
                    raise ValueError('Missing iteration metadata')
            result.rng.bit_generator.state = m['rng']
            result.seen = m['seen']
            return result


def ingest(queries, updates, reservoirs, iteration):
    """Validate a whole transport before adding positive-tag advantage visits.

    Negative tags are opponent policy observations, not advantage training data.
    Average strategy is represented separately by the bank of actually played nets.
    No importance/reach multiplier is applied: the traversal already sampled it.
    """
    if type(iteration) is not int or not 1 <= iteration < 2**64:
        raise ValueError('Positive iteration metadata required')
    if queries['format'] != 2 or updates['format'] != 2 or not updates['policies_frozen_across_updater_passes']:
        raise ValueError('Unsupported or unfrozen traversal batch')
    batch = json.loads(queries['batch_source'])
    if updates['batch_id'] != batch['batch_id'] or updates['observations'] != len(queries['observations']):
        raise ValueError('Traversal batch identity mismatch')
    digest = hashlib.sha256(queries['context_source'].encode('utf-8')).hexdigest()
    if len(reservoirs) != 2 or any(r.player != p or r.context_sha256 != digest for p, r in enumerate(reservoirs)):
        raise ValueError('Reservoir game or player mismatch')
    counts = [0, 0]
    for index, updater, tag, values in updates['records']:
        if (type(index) is not int or not 0 <= index < len(queries['observations'])
                or type(updater) is not int or updater not in (0, 1)
                or type(tag) is not int or abs(tag) not in (2, 3, 4)):
            raise ValueError('Invalid traversal record')
        o = queries['observations'][index]
        _, _, n, v = checked_row(o, values)
        if abs(tag) != n or o['actor'] != (updater if tag > 0 else 1-updater):
            raise ValueError('Record actor or legal menu mismatch')
        if tag < 0 and (np.any(v < 0) or abs(v.sum()-1) > 1e-12):
            raise ValueError('Invalid opponent-policy record')
        if tag > 0:
            counts[updater] += 1
    if any(r.seen+c >= 2**63 for r, c in zip(reservoirs, counts)):
        raise OverflowError('Visit counter exhausted')
    for index, updater, tag, values in updates['records']:
        if tag > 0:
            reservoirs[updater]._insert(checked_row(queries['observations'][index], values), iteration)
    return counts
