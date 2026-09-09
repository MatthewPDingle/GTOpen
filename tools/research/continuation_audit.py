"""Render the isolated Rust continuation audit's aggregate outputs.

Run after: cargo run --release -p solver --example continuation_audit
Then: python tools/research/continuation_audit.py
No hand-history files, app sessions, or saved games are read or modified.
"""
from pathlib import Path
import hashlib
import json
import subprocess

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "research/preflop-evolution/continuation"


def main():
    data = json.loads((OUT / "results.json").read_text())
    records = data["records"]
    assert data["complete"], "Wait for the Rust audit to complete."
    assert len(records) == 12, "Publication expects the full two-case, three-board, paired-rake panel."
    assert all(r["target_met"] for r in records), "Reference solve target not met."
    case_names = {"symmetric": "Same ranges", "caller_vs_raiser": "Caller vs raiser ranges"}
    cases = list(case_names)
    boards = ["As7h2d", "Ts9s8d", "7s7h2d"]
    colors = {"reference": "#3283a8", "raw": "#858b92", "static": "#bf873c", "calibrated": "#9859ad"}
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                         "figure.facecolor": "#fafbfc", "axes.facecolor": "#fafbfc"})

    fig, axes = plt.subplots(2, 2, figsize=(13, 7.8), sharex=True, sharey=True)
    for row, case in enumerate(cases):
        for col, rake in enumerate([0, 5]):
            ax = axes[row, col]
            chosen = [next(r for r in records if r["case"] == case and r["board"] == b and r["rake_pct"] == rake) for b in boards]
            # Paired OOP/IP bars emphasize that each board is a separate conditional reference.
            x = np.arange(3)
            for player, offset, alpha in [(0, -.16, 1), (1, .16, .5)]:
                ax.bar(x+offset, [r["reference_ev_bb"][player] for r in chosen], width=.3,
                       color=colors["reference"], alpha=alpha, label=f"Reference {'OOP' if player == 0 else 'IP'}")
            for model in ["raw", "static", "calibrated"]:
                for player, style in [(0, "-"), (1, "--")]:
                    ax.axhline(chosen[0]["preflop_leaf"][model+"_bb"][player], color=colors[model], ls=style,
                               linewidth=1.3, label=f"{model.capitalize()} {'OOP' if player == 0 else 'IP'}")
            ax.set_title(f"{case_names[case]} · {rake}% rake")
            ax.set_xticks(x, boards)
            ax.set_ylabel("Continuation value (bb, pot-share)")
            ax.grid(axis="y", alpha=.15)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=4, bbox_to_anchor=(.5, .025), frameon=False)
    fig.suptitle("Continuation audit · selected flop references and current preflop estimates", fontsize=15)
    fig.text(.5, .91, "20 bb pot · 80 bb behind · fixed ranges · full turn/river enumeration in a restricted betting tree", ha="center")
    fig.text(.5, .005, "Selected flops are diagnostics, not an all-flop expectation. Distance from a horizontal line is not a measured model error.", ha="center", fontsize=9)
    fig.tight_layout(rect=[0, .13, 1, .9])
    fig.savefig(OUT / "values.png", dpi=160)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.7))
    paired = []
    for case in cases:
        for board in boards:
            pair = [next(r for r in records if r["case"] == case and r["board"] == board and r["rake_pct"] == rake) for rake in [0, 5]]
            delta = [pair[1]["reference_ev_bb"][p] - pair[0]["reference_ev_bb"][p] for p in [0, 1]]
            for model in ["raw", "static", "calibrated"]:
                if model == "calibrated":
                    assert pair[0]["preflop_leaf"][model+"_bb"] == pair[1]["preflop_leaf"][model+"_bb"]
            paired.append({"case": case, "board": board, "reference_ev_change_bb": delta,
                           "calibrated_ev_change_bb": [0, 0], "raw_ev_change_bb": [pair[1]["preflop_leaf"]["raw_bb"][p] - pair[0]["preflop_leaf"]["raw_bb"][p] for p in [0, 1]],
                           "reference_rake_bb": pair[1]["reference_expected_rake_bb"]})
    x = np.arange(len(paired))
    for p, offset, alpha in [(0, -.16, 1), (1, .16, .5)]:
        axes[0].bar(x+offset, [r["reference_ev_change_bb"][p] for r in paired], width=.3,
                    color=colors["reference"], alpha=alpha, label=f"Reference {'OOP' if p == 0 else 'IP'}")
    axes[0].axhline(0, color=colors["calibrated"], linewidth=2, label="Calibrated (unchanged)")
    axes[0].set_xticks(x, [r["board"]+("\nSame" if r["case"] == "symmetric" else "\nAsymmetric") for r in paired], fontsize=8)
    axes[0].set_ylabel("EV change (bb): 5% rake − no rake")
    axes[0].set_title("Paired rake response, with ranges held fixed")
    axes[0].legend(fontsize=8, frameon=False)
    for r in records:
        c = r["convergence"]
        axes[1].plot([p["seconds"] for p in c], [p["gap_pct_pot"] for p in c],
                     alpha=.7, lw=1, label=f"{r['case']} {r['board']} {r['rake_pct']:g}%")
    axes[1].axhline(.3, color="#de6f38", linestyle="--", label="Target: 0.3% pot")
    axes[1].text(.98, .315, "Target: 0.3% pot", transform=axes[1].get_yaxis_transform(),
                 ha="right", va="bottom", color="#b34f1b", fontsize=8)
    axes[1].set_yscale("log")
    axes[1].set_xlabel("Solve + convergence-check seconds (4 CPU threads)")
    axes[1].set_ylabel("Reference average best-response gap (% pot)")
    axes[1].set_title("Reference solve convergence · all 12 jobs")
    axes[1].grid(alpha=.15)
    fig.suptitle("Rake sensitivity and numerical convergence", fontsize=14)
    fig.tight_layout()
    fig.savefig(OUT / "rake-and-convergence.png", dpi=160)
    plt.close(fig)

    source_files = ["cache/realization_fit.json", "cache/preflop_eq169.bin", "crates/solver/examples/continuation_audit.rs",
                    "crates/solver/src/preflop/mod.rs", "crates/solver/src/tree.rs", "crates/solver/src/cfr.rs", "crates/solver/src/best_response.rs"]
    summary = {"schema": 1, "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
               "source_sha256": {path: hashlib.sha256((ROOT/path).read_bytes()).hexdigest() for path in source_files},
               "paired_rake_results": paired,
               "no_rake_accounting": [{"case": case, "starting_pot_bb": 20,
                    "total_predicted_value_bb": {model: sum(next(r for r in records if r["case"] == case and r["rake_pct"] == 0)["preflop_leaf"][model+"_bb"]) for model in ["raw", "static", "calibrated"]}}
                    for case in cases],
               "binary_sha256": hashlib.sha256((ROOT/"target/release/examples/continuation_audit.exe").read_bytes()).hexdigest(),
               "total_build_solve_query_seconds": sum(r[k] for r in records for k in ["build_seconds", "solve_seconds", "query_seconds"]),
               "max_arena_mib": max(r["arena_bytes"] for r in records)/2**20,
               "max_tree_mib": max(r["tree_bytes"] for r in records)/2**20,
               "reference_gap_pct_range": [min(r["gap_pct_pot"] for r in records), max(r["gap_pct_pot"] for r in records)],
               "note": "Arena + tree bytes are instrumented allocations, not process peak RSS. Concurrent development may make source SHA newer than the binary; results use the build launched for this audit."}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2)+"\n")
    print(json.dumps({k: summary[k] for k in ["total_build_solve_query_seconds", "max_arena_mib", "max_tree_mib", "reference_gap_pct_range"]}, indent=2))


if __name__ == "__main__":
    main()
