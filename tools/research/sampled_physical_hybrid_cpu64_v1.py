"""NumPy float64 reference for the frozen hybrid bank, with ordered averaging.

Exactly widens the stored float32 weights. Uses no CUDA implementation or
candidate selection. Inputs still contain only the player's visible features.
"""
import numpy as np
from sampled_physical_bank_v1 import histories
from sampled_physical_preflop_table_v1 import Table
from sampled_physical_hybrid_checkpoint_v1 import validate_model


class HybridCpuBank64:
    def __init__(self, documents, *, context_source):
        self.context_source = context_source
        self.models = []
        shapes = [(64, 269), (64, 64), (4, 64)]
        for generation, d in enumerate(documents):
            validate_model(d, context_source)
            if d['generation'] != generation:
                raise ValueError('Complete ordered played bank required')
            networks = []
            for net in d['networks']:
                networks.append([
                    (np.asarray(net[f'w{layer}'], dtype=np.float32).astype(np.float64).reshape(shape),
                     np.asarray(net[f'b{layer}'], dtype=np.float32).astype(np.float64))
                    for layer, shape in enumerate(shapes)])
            tables = [None if t is None else Table(t, context_source) for t in d['preflop_tables']]
            self.models.append((networks, tables))
        if not self.models:
            raise ValueError('Nonempty played bank required')

    def average(self, queries, *, guard):
        if queries['context_source'] != self.context_source:
            raise ValueError('Query context mismatch')
        obs = queries['observations']
        if not obs:
            raise ValueError('Nonempty query batch required')
        history = histories(obs)
        x = np.zeros((len(obs), 269), dtype=np.float64)
        actors = np.empty(len(obs), dtype=np.int64)
        legal = np.zeros((len(obs), 4), dtype=bool)
        for i, o in enumerate(obs):
            active = o['active_features']
            if len(active) != 36 or len(set(active)) != 36 or any(type(j) is not int or not 0 <= j < 269 for j in active):
                raise ValueError('Invalid visible feature row')
            if o['actor'] not in (0, 1) or o['n'] not in (2, 3, 4):
                raise ValueError('Invalid player or action count')
            x[i, active] = 1.; actors[i] = o['actor']; legal[i, :o['n']] = True
        ids = [np.flatnonzero(actors == p) for p in (0, 1)]
        numerator = np.zeros((len(obs), 4)); denominator = np.zeros(len(obs))
        for networks, tables in self.models:
            guard(); scores = np.zeros((len(obs), 4))
            for player, indices in enumerate(ids):
                if not len(indices): continue
                y = x[indices]
                for layer, (w, b) in enumerate(networks[player]):
                    y = y@w.T+b
                    if layer != 2: y = np.maximum(y, 0.)
                scores[indices] = y
            if not np.isfinite(scores).all():
                raise ValueError('Nonfinite network scores')
            policy = np.maximum(scores, 0.)*legal
            sums = policy.sum(1); positive = sums > 0
            policy[positive] /= sums[positive, None]
            for i in np.flatnonzero(~positive):
                policy[i, int(np.argmax(scores[i, :obs[i]['n']]))] = 1.
            for player, table in enumerate(tables):
                if table is not None:
                    if table.player != player: raise ValueError('Table player mismatch')
                    policy, _ = table.apply(obs, policy)
            reach = np.ones(len(obs))
            for i, prior in enumerate(history):
                for index, action in prior: reach[i] *= policy[index, action]
            numerator += policy*reach[:, None]; denominator += reach
        supported = denominator > 0
        result = np.zeros_like(numerator)
        result[supported] = numerator[supported]/denominator[supported, None]
        for i in np.flatnonzero(~supported): result[i, :obs[i]['n']] = 1./obs[i]['n']
        if (not np.isfinite(result).all() or np.any(result < 0) or np.any(result*~legal)
                or np.max(np.abs(result.sum(1)-1)) > 1e-12):
            raise ValueError('Invalid averaged policy')
        return result, denominator
