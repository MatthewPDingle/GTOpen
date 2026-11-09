#!/usr/bin/env python3
"""Score the leaf net on a real preflop solution's heads-up flops.

The go/no-go check scored the net on ranges from the datagen generator. This
check uses the ranges a solved Preflop Lab game actually reaches:

    solve-cli datagen leaves GAME.bin --out datagen_leafcheck --leaves 40 --boards 8
    solve-cli datagen solve datagen_leafcheck        # exact flop solves (GPU; resumes)
    python tools/datagen/leafcheck.py datagen_leafcheck

The first step picks the leaves that carry the most chips (reach x pot) and
draws random flops for each. This script prices every solved flop with the
realization models and the net (solve-cli datagen leafnet) and scores them
against the exact solves the same way gonogo.py does: per-class error
weighted by combo mass, plus the error of each player's whole-range value.
Single-flop noise is in every model's score alike, so the differences are
the signal; the interval resamples whole leaves. Writes DIR/report.md and
DIR/report.json.
"""

import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

try:
    import numpy as np
except ImportError:
    sys.exit("numpy is needed:  python -m pip install numpy")

from gonogo import INPUT_KEYS, MODELS, NC, arrays, bootstrap, per_job_sums, totals  # noqa: E402
from validate import cuda_env, default_cli  # noqa: E402


def price(cli, net, records, chunk=2000):
    """Model values and the net's values for every record: {name: (n, 2, 169)}."""
    out = {m: [] for m in MODELS + ["net"]}
    for i in range(0, len(records), chunk):
        part = records[i:i + chunk]
        text = "\n".join(json.dumps({k: r[k] for k in INPUT_KEYS}) for r in part) + "\n"
        proc = subprocess.run([cli, "datagen", "leafnet", net], input=text, capture_output=True, text=True,
                              cwd=ROOT, env=cuda_env())
        got = [json.loads(l) for l in proc.stdout.splitlines() if l.startswith("{")]
        if proc.returncode != 0 or len(got) != len(part):
            sys.exit(f"solve-cli datagen leafnet failed: {proc.stderr.strip()[-600:]}")
        for g in got:
            for m in MODELS:
                out[m].append(g["models"][m])
            out["net"].append(g["leafnet"])
    return {m: np.asarray(v, dtype=np.float32) for m, v in out.items()}


def leaf_label(leaf):
    return " / ".join(leaf["path"])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dir", help="folder from solve-cli datagen leaves / solve")
    ap.add_argument("--net", default=os.path.join(ROOT, "cache", "leaf_net_v1.bin"))
    ap.add_argument("--solve-cli", default=default_cli())
    ap.add_argument("--bootstrap", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    with open(os.path.join(args.dir, "leaves.json"), encoding="utf-8") as f:
        info = json.load(f)
    records = []
    with open(os.path.join(args.dir, "solved.jsonl"), encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rec = json.loads(line)
                if rec.get("type") == "example":
                    records.append(rec)
    if not records:
        sys.exit("no solved examples yet: run  solve-cli datagen solve " + args.dir)
    jobs = np.array([int(r["job"]) for r in records], dtype=np.int64)
    if len(set(jobs.tolist())) < 2:
        sys.exit("need solved flops from at least 2 leaves")

    vals = price(args.solve_cli, args.net, records)
    rng, meta, y, mask, reach, w = arrays(records)
    sums = {m: per_job_sums(jobs, v, y, w, reach, mask) for m, v in vals.items()}
    scores = {m: totals(s) for m, s in sums.items()}
    ci = bootstrap(sums["balanced"], sums["net"], args.bootstrap, args.seed)
    fixed = float(np.sqrt(max(scores["balanced"][0] - scores["net"][0], 0.0)))
    worse = float(np.sqrt(max(scores["net"][0] - scores["balanced"][0], 0.0)))
    moved_w = (w * (vals["net"] - vals["balanced"]) ** 2).sum() / max(float(w.sum()), 1e-12)
    moved = float(np.sqrt(moved_w))

    by_job = {l["job"]: l for l in info["leaves"]}
    rows = []
    for j in sorted(set(jobs.tolist())):
        b, n = sums["balanced"][j], sums["net"][j]
        leaf = by_job.get(j, {"path": [str(j)], "positions": ["?", "?"], "pot_bb": float("nan"), "chip_share": 0})
        rows.append({
            "job": j, "leaf": leaf_label(leaf), "positions": leaf["positions"], "pot_bb": leaf["pot_bb"],
            "chip_share": leaf.get("chip_share", 0), "boards": int((jobs == j).sum()),
            "class_error": {"balanced": float(b[0] / b[1]), "net": float(n[0] / n[1])},
            "range_error": {"balanced": float(b[2] / max(b[3], 1)), "net": float(n[2] / max(n[3], 1))},
        })
    better = sum(r["class_error"]["net"] < r["class_error"]["balanced"] for r in rows)
    kinds = np.array([r["pot_type"] for r in records])
    by_type = {}
    for t in ["limped", "srp", "3bet", "4bet"]:
        sel = kinds == t
        if not sel.any():
            continue
        tot = {m: totals({j: s for j, s in sums[m].items() if j in set(jobs[sel].tolist())}) for m in ("balanced", "net")}
        by_type[t] = {"leaves": len(set(jobs[sel].tolist())), "flops": int(sel.sum()),
                      "class_error": {m: v[0] for m, v in tot.items()}, "range_error": {m: v[1] for m, v in tot.items()}}
    beats = ci[0][0] > 0 and ci[1][0] > 0
    loses = ci[0][1] < 0 and ci[1][1] < 0
    verdict = ("the net is closer to the exact solves than balanced" if beats else
               "the net is further from the exact solves than balanced" if loses else
               "no clear difference between the net and balanced")

    report = {
        "game": info.get("game"), "realization": info.get("realization"), "iteration": info.get("iteration"),
        "leaves": len(rows), "solved_flops": len(records), "chip_share_covered": sum(r["chip_share"] for r in rows),
        "class_error": {m: s[0] for m, s in scores.items()}, "range_error": {m: s[1] for m, s in scores.items()},
        "balanced_minus_net_ci95": {"class": ci[0], "range": ci[1]},
        "fixed_pct_pot": 100 * fixed, "worse_pct_pot": 100 * worse, "moved_pct_pot": 100 * moved,
        "leaves_where_net_better": better, "verdict": verdict, "by_pot_type": by_type, "per_leaf": rows,
    }
    with open(os.path.join(args.dir, "report.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(report, f, indent=1)

    L = [f"# Leaf net on a real preflop solution: {verdict}", ""]
    covered = sum(r["chip_share"] for r in rows)
    L.append(f"Game `{os.path.basename(str(info.get('game')))}` ({info.get('realization')}, "
             f"{info.get('iteration')} iterations): {len(rows)} heads-up flop leaves covering "
             f"{100 * covered:.0f}% of the chips that reach heads-up flops, "
             f"{len(records)} exact flop solves.")
    L.append("")
    L.append("| model | class error | range error |")
    L.append("|---|---|---|")
    for m in ["net"] + MODELS:
        L.append(f"| {m} | {scores[m][0]:.4f} | {scores[m][1]:.5f} |")
    L.append("")
    L.append(f"Balanced minus net, 95% interval over leaves: class {ci[0][0]:+.4f} to {ci[0][1]:+.4f}, "
             f"range {ci[1][0]:+.5f} to {ci[1][1]:+.5f} (positive = the net is closer).")
    if fixed > 0:
        L.append(f"The net removes about {100 * fixed:.1f}% of the pot (RMS) of balanced's error on these "
                 f"leaves; it moves values by {100 * moved:.1f}% of the pot.")
    else:
        L.append(f"The net adds about {100 * worse:.1f}% of the pot (RMS) of error on these leaves; "
                 f"it moves values by {100 * moved:.1f}% of the pot.")
    L.append(f"The net is closer on {better} of {len(rows)} leaves. One leaf's few flops are noisy, so "
             "read single rows loosely.")
    L.append("")
    L.append("By pot type (class error, then range error):")
    L.append("")
    L.append("| pot type | leaves | flops | class balanced | class net | range balanced | range net |")
    L.append("|---|---|---|---|---|---|---|")
    for t, d in by_type.items():
        L.append(f"| {t} | {d['leaves']} | {d['flops']} | {d['class_error']['balanced']:.4f} | "
                 f"{d['class_error']['net']:.4f} | {d['range_error']['balanced']:.5f} | {d['range_error']['net']:.5f} |")
    L.append("")
    L.append("| leaf | oop / ip | pot | chips | flops | class err balanced | net | range err balanced | net |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for r in sorted(rows, key=lambda r: -r["chip_share"]):
        L.append(f"| {r['leaf']} | {r['positions'][0]} / {r['positions'][1]} | {r['pot_bb']:.1f} | "
                 f"{100 * r['chip_share']:.1f}% | {r['boards']} | {r['class_error']['balanced']:.4f} | "
                 f"{r['class_error']['net']:.4f} | {r['range_error']['balanced']:.5f} | {r['range_error']['net']:.5f} |")
    L.append("")
    with open(os.path.join(args.dir, "report.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L))
    print("\n".join(L[:12]))
    print(f"report written to {os.path.join(args.dir, 'report.md')}")


if __name__ == "__main__":
    main()
