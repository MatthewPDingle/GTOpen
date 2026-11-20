"""The "near zero" inputs as the first module of a net in training.

A leaf net's range inputs are weights on a linear scale (a range's most
played hand is 1), so a hand the range does not hold (0) and a hand it plays
a little (0.02) look alike, and the net cannot give them different values.
A preflop solve reads the net hardest exactly there: the value of a hand it
does not play yet decides whether the hand enters the range. The "near zero"
layout (tools/datagen/leafnet_io.py, crates/solver/src/preflop/leafnet.rs)
adds one input per class and player, exp(-weight / NEAR_ZERO_TAU): 1 at
weight 0, 0.37 at 0.02, under 0.01 from 0.1 up.

In training the harness hands a net normalized inputs of the first layout
(n, 686). NearZero is the module that turns them into the wider layout: it
takes the normalization off the range columns, builds the extra inputs and
normalizes those with their own training mean and scale. The harness's export
drops the module and writes that mean and scale after the first layout's, so
the net file is a plain Linear/ReLU stack over 1,024 inputs and the Rust
loader, which builds the same inputs from the weights themselves, gives the
same numbers.
"""

import os
import sys

import numpy as np
import torch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "datagen"))
from leafnet_io import NC, NEAR_ZERO_TAU, N_INPUTS  # noqa: E402


class NearZero(torch.nn.Module):
    def __init__(self, mu, sd, extra_mu=None, extra_sd=None):
        """mu, sd: the first layout's normalization (the harness's data.mu and data.sd). extra_mu, extra_sd:
        the extra inputs' own (fit() sets them from the training rows; until then 0 and 1)."""
        super().__init__()
        k = 2 * NC
        as_t = lambda a: torch.as_tensor(np.asarray(a, np.float32)[:k].copy())  # noqa: E731
        self.register_buffer("mu", as_t(mu))
        self.register_buffer("sd", as_t(sd))
        self.register_buffer("extra_mu", torch.zeros(k) if extra_mu is None else as_t(extra_mu))
        self.register_buffer("extra_sd", torch.ones(k) if extra_sd is None else as_t(extra_sd))

    def raw(self, xn):
        """exp(-weight / tau) for each class of both ranges, from normalized first-layout inputs."""
        weight = (xn[:, :2 * NC].float() * self.sd + self.mu).clamp(0.0, 1.0)
        return torch.exp(-weight / NEAR_ZERO_TAU)

    def forward(self, xn):
        if xn.shape[1] != N_INPUTS:
            raise ValueError(f"NearZero takes the first layout ({N_INPUTS} inputs), not {xn.shape[1]}")
        return torch.cat([xn, (self.raw(xn) - self.extra_mu) / self.extra_sd], dim=1)

    def fit(self, x_train, chunk=65536):
        """Set the extra inputs' mean and scale from the training rows (normalized first-layout inputs, any
        float type and device). An input that never moves keeps scale 1, as the harness does for its own."""
        dev = self.mu.device
        with torch.no_grad():
            n, s1, s2 = 0, torch.zeros(2 * NC, dtype=torch.float64, device=dev), torch.zeros(2 * NC, dtype=torch.float64, device=dev)
            for i in range(0, len(x_train), chunk):
                e = self.raw(x_train[i:i + chunk].to(dev)).double()
                n, s1, s2 = n + len(e), s1 + e.sum(0), s2 + (e * e).sum(0)
            mean = s1 / max(n, 1)
            sd = (s2 / max(n, 1) - mean * mean).clamp_min(0).sqrt()
            self.extra_mu.copy_(mean.float())
            self.extra_sd.copy_(torch.where(sd < 1e-3, torch.ones_like(sd), sd).float())
        return self


def split(model):
    """(the model's NearZero or None, its other modules) for a torch.nn.Sequential; the module may only be
    the first."""
    mods = list(model)
    head = mods[0] if mods and isinstance(mods[0], NearZero) else None
    rest = mods[1:] if head is not None else mods
    if any(isinstance(m, NearZero) for m in rest):
        raise ValueError("not deployable: NearZero may only be the first module")
    return head, rest


def file_norm(head, mu, sd):
    """The net file's input mean and scale: the first layout's, then the extra inputs' when the net has them."""
    if head is None:
        return mu, sd
    return (np.concatenate([np.asarray(mu, np.float32), head.extra_mu.detach().cpu().numpy()]),
            np.concatenate([np.asarray(sd, np.float32), head.extra_sd.detach().cpu().numpy()]))
