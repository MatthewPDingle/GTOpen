"""Visible-summary full retained-data fitter; matched seeded initialization.

CPU is available for small numerical controls, CUDA for future trial fitting.
No active trial imports this module. Original grouped targets and loss weights
are preserved; only 33 visible summaries and zero-initialized columns are added.
"""
import time

import numpy as np

from sampled_physical_fit_v1 import grouped_rows, export_network
from sampled_visible_initialization_v1 import features, fresh_visible_network
from sampled_visible_hybrid_checkpoint_v1 import FEATURE_SPEC


class PreparedObjective:
    def __init__(self, grouped, device, guard):
        import torch
        device = torch.device(device)
        if device.type not in ('cpu','cuda'):
            raise ValueError('Explicit CPU or CUDA device required')
        guard()
        active = grouped['active']
        visible = features([dict(active_features=row.tolist()) for row in active])
        weights = ((np.arange(4)[None, :] < grouped['arity'][:, None])
                   * grouped['counts'][:, None])
        self.x = torch.as_tensor(visible, dtype=torch.float32, device=device)
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
            raise ValueError('Model must match the prepared visible float32 dataset')
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
    if device not in ('cpu','cuda') or type(steps) is not int or steps < 1:
        raise ValueError('CPU/CUDA and a positive fit budget required')
    if not np.isfinite(learning_rate) or learning_rate <= 0:
        raise ValueError('Positive learning rate required')
    guard()
    began = time.monotonic()
    grouped = grouped_rows(reservoir)
    model = fresh_visible_network(seed).to(device)
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
        prepared_tensor_bytes=prepared.tensor_bytes,representation=FEATURE_SPEC, setup_seconds=setup_seconds,
        optimizer_seconds=fit_seconds, prepared_once=True,
        scope='Original grouped retained-data objective and full gradient steps with explicit visible summaries and matched zero-column initialization. Fitting loss is not poker strength.')
