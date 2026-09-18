"""Audit settings, score both checkpoints, and write a bounded comparison."""
import csv
import importlib.util
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
REF = OUT.parent / "wizard-benchmark-20260918"
spec = importlib.util.spec_from_file_location("wizard_score", REF / "score.py")
scorer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scorer)


def read(path):
    return json.loads(path.read_text())


def dump(name, data):
    (OUT / name).write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")


def hand_index(hand):
    ranks = "23456789TJQKA"
    hi, lo = (ranks.index(c) for c in hand[:2])
    return lo * 13 + hi if hand.endswith("o") else hi * 13 + lo


def action_name(action):
    if action["kind"] == "fold":
        return "Fold"
    if action["kind"] == "call":
        return "Call"
    if action["kind"] in ("jam", "raise"):
        return ("Allin " if action["kind"] == "jam" else "Raise ") + f'{action["to"]:g}'
    raise ValueError("Unmapped action")


def audited_context(cfg, reference):
    c = reference["context"]
    assert cfg["positions"] == ["UTG", "UTG1", "MP", "HJ", "CO", "BTN", "SB", "BB"]
    assert cfg["utg_straddle"] and cfg["stack"] == c["stack_bb"]
    assert cfg["posts"][1:] + cfg["posts"][:1] == c["posts_bb"]
    assert cfg["ante"] == c["ante_bb"]
    assert cfg["rake_pct"] == c["rake_pct"] and cfg["rake_cap"] == c["rake_cap_bb"]
    assert all(menu == [c["open_to_bb"]] for menu in cfg["open_raises_by_seat"])
    assert cfg["raise_mults_by_seat"] == [[5], [3], [3], [3], [3], [3], [4], [4.5]]
    assert cfg["fourbet_mults_by_seat"][1] == [2.5]
    assert cfg["add_allin"] and cfg["max_raises"] == 4 and cfg["allin_threshold"] == .4
    # Only the inspected-node contract is matched. TREE-AUDIT.md lists
    # downstream differences; never upgrade this to a full-tree equivalence.
    return c


def candidate(reference, cfg, nodes):
    context = audited_context(cfg, reference)
    result = {"context": context, "cases": []}
    actor_map = {"nl25-utg-open": "UTG1", "nl25-lj-vs-utg": "MP", "nl25-sb-vs-utg": "SB",
                 "nl25-bb-vs-utg": "BB", "nl25-str-vs-utg": "UTG", "nl25-utg-vs-lj-3bet": "UTG1"}
    for case in reference["cases"]:
        node = nodes[case["id"]]
        assert node["actor_pos"] == actor_map[case["id"]]
        names = [action_name(a) for a in node["actions"]]
        expected = {a["action"] for a in case["probes"][0]["combos"][0]["actions"]}
        assert set(names) == expected and len(names) == len(expected)
        assert len(node["strategy"]) == 169 * len(names)
        hands = {p["hand"]: {name: node["strategy"][a * 169 + hand_index(p["hand"])]
                             for a, name in enumerate(names)} for p in case["probes"]}
        result["cases"].append({"id": case["id"], "hands": hands})
    return result


def main():
    reference, cfg = read(REF / "ui-captures.json"), read(OUT / "config.json")
    results, candidates, nodes = {}, {}, {}
    for stage in ("initial", "refined"):
        nodes[stage] = read(OUT / f"{stage}-nodes.json")
        candidates[stage] = candidate(reference, cfg, nodes[stage])
        results[stage] = scorer.score(reference, candidates[stage])
        assert results[stage]["complete_probe_coverage"]
        dump(f"{stage}-candidate.json", candidates[stage])
        dump(f"{stage}-scores.json", results[stage])
    rows = []
    for i, case in enumerate(reference["cases"]):
        key = case["id"]
        node = nodes["refined"][key]
        aggregate = {action_name(a): a["freq"] * 100 for a in node["actions"]}
        for probe in case["probes"]:
            h = probe["hand"]
            p0 = candidates["initial"]["cases"][i]["hands"][h]
            p1 = candidates["refined"]["cases"][i]["hands"][h]
            row = next(r for r in results["refined"]["rows"] if r["case"] == key and r["hand"] == h).copy()
            row.update(candidate=p1, wizard={a["action"]: float(a["percent"].strip("%"))/100
                       for a in probe["combos"][0]["actions"]},
                       wizard_evs={a["action"]: float(a["ev"]) for a in probe["combos"][0]["actions"]},
                       candidate_incoming_weight=node["reach"][hand_index(h)],
                       wizard_incoming_weight=probe["incoming_hand_weight"],
                       candidate_branch_probability=node.get("branch_probability"),
                       refinement_strategy_tv=sum(abs(p1[a] - p0[a]) for a in p1)/2)
            old = next(r for r in results["initial"]["rows"] if r["case"] == key and r["hand"] == h)
            row["refinement_regret_delta_bb"] = row["local_regret_bb"] - old["local_regret_bb"]
            rows.append(row)
        case["candidate_aggregate_percent"] = aggregate
    summary = {"scope": "Six inspected menus matched; downstream tree differences remain.",
               "cases": [{"id": c["id"], "wizard": c["aggregate_percent"],
                          "gtopen": c["candidate_aggregate_percent"]} for c in reference["cases"]],
               "max_refinement_strategy_tv": max(r["refinement_strategy_tv"] for r in rows),
               "max_abs_refinement_regret_delta_bb": max(abs(r["refinement_regret_delta_bb"]) for r in rows),
               "rows": rows}
    dump("comparison.json", summary)
    with (OUT / "comparison.csv").open("w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["case", "hand", "action", "gtopen_percent", "wizard_percent", "wizard_action_ev_bb",
                         "local_regret_bb", "gtopen_incoming_weight", "wizard_incoming_weight"])
        for row in rows:
            for a, p in row["candidate"].items():
                writer.writerow([row["case"], row["hand"], a, p*100, row["wizard"][a]*100, row["wizard_evs"][a],
                                 row["local_regret_bb"], row["candidate_incoming_weight"], row["wizard_incoming_weight"]])
    print(json.dumps({"cases": summary["cases"], "largest_disagreements": sorted(rows, key=lambda r:r["local_regret_bb"], reverse=True)[:10],
                      "max_refinement_tv": summary["max_refinement_strategy_tv"],
                      "max_regret_drift": summary["max_abs_refinement_regret_delta_bb"]}, indent=2))


if __name__ == "__main__":
    main()
