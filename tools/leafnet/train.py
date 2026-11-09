#!/usr/bin/env python3
"""Leaf-net trainer: THE file the autoresearch agent edits (see program.md).

    python tools/leafnet/train.py --desc "what this run changes" [--seed N]

run() trains on the frozen snapshot within the harness's fixed budget and
returns a torch.nn.Sequential of Linear and ReLU layers that maps normalized
features (n, 686) to the residual (n, 338): solved value minus the balanced
model's, out of position 169 classes then in position 169, as a fraction of
the pot. Anything else (batch norm, other activations, ensembles) must be
folded into such a stack before returning, or the harness rejects the run as
not deployable. The harness scores it, applies the keep rule and logs it.

Baseline: leaf net v1's setup from gonogo.py (2 x 512 ReLU, Adam 1e-3,
L2 1e-5 on weights, batch 256, early stopping on validation, lr x0.3 when
validation stalls).
"""

import copy
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import torch  # noqa: E402

import harness  # noqa: E402

CONFIG = {
    "hidden": 512,          # width of each hidden layer
    "depth": 2,             # hidden layers
    "lr": 1e-3,
    "weight_decay": 1e-5,   # L2 on weights (not biases), added to the gradient as in gonogo's numpy Adam
    "batch": 256,
    "eval_every": 250,      # steps between validation checks
    "patience": 20,         # validation checks without improvement before stopping
    "lr_drop": 0.3,         # lr multiplier at patience // 2 stale checks
    "last_layer_scale": 0.1,
}


def build(cfg, n_in, n_out):
    layers, d = [], n_in
    for _ in range(cfg["depth"]):
        lin = torch.nn.Linear(d, cfg["hidden"])
        torch.nn.init.normal_(lin.weight, std=(2.0 / d) ** 0.5)
        torch.nn.init.zeros_(lin.bias)
        layers += [lin, torch.nn.ReLU()]
        d = cfg["hidden"]
    out = torch.nn.Linear(d, n_out)
    torch.nn.init.normal_(out.weight, std=(2.0 / d) ** 0.5 * cfg["last_layer_scale"])
    torch.nn.init.zeros_(out.bias)
    return torch.nn.Sequential(*layers, out)


def run(cfg, data, budget, generator):
    model = build(cfg, data.n_in, data.n_out).to(data.device)
    weights = [p for n, p in model.named_parameters() if n.endswith("weight")]
    biases = [p for n, p in model.named_parameters() if n.endswith("bias")]
    opt = torch.optim.Adam([{"params": weights, "weight_decay": cfg["weight_decay"]},
                            {"params": biases, "weight_decay": 0.0}], lr=cfg["lr"])
    best, best_state, stale, step = float("inf"), None, 0, 0
    batches = data.batches(cfg["batch"], generator)
    model.train()
    while not budget.done(step):
        x, r, w = next(batches)
        loss = (w * (model(x) - r) ** 2).sum() / w.sum().clamp_min(1e-9)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        opt.step()
        step += 1
        if step % cfg["eval_every"] == 0:
            va = data.val_loss(model)
            if va < best * (1 - 1e-4):
                best, stale, best_state = va, 0, copy.deepcopy(model.state_dict())
            else:
                stale += 1
                if stale == cfg["patience"] // 2:
                    for g in opt.param_groups:
                        g["lr"] *= cfg["lr_drop"]
                if stale >= cfg["patience"]:
                    break
    if best_state is not None:
        model.load_state_dict(best_state)
    model.steps_taken = step
    return model


if __name__ == "__main__":
    harness.main(run, CONFIG)
