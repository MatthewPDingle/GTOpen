"""Weighted GPU fit using the previously qualified ordered objective."""
import time
import numpy as np
from weighted_visible_objective_v1 import grouped_rows, PreparedWeightedObjective
from sampled_visible_initialization_v1 import fresh_visible_network
from sampled_physical_fit_v1 import export_network


def fit(reservoir, *, seed, steps, device, chunk_size, guard, learning_rate=.003):
    import torch
    if device != 'cuda' or type(steps) is not int or steps < 1: raise ValueError('CUDA and positive fit count required')
    if type(chunk_size) is not int or chunk_size < 1 or not np.isfinite(learning_rate) or learning_rate <= 0:
        raise ValueError('Positive chunk size and learning rate required')
    guard(); started = time.monotonic(); grouped = grouped_rows(reservoir)
    model = fresh_visible_network(seed).to(device)
    prepared = PreparedWeightedObjective(grouped,device,dtype=torch.float32,guard=guard)
    optimizer = torch.optim.Adam(model.parameters(),lr=learning_rate)
    with torch.no_grad(): before = prepared.objective(model,chunk_size,guard)
    setup = time.monotonic()-started; fit_started = time.monotonic()
    for _ in range(steps):
        guard(); optimizer.zero_grad(set_to_none=True)
        prepared.objective(model,chunk_size,guard,backward=True); optimizer.step()
    fit_seconds = time.monotonic()-fit_started
    with torch.no_grad(): after = prepared.objective(model,chunk_size,guard)
    if any(not bool(torch.isfinite(p).all()) for p in model.parameters()): raise ValueError('Nonfinite fitted parameters')
    return export_network(model),dict(player=reservoir.player,device=device,steps=steps,seed=seed,
        learning_rate=learning_rate,chunk_size=chunk_size,retained_examples=grouped['examples'],
        grouped_observations=len(grouped['active']),weighted_legal_target_mass=grouped['denominator'],
        advantage_scale=grouped['scale'],normalized_grouped_loss_before=before,normalized_grouped_loss_after=after,
        normalized_within_observation_variance=grouped['variance'],setup_seconds=setup,optimizer_seconds=fit_seconds)
