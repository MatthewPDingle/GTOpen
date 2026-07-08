#!/usr/bin/env python3
"""M5 Phase C: fit the calibrated realization table from Phase B data.

Weighted least squares (reach x pot weights) predicting r_obs from
position, SPR bucket, and 169-class features. Output:
cache/realization_fit.json — evaluated by the engine as a dot product,
clipped; spr enters by bucket with a position interaction so the
position premium can widen with depth.

Usage: python3 m5_spots/fit_phase_c.py [obs.jsonl] [out.json]
"""

import json
import os
import sys
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OBS = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "m5_out/realization_obs.jsonl")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "cache/realization_fit.json")

SPR_EDGES = [2.5, 5.0, 8.0, 13.0, 22.0]  # 6 buckets
RANKS = "23456789TJQKA"

def spr_bucket(spr):
    for i, e in enumerate(SPR_EDGES):
        if spr < e:
            return i
    return len(SPR_EDGES)

def class_feats(label):
    """pair, suited, gap (clipped 0-5), hi, lo as 0-1 ranks."""
    hi = RANKS.index(label[0]) / 12.0
    lo = RANKS.index(label[1]) / 12.0
    pair = 1.0 if len(label) == 2 else 0.0
    suited = 1.0 if label.endswith("s") else 0.0
    gap = 0.0 if pair else min(RANKS.index(label[0]) - RANKS.index(label[1]), 5) / 5.0
    return pair, suited, gap, hi, lo

NB = len(SPR_EDGES) + 1

def class_of(label):
    """169-class index in the engine's lattice convention."""
    hi, lo = RANKS.index(label[0]), RANKS.index(label[1])
    if len(label) == 2:
        return hi * 13 + lo
    return hi * 13 + lo if label[2] == "s" else lo * 13 + hi

def features(pos_frac, spr, label, eq, range_eq, init):
    """v2: PER-CLASS offsets instead of linear rank features. With ~500
    observations per class, each class's realization is measured directly —
    linear hi/lo/gap features extrapolated brutally outside their training
    contexts (v1 folded every offsuit ace preflop while defending 100% of
    suited junk). Remaining shared features are all terminal-evaluable."""
    b = spr_bucket(spr)
    x = np.zeros(1 + 2 * NB + 4 + 169)
    x[0] = pos_frac
    x[1 + b] = 1.0                 # spr bucket level (absorbs the intercept)
    x[1 + NB + b] = pos_frac       # position premium per spr bucket
    o = 1 + 2 * NB
    x[o + 0] = eq - 0.5            # own-class equity at this terminal
    x[o + 1] = (eq - 0.5) ** 2
    x[o + 2] = range_eq - 0.5      # range advantage (nut share ≠ position)
    x[o + 3] = init                # +0.5 has initiative, -0.5 faces it, 0 limped
    x[o + 4 + class_of(label)] = 1.0
    return x

def spot_initiative(name):
    """Postflop initiative holder from the line name: 0=OOP, 1=IP, None=limped."""
    if "limp" in name:
        return None
    if "bb_call" in name:
        return 1          # opener is IP vs the BB defender
    if "utg_open_btn_call" in name:
        return 0          # UTG opened and is OOP vs BTN
    if "utg_open_btn_3bet" in name:
        return 1          # BTN 3-bet, UTG called; BTN is IP
    if "sb_3bet" in name:
        return 0          # SB 3-bet, BTN called; SB is OOP
    raise RuntimeError(f"unknown line shape: {name}")

def load():
    import glob
    # fingerprint headers back to spot names: pot + both range prefixes
    fp2name = {}
    for f in glob.glob(os.path.join(os.path.dirname(OBS), "spots", "*.json")):
        spot = json.load(open(f))
        fp = (round(spot["tree"]["starting_pot"], 3),
              spot["range_oop"][:40], spot["range_ip"][:40])
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
                    raise RuntimeError(f"header not matched to a spot file: pot {pot}")
            elif r["type"] == "obs":
                # mini_* smoke-test spots use a different bet menu — R is
                # conditional on the menu, so they don't belong in this fit
                if cur.startswith("mini"):
                    dropped += 1
                    continue
                rows.append((r, pot, cur))
    if dropped:
        print(f"dropped {dropped} mini-menu smoke-test rows")
    return rows

def main():
    rows = load()
    print(f"{len(rows)} observations from {len({n for _, _, n in rows})} spots")
    # per (spot, board, player) range equity: reach-weighted mean class eq
    from collections import defaultdict
    acc = defaultdict(lambda: [0.0, 0.0])
    for r, _, n in rows:
        k = (n, r["board"], r["player"])
        acc[k][0] += r["eq"] * r["reach"]
        acc[k][1] += r["reach"]
    reqs = {k: v[0] / v[1] for k, v in acc.items()}
    def init_of(r, name):
        a = spot_initiative(name)
        if a is None:
            return 0.0
        return 0.5 if r["player"] == a else -0.5
    X = np.stack([
        features(r["pos_frac"], r["spr"], r["label"], r["eq"],
                 reqs[(n, r["board"], r["player"])], init_of(r, n))
        for r, _, n in rows
    ])
    y = np.array([min(max(r["r_obs"], 0.0), 3.0) for r, _, _ in rows])  # winsorize
    w = np.array([r["reach"] * p for r, p, _ in rows])
    w /= w.mean()

    # holdout by board (texture generalization, not row memorization)
    boards = np.array([r["board"] for r, _, _ in rows])
    uniq = sorted(set(boards))
    test_boards = set(uniq[::5])  # every 5th canonical board
    test = np.array([b in test_boards for b in boards])
    train = ~test

    def wls(X, y, w):
        Xw = X * w[:, None]
        beta, *_ = np.linalg.lstsq(Xw.T @ X, Xw.T @ y, rcond=None)
        return beta

    beta = wls(X[train], y[train], w[train])
    def r2(mask):
        pred = X[mask] @ beta
        resid = y[mask] - pred
        wm = w[mask]
        tss = np.sum(wm * (y[mask] - np.average(y[mask], weights=wm)) ** 2)
        return 1 - np.sum(wm * resid**2) / tss
    print(f"weighted R²: train {r2(train):.3f} · holdout {r2(test):.3f}")

    # refit on everything for the shipped table
    beta = wls(X, y, w)
    names = (["pos"]
             + [f"spr{i}" for i in range(NB)]
             + [f"pos_spr{i}" for i in range(NB)]
             + ["eq", "eq2", "range_eq", "initiative"])
    nshared = len(names)
    coef = dict(zip(names, [float(b) for b in beta[:nshared]]))
    class_offsets = [float(b) for b in beta[nshared:]]
    assert len(class_offsets) == 169

    # ---- sanity: the monotonicities M5 requires ----
    def R(pos, spr, label, eq=0.5, range_eq=0.5, init=0.0):
        return float(features(pos, spr, label, eq, range_eq, init) @ beta)
    # Data finding (2026-07-08): INITIATIVE, not position per se, drives
    # aggregate realization — raw mean r_obs 1.25 with initiative vs 0.42
    # facing it; controlled, pure position is a small negative residual
    # ("IP over-realizes" is mostly "the aggressor does, and he's usually
    # IP"). Checks assert what the data supports.
    ck = coef
    checks = [
        ("initiative premium", ck["initiative"] > 0.2),
        ("IP aggressor beats OOP defender (spr 8)",
         R(0.5, 8, "T9s", init=0.5) > R(-0.5, 8, "T9s", init=-0.5)),
        ("value hands over-realize convexly", ck["eq2"] > 0),
        ("range advantage over-realizes", ck["range_eq"] > 0),
        ("suited > offsuit (76)", R(0.0, 8, "76s") > R(0.0, 8, "76o")),
        ("connected > gapped junk", R(0.0, 8, "76s") > R(0.0, 8, "72s")),
        ("Q2o under-realizes vs 76s", R(0.0, 8, "76s") > R(0.0, 8, "Q2o")),
        # v1 postmortem gates: offsuit aces must NOT crater to the floor,
        # and suited junk must not out-realize them at realistic equities
        ("A9o keeps a sane R", R(-0.5, 20, "A9o", eq=0.55, init=-0.5) > 0.45),
        ("A9o >= 32s at realistic eqs",
         R(-0.5, 20, "A9o", eq=0.55, init=-0.5) >= R(-0.5, 20, "32s", eq=0.34, init=-0.5)),
    ]
    # debug: decomposition for the postmortem classes
    o = 1 + 2 * NB
    print(f"  shared: pos {beta[0]:+.3f} eq {coef['eq']:+.3f} eq2 {coef['eq2']:+.3f} "
          f"range_eq {coef['range_eq']:+.3f} init {coef['initiative']:+.3f}")
    print(f"  spr levels: {[round(float(beta[1+i]),3) for i in range(NB)]}")
    for lab in ("A9o", "32s", "T9s", "AA"):
        k = class_of(lab)
        print(f"  offset[{lab}] = {class_offsets[k]:+.3f}")
    ok = True
    for name, passed in checks:
        print(f"  {'PASS' if passed else 'FAIL'}  {name}")
        ok &= passed
    if not ok:
        print("SANITY FAILURES — not writing the table")
        sys.exit(1)

    # examples for the report: defender vs aggressor at spr 8
    for label in ("AA", "76s", "76o", "Q2o", "22"):
        print(f"  R({label}) @spr8  OOP-defender {R(-0.5, 8, label, init=-0.5):.2f}"
              f" · IP-aggressor {R(0.5, 8, label, init=0.5):.2f}")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump({
            "version": 2,
            "spr_edges": SPR_EDGES,
            "coef": coef,
            "class_offsets": class_offsets,
            "clip": [0.2, 2.5],
            "meta": {
                "n_obs": len(rows),
                "train_r2": round(r2(train), 4),
                "holdout_r2": round(r2(test), 4),
                "data": "phase_b_2026-07-08",
                "note": "r_obs = EV/(pot*EQ) at solved flop roots; HU only; "
                        "features: pos_frac, spr bucket (+pos interaction), "
                        "pair/suited/gap/hi/lo, own-class eq (centered, +sq), "
                        "range mean eq (centered), initiative (+-0.5/0) - "
                        "all terminal-evaluable. FINDING: initiative, not "
                        "position, drives aggregate realization",
            },
        }, f, indent=1)
    print(f"wrote {OUT}")

if __name__ == "__main__":
    main()
