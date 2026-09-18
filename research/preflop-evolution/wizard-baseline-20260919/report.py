"""Assemble evidence tables. Interpretation still requires review."""
import analyze
import run

OUT = run.OUT
NAMES = {
    "nl25-utg-open": "UTG unopened", "nl25-lj-vs-utg": "LJ vs UTG",
    "nl25-sb-vs-utg": "SB vs UTG", "nl25-bb-vs-utg": "BB vs UTG",
    "nl25-str-vs-utg": "Straddler vs UTG", "nl25-utg-vs-lj-3bet": "UTG vs LJ 3-bet",
}


def mix(probs, percentages=False):
    return "; ".join(f"{a} {p * (1 if percentages else 100):.2f}%" for a, p in probs.items())


def main():
    data = analyze.read(OUT / "comparison.json")
    initial = analyze.read(OUT / "initial-status.json")
    refined = analyze.read(OUT / "refined-status.json")
    nodes = analyze.read(OUT / "refined-nodes.json")
    enriched = []
    for case in data["cases"]:
        key = case["id"]
        evs = analyze.read(OUT / (key + "-action-evs.json"))
        assert evs["units"] == "original bb relative to folding here"
        names = [analyze.action_name(a) for a in nodes[key]["actions"]]
        for row in (r for r in data["rows"] if r["case"] == key):
            values = next(h for h in evs["hands"] if h["hand"] == row["hand"])
            assert len(values["actions"]) == len(names)
            own = {}
            for name, action in zip(names, values["actions"]):
                assert abs(action["frequency"] - row["candidate"][name]) < 1e-6
                own[name] = action["ev_bb"]
            assert abs(own["Fold"]) < 1e-3
            enriched.append({**row, "gtopen_own_action_evs": own})
    analyze.dump("comparison-with-own-values.json", {**data, "rows": enriched})
    lines = ["# GTOpen / Wizard baseline: evidence tables", "",
             "19 September 2026. Generated evidence; see README.md for reviewed interpretation.", "",
             "Six inspected decision menus match. The downstream trees and continuation models do not;",
             "this is a diagnostic comparison, not an exact solver-equivalence test.", "",
             "## Solve and stability", "",
             "| Checkpoint | Iterations | Internal total BR gap (bb) | Stage minutes |",
             "|---|---:|---:|---:|"]
    for label, s in (("Initial", initial), ("Additional 250", refined)):
        lines.append(f"| {label} | {s['iteration']} | {s['gap_total']:.7f} | {s['wall_seconds']/60:.1f} |")
    lines += ["", f"Initial target reached: **{initial['gap_total'] < .005}**.",
              f"Largest probe strategy change during refinement: **{100*data['max_refinement_strategy_tv']:.3f} percentage points** (total variation).",
              f"Largest change in local Wizard-action regret: **{data['max_abs_refinement_regret_delta_bb']:.5f}bb**.", "",
              "The internal gap measures GTOpen's approximation, not full-game accuracy. Small global",
              "gap does not by itself certify every rare branch. Refinement drift is reported separately.", "",
              "## Whole-range frequencies", "",
              "| Decision | Wizard | GTOpen |", "|---|---|---|"]
    for c in data["cases"]:
        lines.append(f"| {NAMES[c['id']]} | {mix(c['wizard'], True)} | {mix(c['gtopen'], True)} |")
    lines += ["", "UTG's response to the 3-bet is conditional on its own opening range in each solver.",
              "Different incoming ranges can therefore contribute to aggregate differences.", "",
              "## Selected hand diagnostics", "",
              "Local regret = best displayed Wizard action EV minus GTOpen's mixture of those EVs.",
              "It scores one decision followed by Wizard continuation, not GTOpen exploitability.",
              "EV display rounding alone gives roughly +/-0.01bb uncertainty; unknown solution error",
              "and tree differences are additional. These 48 selected probes are not a population average.", "",
              "| Decision | Hand | Local regret (bb) | GTOpen choice | Wizard choice |",
              "|---|---|---:|---|---|"]
    for r in sorted(enriched, key=lambda r: r["local_regret_bb"], reverse=True):
        lines.append(f"| {NAMES[r['case']]} | {r['hand']} | {r['local_regret_bb']:.4f} | {mix(r['candidate'])} | {mix(r['wizard'])} |")
    lines += ["", "## Action values under each solver's own continuation", "",
              "These values use different opponent ranges and future policies. Their difference does",
              "not isolate continuation-model error. Both use original bb relative to folding here.", "",
              "| Decision | Hand | Action | Wizard EV | GTOpen own EV |", "|---|---|---|---:|---:|"]
    for r in enriched:
        if r["case"] in ("nl25-str-vs-utg", "nl25-utg-vs-lj-3bet"):
            for action in r["wizard_evs"]:
                if action == "Call":
                    lines.append(f"| {NAMES[r['case']]} | {r['hand']} | {action} | {r['wizard_evs'][action]:.2f} | {r['gtopen_own_action_evs'][action]:.4f} |")
    lines += ["", "## Extra cold-call branches", "",
              "Wizard excludes these calls after UTG6/LJ18; GTOpen currently permits them.", "",
              "| Actor (GTOpen label) | Call frequency |", "|---|---:|"]
    for node in analyze.read(OUT / "later-menu-audit.json"):
        if node.get("role"):
            continue
        call = next(a for a in node["actions"] if a["kind"] == "call")
        lines.append(f"| {node['actor']} | {100*call['freq']:.3f}% |")
    lines += ["", "See TREE-AUDIT.md for all known differences and the fixed run plan.", "",
              "![Selected decision costs](decision-costs.png)", "", "![Internal convergence](convergence.png)", ""]
    (OUT / "RESULTS.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
