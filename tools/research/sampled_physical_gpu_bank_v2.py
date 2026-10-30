"""Float64 inference for a complete dense played bank. Stored float32 weights
are exactly widened; policy and ordered own-reach averaging are unchanged.
"""
import numpy as np

from sampled_physical_bank_v1 import histories
from sampled_physical_checkpoint_v1 import validate_model


class CudaBank64:
    def __init__(self, documents, weights_by_player, *, context_source, models_per_chunk=8, guard):
        documents = list(documents)
        for generation, document in enumerate(documents):
            validate_model(document)
            if document['generation'] != generation:
                raise ValueError('Complete ordered played bank required')
        self.context_source = context_source
        model_pairs = [d['networks'] for d in documents]
        import torch
        if not torch.cuda.is_available():
            raise ValueError('CUDA required')
        if torch.backends.cuda.matmul.allow_tf32 or torch.backends.cudnn.allow_tf32:
            raise ValueError('TF32 must be disabled explicitly')
        if type(models_per_chunk) is not int or models_per_chunk <= 0:
            raise ValueError('Positive model chunk required')
        weights = np.asarray(weights_by_player, dtype=np.float64)
        if (weights.ndim != 2 or weights.shape[0] != 2 or weights.shape[1] == 0
                or not np.isfinite(weights).all() or np.any(weights <= 0)
                or not np.isfinite(weights.sum())):
            raise ValueError('Two positive finite model-weight sequences required')
        shapes = {'w0': (64, 269), 'b0': (64,), 'w1': (64, 64),
                  'b1': (64,), 'w2': (4, 64), 'b2': (4,)}
        values = {name: [] for name in shapes}
        for pair in model_pairs:
            guard()
            if len(pair) != 2:
                raise ValueError('Two player networks required')
            for name, shape in shapes.items():
                a = np.asarray([p[name] for p in pair], dtype=np.float32)
                if a.size != 2 * int(np.prod(shape)) or not np.isfinite(a).all():
                    raise ValueError('Invalid network weights')
                values[name].append(a.astype(np.float64).reshape(2, *shape))
        if len(values['w0']) != weights.shape[1]:
            raise ValueError('Incomplete or excessive model bank')
        self.parameters = {name: torch.as_tensor(np.stack(a), device='cuda')
                           for name, a in values.items()}
        self.weights = torch.as_tensor(weights, device='cuda')
        self.count = weights.shape[1]
        self.chunk = models_per_chunk

    def average(self, queries, *, guard):
        import torch
        if queries['context_source'] != self.context_source:
            raise ValueError('Query context mismatch')
        observations = queries['observations']
        if not observations:
            raise ValueError('Nonempty query batch required')
        history = histories(observations)
        x = np.zeros((len(observations), 269), np.float64)
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
