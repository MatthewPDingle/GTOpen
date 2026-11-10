"""Flop tables, the flop-aware Teacher model and per-example flops: shared by
train.py's teacher recipe and referee.py's low-noise validation targets.

Frozen like harness.py (the referee depends on it): train.py may define its
own variants instead of editing this file.
"""
import gzip
import itertools
import json
import os

import numpy as np
import torch

import harness

NC = 169
RANKS = "23456789TJQKA"

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


def side_cache_dir(data):
    """Where side data and teachers are cached: next to WORK (never inside it)."""
    d = os.path.join(os.path.dirname(os.path.abspath(data.work)), "leafnet-loop2")
    os.makedirs(d, exist_ok=True)
    return d


def load_side(data):
    """Canonical flop id of every snapshot row (-1 for test rows, which are never read) and the solved
    flop equities (n, 2, 169), and the cache folder. Cached next to WORK (never inside it)."""
    cache_dir = side_cache_dir(data)
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
