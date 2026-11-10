#!/usr/bin/env python3
"""Low-noise validation targets for the keep rule ("val_cv").

    python tools/leafnet/referee.py [--snapshot SNAP] [--seed 7919]

Every validation example is solved on ONE random flop, so its value carries
that flop's luck, which no flop-blind net can predict. Once a net is good,
that luck is most of the validation error and it hides real differences
between nets. This trains a flop-aware referee teacher (flops.Teacher, fixed
settings, a seed no training run uses) on the training split, then writes
validation targets with its flop luck taken out:

    y_cv = y - (referee on the example's own flop - referee's average over all flops)

averaged with the flop probabilities and scoring weights, the same way
`Teacher.marginal` averages. The correction has mean zero over flops for every
spot whatever the referee gets wrong, so y_cv has the same expected error
differences between nets as y. It is far less noisy. A referee that fits
poorly removes less noise but does not tilt the score, so it doesn't favour
nets trained on a teacher. The keep rule still checks the raw validation
error as a guard (harness.py).

Writes snapshots/SNAP/referee/val_cv.npy (n_val, 2, 169) and referee.json
(settings, the referee's errors, the file's sha256, which harness.py checks).
Run it once per snapshot, before `harness.py noise` (or follow it with
`harness.py rescore` on a snapshot that already has runs). Frozen: the
autoresearch agent never edits it.
"""

import argparse
import copy
import datetime
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402
import torch  # noqa: E402

import flops  # noqa: E402
import harness  # noqa: E402
from gonogo import totals  # noqa: E402

NC = flops.NC
REF_SEED = 7919
SETTINGS = {"steps": 16000, "lr": 1e-3, "wd": 1e-5, "eq": 1.0, "batch": 512}


def sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def train_referee(data, seed, s):
    """A flop-aware teacher on the whole training split, early-stopped on validation (with the flop)."""
    dev = data.device
    flop, eq, _ = flops.load_side(data)
    split = np.load(os.path.join(data.dir, "split.npy"))
    tr, va = np.nonzero(split == harness.SPLITS["train"])[0], np.nonzero(split == harness.SPLITS["val"])[0]
    assert len(tr) == data.n_train and len(va) == data.val.n
    tabs = flops.flop_tables()
    mu, sd = (torch.from_numpy(a[:2 * NC]).to(dev) for a in (data.mu, data.sd))
    rng_of = lambda xn: (xn[:, :2 * NC].float() * sd + mu).clamp(0, 1).view(-1, 2, NC)
    f_tr, f_va = (torch.from_numpy(flop[i].astype(np.int64)).to(dev) for i in (tr, va))
    assert int(f_tr.min()) >= 0 and int(f_va.min()) >= 0
    eq_tr = torch.from_numpy(eq[tr].reshape(len(tr), -1)).to(dev)
    rng_va = rng_of(data.x_val)
    harness.seed_everything(seed)
    gen = torch.Generator().manual_seed(seed)
    model = flops.Teacher(data.n_in, tabs).to(dev)
    weights = [p for n, p in model.named_parameters() if n.endswith("weight")]
    others = [p for n, p in model.named_parameters() if not n.endswith("weight")]
    opt = torch.optim.Adam([{"params": weights, "weight_decay": s["wd"]},
                            {"params": others, "weight_decay": 0.0}], lr=s["lr"])

    def own_val():
        with torch.no_grad():
            return torch.cat([model(data.x_val[i:i + 2048], rng_va[i:i + 2048], f_va[i:i + 2048])[0]
                              for i in range(0, len(f_va), 2048)])

    def val_loss():
        model.eval()
        pred = own_val()
        model.train()
        return float((data.w_val * (pred - data.r_val) ** 2).sum() / data.w_val.sum())

    best, best_state, stale, step, n, bs, done = float("inf"), None, 0, 0, data.n_train, s["batch"], False
    t0 = time.time()
    while not done:
        perm = torch.randperm(n, generator=gen, device="cpu").to(dev)
        for i in range(0, n - bs + 1, bs):
            idx = perm[i:i + bs]
            x, r, w = data.x_train[idx].float(), data.r_train[idx].float(), data.w_train[idx].float()
            val, e = model(x, rng_of(x), f_tr[idx])
            ws = w.sum().clamp_min(1e-9)
            loss = (w * (val - r) ** 2).sum() / ws + s["eq"] * (w * (e - (eq_tr[idx].float() - 0.5)) ** 2).sum() / ws
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step()
            step += 1
            if step % 500 == 0:
                v = val_loss()
                if v < best * (1 - 1e-4):
                    best, stale, best_state = v, 0, copy.deepcopy(model.state_dict())
                else:
                    stale += 1
                    if stale == 4:
                        for g in opt.param_groups:
                            g["lr"] *= 0.3
                harness.log(f"referee step {step}: validation error with the flop {v:.5f} (best {best:.5f})")
                if stale >= 8 or step >= s["steps"]:
                    done = True
                    break
    model.load_state_dict(best_state)
    model.eval()
    own = own_val()
    avg = torch.cat([model.marginal(data.x_val[i:i + 1024], rng_va[i:i + 1024])[0]
                     for i in range(0, len(f_va), 1024)])
    torch.cuda.empty_cache()
    info = {"steps": step, "seconds": round(time.time() - t0), "val_error_with_flop": best}
    return own.cpu().numpy(), avg.cpu().numpy(), info


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--work", default=harness.work_dir())
    ap.add_argument("--snapshot")
    ap.add_argument("--seed", type=int, default=REF_SEED)
    ap.add_argument("--force", action="store_true", help="replace an existing referee (rescore every run after)")
    args = ap.parse_args()
    data = harness.Data(args.work, args.snapshot)
    out = os.path.join(data.dir, "referee")
    path = os.path.join(out, "val_cv.npy")
    if os.path.exists(path) and not args.force:
        sys.exit(f"{path} exists (use --force to replace it, then `harness.py rescore`)")
    own, avg, info = train_referee(data, args.seed, SETTINGS)
    val = data.val
    corr = (own - avg).reshape(val.n, 2, NC) * val.mask
    y_cv = (val.y - corr).astype(np.float32)
    os.makedirs(out, exist_ok=True)
    np.save(path, y_cv)
    bal = val.base["balanced"]
    raw, cv = totals(val.sums(bal)), totals(per_job(val, bal, y_cv))
    r_own = totals(per_job(val, bal + own.reshape(val.n, 2, NC), val.y))
    r_avg_raw = totals(per_job(val, bal + avg.reshape(val.n, 2, NC), val.y))
    r_avg_cv = totals(per_job(val, bal + avg.reshape(val.n, 2, NC), y_cv))
    meta = {"created": datetime.datetime.now().isoformat(timespec="seconds"), "snapshot": data.snapshot,
            "seed": args.seed, "settings": SETTINGS, **info, "n_val": int(val.n),
            "flops_sha256": sha256(os.path.join(HERE, "flops.py"))[:16],
            "val_cv_sha256": sha256(path),
            "class_error": {"balanced_raw": raw[0], "balanced_cv": cv[0], "referee_own_flop_raw": r_own[0],
                            "referee_flop_average_raw": r_avg_raw[0], "referee_flop_average_cv": r_avg_cv[0]}}
    with open(os.path.join(out, "referee.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(meta, f, indent=1)
    print(json.dumps(meta, indent=1))


def per_job(es, pred, y):
    from gonogo import per_job_sums
    return per_job_sums(es.jobs, pred, y, es.w, es.reach, es.mask)


if __name__ == "__main__":
    main()
