"""Unqualified CUDA candidate: reuse common queries across complete model banks.

No live runtime imports this module. Shared tensors are read-only by contract;
model-specific tables, own-action reach and ordered accumulation stay separate.
"""
from copy import deepcopy
from dataclasses import dataclass

from sampled_visible_hybrid_gpu_bank_bulk_v1 import (
    VisibleHybridCudaBank64 as OriginalBank,
    prepare_tables,
)
from shared_visible_query_arrays_v1 import prepare


@dataclass(frozen=True, eq=False)
class PreparedCudaQueries:
    queries: dict
    features: object
    actors: object
    legal: object
    prior: object
    action: object
    valid: object
    ids: tuple


def prepare_cuda_queries(queries, *, guard):
    import torch
    guard()
    # Isolate the prepared inputs from subsequent caller mutation.
    snapshot = deepcopy(queries)
    arrays = prepare(snapshot)
    tensors = {name: torch.tensor(getattr(arrays, name), device='cuda')
               for name in ('features', 'actors', 'legal', 'prior', 'action', 'valid')}
    ids = tuple(torch.nonzero(tensors['actors'] == p).flatten() for p in (0, 1))
    guard()
    return PreparedCudaQueries(snapshot, **tensors, ids=ids)


class VisibleHybridCudaBank64(OriginalBank):
    def average(self, queries, *, guard):
        return self.average_prepared(prepare_cuda_queries(queries, guard=guard), guard=guard)

    def average_prepared(self, prepared, *, guard):
        import torch
        queries = prepared.queries
        if queries['context_source'] != self.context_source:
            raise ValueError('Hybrid bank queries belong to another game')
        observations = queries['observations']
        pre_ids, table_values, table_mask = prepare_tables(queries,self.tables,self.context_source)
        pre_ids = torch.as_tensor(pre_ids,device='cuda')
        table_values = torch.as_tensor(table_values,device='cuda')
        table_mask = torch.as_tensor(table_mask,device='cuda')
        features, actors, legal = prepared.features, prepared.actors, prepared.legal
        prior, action, valid = prepared.prior, prepared.action, prepared.valid
        ids = prepared.ids
        depth = prior.shape[1]
        numerator = torch.zeros((len(observations), 4), dtype=torch.float64, device='cuda')
        denominator = torch.zeros(len(observations), dtype=torch.float64, device='cuda')
        with torch.no_grad():
            for start in range(0, self.count, self.chunk):
                guard()
                stop = min(self.count, start + self.chunk)
                count = stop - start
                scores = torch.zeros((count, len(observations), 4), dtype=torch.float64, device='cuda')
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
