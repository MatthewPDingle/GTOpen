"""Research candidate: learn uniform-opponent equity, price terminal calls.

This is not a production-compatible policy or a range-conditioned equity model.
Card-only equity is sufficient only for the fixed uniform-legal-opponent target
of the current river reference. Betting-conditioned opponent ranges require a
different equity provider/representation and cannot silently use this model.
"""
import numpy as np
import torch
from torch import nn

SCOPE = 'uniform-legal-opponent-terminal-river-v1'
MODEL_TYPE = 'card-equity-priced-terminal-value-v1'
CARD_COLUMNS = tuple(range(133)) + tuple(range(269, 302)) + tuple(range(362, 387))
WIDTH = len(CARD_COLUMNS)
assert WIDTH == 191


def require_scope(scope):
    if scope != SCOPE:
        raise ValueError('This candidate is restricted to the uniform-opponent terminal river reference')


class EquityPricedNetwork(nn.Module):
    """One shared equity head; known fold value is exactly zero.

The 191 visible-card columns retain the 133 card indicators, 33 hand summaries
and 25 hand-relative-to-board features. Actor, betting history and public price
features are excluded from equity prediction, because this reference deliberately
holds the opponent distribution uniform. This exclusion is unsafe for a real
betting-conditioned range and must not become a production default.
"""
    def __init__(self, *, scope):
        super().__init__()
        require_scope(scope)
        self.scope = scope
        self.net = nn.Sequential(nn.Linear(WIDTH, 64), nn.ReLU(),
                                 nn.Linear(64, 64), nn.ReLU(), nn.Linear(64, 1))
        self.register_buffer('card_columns', torch.tensor(CARD_COLUMNS, dtype=torch.long))

    def forward(self, full_features):
        if full_features.ndim != 2 or full_features.shape[1] != 387:
            raise ValueError('Full 387-column visible/public feature rows required')
        cards = full_features.index_select(1, self.card_columns)
        return torch.sigmoid(self.net(cards).squeeze(1))

    def normalized_values(self, full_features, economics, *, terminal_call_confirmed):
        if terminal_call_confirmed is not True:
            raise ValueError('A qualified terminal heads-up Fold/Call context is required')
        if economics.ndim != 2 or economics.shape != (len(full_features), 5):
            raise ValueError('One five-column economics row per observation required')
        # Values retain their documented physical normalization. The fitting
        # adapter must validate finite positive stacks/net pots and legal prices
        # once when constructing a dataset, not synchronize CUDA every minibatch.
        q = self(full_features)
        e = economics.to(dtype=q.dtype, device=q.device)
        call = q * (e[:, 1] / e[:, 0]) - e[:, 2] / e[:, 0]
        return torch.stack((torch.zeros_like(call), call), dim=1)


def fresh(seed, *, scope, device='cpu', dtype=torch.float32):
    """Reproducible card encoder, neutral 50% initial equity and no global RNG mutation."""
    require_scope(scope)
    if type(seed) is not int or seed < 0:
        raise ValueError('Nonnegative integer seed required')
    with torch.random.fork_rng(devices=[]):
        torch.manual_seed(seed)
        model = EquityPricedNetwork(scope=scope)
        with torch.no_grad():
            model.net[-1].weight.zero_()
            model.net[-1].bias.zero_()
    return model.to(device=device, dtype=dtype)


def validate_economics(economics, *, terminal_call_confirmed):
    if terminal_call_confirmed is not True:
        raise ValueError('Terminal call confirmation required')
    e = np.asarray(economics, dtype=np.float64)
    if e.ndim != 2 or e.shape[1] != 5 or len(e) == 0 or not np.isfinite(e).all():
        raise ValueError('Finite nonempty five-column economics required')
    if np.any(e[:, :3] <= 0) or np.any((e[:, 3] != 0) & (e[:, 3] != 1)):
        raise ValueError('Positive stack, net pot, call cost and a heads-up actor required')
    if np.any(e[:, 2] > e[:, 0]):
        raise ValueError('Call must fit the starting stack')
    if not np.allclose(e[:, 4], e[:, 2] / e[:, 1], rtol=0, atol=1e-12):
        raise ValueError('Calling-price metadata does not match the cash flows')
    return e


def numpy_equity(state_dict, full_features):
    """Independent dense readback, widening saved weights before arithmetic."""
    x = np.asarray(full_features, dtype=np.float64)
    if x.ndim != 2 or x.shape[1] != 387 or not np.isfinite(x).all():
        raise ValueError('Finite complete visible/public rows required')
    if not np.array_equal(state_dict.get('card_columns'), CARD_COLUMNS):
        raise ValueError('Saved card-column contract changed')
    x = x[:, CARD_COLUMNS]
    for layer in (0, 2, 4):
        w = np.asarray(state_dict[f'net.{layer}.weight'], dtype=np.float64)
        b = np.asarray(state_dict[f'net.{layer}.bias'], dtype=np.float64)
        if not np.isfinite(w).all() or not np.isfinite(b).all():
            raise ValueError('Nonfinite model weights')
        x = x @ w.T + b
        if layer != 4:
            x = np.maximum(x, 0)
    if x.shape != (len(full_features), 1):
        raise ValueError('Wrong equity-head shape')
    logits = x[:, 0]
    if not np.isfinite(logits).all():
        raise ValueError('Nonfinite equity logits')
    q = np.empty_like(logits)
    positive = logits >= 0
    q[positive] = 1 / (1 + np.exp(-logits[positive]))
    t = np.exp(logits[~positive])
    q[~positive] = t / (1 + t)
    return q


def price_estimate(equity, economics, *, scope, terminal_call_confirmed,
                   assumed_equity_error_bound=None):
    """Price an estimate; optional bounds are assumptions, not learned confidence.

All rows keep a definite greedy action and remain in evaluation. A separate
stability code (-1 unresolved, 0 fold, 1 call) must never be used to drop hard
rows from a scientific accuracy metric. Ties choose fold.
    """
    require_scope(scope)
    e = validate_economics(economics, terminal_call_confirmed=terminal_call_confirmed)
    q = np.asarray(equity, dtype=np.float64)
    if q.shape != (len(e),) or not np.isfinite(q).all() or np.any((q < 0) | (q > 1)):
        raise ValueError('One finite equity in [0,1] per economics row required')
    margin = e[:, 1] * q - e[:, 2]
    result = dict(fold_value_bb=np.zeros_like(margin), call_value_bb=margin,
                  normalized_call_value=margin / e[:, 0], call_probability=(margin > 0).astype(float))
    if assumed_equity_error_bound is not None:
        bound = np.broadcast_to(np.asarray(assumed_equity_error_bound, dtype=np.float64), q.shape)
        if not np.isfinite(bound).all() or np.any((bound < 0) | (bound > 1)):
            raise ValueError('Finite assumed equity error bounds in [0,1] required')
        lower = e[:, 1] * np.maximum(0, q - bound) - e[:, 2]
        upper = e[:, 1] * np.minimum(1, q + bound) - e[:, 2]
        result.update(assumed_call_value_lower_bb=lower, assumed_call_value_upper_bb=upper,
                      assumed_greedy_loss_bound_bb=e[:, 1] * bound,
                      stability_code=np.where(lower > 0, 1, np.where(upper <= 0, 0, -1)))
    return result
