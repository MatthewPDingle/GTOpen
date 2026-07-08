#!/usr/bin/env python3
"""M5 Phase C fitter (v4): calibrated realization table from Phase B data.

v3 shipped class_base = each class's in-context mean r_obs. Postmortem
(the "calibrated hates A6s-ATs" ladder): those means encode each class's
ROLE MIX in the 23 training spots. The per-role split shows the real
structure is a class x role INTERACTION — middle suited aces realize
fine with initiative (ATs 1.17) but crater as defenders (0.39, kicker
domination), wheel aces defend far better (A5s 0.77, undominated wheel
outs) — so a hand measured 67% in defender rows (ATs) is not comparable
to one measured 39% there (A5s). A single global role multiplier cannot
repair that, and full role normalization is the causal trap mirrored
(it strips the aggression premium the engine relies on). v4 instead:
  1. DIRECT STANDARDIZATION: each class's base is recomputed at the
     reference role mix (structurally facing = init = (1-limp)/2) from
     its OWN per-role means (cells shrunk toward IPF class-x-role
     priors, lambda=15 rows), blended with the in-context mean by
     ALPHA x role-coverage (4*f*i/(f+i)^2) — a class measured in only
     one role keeps its in-context value, because the counterfactual
     cell would be pure IPF extrapolation (32s "with initiative" at
     0.98 is fiction; it never has initiative anywhere). The table
     stays one number per class — no purchasable role signal.
  2. Equity-anchored shrinkage: low-count and unobserved classes shrink
     toward a ridge curve over hand structure (equity vs random, suited,
     pair, two-card straight windows, high card) instead of the flat
     global mean — unknown classes land on the strength curve.
  3. Domination-chain monotonicity (weighted PAVA): suited broadway-ace
     ladder AKs>=...>=A6s (wheel A5s-A2s deliberately NOT chained to it,
     their premium is real: ~1.3x ATs at reference mix, down from v3's
     role-inflated 1.67x), same offsuit, K/Q broadway kickers, and
     suited >= same-rank offsuit everywhere.
Context multiplier stage unchanged from v3 (analysis-only; the engine
consumes class_base x static positional weight, never the context
features — see the causal-trap note in preflop/mod.rs).

Usage: python3 m5_spots/fit_phase_c.py [obs.jsonl] [out.json]
"""

import glob
import json
import os
import sys
from collections import defaultdict

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OBS = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "m5_out/realization_obs.jsonl")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "cache/realization_fit.json")

SPR_EDGES = [2.5, 5.0, 8.0, 13.0, 22.0]
NB = len(SPR_EDGES) + 1
RANKS = "23456789TJQKA"
LAMN = 40.0      # class-base shrinkage, in rows
RIDGE = 200.0    # context ridge: mostly trust the bases
M_CLIP = (0.8, 1.25)
ALPHAS = [0.85, 0.75, 0.95]  # standardization blend candidates, in preference order
LAMC = 15.0                  # class-x-role cell shrinkage, in rows
CURVE_RIDGE = 5.0
CURVE_CLIP = (0.35, 1.45)

def spr_bucket(s):
    for i, e in enumerate(SPR_EDGES):
        if s < e:
            return i
    return NB - 1

def class_of(label):
    hi, lo = RANKS.index(label[0]), RANKS.index(label[1])
    if len(label) == 2:
        return hi * 13 + lo
    return hi * 13 + lo if label[2] == "s" else lo * 13 + hi

def ci(hi, lo, suited):
    if hi == lo:
        return hi * 13 + hi
    return hi * 13 + lo if suited else lo * 13 + hi

def class_shape(k):
    r, c = divmod(k, 13)
    hi, lo = max(r, c), min(r, c)
    return hi, lo, (r > c), (r == c)   # suited flag, pair flag

def class_combos(k):
    _, _, suited, pair = class_shape(k)
    return 6 if pair else (4 if suited else 12)

def straight_windows(hi, lo):
    """Two-card straight windows containing BOTH ranks (wheel included)."""
    if hi == lo:
        return 0
    wins = [{12, 0, 1, 2, 3}] + [set(range(s, s + 5)) for s in range(9)]
    return sum(1 for w in wins if hi in w and lo in w)

def spot_initiative(name):
    """Postflop initiative holder from the line name: 0=OOP, 1=IP, None=limped."""
    if "limp" in name:
        return None
    if "bb_call" in name:
        return 1
    if "utg_open_btn_call" in name:
        return 0
    if "utg_open_btn_3bet" in name:
        return 1
    if "sb_3bet" in name:
        return 0
    raise RuntimeError(f"unknown line shape: {name}")

def load():
    fp2name = {}
    for f in glob.glob(os.path.join(os.path.dirname(OBS), "spots", "*.json")):
        sp = json.load(open(f))
        fp = (round(sp["tree"]["starting_pot"], 3),
              sp["range_oop"][:40], sp["range_ip"][:40])
        fp2name[fp] = os.path.basename(f)[:-5]
    rows, pot, cur, dropped = [], 1.0, None, 0
    with open(OBS) as f:
        for line in f:
            r = json.loads(line)
            if r["type"] == "header":
                sc = r["spot_config"]
                pot = sc["tree"]["starting_pot"]
                fp = (round(pot, 3), sc["range_oop"][:40], sc["range_ip"][:40])
                cur = fp2name.get(fp)
                if cur is None:
                    raise RuntimeError(f"header not matched: pot {pot}")
            elif r["type"] == "obs":
                if cur.startswith("mini"):
                    dropped += 1  # different bet menu; R is menu-conditional
                    continue
                rows.append((r, pot, cur))
    if dropped:
        print(f"dropped {dropped} mini-menu smoke-test rows")
    return rows

def load_strength():
    """Reach-weighted all-in equity vs a random hand, from the solver cache."""
    raw = open(os.path.join(ROOT, "cache/preflop_eq169.bin"), "rb").read()
    t = np.frombuffer(raw[4:], dtype="<f4").reshape(169, 169).astype(float)
    prob = np.array([class_combos(k) for k in range(169)], float) / 1326.0
    return t @ prob

def pava_desc(v, w):
    """Weighted isotonic regression enforcing v[0] >= v[1] >= ... (PAVA)."""
    vals, wts, idx = [], [], []
    for i in range(len(v)):
        vals.append(v[i]); wts.append(w[i]); idx.append([i])
        while len(vals) > 1 and vals[-2] < vals[-1]:
            v2, w2, i2 = vals.pop(), wts.pop(), idx.pop()
            vals[-1] = (vals[-1] * wts[-1] + v2 * w2) / (wts[-1] + w2)
            wts[-1] += w2
            idx[-1].extend(i2)
    out = np.array(v, float)
    for val, ids in zip(vals, idx):
        for i in ids:
            out[i] = val
    return out

def main():
    rows = load()
    print(f"{len(rows)} observations from {len({n for _, _, n in rows})} spots")
    acc = defaultdict(lambda: [0.0, 0.0])
    for r, _, n in rows:
        k = (n, r["board"], r["player"])
        acc[k][0] += r["eq"] * r["reach"]
        acc[k][1] += r["reach"]
    reqs = {k: v[0] / v[1] for k, v in acc.items()}

    y = np.array([min(max(r["r_obs"], 0.0), 3.0) for r, _, _ in rows])
    wr = np.array([r["reach"] for r, _, _ in rows])
    w = np.array([r["reach"] * p for r, p, _ in rows])
    w /= w.mean()
    ks = np.array([class_of(r["label"]) for r, _, _ in rows])
    # role per row: 0 = facing the aggressor, 1 = has initiative, 2 = limped
    roles = np.array([2 if (a := spot_initiative(n)) is None
                      else (1 if r["player"] == a else 0) for r, _, n in rows])

    gmean = float(np.sum(wr * y) / np.sum(wr))
    nk = np.array([(ks == k).sum() for k in range(169)])
    wsum = np.zeros(169)
    raw = np.full(169, gmean)
    for k in range(169):
        m = ks == k
        if m.any():
            wsum[k] = wr[m].sum()
            raw[k] = float(np.sum(wr[m] * y[m]) / wsum[k])
    observed = nk > 0

    # --- stage 1a: role standardization ---
    # IPF class x role main effects give the PRIOR for thin cells
    eff = raw.copy()
    rho = np.ones(3)
    for _ in range(60):
        for r3 in range(3):
            m = roles == r3
            rho[r3] = np.sum(wr[m] * y[m]) / max(np.sum(wr[m] * eff[ks[m]]), 1e-12)
        rho /= np.sum(wr * rho[roles]) / np.sum(wr)   # mean multiplier = 1
        for k in np.where(observed)[0]:
            m = ks == k
            eff[k] = np.sum(wr[m] * y[m]) / max(np.sum(wr[m] * rho[roles[m]]), 1e-12)
    print(f"role multipliers (facing/init/limped): "
          f"{rho[0]:.3f} / {rho[1]:.3f} / {rho[2]:.3f}")
    # reference role mix: structurally, every non-limped HU flop has exactly
    # one initiative holder and one defender, so facing = init = (1-limp)/2
    # (the raw 47/44 data split is just reach-weighting noise around that)
    limp_share = float(np.sum(wr[roles == 2]) / np.sum(wr))
    pi_ref = np.array([(1 - limp_share) / 2, (1 - limp_share) / 2, limp_share])
    print(f"reference role mix (facing/init/limped): "
          f"{pi_ref[0]:.2f} / {pi_ref[1]:.2f} / {pi_ref[2]:.2f}")
    # per-class per-role cells, shrunk toward the IPF prior eff[k] * rho[r];
    # coverage = how much of the facing/init split the class really spans
    std = raw.copy()
    cov = np.zeros(169)
    for k in np.where(observed)[0]:
        cells = np.zeros(3)
        share = np.zeros(3)
        for r3 in range(3):
            m = (ks == k) & (roles == r3)
            n_cell = int(m.sum())
            share[r3] = float(np.sum(wr[m]))
            prior = eff[k] * rho[r3]
            if n_cell:
                m_cell = float(np.sum(wr[m] * y[m]) / np.sum(wr[m]))
                cells[r3] = (n_cell * m_cell + LAMC * prior) / (n_cell + LAMC)
            else:
                cells[r3] = prior
        std[k] = float(pi_ref @ cells)
        fi = share[0] + share[1]
        cov[k] = 4.0 * share[0] * share[1] / (fi * fi) if fi > 0 else 0.0

    # --- stage 1b: equity-anchored curve (fit per alpha on corrected bases) ---
    strength = load_strength()
    feats = np.zeros((169, 7))
    for k in range(169):
        hi, lo, suited, pair = class_shape(k)
        s = strength[k]
        feats[k] = [1.0, s, s * s, float(suited), float(pair),
                    straight_windows(hi, lo) / 4.0, hi / 12.0]

    def build(alpha):
        a_k = alpha * cov
        base = (1.0 - a_k) * raw + a_k * std
        base *= gmean / (np.sum(wsum * base) / np.sum(wsum))   # keep the scale
        X, bw = feats[observed], nk[observed].astype(float)
        A = (X * bw[:, None]).T @ X + CURVE_RIDGE * np.eye(7)
        A[0, 0] -= CURVE_RIDGE
        beta = np.linalg.solve(A, (X * bw[:, None]).T @ base[observed])
        g = np.clip(feats @ beta, *CURVE_CLIP)
        out = np.where(observed, (nk * base + LAMN * g) / (nk + LAMN), g)
        wgt = nk + LAMN
        lad = lambda labs: [class_of(l) for l in labs]
        chains = [lad(["AKs", "AQs", "AJs", "ATs", "A9s", "A8s", "A7s", "A6s"]),
                  lad(["AKo", "AQo", "AJo", "ATo", "A9o", "A8o", "A7o", "A6o"]),
                  lad(["A5s", "A4s", "A3s", "A2s"]), lad(["A5o", "A4o", "A3o", "A2o"]),
                  lad(["KQs", "KJs", "KTs"]), lad(["KQo", "KJo", "KTo"]),
                  lad(["QJs", "QTs"]), lad(["QJo", "QTo"])]
        for ch in chains:
            out[ch] = pava_desc(out[ch], wgt[ch])
        for hi in range(13):
            for lo in range(hi):
                out[ci(hi, lo, False)] = min(out[ci(hi, lo, False)], out[ci(hi, lo, True)])
        return out

    def base_gates(b):
        return [
            ("wheel premium bounded (A5s <= 1.45 ATs; v3 was 1.67)",
             b[class_of("A5s")] <= 1.45 * b[class_of("ATs")]),
            ("middle aces recovered (ATs >= 0.70, A9s >= 0.60; v3: 0.64/0.52)",
             b[class_of("ATs")] >= 0.70 and b[class_of("A9s")] >= 0.60),
            ("AA base over-realizes", b[class_of("AA")] > 1.0),
            ("scale preserved", abs(np.sum(wsum * b) / np.sum(wsum) - gmean) < 0.02),
        ]

    base, alpha = None, None
    for a in ALPHAS:
        cand = build(a)
        checks = base_gates(cand)
        tag = " ".join("PASS" if p else "FAIL" for _, p in checks)
        print(f"alpha={a}: ATs {cand[class_of('ATs')]:.2f} A5s {cand[class_of('A5s')]:.2f} "
              f"AA {cand[class_of('AA')]:.2f} JTs {cand[class_of('JTs')]:.2f}  [{tag}]")
        if base is None and all(p for _, p in checks):
            base, alpha = cand, a
    if base is None:
        print("no alpha passes the base gates — not writing the table")
        sys.exit(1)
    print(f"selected alpha={alpha}")

    # --- stage 2: context multiplier (unchanged from v3, analysis-only) ---
    def ctx_feats(r, name):
        a = spot_initiative(name)
        init = 0.0 if a is None else (0.5 if r["player"] == a else -0.5)
        x = np.zeros(2 + NB + 2)
        x[0] = 1.0
        x[1] = r["pos_frac"]
        x[2 + spr_bucket(r["spr"])] = 1.0
        x[2 + NB] = reqs[(name, r["board"], r["player"])] - 0.5
        x[3 + NB] = init
        return x

    Xc = np.stack([ctx_feats(r, n) for r, _, n in rows])
    ratio = y / base[ks]
    A = (Xc * w[:, None]).T @ Xc + RIDGE * np.eye(Xc.shape[1])
    A[0, 0] -= RIDGE  # do not shrink the intercept
    beta = np.linalg.solve(A, (Xc * w[:, None]).T @ ratio)
    names = ["c0", "pos"] + [f"spr{i}" for i in range(NB)] + ["range_eq", "initiative"]
    print({n: round(float(v), 4) for n, v in zip(names, beta)})

    def mult(pos, spr, req, init):
        x = np.zeros(len(beta))
        x[0] = 1.0
        x[1] = pos
        x[2 + spr_bucket(spr)] = 1.0
        x[2 + NB] = req - 0.5
        x[3 + NB] = init
        return float(np.clip(x @ beta, *M_CLIP))

    def R(lab, pos, spr, req=0.5, init=0.0):
        return float(np.clip(base[class_of(lab)] * mult(pos, spr, req, init), 0.2, 2.5))

    pred = base[ks] * np.clip(Xc @ beta, *M_CLIP)
    r2 = 1 - float(np.sum(w * (y - pred) ** 2) / np.sum(w * (y - gmean) ** 2))
    print(f"v4 weighted R²: {r2:.3f}")

    checks = [
        ("initiative premium", beta[3 + NB] > 0.03),
        ("aggressor beats defender", R("T9s", 0.5, 8, init=0.5) > R("T9s", -0.5, 8, init=-0.5)),
        ("suited > offsuit (76)", R("76s", 0, 8) > R("76o", 0, 8)),
        ("connected > gapped junk", R("76s", 0, 8) > R("72s", 0, 8)),
        ("A9o >= 32s in defend context",
         R("A9o", -0.5, 20, init=-0.5) >= R("32s", -0.5, 20, init=-0.5)),
        ("A9o never craters (v1 postmortem)", R("A9o", -0.5, 20, init=-0.5) > 0.40),
        ("AA over-realizes", R("AA", 0, 8) > 1.0),
    ] + base_gates(base)
    ok = True
    for name, passed in checks:
        print(f"  {'PASS' if passed else 'FAIL'}  {name}")
        ok &= passed
    if not ok:
        print("SANITY FAILURES — not writing the table")
        sys.exit(1)
    print(f"{'hand':>4} {'v4':>5}  |  suited-ace ladder")
    for lab in ("AKs", "AQs", "AJs", "ATs", "A9s", "A8s", "A7s", "A6s",
                "A5s", "A4s", "A3s", "A2s", "AA", "JJ", "66", "JTs",
                "K8s", "K5s", "ATo", "KJo", "72o"):
        print(f"{lab:>4} {base[class_of(lab)]:>5.2f}")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump({
        "version": 4,
        "spr_edges": SPR_EDGES,
        "class_base": [round(float(v), 5) for v in base],
        "ctx": {n: float(v) for n, v in zip(names, beta)},
        "mult_clip": list(M_CLIP),
        "clip": [0.2, 2.5],
        "meta": {
            "n_obs": len(rows), "r2": round(r2, 4), "data": "phase_b_2026-07-08",
            "alpha": alpha,
            "rho": {"facing": round(float(rho[0]), 4), "init": round(float(rho[1]), 4),
                    "limped": round(float(rho[2]), 4)},
            "pi_ref": [round(float(v), 4) for v in pi_ref],
            "note": "v4 = role-standardized bases: per-class per-role means "
                    "(cells shrunk lambda=15 toward IPF class-x-role priors) "
                    "recombined at the global reference role mix, blended "
                    "alpha with the in-context mean; equity-anchored curve as "
                    "shrinkage target (ridge over strength/suited/pair/straight-"
                    "windows/high-card); weighted-PAVA domination chains "
                    "(broadway aces, K/Q kickers, suited>=offsuit; wheel aces "
                    "unchained). Equity itself still deliberately excluded as a "
                    "model input; rake drain embedded: gross pot, no deduction.",
        },
    }, open(OUT, "w"), indent=1)
    print(f"wrote {OUT}")

if __name__ == "__main__":
    main()
