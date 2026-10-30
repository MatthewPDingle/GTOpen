"""Prepare the retained fitting dataset on CUDA once, preserving chunk order.

Same grouped, count-weighted loss and one Adam update per full retained-data
pass as sampled_physical_fit_v1. No minibatches, altered targets or new sampler.
"""
import time

import numpy as np

from sampled_physical_fit_v1 import grouped_rows, fresh_network, export_network


class PreparedObjective:
    def __init__(self, grouped, device, guard):
        import torch
        device = torch.device(device)
        if device.type != 'cuda':
            raise ValueError('This implementation requires CUDA')
        guard()
        active = grouped['active']
        features = np.zeros((len(active), 269), dtype=np.float32)
        features[np.arange(len(active))[:, None], active] = 1
        weights = ((np.arange(4)[None, :] < grouped['arity'][:, None])
                   * grouped['counts'][:, None])
        self.x = torch.as_tensor(features, dtype=torch.float32, device=device)
        self.target = torch.as_tensor(grouped['targets'], dtype=torch.float32, device=device)
        self.weight = torch.as_tensor(weights, dtype=torch.float32, device=device)
        self.denominator = grouped['denominator']
        self.tensor_bytes = sum(t.numel()*t.element_size() for t in (self.x, self.target, self.weight))
        guard()

    def objective(self, model, chunk_size, guard, backward=False):
        import torch
        if type(chunk_size) is not int or chunk_size <= 0:
            raise ValueError('Positive chunk size required')
        parameter = next(model.parameters())
        if parameter.device != self.x.device or parameter.dtype != torch.float32:
            raise ValueError('Model must match the prepared CUDA float32 dataset')
        total = torch.zeros((), dtype=torch.float64, device=self.x.device)
        for start in range(0, len(self.x), chunk_size):
            guard()
            stop = min(start+chunk_size, len(self.x))
            loss = ((model(self.x[start:stop])-self.target[start:stop]).square()
                    * self.weight[start:stop]).sum()/self.denominator
            # Keep the original order of chunk losses and gradient accumulation.
            # Move only the final scalar to the CPU, not every chunk's scalar.
            total += loss.detach().double()
            if backward:
                loss.backward()
        value = float(total)
        if not np.isfinite(value):
            raise ValueError('Nonfinite fitting loss')
        return value


def fit(reservoir, *, seed, steps, device, chunk_size, guard, learning_rate=.003):
    import torch
    if device != 'cuda' or type(steps) is not int or steps < 1:
        raise ValueError('CUDA and a positive fit budget required')
    if not np.isfinite(learning_rate) or learning_rate <= 0:
        raise ValueError('Positive learning rate required')
    guard()
    began = time.monotonic()
    grouped = grouped_rows(reservoir)
    model = fresh_network(seed).to(device)
    prepared = PreparedObjective(grouped, next(model.parameters()).device, guard)
    setup_seconds = time.monotonic()-began
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    with torch.no_grad(): before = prepared.objective(model, chunk_size, guard)
    fit_started = time.monotonic()
    for _ in range(steps):
        optimizer.zero_grad(set_to_none=True)
        prepared.objective(model, chunk_size, guard, backward=True)
        optimizer.step()
    with torch.no_grad(): after = prepared.objective(model, chunk_size, guard)
    fit_seconds = time.monotonic()-fit_started
    if any(not bool(torch.isfinite(p).all()) for p in model.parameters()):
        raise ValueError('Nonfinite fitted parameters')
    return export_network(model), dict(player=reservoir.player, device=device, steps=steps,
        seed=seed, learning_rate=learning_rate, chunk_size=chunk_size,
        retained_examples=grouped['examples'], grouped_observations=len(grouped['active']),
        legal_target_count=grouped['denominator'], advantage_scale=grouped['scale'],
        normalized_grouped_loss_before=before, normalized_grouped_loss_after=after,
        normalized_within_observation_variance=grouped['variance'],
        prepared_cuda_tensor_bytes=prepared.tensor_bytes, setup_seconds=setup_seconds,
        optimizer_seconds=fit_seconds, prepared_once=True,
        scope='Same fixed retained-data objective and full gradient steps; prepared CUDA tensors reused across steps. Fitting loss does not measure poker strength.')
