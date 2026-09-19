"""Strict saved-checkpoint qualification for the deferred paging candidate.

This does not execute GPU work or certify the unsaved postflop arrays. The
separate switching test must establish their bitwise equality first.
"""
import hashlib
import json
import math
from pathlib import Path
import sys


CHECKPOINTS = [1, 20, 100, 500, 2000]


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf8")


def read(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate JSON key: {key}")
            result[key] = value
        return result
    result = json.loads(Path(path).read_text(), object_pairs_hook=unique)
    canonical(result)  # Reject NaN and infinities anywhere in the document.
    return result


def compare(baseline, candidate, accounting=True):
    for label, result in [("baseline", baseline), ("candidate", candidate)]:
        canonical(result)
        records = result["records"]
        if [r["iteration"] for r in records] != CHECKPOINTS:
            raise ValueError(f"{label}: require the complete registered checkpoint sequence")
        times = [r["elapsed_seconds"] for r in records]
        if not all(isinstance(t, (int, float)) and not isinstance(t, bool)
                   and math.isfinite(t) and t > 0 for t in times):
            raise ValueError(f"{label}: invalid elapsed time")
        if any(a >= b for a, b in zip(times, times[1:])):
            raise ValueError(f"{label}: elapsed time is not increasing")
        evaluation = records[-1]["evaluation"]
        if not 0 <= evaluation["gap_total"] < .01:
            raise ValueError(f"{label}: final convergence gate failed")
        if min(evaluation["gaps"]) < -1e-6:
            raise ValueError(f"{label}: negative player gap")
        traffic = result["transferred_bytes"]
        if type(traffic) is not int or traffic <= 0:
            raise ValueError(f"{label}: invalid arena traffic counter")

    # Remove only registered observational differences; all future unknown
    # fields and every saved node/hand/action/checkpoint must still agree.
    def scientific_content(result):
        return {key: ([{k: v for k, v in row.items() if k != "elapsed_seconds"}
                       for row in value] if key == "records" else value)
                for key, value in result.items() if key != "transferred_bytes"}

    left = canonical(scientific_content(baseline))
    right = canonical(scientific_content(candidate))
    if left != right:
        raise ValueError("Saved scientific content differs: exact checkpoint parity failed")
    if candidate["transferred_bytes"] * 6 != baseline["transferred_bytes"] * 5:
        raise ValueError("Arena traffic is not exactly five sixths of the baseline")

    audits = None
    if accounting:
        from integrated_coverage_review import audit_result
        audits = {"baseline": audit_result(baseline), "candidate": audit_result(candidate)}
    return {
        "passed": True,
        "checkpoint_iterations": CHECKPOINTS,
        "every_saved_scientific_field_identical": True,
        "scientific_content_sha256": hashlib.sha256(left).hexdigest(),
        "arena_traffic_ratio": candidate["transferred_bytes"] / baseline["transferred_bytes"],
        "baseline_seconds": baseline["records"][-1]["elapsed_seconds"],
        "candidate_seconds": candidate["records"][-1]["elapsed_seconds"],
        "accounting": audits,
        "limitation": "Saved evaluations and preflop policies only. Separate GPU switching "
                      "parity and source/resource qualification remain mandatory. Timing "
                      "alone is not an uncontended performance comparison.",
    }


def main():
    if len(sys.argv) != 4:
        raise SystemExit("BASELINE_JSON CANDIDATE_JSON OUTPUT_JSON")
    baseline, candidate, output = map(Path, sys.argv[1:])
    if output.exists():
        raise FileExistsError(output)
    result = compare(read(baseline), read(candidate))
    result["input_sha256"] = {str(p.resolve()): hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in [baseline, candidate, Path(__file__)]}
    with output.open("x", encoding="utf8") as handle:
        json.dump(result, handle, indent=2, allow_nan=False)
        handle.write("\n")
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
