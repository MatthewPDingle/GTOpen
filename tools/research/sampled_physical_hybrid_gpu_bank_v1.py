"""Persistent CUDA bank with direct preflop tables applied before own reach.

Only explicit version-2 hybrid model documents are accepted. CUDA postflop
inference and ordered float64 averaging retain the network-only reference math.
"""
import json
import numpy as np
from sampled_physical_gpu_bank_v1 import CudaBank
from sampled_physical_bank_v1 import histories
from sampled_physical_preflop_table_v1 import Table, validate_preflop
from sampled_physical_hybrid_checkpoint_v1 import validate_model


def prepare_tables(queries, tables, context_source):
    if queries['context_source'] != context_source:
        raise ValueError('Query context mismatch')
    context = json.loads(context_source); obs = queries['observations']
    indices = []; keys = []
    for i,o in enumerate(obs):
        if (int(o['hi']) < 2**63) != (o['phase'] == 0):
            raise ValueError('Query phase/key mismatch')
        if o['phase'] == 0:
            indices.append(i); keys.append(validate_preflop(o,context,o['actor']))
    values = np.zeros((len(tables),len(indices),4),dtype=np.float64)
    mask = np.zeros((len(tables),len(indices)),dtype=bool)
    for m,pair in enumerate(tables):
        if len(pair) != 2: raise ValueError('Two table slots required')
        for j,(i,key) in enumerate(zip(indices,keys)):
            o = obs[i]; table = pair[o['actor']]
            if table is None: continue
            if table.player != o['actor']: raise ValueError('Table player mismatch')
            if key not in table.rows: continue
            n,active,p = table.rows[key]
            if n != o['n'] or active != tuple(sorted(o['active_features'])):
                raise ValueError('Query/table geometry mismatch')
            values[m,j] = p; mask[m,j] = True
    return np.asarray(indices,dtype=np.int64),values,mask


class HybridCudaBank(CudaBank):
    def __init__(self, model_documents, weights_by_player, *, context_source,
                 models_per_chunk=8, guard):
        models = list(model_documents); tables = []
        for generation,document in enumerate(models):
            guard(); validate_model(document,context_source)
            if document['generation'] != generation:
                raise ValueError('Complete ordered played model bank required')
            pair = [None if d is None else Table(d,context_source) for d in document['preflop_tables']]
            tables.append(pair)
        self.tables = tables; self.context_source = context_source
        super().__init__((d['networks'] for d in models),weights_by_player,
            models_per_chunk=models_per_chunk,guard=guard)

    def average(self, queries, *, guard):
        import torch
        if queries['context_source'] != self.context_source:
            raise ValueError('Hybrid bank queries belong to another game')
        observations = queries['observations']
        pre_ids, table_values, table_mask = prepare_tables(queries,self.tables,self.context_source)
        pre_ids = torch.as_tensor(pre_ids,device='cuda')
        table_values = torch.as_tensor(table_values,device='cuda')
        table_mask = torch.as_tensor(table_mask,device='cuda')
        if not observations:
            raise ValueError('Nonempty query batch required')
        history = histories(observations)
        x = np.zeros((len(observations), 269), np.float32)
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
            if actor not in (0, 1) or n not in (2, 3, 4):
                raise ValueError('Invalid actor or legal menu')
            x[i, active] = 1
            actors[i] = actor
            mask[i, :n] = True
            for j, (index, a) in enumerate(history[i]):
                prior[i, j], action[i, j], valid[i, j] = index, a, True
        features = torch.as_tensor(x, device='cuda')
        actors = torch.as_tensor(actors, device='cuda')
        legal = torch.as_tensor(mask, device='cuda')
        prior = torch.as_tensor(prior, device='cuda')
        action = torch.as_tensor(action, device='cuda')
        valid = torch.as_tensor(valid, device='cuda')
        ids = [torch.nonzero(actors == p).flatten() for p in (0, 1)]
        numerator = torch.zeros((len(observations), 4), dtype=torch.float64, device='cuda')
        denominator = torch.zeros(len(observations), dtype=torch.float64, device='cuda')
        with torch.no_grad():
            for start in range(0, self.count, self.chunk):
                guard()
                stop = min(self.count, start + self.chunk)
                count = stop - start
                scores = torch.zeros((count, len(observations), 4), dtype=torch.float32, device='cuda')
                for player in (0, 1):
                    indices = ids[player]
                    if not len(indices):
                        continue
                    y = features[indices].unsqueeze(0).expand(count, -1, -1)
                    for layer in range(3):
                        w = self.parameters[f'w{layer}'][start:stop, player]
                        b = self.parameters[f'b{layer}'][start:stop, player]
                        y = torch.bmm(y, w.transpose(1, 2)) + b.unsqueeze(1)
                        if layer != 2:
                            y = torch.relu(y)
                    scores[:, indices] = y
                if not torch.isfinite(scores).all():
                    raise ValueError('Nonfinite network output')
                scores = scores.double()
                positive = torch.clamp(scores, min=0) * legal
                totals = positive.sum(dim=2, keepdim=True)
                fallback = torch.nn.functional.one_hot(
                    scores.masked_fill(~legal, -torch.inf).argmax(dim=2), 4).double()
                probabilities = torch.where(totals > 0, positive / totals.clamp_min(1e-300), fallback)
                if len(pre_ids):
                    probabilities[:,pre_ids] = torch.where(table_mask[start:stop,:,None],
                        table_values[start:stop],probabilities[:,pre_ids])
                # Use overridden probabilities in every ancestor reach factor.
                reach = self.weights[actors, start:stop].transpose(0, 1).clone()
                for j in range(depth):
                    factors = probabilities[:, prior[:, j], action[:, j]]
                    reach *= torch.where(valid[:, j], factors, 1.)
                # Preserve model order rather than changing to a tree reduction.
                for m in range(count):
                    numerator += probabilities[m] * reach[m].unsqueeze(1)
                    denominator += reach[m]
        supported = denominator > 0
        result = torch.empty_like(numerator)
        result[supported] = numerator[supported] / denominator[supported].unsqueeze(1)
        result[~supported] = legal[~supported].double() / legal[~supported].sum(dim=1, keepdim=True)
        if (not torch.isfinite(result).all() or (result < 0).any()
                or (result * ~legal).any() or (result.sum(dim=1) - 1).abs().max() > 1e-12):
            raise ValueError('Invalid averaged policy')
        return result.cpu().numpy(), denominator.cpu().numpy()
