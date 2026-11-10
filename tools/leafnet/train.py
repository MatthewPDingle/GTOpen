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

Flop-aware teachers (CONFIG["teacher"], flops.py). Every training example is
one leaf solved on ONE uniformly random flop, so most of its target is flop
luck. A teacher that also sees the flop, how each hand class connects with it
and where the class sits in both ranges on that flop explains almost all of
that luck (validation error about 0.003 against 0.139 flop-blind). Its
prediction averaged over all 1,755 distinct flops with the scoring weights is
a flop-blind target without the luck. Only training jobs teach a teacher (in
a scaling-grid data fraction, only that fraction's jobs); validation jobs
stop it early, as they stop the net; test jobs are never read. This file
never reads the referee's files (snapshots/.../referee/).

What the net is trained on (CONFIG["mode"]):
- "distill" (kept since loop 3): the mean flop average of several teachers
  (CONFIG["t_ens"], seeds 0-4), for the real leaves and, with "syn_ens", for
  the synthetic leaves. The net's error against that target was the same on
  training and validation leaves: it was underfitting, not overfitting. So
  the kept net is wide and shallow (2x768), lightly regularised and trained
  long; deeper nets (4x512, 5x512) and one very wide layer (1x1536) fit worse.
- "cv" (loop 2): the solved value minus one teacher's flop luck (value -
  (teacher on this flop - teacher's flop average)). Unbiased whatever the
  teacher gets wrong, but it keeps the teacher's residual noise; the better
  choice for a small net (2x256).

Synthetic leaves (CONFIG["n_syn"]): mixes of two training leaves of the same
pot type (ranges blended, pot and stack interpolated on a log scale, rake
from one of the two), priced with the balanced model by solve-cli like any
real leaf and labelled with the teachers' flop average. Leaving them out
costs accuracy on validation and on real leaves.

Seeds. With "t_ens" every seed shares the same teachers, and "syn_seed" also
shares the synthetic leaves, so seed replicates differ only in the net's
initialisation and batch order.

Cost. Side data (flops, teacher targets and models, synthetic leaves) is
cached in leafnet-loop2/ next to WORK. The teachers of "t_ens" must be in
that cache: each comes from a run of this file with that seed and "t_ens":
[] (about 9 minutes each). With them cached, a run takes about 6 minutes.
Training all five teachers inside one run would not fit the harness's
15-minute cap.

CONFIG["teacher"] = False gives back the plain recipe of the first loop.
"""

import copy
import hashlib
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402
import torch  # noqa: E402

import harness  # noqa: E402

CONFIG = {
    "hidden": 768,          # width of each hidden layer
    "depth": 2,             # hidden layers
    "lr": 1.953e-3,
    "weight_decay": 4.23e-6,  # L2 on weights (not biases), added to the gradient as in gonogo's numpy Adam
    "batch": 512,
    "eval_every": 250,      # steps between validation checks
    "patience": 40,         # validation checks without improvement before stopping
    "lr_drop": 0.114,       # lr multiplier at patience // 2 stale checks
    "last_layer_scale": 0.347,
    "teacher": True,        # flop-aware teacher, marginalized over all flops (see the module docstring)
    "mode": "distill",         # "cv": value minus the teacher's flop luck; "distill": the teacher's flop average
    "distill_mix": 0.0,     # weight of the pure flop-average loss next to the cv loss
    "t_steps": 16000,       # teacher step cap
    "t_lr": 1e-3,
    "t_wd": 1e-5,
    "t_eq": 1.0,            # weight of the teacher's auxiliary flop-equity output
    "t_cache": True,        # reuse the teacher's targets for the same snapshot, seed and teacher settings
    "val_cv": True,         # early-stop on validation targets with the teacher's flop luck removed
    "max_steps": 40000,     # student step cap (the harness's own budget is 60,000)
    "n_syn": 60000,         # teacher-labelled synthetic leaves (mixes of two training leaves) added to training
    "syn_lam_min": 0.0,     # smallest weight of the first leaf's ranges in a mix (0 = any blend)
    "syn_weight": 1.0,      # weight of the synthetic-leaf loss
    "t_ens": [0, 1, 2, 3, 4],  # average the real leaves' targets over the teachers of these seeds ([] = this run's only)
    "schedule": "plateau",  # "plateau": drop and stop on stale validation; "cosine": lr falls to 1% over max_steps
    "syn_seed": 0,          # whose teacher cache and synthetic leaves to use (None = the run's own seed)
    "syn_ens": True,        # label the synthetic leaves with the same teacher ensemble (needs the seeds' saved teachers)
}

from flops import NC, Teacher, flop_tables, load_side  # noqa: E402


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def train_rows(data, split):
    """Snapshot rows of the examples the student trains on, in data.x_train's order: the whole training
    split, or the part of it a scaling-grid data fraction keeps (data.train_index)."""
    tr = np.nonzero(split == harness.SPLITS["train"])[0]
    sel = getattr(data, "train_index", None)
    rows = tr if sel is None else tr[sel]
    assert len(rows) == data.n_train, "training rows do not match the training tensors"
    return rows


def subset_tag(data):
    """Cache-name suffix for a data fraction (empty for the whole training split), so the teacher and its
    synthetic leaves are never shared between fractions."""
    sel = getattr(data, "train_index", None)
    if sel is None:
        return ""
    return f"-n{len(sel)}-{hashlib.sha256(np.asarray(sel, np.int64).tobytes()).hexdigest()[:8]}"


def teacher_targets(cfg, data, generator):
    """Trains the teacher and returns, for the training rows: its flop average (n, 338), its prediction
    on each row's own flop (n, 338) and the flop-averaged weights (n, 338)."""
    flop, eq, cache_dir = load_side(data)
    tag = "-".join(str(cfg[k]) for k in ("t_steps", "t_lr", "t_wd", "t_eq"))
    stem = f"{data.snapshot}-s{cfg['seed']}-{tag}{subset_tag(data)}"
    n_syn = int(cfg.get("n_syn", 0))
    cache = os.path.join(cache_dir, f"teacher2-{stem}.pt")
    model_path = os.path.join(cache_dir, f"teacher2-model-{stem}.pt")
    lam_min = float(cfg.get("syn_lam_min", 0.0))
    syn_cache = os.path.join(cache_dir, f"syn-{stem}-{n_syn}" + (f"-lam{lam_min}" if lam_min else "") + ".pt")
    old = os.path.join(cache_dir, f"teacher-{stem}.pt")   # first format: no validation side, no saved teacher
    z = None
    for path in (cache, old):
        if cfg.get("t_cache") and os.path.exists(path) and not (path == old and (cfg.get("val_cv") or n_syn)):
            z = torch.load(path, map_location=data.device)
            log(f"teacher targets from {path}")
            break
    if z is not None and n_syn and os.path.exists(syn_cache):
        z.update(torch.load(syn_cache, map_location=data.device))
        log(f"synthetic leaves from {syn_cache}")
        return z
    if z is not None and not n_syn:
        return z
    have_model = bool(cfg.get("t_cache")) and os.path.exists(model_path)
    if z is not None and not have_model:
        z = None
    dev = data.device
    split = np.load(os.path.join(data.dir, "split.npy"))
    tr, va = train_rows(data, split), np.nonzero(split == harness.SPLITS["val"])[0]
    t0 = time.time()
    tabs = flop_tables()
    log(f"flop tables in {time.time() - t0:.0f} s")
    mu, sd = (torch.from_numpy(a[:2 * NC]).to(dev) for a in (data.mu, data.sd))
    rng_of = lambda xn: (xn[:, :2 * NC].float() * sd + mu).clamp(0, 1).view(-1, 2, NC)
    f_tr, f_va = (torch.from_numpy(flop[i].astype(np.int64)).to(dev) for i in (tr, va))
    assert int(f_tr.min()) >= 0 and int(f_va.min()) >= 0
    eq_tr = torch.from_numpy(eq[tr].reshape(len(tr), -1)).to(dev)           # float16
    rng_va = rng_of(data.x_val)
    model = Teacher(data.n_in, tabs).to(dev)
    weights = [p for n, p in model.named_parameters() if n.endswith("weight")]
    others = [p for n, p in model.named_parameters() if not n.endswith("weight")]
    opt = torch.optim.Adam([{"params": weights, "weight_decay": cfg["t_wd"]},
                            {"params": others, "weight_decay": 0.0}], lr=cfg["t_lr"])

    def val_loss():
        model.eval()
        with torch.no_grad():
            pred = torch.cat([model(data.x_val[i:i + 2048], rng_va[i:i + 2048], f_va[i:i + 2048])[0]
                              for i in range(0, len(f_va), 2048)])
        model.train()
        return float((data.w_val * (pred - data.r_val) ** 2).sum() / data.w_val.sum())

    best, best_state, stale, step, n, bs = float("inf"), None, 0, 0, data.n_train, 512
    done = have_model
    if have_model:
        best_state = torch.load(model_path, map_location=dev)
        log(f"teacher from {model_path}")
    while not done:
        perm = torch.randperm(n, generator=generator, device="cpu").to(dev)
        for i in range(0, n - bs + 1, bs):
            idx = perm[i:i + bs]
            x, r, w = data.x_train[idx].float(), data.r_train[idx].float(), data.w_train[idx].float()
            val, e = model(x, rng_of(x), f_tr[idx])
            ws = w.sum().clamp_min(1e-9)
            loss = (w * (val - r) ** 2).sum() / ws + cfg["t_eq"] * (w * (e - (eq_tr[idx].float() - 0.5)) ** 2).sum() / ws
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
                log(f"teacher step {step}: flop-aware validation error {v:.5f} (best {best:.5f})")
                if stale >= 8 or step >= cfg["t_steps"]:
                    done = True
                    break
    model.load_state_dict(best_state)
    model.eval()
    if z is None:
        t1 = time.time()
        Tv, _ = model.marginal(data.x_val, rng_va)
        v_marg = float((data.w_val * (Tv - data.r_val) ** 2).sum() / data.w_val.sum())
        log(f"teacher: {step} steps in {t1 - t0:.0f} s; validation error with the flop {best:.5f}, "
            f"flop-averaged (flop-blind) {v_marg:.6f}")
        T, wbar = model.marginal(data.x_train, rng_of(data.x_train))
        with torch.no_grad():
            own = torch.cat([model(data.x_train[i:i + 2048].float(), rng_of(data.x_train[i:i + 2048]),
                                   f_tr[i:i + 2048])[0] for i in range(0, n, 2048)])
            ownv = torch.cat([model(data.x_val[i:i + 2048], rng_va[i:i + 2048], f_va[i:i + 2048])[0]
                              for i in range(0, len(f_va), 2048)])
        log(f"flop averages for {n:,} training leaves in {time.time() - t1:.0f} s")
        z = {"T": T.half(), "own": own.half(), "wbar": wbar.half(), "Tv": Tv, "ownv": ownv,
             "val_flop": best, "val_marginal": v_marg}
        if cfg.get("t_cache"):
            torch.save(z, cache)
            torch.save(best_state, model_path)
    if n_syn:
        syn = synth_leaves(cfg, data, model, n_syn)
        if cfg.get("t_cache"):
            torch.save(syn, syn_cache)
        z.update(syn)
    del model, opt
    torch.cuda.empty_cache()
    return z


def synth_leaves(cfg, data, model, n_syn):
    """Extra training leaves labelled by the teacher's flop average: mixes of two training leaves of the
    same pot type (ranges blended, pot and stack interpolated on a log scale, rake from one of the two),
    priced with the balanced model by solve-cli like any real leaf. Only training leaves are mixed."""
    sys.path.insert(0, os.path.join(harness.ROOT, "tools", "datagen"))
    import gonogo
    import leafnet_io
    from validate import default_cli
    t0 = time.time()
    r_ = np.random.default_rng(1000 + int(cfg["seed"]))
    tr = train_rows(data, np.load(os.path.join(data.dir, "split.npy")))
    xtr = np.asarray(np.load(os.path.join(data.dir, "x.npy"), mmap_mode="r")[tr], np.float64)
    rng, meta = xtr[:, :2 * NC].reshape(-1, 2, NC), xtr[:, -10:]
    pt = meta[:, 6:10].argmax(1)
    a = r_.integers(0, len(tr), n_syn)
    b = np.zeros(n_syn, np.int64)
    for t in range(4):
        sel = pt[a] == t
        b[sel] = r_.choice(np.nonzero(pt == t)[0], int(sel.sum()))
    lo = float(cfg.get("syn_lam_min", 0.0))    # 0: any blend of the two ranges; near 1: stays close to the first leaf
    lam = np.where(r_.random(n_syn) < 0.7, lo + (1 - lo) * r_.random(n_syn), 1.0)[:, None, None]
    mix = lam * rng[a] + (1 - lam) * rng[b]
    mix = np.round(mix / np.maximum(mix.max(axis=2, keepdims=True), 1e-9), 5)
    u = r_.random(n_syn)
    pot = np.exp(u * meta[a, 0] + (1 - u) * meta[b, 0])
    stack = np.exp(u * meta[a, 1] + (1 - u) * meta[b, 1])
    src = np.where(r_.random(n_syn) < 0.5, a, b)
    rake, cap = meta[src, 3] / 10, meta[src, 4] * np.exp(meta[src, 0])
    recs = [{"job": 0, "index": i, "board": "2c7d9h", "pot_type": leafnet_io.POT_TYPES[pt[a[i]]],
             "pot_bb": float(pot[i]), "stack_bb": float(stack[i]), "rake_pct": float(rake[i]),
             "rake_cap_bb": float(cap[i]), "range": mix[i].tolist()} for i in range(n_syn)]
    base = np.nan_to_num(gonogo.baselines(default_cli(), recs, chunk=4000)["balanced"])
    metaf = np.asarray([leafnet_io.meta_features(r["pot_bb"], r["stack_bb"], r["rake_pct"], r["rake_cap_bb"],
                                                 r["pot_type"]) for r in recs], np.float32)
    xs = gonogo.features(mix.astype(np.float32), metaf, base)
    xsn = torch.from_numpy(((xs - data.mu) / data.sd).astype(np.float32))
    mixt = torch.from_numpy(mix.astype(np.float32))
    t1 = time.time()
    Ts, ws = [], []
    for i in range(0, n_syn, 4096):          # in slices, results parked on the CPU: stays far under the VRAM cap
        t_, w_ = model.marginal(xsn[i:i + 4096].to(data.device), mixt[i:i + 4096].to(data.device))
        Ts.append(t_.half().cpu())
        ws.append(w_.half().cpu())
    torch.cuda.empty_cache()
    log(f"{n_syn:,} synthetic leaves: priced in {t1 - t0:.0f} s, labelled by the teacher in {time.time() - t1:.0f} s")
    return {"xs": xsn.half().to(data.device), "Ts": torch.cat(Ts).to(data.device), "ws": torch.cat(ws).to(data.device)}


def ensemble_syn_labels(cfg, data, xs, Ts_own):
    """The synthetic leaves' labels averaged over the teachers of cfg["t_ens"] (this run's own teacher's
    labels are Ts_own; the others are loaded from their saved models). Cached like the other side data."""
    _, _, cache_dir = load_side(data)
    tag = "-".join(str(cfg[k]) for k in ("t_steps", "t_lr", "t_wd", "t_eq"))
    lam_min = float(cfg.get("syn_lam_min", 0.0))
    seeds = [int(s) for s in cfg["t_ens"]]
    name = (f"synens-{data.snapshot}-s{cfg['seed']}-{tag}{subset_tag(data)}-{len(xs)}"
            + (f"-lam{lam_min}" if lam_min else "") + "-t" + "_".join(map(str, seeds)) + ".pt")
    path = os.path.join(cache_dir, name)
    if cfg.get("t_cache") and os.path.exists(path):
        log(f"ensemble labels for the synthetic leaves from {path}")
        return torch.load(path, map_location=data.device)
    dev = data.device
    t0 = time.time()
    tabs = flop_tables()
    mu, sd = (torch.from_numpy(a[:2 * NC]).to(dev) for a in (data.mu, data.sd))
    total = torch.zeros(Ts_own.shape, dtype=torch.float32)
    n_models = 0
    for s in seeds:
        if s == int(cfg["seed"]):
            total += Ts_own.float().cpu()
            n_models += 1
            continue
        mp = os.path.join(cache_dir, f"teacher2-model-{data.snapshot}-s{s}-{tag}{subset_tag(data)}.pt")
        if not os.path.exists(mp):
            raise FileNotFoundError(f"no saved teacher for seed {s}: run that seed once first ({mp})")
        model = Teacher(data.n_in, tabs).to(dev)
        model.load_state_dict(torch.load(mp, map_location=dev))
        model.eval()
        for i in range(0, len(xs), 4096):
            x = xs[i:i + 4096].float()
            rng = (x[:, :2 * NC] * sd + mu).clamp(0, 1).view(-1, 2, NC)
            total[i:i + 4096] += model.marginal(x, rng)[0].float().cpu()
        n_models += 1
        del model
        torch.cuda.empty_cache()
    out = (total / n_models).half().to(dev)
    log(f"synthetic leaves labelled by {n_models} teachers in {time.time() - t0:.0f} s")
    if cfg.get("t_cache"):
        torch.save(out, path)
    return out


# --------------------------------------------------------------- student ----

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
    T = own = wbar = r_val_cv = xs = Ts = ws = None
    if cfg.get("teacher"):
        # the teachers' side data (and the synthetic leaves) of cfg["syn_seed"] when set, so seed replicates share
        # their targets and differ only in the net's initialisation and batch order
        tcfg = cfg if cfg.get("syn_seed") is None else dict(cfg, seed=int(cfg["syn_seed"]))
        z = teacher_targets(tcfg, data, generator)
        T, own, wbar = z["T"], z["own"], z["wbar"]
        if cfg.get("n_syn"):
            xs, Ts, ws = z["xs"], z["Ts"], z["ws"]
        if cfg.get("t_ens"):
            # average the real leaves' targets over several teachers (seeds); each is trained or read from the cache
            zs = [teacher_targets(dict(cfg, seed=s, n_syn=0, val_cv=False), data, generator) for s in cfg["t_ens"]]
            T = torch.stack([q["T"].float() for q in zs]).mean(0).half()
            own = torch.stack([q["own"].float() for q in zs]).mean(0).half()
            del zs
            if cfg.get("syn_ens") and xs is not None:
                Ts = ensemble_syn_labels(tcfg, data, xs, Ts)
        if cfg.get("val_cv"):
            # early stopping on validation targets with the teacher's flop luck removed (far less noisy)
            r_val_cv = data.r_val - (z["ownv"] - z["Tv"]) * (data.w_val > 0)

    def val_loss(m):
        if r_val_cv is None:
            return data.val_loss(m)
        with torch.no_grad():
            m.eval()
            pred = m(data.x_val)
            m.train()
            return float((data.w_val * (pred - r_val_cv) ** 2).sum() / data.w_val.sum())

    model = build(cfg, data.n_in, data.n_out).to(data.device)
    weights = [p for n, p in model.named_parameters() if n.endswith("weight")]
    biases = [p for n, p in model.named_parameters() if n.endswith("bias")]
    opt = torch.optim.Adam([{"params": weights, "weight_decay": cfg["weight_decay"]},
                            {"params": biases, "weight_decay": 0.0}], lr=cfg["lr"])
    best, best_state, stale, step = float("inf"), None, 0, 0
    n, bs, mix = data.n_train, cfg["batch"], cfg.get("distill_mix", 0.0)
    cosine = cfg.get("schedule", "plateau") == "cosine"   # lr falls to 1% over max_steps; no early stop
    ema = None
    model.train()
    stop = False
    while not stop:
        perm = torch.randperm(n, generator=generator, device="cpu").to(data.device)
        for i in range(0, n - bs + 1, bs):
            if budget.done(step) or step >= cfg.get("max_steps", 10 ** 9):
                stop = True
                break
            idx = perm[i:i + bs]
            x, r, w = data.x_train[idx].float(), data.r_train[idx].float(), data.w_train[idx].float()
            if xs is not None:
                j = torch.randint(0, len(xs), (bs,), generator=generator).to(data.device)
                both = model(torch.cat([x, xs[j].float()]))
                pred, ps = both[:len(x)], both[len(x):]
            else:
                pred = model(x)
            if T is None:
                loss = (w * (pred - r) ** 2).sum() / w.sum().clamp_min(1e-9)
            else:
                t, wb = T[idx].float(), wbar[idx].float()
                if cfg["mode"] == "cv":
                    target = r - (own[idx].float() - t)
                    loss = (w * (pred - target) ** 2).sum() / w.sum().clamp_min(1e-9)
                    if mix:
                        loss = (1 - mix) * loss + mix * (wb * (pred - t) ** 2).sum() / wb.sum().clamp_min(1e-9)
                else:
                    loss = (wb * (pred - t) ** 2).sum() / wb.sum().clamp_min(1e-9)
                lv = float(loss.detach())                                   # real leaves only
                ema = lv if ema is None else 0.99 * ema + 0.01 * lv
                if xs is not None:
                    wj = ws[j].float()
                    loss = loss + cfg.get("syn_weight", 1.0) * (wj * (ps - Ts[j].float()) ** 2).sum() / wj.sum().clamp_min(1e-9)
            if cosine:
                frac = min(step / max(cfg["max_steps"], 1), 1.0)
                for g in opt.param_groups:
                    g["lr"] = cfg["lr"] * (0.01 + 0.99 * 0.5 * (1 + math.cos(math.pi * frac)))
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step()
            step += 1
            if step % cfg["eval_every"] == 0:
                va = val_loss(model)
                if step % (10 * cfg["eval_every"]) == 0 and ema is not None:
                    log(f"step {step}: training loss on the real leaves {ema:.6f}, early-stopping loss {va:.6f}")
                if va < best * (1 - cfg.get("min_rel_gain", 1e-4)):
                    best, stale, best_state = va, 0, copy.deepcopy(model.state_dict())
                elif not cosine:
                    stale += 1
                    if stale == cfg["patience"] // 2:
                        for g in opt.param_groups:
                            g["lr"] *= cfg["lr_drop"]
                    if stale >= cfg["patience"]:
                        stop = True
                        break
    if best_state is not None:
        model.load_state_dict(best_state)
    model.steps_taken = step
    return model


if __name__ == "__main__":
    harness.main(run, CONFIG)
