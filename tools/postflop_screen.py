#!/usr/bin/env python3
"""Record an explicitly requested initial-screen rejection; no GPU or acceptance.

python tools/postflop_screen.py --baseline B002 --candidate E002 --reject
Only a measured candidate with an identical three-fixture state and a slower
single-run complete-cycle sum is eligible for this narrow rejection helper.
"""
import argparse
import json
from pathlib import Path
import re

import postflop_autoresearch as runner


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--reject", action="store_true", required=True,
                        help="Explicitly record rejection after the initial screen")
    args = parser.parse_args()
    for identity in (args.baseline, args.candidate):
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,95}", identity):
            parser.error("Run IDs must be safe directory names")
    runs = runner.RESEARCH / "runs"
    inputs = [runs / identity / "report.json" for identity in (args.baseline, args.candidate)]
    baseline, candidate = [json.loads(p.read_text(encoding="utf-8-sig")) for p in inputs]
    if baseline["status"] != "measured" or candidate["status"] != "measured":
        raise RuntimeError("Both input runs must have completed measurements")
    fixtures = ("rainbow", "two-tone", "river")
    bm = {r["fixture_id"]: r for r in baseline["results"]}
    cm = {r["fixture_id"]: r for r in candidate["results"]}
    if len(baseline["results"]) != 3 or len(candidate["results"]) != 3 or set(bm) != set(fixtures) or set(cm) != set(fixtures):
        raise RuntimeError("Exactly one measurement of each registered fixture is required")
    rows = []
    checks = ("fingerprint", "state_fingerprint", "exploit_bits", "iteration", "config",
              "storage", "algorithm", "use_isomorphism", "target_pct", "check_every", "max_iterations")
    for fixture in fixtures:
        b, c = bm[fixture], cm[fixture]
        equal = {key: b[key] == c[key] for key in checks}
        if not all(equal.values()) or not b["target_met"] or not c["target_met"]:
            raise RuntimeError(f"Exact state/evaluator screen failed for {fixture}: {equal}")
        rows.append({"fixture_id": fixture, "baseline_full_cycle_ms": b["full_cycle_ms"],
                     "candidate_full_cycle_ms": c["full_cycle_ms"],
                     "observed_change_pct": 100 * (c["full_cycle_ms"] / b["full_cycle_ms"] - 1),
                     "baseline_solve_ms": b["solve_ms"], "candidate_solve_ms": c["solve_ms"],
                     "iteration": b["iteration"], "fingerprint": b["fingerprint"],
                     "exploit_bits": b["exploit_bits"], "equality_checks": equal})
    baseline_ms = sum(r["baseline_full_cycle_ms"] for r in rows)
    candidate_ms = sum(r["candidate_full_cycle_ms"] for r in rows)
    if candidate_ms <= baseline_ms:
        raise RuntimeError("This rejection helper requires a slower complete-cycle sum; review promising candidates separately")
    change = 100 * (candidate_ms / baseline_ms - 1)
    reason = (f"Rejected after the initial screen: serialized complete-cycle sum was {change:.2f}% slower than {args.baseline}, "
              "with no promising aggregate gain. Full arena fingerprints, exploitability bits and stopping iterations match on all three fixtures. "
              "One run per binary does not establish a statistically proven regression; isolated fixture changes may be timing noise. "
              "Broader correctness qualification was not performed.")
    preserved = [runs / f"{args.candidate}.patch", Path(candidate["command"][0]), inputs[1], runs / args.candidate / "stdout.log"]
    if not all(p.is_file() for p in preserved):
        raise RuntimeError("Candidate patch, binary, report and raw log must all be preserved")
    comparison = {"schema_version": 1, "created_at": runner.now(), "baseline_id": args.baseline,
                  "candidate_id": args.candidate, "decision": "rejected", "reason": reason,
                  "screen_repetitions": {"baseline": 1, "candidate": 1},
                  "correctness": {"status": "pass", "scope": "Exact three-fixture complete state fingerprints, exploitability bits and stopping-iteration screen; not full qualification"},
                  "performance": {"scope": "Initial single-run screen", "aggregation": "Serialized sum of three registered complete fixture cycles",
                                  "baseline_full_cycle_ms": baseline_ms, "candidate_full_cycle_ms": candidate_ms,
                                  "observed_change_pct": change, "statistical_regression_proven": False},
                  "fixtures": rows, "input_reports": [{"path": str(p), "sha256": runner.sha256(p)} for p in inputs],
                  "preserved_evidence": [{"path": str(p), "sha256": runner.sha256(p)} for p in preserved]}
    filename = f"comparison-{args.baseline}.json"
    raw_path = runs / args.candidate / filename
    web_path = runner.DASHBOARD / "evidence" / args.candidate / filename
    if raw_path.exists() or web_path.exists():
        raise RuntimeError("Comparison evidence already exists; refusing overwrite")
    with runner.exclusive_lock(runner.STATUS.with_suffix(".lock"), timeout=3):
        dashboard = json.loads(runner.STATUS.read_text(encoding="utf-8-sig"))
        row = next(r for r in dashboard["experiments"] if r["id"] == args.candidate)
        if row["status"] != "measured":
            raise RuntimeError("Candidate dashboard row must be measured before initial-screen decision")
        runner.atomic_json(raw_path, comparison)
        runner.atomic_json(web_path, comparison)
        row.update(status="rejected", correctness="pass", reason=reason, baseline_full_cycle_ms=baseline_ms)
        row.setdefault("evidence", []).append({"label": f"{args.baseline} vs {args.candidate} screen",
            "url": f"evidence/{args.candidate}/{filename}", "detail": "Exact state screen passed; no promising aggregate timing gain in one run per binary."})
        # Preserve every global field, including a newer run's activity/heartbeat.
        runner.atomic_json(runner.STATUS, dashboard)
    print(json.dumps({"candidate": args.candidate, "decision": "rejected", "baseline_full_cycle_ms": baseline_ms,
                      "candidate_full_cycle_ms": candidate_ms, "observed_change_pct": change, "evidence": str(web_path)}))


if __name__ == "__main__":
    main()
