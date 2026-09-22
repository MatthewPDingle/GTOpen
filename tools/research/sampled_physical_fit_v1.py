"""Bounded exact retained-data gradient fitter for physical observations.

Groups identical retained observations with their counts, never hand families.
Each optimizer step sums every chunk's gradient before updating parameters.
Caller supplies the resource/activity guard; a guard failure aborts the fit.
"""
import numpy as np


def grouped_rows(reservoir):
    size = reservoir.size
    if size == 0:
        raise ValueError('Cannot fit an empty advantage reservoir')
    keys = reservoir.keys[:size]
    _, first, inverse, count = np.unique(keys, axis=0, return_index=True,
                                         return_inverse=True, return_counts=True)
    active = reservoir.active[first].copy()
    arity = reservoir.arity[first].copy()
    if (not np.array_equal(active[inverse], reservoir.active[:size])
            or not np.array_equal(arity[inverse], reservoir.arity[:size])):
        raise ValueError('A canonical key has inconsistent features or legal actions')
    if (np.any(arity < 2) or np.any(arity > 4) or np.any(active >= 269)
            or np.any(np.diff(active.astype(int), axis=1) <= 0)):
        raise ValueError('Invalid retained observation geometry')
    values = reservoir.values[:size]
    legal = np.arange(4)[None, :] < reservoir.arity[:size, None]
    if not np.isfinite(values).all() or np.any(values[~legal]):
        raise ValueError('Invalid retained advantage target')
    scale = max(.01, float(np.sqrt(np.mean(values**2))))
    if not np.isfinite(scale):
        raise ValueError('Advantage scale overflow')
    targets = values/scale
    means = np.zeros((len(count), 4), dtype=np.float64)
    np.add.at(means, inverse, targets)
    means /= count[:, None]
    denominator = int(np.dot(count, arity.astype(np.int64)))
    variance = float((((targets-means[inverse])**2)*legal).sum()/denominator)
    return dict(active=active, arity=arity, counts=count, targets=means, scale=scale,
                denominator=denominator, variance=variance, examples=size)


def fresh_network(seed):
    import torch
    # CPU initialization only: leave caller's CPU/CUDA training and deal RNGs alone.
    with torch.random.fork_rng(devices=[]):
        torch.random.default_generator.manual_seed(seed)
        return torch.nn.Sequential(torch.nn.Linear(269,64), torch.nn.ReLU(),
            torch.nn.Linear(64,64), torch.nn.ReLU(), torch.nn.Linear(64,4))


def objective(model, grouped, chunk_size, guard, backward=False):
    """Return count-weighted mean loss; optionally accumulate its full gradient."""
    import torch
    if type(chunk_size) is not int or chunk_size <= 0:
        raise ValueError('Positive inference chunk size required')
    parameter = next(model.parameters()); total = 0.
    for start in range(0, len(grouped['active']), chunk_size):
        guard()
        stop = min(start+chunk_size, len(grouped['active']))
        features = np.zeros((stop-start, 269), dtype=np.float32)
        features[np.arange(stop-start)[:, None], grouped['active'][start:stop]] = 1
        x = torch.as_tensor(features, dtype=parameter.dtype, device=parameter.device)
        target = torch.as_tensor(grouped['targets'][start:stop], dtype=parameter.dtype, device=parameter.device)
        weight = ((np.arange(4)[None, :] < grouped['arity'][start:stop, None])
                  * grouped['counts'][start:stop, None])
        weight = torch.as_tensor(weight, dtype=parameter.dtype, device=parameter.device)
        loss = ((model(x)-target).square()*weight).sum()/grouped['denominator']
        if not bool(torch.isfinite(loss)):
            raise ValueError('Nonfinite fitting loss')
        total += float(loss.detach())
        if backward:
            loss.backward()
    return total


def export_network(model):
    result = {}
    for i, layer in enumerate((0, 2, 4)):
        result[f'w{i}'] = model[layer].weight.detach().cpu().numpy().ravel().tolist()
        result[f'b{i}'] = model[layer].bias.detach().cpu().numpy().tolist()
    return result


def fit(reservoir, *, seed, steps, device, chunk_size, guard, learning_rate=.003):
    import torch
    if device not in ('cpu', 'cuda') or type(steps) is not int or steps < 1:
        raise ValueError('Explicit device and positive fit budget required')
    if not np.isfinite(learning_rate) or learning_rate <= 0:
        raise ValueError('Positive learning rate required')
    guard()
    grouped = grouped_rows(reservoir)
    model = fresh_network(seed).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    with torch.no_grad(): before = objective(model, grouped, chunk_size, guard)
    for _ in range(steps):
        optimizer.zero_grad(set_to_none=True)
        objective(model, grouped, chunk_size, guard, backward=True)
        # No step within a chunk: this is the full retained-data gradient.
        optimizer.step()
    with torch.no_grad(): after = objective(model, grouped, chunk_size, guard)
    if any(not bool(torch.isfinite(p).all()) for p in model.parameters()):
        raise ValueError('Nonfinite fitted parameters')
    return export_network(model), dict(player=reservoir.player, device=device, steps=steps,
        seed=seed, learning_rate=learning_rate, chunk_size=chunk_size,
        retained_examples=grouped['examples'], grouped_observations=len(grouped['active']),
        legal_target_count=grouped['denominator'], advantage_scale=grouped['scale'],
        normalized_grouped_loss_before=before, normalized_grouped_loss_after=after,
        normalized_within_observation_variance=grouped['variance'],
        scope='Fixed retained-data fit; fitting loss does not measure poker strength.')
