"""Pure initial-node target corrections; not connected to any training walker.

Caller must certify the fixed private-pair population, current played policy,
and first-own-action geometry. These are conditional expectations, not exact
returns for an individual deal. No random numbers or policy updates occur here.
"""
import numpy as np


def bb_correction(policy, sampled_jam, exact_jam):
    policy = np.asarray(policy, dtype=np.float64)
    if policy.shape != (4,) or not np.isfinite(policy).all() or np.min(policy) < 0 or abs(policy.sum()-1) > 1e-12:
        raise ValueError('Four normalized BB action probabilities required')
    if not np.isfinite([sampled_jam, exact_jam]).all():
        raise ValueError('Finite sampled and conditional shove values required')
    delta = float(exact_jam - sampled_jam)
    value_delta = float(policy[3] * delta)
    regret_delta = np.full(4, -value_delta)
    regret_delta[3] += delta
    return value_delta, regret_delta


def btn_targets(call_probability, fold_value, call_value_entry, jam_reach):
    if not np.isfinite([call_probability, fold_value, call_value_entry, jam_reach]).all():
        raise ValueError('Finite BTN policy, payouts and reach required')
    if not 0 <= call_probability <= 1 or not 0 < jam_reach <= 1:
        raise ValueError('A visited BTN node requires positive shove reach and a valid policy')
    values = np.array([fold_value, call_value_entry / jam_reach])
    if not np.isfinite(values).all():
        raise ValueError('Conditional payoff overflow')
    mean = float(values @ np.array([1-call_probability, call_probability]))
    return mean, values-mean
