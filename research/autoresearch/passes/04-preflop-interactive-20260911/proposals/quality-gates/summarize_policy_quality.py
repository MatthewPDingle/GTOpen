"""Read-only summary of frozen CPU/GPU policy-quality JSON or prefixed logs.

Usage: python summarize_policy_quality.py QUALITY.log [QUALITY.log ...]
No solving, native-file writes, threshold tuning or overall-quality certification.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path


def quality_object(text):
    decoder = json.JSONDecoder()
    for index, char in enumerate(text):
        if char != "{":
            continue
        try:
            item, _ = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict) and "candidate_learning_gap_bb" in item:
            return item
    raise ValueError("No policy-quality object found")


def finite(item, key):
    value = item[key]
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"Missing/nonfinite numeric metric: {key}")
    return value


def summarize(path):
    raw = path.read_bytes()
    value = quality_object(raw.decode("utf-8-sig"))
    metrics = {key: finite(value, key) for key in (
        "reference_learning_gap_bb", "candidate_learning_gap_bb", "excess_learning_gap_bb",
        "unilateral_mean_positive_loss_bb", "unilateral_max_positive_loss_bb")}
    checks = {
        "reference_converged": metrics["reference_learning_gap_bb"] <= 0.005,
        "excess_gap": metrics["excess_learning_gap_bb"] <= 0.02,
        "unilateral_positive_mean": metrics["unilateral_mean_positive_loss_bb"] <= 0.01,
        "unilateral_positive_max": metrics["unilateral_max_positive_loss_bb"] <= 0.03,
    }
    global_pass = all(checks.values())
    recorded_global = value.get("passes_global_policy_gates_with_converged_reference")
    local = []
    for row in value.get("selected_local_action_quality", []):
        result = {key: row.get(key) for key in (
            "path", "position", "status", "forced_or_frozen", "joint_reach_independent_model",
            "weighted_action_loss_bb", "reference_weighted_action_loss_bb",
            "worst_relevant_probability_on_strongly_inferior_actions", "passes_local_tail_gate")}
        if row.get("status") == "evaluated" and not row.get("forced_or_frozen", False):
            relevant = [hand for hand in row.get("hands", [])
                        if finite(hand, "conditional_hand_mass") >= 0.0025]
            if relevant:
                worst = max(finite(hand, "probability_on_actions_losing_over_0_1bb")
                            for hand in relevant)
                result["recomputed_local_pass"] = worst <= 0.1
                result["recomputed_worst_bad_action_probability"] = worst
                result["recorded_flag_matches"] = result["recomputed_local_pass"] == row.get("passes_local_tail_gate")
            else:
                result["recomputed_local_pass"] = None
                result["unverified_reason"] = "No relevant hand rows available"
        else:
            result["recomputed_local_pass"] = None
            result["unverified_reason"] = "Forced/frozen or not evaluated"
        local.append(result)
    applicable = [row for row in local if row["recomputed_local_pass"] is not None]
    return {
        "file": str(path.resolve()), "sha256": hashlib.sha256(raw).hexdigest(),
        "candidate_model": value.get("candidate_model"), "candidate_iteration": value.get("candidate_iteration"),
        "reference_model": value.get("reference_model"), "reference_iteration": value.get("reference_iteration"),
        "metrics": metrics, "global_checks": checks, "global_pass": global_pass,
        "recorded_global_flag_matches": recorded_global == global_pass,
        "local_rows": local,
        "evaluated_local_rows_pass": all(row["recomputed_local_pass"] for row in applicable) if applicable else None,
        "not_evaluated": value.get("not_evaluated", []),
        "scope": "Global policy and explicitly evaluated local rows only; no physical, workflow, speed or full-acceptance claim",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("quality_files", nargs="+", type=Path)
    args = parser.parse_args()
    results = []
    for path in args.quality_files:
        try:
            results.append(summarize(path))
        except (OSError, ValueError, KeyError, TypeError) as error:
            results.append({"file": str(path), "status": "unsupported", "error": str(error)})
    print(json.dumps(results, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
