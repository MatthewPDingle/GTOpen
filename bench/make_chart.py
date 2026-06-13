#!/usr/bin/env python3
"""Render the FREEPIO optimization benchmark chart from bench/*.log files."""
import json
import os
import re
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))

# FREEPIO UI palette
BG = "#23262b"
PANEL = "#2a2e34"
FG = "#d7dade"
GRID = "#3a3f46"
GREEN = "#2fc26e"
BLUE = "#4a78c8"
RED = "#e8484c"
ORANGE = "#f28c26"
CYAN = "#8edced"


def parse_log(name):
    path = os.path.join(HERE, name + ".log")
    iters, pct, secs, gpu_secs = [], [], [], []
    arena_mb = None
    rss_mb = None
    with open(path) as f:
        for line in f:
            m = re.match(
                r"iter\s+(\d+)\s+exploitability\s+([\d.]+) chips \(([\d.]+)% pot\)\s+\[([\d.]+)s(?:, gpu ([\d.]+)s)?\]",
                line,
            )
            if m:
                iters.append(int(m.group(1)))
                pct.append(float(m.group(3)))
                secs.append(float(m.group(4)))
                if m.group(5):
                    gpu_secs.append(float(m.group(5)))
            m = re.search(r"arenas ([\d.]+) MB", line)
            if m:
                arena_mb = float(m.group(1))
            m = re.search(r"peak_rss (\d+) MB", line)
            if m:
                rss_mb = float(m.group(1))
    tpath = os.path.join(HERE, name + ".time")
    if rss_mb is None and os.path.exists(tpath):
        with open(tpath) as f:
            for line in f:
                m = re.search(r"Maximum resident set size \(kbytes\): (\d+)", line)
                if m:
                    rss_mb = int(m.group(1)) / 1024.0
    return dict(iters=iters, pct=pct, secs=secs, gpu_secs=gpu_secs, arena_mb=arena_mb, rss_mb=rss_mb)


runs = {
    "baseline": parse_log("baseline_f32_dcfr"),
    "f32": parse_log("new_f32_dcfr"),
    "i16": parse_log("new_i16_dcfr"),
    "pcfr": parse_log("new_i16_pcfr"),
    "gpu": parse_log("gpu_f32_dcfr"),
}

for k, r in runs.items():
    r["s_per_iter"] = r["secs"][-1] / r["iters"][-1]
# GPU steady state: kernel time between first and last check (skips PTX JIT warmup)
g = runs["gpu"]["gpu_secs"]
gi = runs["gpu"]["iters"]
runs["gpu"]["s_per_iter"] = (g[-1] - g[0]) / (gi[-1] - gi[0])

with open(os.path.join(HERE, "results.json"), "w") as f:
    json.dump(runs, f, indent=2)

plt.rcParams.update(
    {
        "figure.facecolor": BG,
        "axes.facecolor": PANEL,
        "axes.edgecolor": GRID,
        "axes.labelcolor": FG,
        "text.color": FG,
        "xtick.color": FG,
        "ytick.color": FG,
        "grid.color": GRID,
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.titleweight": "bold",
    }
)

fig = plt.figure(figsize=(14, 9.4))
gs = fig.add_gridspec(
    2, 2, left=0.06, right=0.97, top=0.86, bottom=0.07, hspace=0.42, wspace=0.22
)

fig.suptitle(
    "FREEPIO solver optimizations — bench_spot.json (Ks7h2d, 100bb SRP, 1.25M nodes, 257v319 combos, 16 threads)",
    fontsize=13,
    fontweight="bold",
    y=0.975,
)
fig.text(
    0.06,
    0.895,
    "(1) i16/u16 compressed arenas, per-node scaling     "
    "(2) pooled scratch buffers — zero per-visit allocations     "
    "(3) PCFR+ optional     (4) CUDA level-sweep CFR on RTX 3090",
    fontsize=10,
    color=ORANGE,
)

# --- Panel 1: time per iteration -------------------------------------------
ax = fig.add_subplot(gs[0, 0])
labels = ["baseline\n(f32, mallocs)", "new f32\n(scratch pool)", "new i16\n(compressed)", "GPU 3090\n(f32, steady)"]
vals = [runs["baseline"]["s_per_iter"], runs["f32"]["s_per_iter"], runs["i16"]["s_per_iter"], runs["gpu"]["s_per_iter"]]
colors = [GRID, BLUE, GREEN, ORANGE]
bars = ax.bar(labels, vals, color=colors, width=0.62)
for b, v in zip(bars, vals):
    delta = (v / vals[0] - 1) * 100
    note = f"{v:.3f}s" + (f"\n{delta:+.1f}%" if b != bars[0] else "")
    ax.annotate(
        note,
        (b.get_x() + b.get_width() / 2, v),
        ha="center",
        va="bottom",
        fontsize=10,
        fontweight="bold",
    )
ax.set_ylim(0, max(vals) * 1.3)
ax.set_ylabel("seconds / iteration (incl. BR checks)")
ax.set_title("Iteration speed — 100 DCFR iterations (GPU bar = kernel time)")
ax.grid(axis="y", alpha=0.5)

# --- Panel 2: memory ---------------------------------------------------------
ax = fig.add_subplot(gs[0, 1])
groups = ["solver arenas", "process peak RSS"]
f32_vals = [runs["f32"]["arena_mb"], runs["f32"]["rss_mb"]]
i16_vals = [runs["i16"]["arena_mb"], runs["i16"]["rss_mb"]]
x = range(len(groups))
w = 0.36
b1 = ax.bar([i - w / 2 for i in x], f32_vals, w, color=BLUE, label="f32 arenas")
b2 = ax.bar([i + w / 2 for i in x], i16_vals, w, color=GREEN, label="i16 compressed")
for bars_ in (b1, b2):
    for b in bars_:
        ax.annotate(
            f"{b.get_height():.0f}",
            (b.get_x() + b.get_width() / 2, b.get_height()),
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
        )
for i in x:
    saving = (1 - i16_vals[i] / f32_vals[i]) * 100
    ax.annotate(
        f"−{saving:.0f}%",
        (i + w / 2, i16_vals[i] / 2),
        ha="center",
        color="#ffffff",
        fontsize=11,
        fontweight="bold",
    )
ax.set_xticks(list(x))
ax.set_xticklabels(groups)
ax.set_ylabel("MB")
ax.set_title("Memory — same tree, both storage modes")
ax.legend(facecolor=PANEL, edgecolor=GRID, labelcolor=FG)
ax.grid(axis="y", alpha=0.5)

# --- Panel 3: convergence vs iterations -------------------------------------
ax = fig.add_subplot(gs[1, 0])
ax.plot(
    runs["f32"]["iters"], runs["f32"]["pct"], color=BLUE, lw=2.2, label="DCFR · f32"
)
ax.plot(
    runs["i16"]["iters"],
    runs["i16"]["pct"],
    color=GREEN,
    lw=2.2,
    ls="--",
    label="DCFR · i16 compressed",
)
ax.plot(
    runs["pcfr"]["iters"],
    runs["pcfr"]["pct"],
    color=RED,
    lw=2.2,
    label="PCFR+ · i16 compressed",
)
ax.set_yscale("log")
ax.set_xlabel("iteration")
ax.set_ylabel("exploitability (% of pot, log)")
ax.set_title("Convergence per iteration — i16 curve sits on top of f32 (accuracy preserved)")
ax.legend(facecolor=PANEL, edgecolor=GRID, labelcolor=FG)
ax.grid(True, which="both", alpha=0.4)
final_diff = abs(runs["f32"]["pct"][-1] - runs["i16"]["pct"][-1])
ax.annotate(
    f"f32 vs i16 @100 iters: Δ {final_diff:.3f}% pot (bound: 0.1%)",
    xy=(0.97, 0.93),
    xycoords="axes fraction",
    ha="right",
    fontsize=9,
    color=CYAN,
)

# --- Panel 4: convergence vs wall clock --------------------------------------
ax = fig.add_subplot(gs[1, 1])
ax.plot(
    runs["baseline"]["secs"],
    runs["baseline"]["pct"],
    color=GRID,
    lw=4.0,
    label="baseline (old binary)",
)
ax.plot(runs["f32"]["secs"], runs["f32"]["pct"], color=BLUE, lw=2.2, label="DCFR · f32")
ax.plot(
    runs["i16"]["secs"],
    runs["i16"]["pct"],
    color=GREEN,
    lw=2.2,
    ls="--",
    label="DCFR · i16 compressed",
)
ax.plot(
    runs["pcfr"]["secs"],
    runs["pcfr"]["pct"],
    color=RED,
    lw=2.2,
    label="PCFR+ · i16 compressed",
)
ax.plot(
    runs["gpu"]["secs"],
    runs["gpu"]["pct"],
    color=ORANGE,
    lw=2.6,
    label="GPU 3090 · DCFR f32 (wall, incl. GPU BR checks)",
)
ax.set_yscale("log")
ax.set_xlabel("wall clock (s)")
ax.set_ylabel("exploitability (% of pot, log)")
ax.set_title("Convergence per second of wall clock")
ax.legend(facecolor=PANEL, edgecolor=GRID, labelcolor=FG)
ax.grid(True, which="both", alpha=0.4)

out = os.path.join(HERE, "optimization_report.png")
fig.savefig(out, dpi=130)
print("wrote", out)
print(json.dumps({k: {kk: r[kk] for kk in ("s_per_iter", "arena_mb", "rss_mb")} for k, r in runs.items()}, indent=2))
