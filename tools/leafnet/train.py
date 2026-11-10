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

Flop-aware teacher (CONFIG["teacher"]). Every training example is one leaf
solved on ONE uniformly random flop, so most of its target is flop luck. A
teacher that also sees the flop, how each hand class connects with it and
where the class sits in both ranges on that flop explains almost all of that
luck (validation error about 0.003 against 0.139 flop-blind). Its prediction
is averaged over all 1,755 distinct flops with the scoring weights, and the
deployed flop-blind net is trained on the solved value with the teacher's
flop luck removed ("cv": value - (teacher on this flop - teacher's flop
average)): same mean, far less noise. Only training jobs teach the teacher;
validation jobs stop it early, as they stop the net; test jobs are never read.

Synthetic leaves (CONFIG["n_syn"]). With clean targets the limit is how many
distinct leaves the net sees. The teacher labels extra leaves for free: mixes
of two training leaves of the same pot type (ranges blended, pot and stack
interpolated on a log scale, rake from one of the two), priced with the
balanced model by solve-cli like any real leaf and labelled with the
teacher's flop average. 60,000 of them are on in the kept configuration
(confirmed on seeds 0, 1 and 2 with `harness.py confirm`).

Options that are off in the kept configuration: early stopping on validation
targets with the flop luck removed (val_cv), targets averaged over several
teachers (t_ens), mixes that stay close to one real leaf (syn_lam_min), and
the pure flop average as the target (mode "distill"). CONFIG["teacher"] =
False gives back the plain recipe of the first loop (4x512, Adam, L2).

Side data (flop of each example, flop tables, teacher targets, synthetic
leaves) is cached in leafnet-loop2/ next to WORK. A run from scratch
(teacher and synthetic leaves included) takes about 10 minutes next to the
generator, inside the harness's 15-minute cap.
"""

import copy
import gzip
import itertools
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402
import torch  # noqa: E402

import harness  # noqa: E402

CONFIG = {
    "hidden": 512,          # width of each hidden layer
    "depth": 4,             # hidden layers
    "lr": 1.953e-3,
    "weight_decay": 4.23e-5,  # L2 on weights (not biases), added to the gradient as in gonogo's numpy Adam
    "batch": 512,
    "eval_every": 250,      # steps between validation checks
    "patience": 20,         # validation checks without improvement before stopping
    "lr_drop": 0.114,       # lr multiplier at patience // 2 stale checks
    "last_layer_scale": 0.347,
    "teacher": True,        # flop-aware teacher, marginalized over all flops (see the module docstring)
    "mode": "cv",           # "cv": value minus the teacher's flop luck; "distill": the teacher's flop average
    "distill_mix": 0.0,     # weight of the pure flop-average loss next to the cv loss
    "t_steps": 16000,       # teacher step cap
    "t_lr": 1e-3,
    "t_wd": 1e-5,
    "t_eq": 1.0,            # weight of the teacher's auxiliary flop-equity output
    "t_cache": True,        # reuse the teacher's targets for the same snapshot, seed and teacher settings
    "val_cv": False,        # early-stop on validation targets with the teacher's flop luck removed
    "max_steps": 60000,     # student step cap (the harness's own budget is 60,000)
    "n_syn": 60000,         # teacher-labelled synthetic leaves (mixes of two training leaves) added to training
    "syn_lam_min": 0.0,     # smallest weight of the first leaf's ranges in a mix (0 = any blend)
    "syn_weight": 1.0,      # weight of the synthetic-leaf loss
    "t_ens": [],            # average the real leaves' targets over the teachers of these seeds ([] = this run's only)
}

NC = 169
RANKS = "23456789TJQKA"


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


# ------------------------------------------------- flops and hand strength ----

def canon_key(cards):
    """[(rank, suit)] x 3 -> the flop's suit-isomorphism class: (ranks high to low, suit pattern)."""
    best = None
    for perm in itertools.permutations(cards):
        rk = tuple(c[0] for c in perm)
        if rk[0] < rk[1] or rk[1] < rk[2]:
            continue
        m, pat = {}, []
        for _, s in perm:
            if s not in m:
                m[s] = len(m)
            pat.append(m[s])
        key = (rk, tuple(pat))
        if best is None or key < best:
            best = key
    return best


def eval5(R, S):
    """Five-card hand values (higher wins), categories 0..8, for rank and suit arrays (N, 5)."""
    cnt = (R[:, :, None] == np.arange(13)[None, None, :]).sum(1)
    flush = (S == S[:, :1]).all(1)
    distinct = (cnt > 0).sum(1)
    mx, mn = R.max(1), R.min(1)
    wheel = (distinct == 5) & (cnt[:, [12, 0, 1, 2, 3]] > 0).all(1)
    straight = ((distinct == 5) & (mx - mn == 4)) | wheel
    key = np.take_along_axis(cnt, R, 1) * 16 + R
    rs = (-np.sort(-key, axis=1)) % 16
    tb = (((rs[:, 0] * 13 + rs[:, 1]) * 13 + rs[:, 2]) * 13 + rs[:, 3]) * 13 + rs[:, 4]
    maxc, npairs = cnt.max(1), (cnt == 2).sum(1)
    cat = np.zeros(len(R), np.int64)
    cat[(npairs == 1) & (maxc == 2)] = 1
    cat[npairs == 2] = 2
    cat[(maxc == 3) & (npairs == 0)] = 3
    cat[straight & ~flush] = 4
    cat[flush & ~straight] = 5
    cat[(maxc == 3) & (npairs == 1)] = 6
    cat[maxc == 4] = 7
    cat[straight & flush] = 8
    top = np.where(wheel, 3, mx)
    return cat * 13 ** 5 + np.where(straight, top, tb), cat, cnt, straight, flush


def flop_tables():
    """Everything the teacher knows about the 1,755 distinct flops:
    ids {key: id}, mult (F,) flops per class, avail (F, 169) unblocked combos per hand class,
    feats (F, 65) texture, hs (F, 169, 12) how each hand class connects (strength percentile among all
    hands, flush draw, backdoor flush draw, gutshot, open-ended, made-hand category)."""
    deck = [(r, s) for r in range(13) for s in range(4)]
    counts = {}
    for combo in itertools.combinations(deck, 3):
        k = canon_key(list(combo))
        counts[k] = counts.get(k, 0) + 1
    keys = sorted(counts)
    ids = {k: i for i, k in enumerate(keys)}
    F = len(keys)
    mult = np.array([counts[k] for k in keys], np.float32)
    feats = np.zeros((F, 65), np.float32)
    pats = [(0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), (0, 1, 2)]
    iu = np.triu_indices(49, 1)
    R = np.zeros((F, 1176, 5), np.int64)
    S = np.zeros((F, 1176, 5), np.int64)
    cls = np.zeros((F, 1176), np.int64)
    for i, (rk, pat) in enumerate(keys):
        board = list(zip(rk, pat))
        rest = np.array([c for c in deck if c not in board])
        a, b = rest[iu[0]], rest[iu[1]]
        R[i, :, 0], R[i, :, 1], S[i, :, 0], S[i, :, 1] = a[:, 0], b[:, 0], a[:, 1], b[:, 1]
        for j, (r, s) in enumerate(board):
            R[i, :, 2 + j], S[i, :, 2 + j] = r, s
        hi, lo = np.maximum(a[:, 0], b[:, 0]), np.minimum(a[:, 0], b[:, 0])
        cls[i] = np.where(hi == lo, hi * 14, np.where(a[:, 1] == b[:, 1], hi * 13 + lo, lo * 13 + hi))
        f = feats[i]
        for j, r in enumerate(rk):
            f[j * 13 + r] = 1
            f[39 + r] += 1 / 3
        f[52 + pats.index(pat)] = 1
        f[57], f[58] = len(set(rk)) == 2, len(set(rk)) == 1
        f[59], f[60], f[61] = (rk[0] - rk[1]) / 12, (rk[1] - rk[2]) / 12, (rk[0] - rk[2]) / 12
        f[62], f[63] = len(set(pat)) == 1, len(set(pat)) == 2
        f[64] = sum(1 for lo_ in range(-1, 9)
                    if {(-1 if (r == 12 and lo_ == -1) else r) for r in set(rk)} <= set(range(lo_, lo_ + 5))) / 3
    val, cat, cnt, straight, flush = eval5(R.reshape(-1, 5), S.reshape(-1, 5))
    val = val.reshape(F, 1176)
    pct = np.zeros((F, 1176), np.float32)
    for i in range(F):
        srt = np.sort(val[i])
        pct[i] = (np.searchsorted(srt, val[i], "left") + np.searchsorted(srt, val[i], "right")) / (2 * 1176)
    suit_max = (S.reshape(-1, 5)[:, :, None] == np.arange(4)[None, None, :]).sum(1).max(1)
    pres = np.concatenate([cnt[:, 12:13] > 0, cnt > 0], axis=1)            # ace low, then 2..A
    outs = np.zeros((len(pres), 13), bool)
    for s in range(10):
        win = pres[:, s:s + 5]
        four = win.sum(1) == 4
        miss = np.argmin(win, axis=1) + s                                   # index in the ace-low layout
        rank = np.where(miss == 0, 12, miss - 1)
        outs[np.nonzero(four)[0], rank[four]] = True
    n_outs = np.where(straight, 0, outs.sum(1))
    made = np.minimum(cat, 6)
    per = np.concatenate([pct.reshape(-1, 1), ((suit_max == 4) & ~flush)[:, None], (suit_max == 3)[:, None],
                          (n_outs == 1)[:, None], (n_outs >= 2)[:, None],
                          made[:, None] == np.arange(7)[None, :]], axis=1).astype(np.float64)
    idx = (np.arange(F)[:, None] * NC + cls).ravel()
    n = np.bincount(idx, minlength=F * NC)
    hs = np.stack([np.bincount(idx, weights=per[:, k], minlength=F * NC) for k in range(per.shape[1])], 1)
    hs = (hs / np.maximum(n, 1)[:, None]).reshape(F, NC, -1).astype(np.float32)
    avail = n.reshape(F, NC).astype(np.float32)
    return ids, mult, avail, feats, hs


def load_side(data):
    """Canonical flop id of every snapshot row (-1 for test rows, which are never read) and the solved
    flop equities (n, 2, 169). Cached next to WORK (never inside it)."""
    cache_dir = os.path.join(os.path.dirname(os.path.abspath(data.work)), "leafnet-loop2")
    os.makedirs(cache_dir, exist_ok=True)
    cache = os.path.join(cache_dir, f"side-{data.snapshot}.npz")
    if os.path.exists(cache):
        z = np.load(cache)
        return z["flop"], z["eq"], cache_dir
    m = data.manifest
    split = np.load(os.path.join(data.dir, "split.npy"))
    jobs = np.load(os.path.join(data.dir, "jobs.npy"))
    ids = flop_tables()[0]
    n = len(split)
    flop = np.full(n, -1, np.int32)
    eq = np.zeros((n, 2, NC), np.float16)
    row = 0
    for fm in m["files_manifest"]:
        k = fm["examples"]
        if split[row] == harness.SPLITS["test"]:
            row += k
            continue
        with gzip.open(os.path.join(m["source"], fm["file"]), "rt", encoding="utf-8") as f:
            i = 0
            for line in f:
                if '"type":"example"' not in line.replace(" ", ""):
                    continue
                rec = json.loads(line)
                assert int(rec["job"]) == int(jobs[row + i]), "snapshot order does not follow the manifest"
                b = rec["board"]
                flop[row + i] = ids[canon_key([(RANKS.index(b[j]), b[j + 1]) for j in (0, 2, 4)])]
                eq[row + i] = np.nan_to_num(np.array(rec["eq"], np.float64)).astype(np.float16)
                i += 1
            assert i == k
        row += k
    np.savez(cache, flop=flop, eq=eq)
    return flop, eq, cache_dir


# --------------------------------------------------------------- teacher ----

class Teacher(torch.nn.Module):
    """Flop-aware value model: a trunk on the leaf's features, a flop branch, an additive fusion, and a
    small head shared by all 169 classes that sees how the class connects with the flop and where it
    sits in both ranges on that flop."""

    def __init__(self, n_in, tabs, width=768, fuse=1024, H=32):
        super().__init__()
        _, mult, avail, feats, hs = tabs
        L, R, S = torch.nn.Linear, torch.nn.ReLU, torch.nn.Sequential
        ff = np.concatenate([feats, hs[:, :, 0]], axis=1)
        self.trunk = S(L(n_in, width), R(), L(width, width), R())
        self.flop = S(L(ff.shape[1], 512), R(), L(512, 512), R())
        self.U, self.V = L(width, fuse), L(512, fuse, bias=False)
        self.W = L(fuse, width)
        self.O = L(width, 4 * NC)                       # value (2 x 169), then equity (2 x 169)
        self.C = L(width, 2 * 16)
        self.Wc = L(16, H, bias=False)
        self.WLs = L(hs.shape[2], H, bias=False)
        self.wl = torch.nn.Parameter(torch.randn(3, H) * 0.3)
        self.cls_bias = torch.nn.Parameter(torch.zeros(2, NC, H))
        self.Wo = L(H, 2)
        torch.nn.init.normal_(self.O.weight, std=(2.0 / width) ** 0.5 * 0.3)
        order = np.argsort(hs[:, :, 0], axis=1, kind="stable")
        rank = np.argsort(order, axis=1, kind="stable")
        for name, arr in (("flopfeat", ff), ("hs", hs), ("avail", avail), ("mult", mult)):
            self.register_buffer(name, torch.from_numpy(np.ascontiguousarray(arr)).float())
        self.register_buffer("order", torch.from_numpy(order).long())
        self.register_buffer("rank", torch.from_numpy(rank).long())

    def pos(self, rng, A, order, rank):
        """Share of each player's range (on this flop) that is weaker than each class: (..., 2, 169)."""
        r = rng * A.unsqueeze(-2)
        rs = torch.gather(r, -1, order.unsqueeze(-2).expand(r.shape))
        cum = rs.cumsum(-1) - 0.5 * rs
        tot = rs.sum(-1, keepdim=True).clamp_min(1e-6)
        return torch.gather(cum, -1, rank.unsqueeze(-2).expand(r.shape)) / tot

    def forward(self, xn, rng, fid):
        B = len(xn)
        z = torch.relu(self.W(torch.relu(self.U(self.trunk(xn)) + self.V(self.flop(self.flopfeat[fid])))))
        dense = self.O(z).view(B, 2, 2, NC)
        pos = self.pos(rng, self.avail[fid], self.order[fid], self.rank[fid])
        hid = self.Wc(self.C(z).view(B, 2, 16))[:, :, None, :] + self.cls_bias[None] + self.WLs(self.hs[fid])[:, None]
        hid = hid + pos.flip(1)[..., None] * self.wl[0] + pos[..., None] * self.wl[1] + rng[..., None] * self.wl[2]
        loc = self.Wo(torch.relu(hid))
        return (dense[:, 0] + loc[..., 0]).reshape(B, 2 * NC), (dense[:, 1] + loc[..., 1]).reshape(B, 2 * NC)

    @torch.no_grad()
    def marginal(self, xn, rng, chunk=12):
        """The value prediction averaged over all flops with the scoring weights (w = reach / mass):
        returns (n, 338) averages and (n, 338) average weights."""
        E = self.V(self.flop(self.flopfeat))
        Sx = self.WLs(self.hs)
        Ov, bv = self.O.weight[:2 * NC], self.O.bias[:2 * NC]
        F = len(E)
        outs, wbars = [], []
        for i in range(0, len(xn), chunk):
            x, r = xn[i:i + chunk].float(), rng[i:i + chunk]
            B = len(x)
            z = torch.relu(self.W(torch.relu(self.U(self.trunk(x))[:, None] + E[None])))
            val = (z @ Ov.T + bv).view(B, F, 2, NC)
            pos = self.pos(r[:, None], self.avail[None], self.order[None], self.rank[None])
            hid = self.Wc(self.C(z).view(B, F, 2, 16))[:, :, :, None, :] + self.cls_bias
            hid += Sx[None, :, None]
            hid.addcmul_(pos.flip(2)[..., None], self.wl[0])
            hid.addcmul_(pos[..., None], self.wl[1])
            hid.addcmul_(r[:, None, :, :, None].expand(B, F, 2, NC, 1), self.wl[2])
            val += torch.relu_(hid) @ self.Wo.weight[0] + self.Wo.bias[0]
            del hid
            M = (r @ self.avail.T).permute(0, 2, 1).clamp_min(1e-6)            # (B, F, 2) range mass per flop
            q = (self.mult[None, :, None, None] * self.avail[None, :, None, :]) / M[..., None]
            qs = q.sum(1)
            outs.append(((q * val).sum(1) / qs.clamp_min(1e-12)).reshape(B, 2 * NC))
            wbars.append((NC * r * qs / self.mult.sum()).reshape(B, 2 * NC))
        return torch.cat(outs), torch.cat(wbars)


def teacher_targets(cfg, data, generator):
    """Trains the teacher and returns, for the training rows: its flop average (n, 338), its prediction
    on each row's own flop (n, 338) and the flop-averaged weights (n, 338)."""
    flop, eq, cache_dir = load_side(data)
    tag = "-".join(str(cfg[k]) for k in ("t_steps", "t_lr", "t_wd", "t_eq"))
    stem = f"{data.snapshot}-s{cfg['seed']}-{tag}"
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
    tr, va = np.nonzero(split == harness.SPLITS["train"])[0], np.nonzero(split == harness.SPLITS["val"])[0]
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
    split = np.load(os.path.join(data.dir, "split.npy"))
    tr = np.nonzero(split == harness.SPLITS["train"])[0]
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
        z = teacher_targets(cfg, data, generator)
        T, own, wbar = z["T"], z["own"], z["wbar"]
        if cfg.get("n_syn"):
            xs, Ts, ws = z["xs"], z["Ts"], z["ws"]
        if cfg.get("t_ens"):
            # average the real leaves' targets over several teachers (seeds); each is trained or read from the cache
            zs = [teacher_targets(dict(cfg, seed=s, n_syn=0, val_cv=False), data, generator) for s in cfg["t_ens"]]
            T = torch.stack([q["T"].float() for q in zs]).mean(0).half()
            own = torch.stack([q["own"].float() for q in zs]).mean(0).half()
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
                if xs is not None:
                    wj = ws[j].float()
                    loss = loss + cfg.get("syn_weight", 1.0) * (wj * (ps - Ts[j].float()) ** 2).sum() / wj.sum().clamp_min(1e-9)
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step()
            step += 1
            if step % cfg["eval_every"] == 0:
                va = val_loss(model)
                if va < best * (1 - cfg.get("min_rel_gain", 1e-4)):
                    best, stale, best_state = va, 0, copy.deepcopy(model.state_dict())
                else:
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
