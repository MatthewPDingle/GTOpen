"""Freeze the unchanged D036 full-fold blueprint for E070's metadata ABI."""
from pathlib import Path
import json
from prepare_remaining_controls import ROOT, HERE, sha, seal

prior = ROOT / "runs/D036-fold-shuffle-probe-r3/corpus.json"
source = json.loads(prior.read_text(encoding="utf-8"))
scenarios = source["full_scenarios"]
assert len(scenarios) == 17 and all(len(x["node_meta"]) == 56 for x in scenarios)
cases = []
for index, s in enumerate(scenarios):
    for block in [128, 16, 32, 64, 256]:
        for p in [0, 1]:
            for count in [s["count"], 0] if s["id"] == "n0-own1" else [s["count"]]:
                cases.append({"id": len(cases), "scenario_index": index,
                              "p": p, "threads": block, "count": count})
assert len(cases) == 180
corpus = {"id": "E070-up-fold-unexecuted-blueprint", "case_count": 180,
          "kernel_launches_if_executed": 360, "cases": cases,
          "full_scenarios": scenarios, "source_blueprint_sha256": sha(prior),
          "arity": "All fold nodes have zero actions; u16 metadata = owner<<8.",
          "coverage": "The17 original full-fold input scenarios, all5 declared block sizes, both players, and original zero-count cases.56nodes/scenario include finite and overflow patterns, asymmetric/empty/1326hand dimensions, absent/present same-combo and card removal. All output words, guards and15actual immutable device images required exact in both arms.",
          "limits": "The unrelated old raw_total reduction microkernel is omitted: E070 changes only node metadata. No D036 candidate code or old result reused. No timing evidence."}
seal("up-fold", (HERE / "fold_probe_template.rs").read_text(encoding="utf-8"), corpus, 180,
     "Both21arguments; only i32 player pointer replaced in-place by packed-u16 metadata pointer. All arithmetic, reduction and shared-memory sizes unchanged.")
