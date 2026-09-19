"""CPU-only adversarial controls; fabricated candidates are NOT GPU evidence."""
import copy
import hashlib
import json
from pathlib import Path
import sys

import paging_candidate_review as review


def run(baseline_path, output):
    baseline = review.read(baseline_path)
    candidate = copy.deepcopy(baseline)
    assert baseline["transferred_bytes"] % 6 == 0
    candidate["transferred_bytes"] = baseline["transferred_bytes"] // 6 * 5
    for record in candidate["records"]:
        record["elapsed_seconds"] *= .9  # Artificial observation, not a speed result.
    accepted = review.compare(baseline, candidate)
    mutations = {
        "missing_checkpoint": lambda d: d["records"].pop(2),
        "duplicate_checkpoint": lambda d: d["records"].insert(2, copy.deepcopy(d["records"][1])),
        "reordered_checkpoint": lambda d: d["records"].reverse(),
        "early_only": lambda d: d["records"].pop(),
        "intermediate_ev": lambda d: d["records"][1]["evaluation"]["ev"].__setitem__(0, 999),
        "unreported_field": lambda d: d.__setitem__("unexpected", 1),
        "wrong_board_weight": lambda d: d["board_weights"].__setitem__(0, .75),
        "wrong_counter": lambda d: d.__setitem__("transferred_bytes", d["transferred_bytes"] + 1),
        "unchanged_counter": lambda d: d.__setitem__("transferred_bytes", baseline["transferred_bytes"]),
        "nonfinite": lambda d: d["records"][0]["evaluation"]["ev"].__setitem__(0, float("nan")),
        "backwards_time": lambda d: d["records"][-1].__setitem__("elapsed_seconds", .001),
        "unconverged": lambda d: d["records"][-1]["evaluation"].__setitem__("gap_total", .1),
        "single_hand_policy": lambda d: d["records"][-1]["evaluation"]["preflop_policy"][0][0].__setitem__(0, .123456789),
    }
    rejected = {}
    for name, mutate in mutations.items():
        changed = copy.deepcopy(candidate)
        mutate(changed)
        try:
            review.compare(baseline, changed, accounting=False)
        except (ValueError, AssertionError) as error:
            rejected[name] = str(error)
        else:
            raise AssertionError(f"Accepted corrupted fixture: {name}")
    result = {
        "status": "CPU checker controls passed; candidate GPU validation remains pending",
        "synthetic_candidate_only": True,
        "input": str(baseline_path),
        "input_sha256": hashlib.sha256(baseline_path.read_bytes()).hexdigest(),
        "complete_fixture_accounting": accepted["accounting"],
        "rejected_mutations": rejected,
        "negative_controls": len(rejected),
        "timing_or_gpu_claim": False,
    }
    with output.open("x", encoding="utf8") as handle:
        json.dump(result, handle, indent=2, allow_nan=False)
        handle.write("\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("BASELINE_JSON OUTPUT_JSON")
    run(*map(Path, sys.argv[1:]))
