"""Standalone comparison figure; invoked after analyze.py."""
from pathlib import Path
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent


def main():
    data = json.loads((OUT / "comparison.json").read_text())
    titles = ["UTG unopened", "LJ vs UTG", "SB vs UTG", "BB vs UTG", "Straddler vs UTG", "UTG vs LJ 3-bet"]
    fig, axes = plt.subplots(2, 3, figsize=(13, 7), layout="constrained")
    for ax, case, title in zip(axes.flat, data["cases"], titles):
        rows = [r for r in data["rows"] if r["case"] == case["id"]]
        values = [r["local_regret_bb"] for r in rows]
        ax.bar([r["hand"] for r in rows], values,
               color=["#c25645" if v > .05 else "#679385" for v in values])
        ax.axhspan(0, .01, color="#999999", alpha=.18)
        ax.set_title(title)
        ax.set_ylabel("Local action regret (bb)")
        ax.grid(axis="y", alpha=.2)
        ax.set_axisbelow(True)
        ax.tick_params(axis="x", labelsize=9)
    fig.suptitle("Which GTOpen choices are costly against Wizard's continuation?", fontsize=15)
    fig.supxlabel("48 selected probes, not a population average. Shaded 0.01bb band indicates display-rounding scale.\nInspected action menus match; known downstream tree differences remain. This is not exploitability.", fontsize=9)
    fig.savefig(OUT / "decision-costs.png", dpi=170)
    plt.close(fig)
    history = json.loads((OUT / "initial-progress.json").read_text())
    seen, measurements = set(), []
    for s in history:
        it = s.get("accuracy_iteration")
        if it and it not in seen:
            measurements.append(s)
            seen.add(it)
    fig, ax = plt.subplots(figsize=(8, 4), layout="constrained")
    ax.semilogy([s["wall_seconds"]/60 for s in measurements], [s["gap_total"] for s in measurements], "o-", color="#337b68")
    ax.axhline(.005, linestyle="--", color="#aa5544", label="0.005bb target")
    ax.set(xlabel="Elapsed solve time (minutes)", ylabel="Internal total BR gap (bb)", title="Baseline convergence in GTOpen's approximation")
    ax.legend()
    ax.grid(alpha=.2)
    fig.savefig(OUT / "convergence.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
