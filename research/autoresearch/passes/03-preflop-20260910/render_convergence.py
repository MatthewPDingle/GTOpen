"""Render completed extended trajectories, including accuracy-target misses."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
rows = json.loads((HERE / "extended-convergence-comparisons.json").read_text())
if len(rows) != 2 or not all(r.get("exact_trajectory_and_final_state") for r in rows):
    raise SystemExit("Both complete exact trajectory comparisons are required before rendering.")
fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), layout="constrained")
for ax, row in zip(axes, rows):
    for variant, label, color in [("original", "Original", "#697b8b"),
                                  ("candidate", "Optimized", "#398a65")]:
        points = row[variant]["checkpoints"]
        minutes = [(p["iterations_ms_total"] + p["checks_ms_total"] + p["syncs_ms_total"]) / 60000
                   for p in points]
        gaps = [p["learning_gap_bb"] for p in points]
        ax.plot(minutes, gaps, marker="o", markersize=3, color=color, label=label)
    ax.axhline(row["target_gap_bb"], color="#b2643f", ls="--", lw=1,
               label=f"Fixed target: {row['target_gap_bb']:g} bb")
    a, b = row["original"]["result"], row["candidate"]["result"]
    reached = a["converged"] and b["converged"]
    status = f"Both reach target at iteration {a['iteration']}" if reached else f"Both miss target at iteration {a['iteration']}"
    title = "6-seat modeled game" if row["fixture"] == "modeled" else "8-seat all-solver game"
    ax.set(title=title + "\n" + status, xlabel="Solver time (minutes)", ylabel="Learning gap (bb)", yscale="log")
    ax.grid(alpha=.2)
    ax.legend(fontsize=8)
    ax.spines[["top", "right"]].set_visible(False)
fig.suptitle("Preflop accuracy trajectories · unchanged stopping rules", fontsize=14, fontweight="bold")
fig.supxlabel("Identical checkpoint values and final native strategy; time includes iterations, synchronization and accuracy checks.\n"
              "Startup and file save/reload are excluded. A target miss is not a time-to-convergence result.", fontsize=9)
fig.savefig(HERE / "final-convergence.png", dpi=160)
fig.savefig(HERE / "final-convergence.svg")
plt.close(fig)
print("Rendered both completed exact trajectories.")
