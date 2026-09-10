"""Render only the frozen final/control pairs; retain all other trials separately."""
import json
from pathlib import Path
import statistics
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
PAIRS = [
    ("8 seats · 1.57M nodes", "baseline-eight-a", "final-eight-a"),
    ("7 seats · 1.00M nodes", "baseline-seven-a", "final-seven-a"),
    ("6 seats · 23K nodes", "baseline-six-a", "final-six-a"),
    ("3 seats · 100 nodes", "baseline-three-a", "final-three-a"),
]


def result(run):
    values = [json.loads(line[6:]) for line in (HERE / "raw" / f"{run}.log").read_text().splitlines()
              if line.startswith("BENCH ")]
    finals = [value for value in values if value.get("phase") == "result"]
    if len(finals) != 1:
        raise ValueError(f"{run}: expected one completed result")
    return finals[0]


rows = []
for label, control_id, final_id in PAIRS:
    control, final = result(control_id), result(final_id)
    for field in ("arena_hash", "iteration", "gaps", "evs"):
        if control[field] != final[field]:
            raise ValueError(f"{final_id}: {field} mismatch")
    row = {"fixture": label, "control": control_id, "candidate": final_id, "exact": True}
    for metric in ("iteration_ms", "check_ms"):
        values = [statistics.median(r["times_ms"][1:] or r["times_ms"]) if metric == "iteration_ms"
                  else r[metric] for r in (control, final)]
        row[metric] = {"original": values[0], "final": values[1],
                       "reduction_percent": 100 * (1 - values[1] / values[0])}
    rows.append(row)
(HERE / "final-performance.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf8")

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), layout="constrained")
for ax, metric, title in zip(axes, ("iteration_ms", "check_ms"), ("Iteration time", "Accuracy-check time")):
    for index, row in enumerate(rows):
        ratio = row[metric]["final"] / row[metric]["original"]
        ax.barh(index, 1, color="#e2e8ed", height=.62)
        ax.barh(index, ratio, color="#398a65", height=.62)
        ax.text(ratio + .02, index, f"{row[metric]['reduction_percent']:.1f}% less", va="center", fontsize=10)
    ax.set(yticks=range(len(rows)), yticklabels=[r["fixture"] for r in rows], xlim=(0, 1.08),
           xticks=[0, .25, .5, .75, 1], xticklabels=["0%", "25%", "50%", "75%", "100%"],
           xlabel="Time relative to the original implementation", title=title)
    ax.invert_yaxis()
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0)
fig.suptitle("Preflop GPU performance · identical fixed work", fontsize=15, fontweight="bold")
fig.supxlabel("RTX 3090 · 16 threads · 23 GB budget · original strategy fingerprints, gaps and EVs match\n"
              "Green: final implementation. Gray: original. Iteration median excludes the first iteration.", fontsize=9)
fig.savefig(HERE / "final-performance.png", dpi=160)
fig.savefig(HERE / "final-performance.svg")
plt.close(fig)
print(json.dumps({"pairs": len(rows), "status": "all exact", "outputs": ["final-performance.json", "final-performance.png", "final-performance.svg"]}))
