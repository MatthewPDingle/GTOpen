#!/usr/bin/env python3
"""M5 Phase C fitter (v3): calibrated realization table from Phase B data.

Two stages, chosen after v1/v2 postmortems (linear class features and even
per-class offsets entangled with shared eq terms extrapolate badly at
preflop decision boundaries):
  1. class_base[169] — reach-weighted mean r_obs per class, shrunk by row
     count (lambda=40) toward the global mean. Direct measurement: class
     orderings can never invert.
  2. context multiplier — ridge (200) WLS on r_obs/class_base with
     pos_frac, SPR bucket, range-equity edge and INITIATIVE, clamped to
     [0.8, 1.25]: a gentle tilt around each class's typical context.
Equity is deliberately NOT a model input: bases embed each class's
realization at its typical equity, and the lab multiplies by equity
directly. The table embeds the postflop RAKE drain (r_obs = net EV over
gross pot): calibrated terminals use the gross pot, no separate deduction.

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
LAMN = 40.0     # class-base shrinkage, in rows
RIDGE = 200.0   # context ridge: mostly trust the bases
M_CLIP = (0.8, 1.25)

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

    gmean = float(np.sum(wr * y) / np.sum(wr))
    base = np.zeros(169)
    for k in range(169):
        m = ks == k
        nk = int(m.sum())
        mk = float(np.sum(wr[m] * y[m]) / np.sum(wr[m])) if nk else gmean
        base[k] = (nk * mk + LAMN * gmean) / (nk + LAMN)

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
    print(f"v3 weighted R²: {r2:.3f}")

    checks = [
        ("initiative premium", beta[3 + NB] > 0.03),
        ("aggressor beats defender", R("T9s", 0.5, 8, init=0.5) > R("T9s", -0.5, 8, init=-0.5)),
        ("suited > offsuit (76)", R("76s", 0, 8) > R("76o", 0, 8)),
        ("connected > gapped junk", R("76s", 0, 8) > R("72s", 0, 8)),
        ("A9o >= 32s in defend context",
         R("A9o", -0.5, 20, init=-0.5) >= R("32s", -0.5, 20, init=-0.5)),
        ("A9o never craters (v1 postmortem)", R("A9o", -0.5, 20, init=-0.5) > 0.40),
        ("AA over-realizes", R("AA", 0, 8) > 1.0),
    ]
    ok = True
    for name, passed in checks:
        print(f"  {'PASS' if passed else 'FAIL'}  {name}")
        ok &= passed
    if not ok:
        print("SANITY FAILURES — not writing the table")
        sys.exit(1)
    for lab in ("AA", "T9s", "KQo", "A9o", "76s", "32s", "72o"):
        print(f"  {lab}: base {base[class_of(lab)]:.2f} · "
              f"def@spr20 {R(lab, -0.5, 20, init=-0.5):.2f} · "
              f"aggr@spr8 {R(lab, 0.5, 8, init=0.5):.2f}")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump({
        "version": 3,
        "spr_edges": SPR_EDGES,
        "class_base": [round(float(v), 5) for v in base],
        "ctx": {n: float(v) for n, v in zip(names, beta)},
        "mult_clip": list(M_CLIP),
        "clip": [0.2, 2.5],
        "meta": {
            "n_obs": len(rows), "r2": round(r2, 4), "data": "phase_b_2026-07-08",
            "note": "R = class_base (reach-weighted, count-shrunk lambda=40) x "
                    "context multiplier (ridge=200, clamp 0.8-1.25: pos, spr "
                    "bucket, range_eq edge, initiative). Equity deliberately "
                    "excluded. Rake drain embedded: gross pot, no deduction.",
        },
    }, open(OUT, "w"), indent=1)
    print(f"wrote {OUT}")

if __name__ == "__main__":
    main()
