#!/usr/bin/env python3
"""Compare preserved postflop runs without running GPUs or accepting a candidate.

Example: --id E003-warm-comparison --candidate-id E003
  --baseline-runs B004 B005 B006R --candidate-runs E003R2 E003R3 E003R4
  --warm-cache-cohort --excluded-runs B003 E003 B006 --reject

Lists pair by position. Default publication is qualifying/pending; --reject is
restricted to failure of the registered aggregate or repeated fixture-regression gate.
"""
import argparse
import csv
import json
import math
from pathlib import Path
import re
import statistics

import postflop_autoresearch as runner

FIXTURES = ("rainbow", "two-tone", "river")
BOARDS = ("Ks7h2d", "Ks7s2d", "Ks7h2dQhTc")
EVALUATOR_FILES = ("bench_spot.json", "crates/solver/tests/postflop_autoresearch.rs")
EXACT_FIELDS = ("state_fingerprint", "fingerprint", "exploit_bits", "iteration",
                "board", "fixture_index", "config", "storage", "algorithm",
                "use_isomorphism", "nodes", "cpu_arena_bytes", "target_pct",
                "check_every", "max_iterations", "runtime_nvrtc_jit_included",
                "flushed_progress_logging_included")
TIMINGS = ("full_cycle_ms", "build_ms", "init_ms", "solve_ms", "readback_ms")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_run(identity):
    path = runner.RESEARCH / "runs" / identity / "report.json"
    report = json.loads(path.read_text(encoding="utf-8-sig"))
    require(report["id"] == identity, f"Report ID differs: {identity}")
    return report, {"id": identity, "path": str(path), "sha256": runner.sha256(path)}


def source_hashes(manifest):
    hashes = manifest.get("source_sha256", manifest.get("hashes"))
    require(isinstance(hashes, dict) and bool(hashes), "Build manifest lacks source hashes")
    return {key.replace("\\", "/"): value.lower() for key, value in hashes.items()}


def gpu_identity(report):
    telemetry = report["telemetry_before"]["gpu"]
    require(telemetry["returncode"] == 0, "Missing successful pre-run GPU identity")
    rows = list(csv.reader(telemetry["stdout"].splitlines(), skipinitialspace=True))
    require(rows and all(len(row) >= 4 for row in rows), "Incomplete GPU identity")
    return [row[:4] for row in rows]  # name, UUID, driver, capacity; exclude live load.


def validate_run(report, verified_files):
    identity = report["id"]
    require(report["status"] == "measured" and report["returncode"] == 0
            and report["test_pass_count"] == 1, f"Run is not a successful measurement: {identity}")
    require([r["fixture_id"] for r in report["results"]] == list(FIXTURES),
            f"Exactly the three fixtures in fixed order are required: {identity}")
    require(report["command"][1:] == ["postflop_complete_cycle", "--nocapture", "--test-threads=1", "--ignored"],
            f"Different native test invocation: {identity}")
    env = report["environment"]
    require(env["RAYON_NUM_THREADS"] == "16" and env["POSTFLOP_AUTORESEARCH_FIXTURE"] is None
            and env["POSTFLOP_AUTORESEARCH_STORAGE"] == "compressed"
            and env["POSTFLOP_AUTORESEARCH_PROFILE"] == "0", f"Not the registered primary environment: {identity}")
    manifest = report["binary_build_manifest"]
    require(manifest["binary_hash_verified"] is True
            and manifest["data"]["binary_sha256"].lower() == report["binary_sha256"].lower(),
            f"Binary/build manifest association failed: {identity}")
    for path, expected in ((Path(report["command"][0]), report["binary_sha256"]),
                           (Path(manifest["path"]), manifest["sha256"]),
                           (runner.RESEARCH / "runs" / identity / "stdout.log", report["stdout_sha256"])):
        if str(path) not in verified_files:
            verified_files[str(path)] = runner.sha256(path)
        require(verified_files[str(path)] == expected.lower(), f"Preserved artifact changed: {path}")
    hashes = source_hashes(manifest["data"])
    observed = report["provenance"]["benchmark_sha256"]
    for filename in EVALUATOR_FILES:
        require(filename in hashes and hashes[filename] == observed[filename].lower(),
                f"Build/runtime evaluator hash differs: {identity}: {filename}")
    for board, result in zip(BOARDS, report["results"]):
        require(result["board"] == board and result["storage"] == "compressed"
                and result["target_met"] is True and result["target_pct"] == 0.3
                and result["check_every"] == 20 and result["max_iterations"] == 400
                and result["runtime_nvrtc_jit_included"] is True
                and result["flushed_progress_logging_included"] is True,
                f"Fixed evaluator conditions differ: {identity}/{result['fixture_id']}")
        for field in TIMINGS:
            require(isinstance(result[field], (int, float)) and math.isfinite(result[field])
                    and result[field] > 0, f"Invalid timing: {identity}/{field}")
    return hashes


def distribution(values):
    return {"count": len(values), "median_ms": statistics.median(values),
            "min_ms": min(values), "max_ms": max(values),
            "range_ms": max(values) - min(values), "raw_ms": values}


def gain(baseline, candidate):
    return 100 * (baseline - candidate) / baseline


def fixture_regression_guard(rows, pairs):
    """Require median regression plus repeated paired evidence, not one outlier."""
    required = max(2, len(pairs) // 2 + 1)
    fixtures = []
    for row in rows:
        fixture = row["fixture_id"]
        median_regression = -row["observed_gain_pct"]
        regressions = [-pair["fixture_gain_pct"][fixture] for pair in pairs]
        repeats = sum(value > 3.0 for value in regressions)
        failed = median_regression > 3.0 and repeats >= required
        fixtures.append({"fixture_id": fixture, "median_regression_pct": median_regression,
                         "paired_regression_pct": regressions,
                         "repetitions_above_3pct": repeats, "paired_repetitions": len(pairs),
                         "required_repetitions": required, "repeatable_material_regression": failed,
                         "reason": (f"{fixture}: median regression {median_regression:.4f}%; "
                                    f"{repeats}/{len(pairs)} paired repetitions exceed 3% "
                                    f"(requires median >3% and at least {required} repetitions).")})
    affected = [row["fixture_id"] for row in fixtures if row["repeatable_material_regression"]]
    return {"threshold_pct": 3.0,
            "median_basis": "Regression of candidate fixture median versus baseline fixture median",
            "repeat_rule": "Strict majority of paired repetitions, with a minimum of two",
            "fixtures": fixtures, "affected_fixtures": affected, "failed": bool(affected)}


def rejection_reasons(performance):
    reasons = []
    if not performance["aggregate_gate_met"]:
        reasons.append("Below the registered 2% aggregate gate; no reproducible aggregate benefit established.")
    guard = performance["fixture_regression_guard"]
    for fixture in guard["fixtures"]:
        if fixture["repeatable_material_regression"]:
            reasons.append("Repeatable material fixture regression: " + fixture["reason"])
    return reasons


def summarize(baseline, candidate, frozen_hashes):
    require(len(baseline) == len(candidate) and len(baseline) >= 3,
            "At least three equal-sized baseline/candidate cohorts are required")
    verified_files = {}
    cohorts = {}
    all_runs = baseline + candidate
    reference = baseline[0]
    for name, runs in (("baseline", baseline), ("candidate", candidate)):
        hashes = [validate_run(run, verified_files) for run in runs]
        require(all(run["binary_sha256"] == runs[0]["binary_sha256"] for run in runs),
                f"Multiple binaries inside {name} cohort")
        require(all(h == hashes[0] for h in hashes), f"Build-time source changed inside {name} cohort")
        require(all(run["binary_build_manifest"]["sha256"] == runs[0]["binary_build_manifest"]["sha256"] for run in runs),
                f"Build manifests changed inside {name} cohort")
        cohorts[name] = {"run_ids": [r["id"] for r in runs], "count": len(runs),
                         "binary_sha256": runs[0]["binary_sha256"],
                         "build_manifest": runs[0]["binary_build_manifest"], "source_sha256": hashes[0]}
    for run in all_runs:
        require(run["environment"] == reference["environment"], f"Environment differs: {run['id']}")
        require(gpu_identity(run) == gpu_identity(reference), f"GPU/driver differs: {run['id']}")
        hashes = source_hashes(run["binary_build_manifest"]["data"])
        for filename in EVALUATOR_FILES:
            require(hashes[filename] == frozen_hashes[filename], f"Frozen evaluator differs: {run['id']}/{filename}")
        for ref, result in zip(reference["results"], run["results"]):
            for field in EXACT_FIELDS:
                require(result[field] == ref[field], f"Exact screen mismatch: {run['id']}/{result['fixture_id']}/{field}")
    rows = []
    for index, fixture in enumerate(FIXTURES):
        b = {key: distribution([r["results"][index][key] for r in baseline]) for key in TIMINGS}
        c = {key: distribution([r["results"][index][key] for r in candidate]) for key in TIMINGS}
        rows.append({"fixture_id": fixture, "baseline": b, "candidate": c,
                     "observed_gain_pct": gain(b["full_cycle_ms"]["median_ms"], c["full_cycle_ms"]["median_ms"]),
                     "exact_screen": {"status": "pass", "fields": list(EXACT_FIELDS),
                                      "fingerprint": reference["results"][index]["fingerprint"],
                                      "exploit_bits": reference["results"][index]["exploit_bits"],
                                      "iteration": reference["results"][index]["iteration"]}})
    bs = sum(r["baseline"]["full_cycle_ms"]["median_ms"] for r in rows)
    cs = sum(r["candidate"]["full_cycle_ms"]["median_ms"] for r in rows)
    pairs = []
    for b, c in zip(baseline, candidate):
        bt = sum(r["full_cycle_ms"] for r in b["results"])
        ct = sum(r["full_cycle_ms"] for r in c["results"])
        pairs.append({"baseline_id": b["id"], "candidate_id": c["id"],
                      "order": [r["id"] for r in sorted((b, c), key=lambda r: r["started_at"])],
                      "baseline_full_cycle_ms": bt, "candidate_full_cycle_ms": ct,
                      "observed_gain_pct": gain(bt, ct),
                      "fixture_gain_pct": {f: gain(br["full_cycle_ms"], cr["full_cycle_ms"])
                                           for f, br, cr in zip(FIXTURES, b["results"], c["results"])}})
    bsrc, csrc = cohorts["baseline"]["source_sha256"], cohorts["candidate"]["source_sha256"]
    return {"cohorts": cohorts, "environment": reference["environment"], "gpu_identity": gpu_identity(reference),
            "source_changes": [{"path": key, "baseline": bsrc.get(key), "candidate": csrc.get(key)}
                               for key in sorted(set(bsrc) | set(csrc)) if bsrc.get(key) != csrc.get(key)],
            "source_scope": "Recorded build-time source hashes; cross-cohort implementation differences are expected. Current working-tree snapshots do not identify preserved binary sources.",
            "fixtures": rows, "pairs": pairs,
            "chronology": [{"id": r["id"], "started_at": r["started_at"], "finished_at": r["finished_at"]}
                           for r in sorted(all_runs, key=lambda r: r["started_at"])],
            "performance": {"aggregation": "Sum of per-fixture medians of serialized complete fixture cycles",
                            "baseline_full_cycle_ms": bs, "candidate_full_cycle_ms": cs,
                            "observed_gain_pct": gain(bs, cs), "required_gain_pct": 2.0,
                            "aggregate_gate_met": gain(bs, cs) >= 2,
                            "fixture_median_regression_above_3pct": [r["fixture_id"] for r in rows if r["observed_gain_pct"] < -3],
                            "fixture_regression_guard": fixture_regression_guard(rows, pairs),
                            "statistical_significance_established": False},
            "preserved_artifacts": [{"path": path, "sha256": digest} for path, digest in verified_files.items()]}


def publish(args, comparison):
    raw = runner.RESEARCH / "comparisons" / args.id / "report.json"
    public = runner.DASHBOARD / "evidence" / args.id / "report.json"
    require(not raw.exists() and not public.exists(), "Comparison ID already exists; refusing overwrite")
    with runner.exclusive_lock(runner.STATUS.with_suffix(".lock"), timeout=3):
        require(not raw.exists() and not public.exists(), "Comparison ID already exists; refusing overwrite")
        dashboard = json.loads(runner.STATUS.read_text(encoding="utf-8-sig"))
        rows = [r for r in dashboard["experiments"] if r["id"] == args.candidate_id]
        require(len(rows) == 1 and rows[0]["status"] in ("measured", "qualifying"),
                "Candidate must have one measured/qualifying dashboard row")
        row = rows[0]
        runner.atomic_json(raw, comparison)
        runner.atomic_json(public, comparison)
        row.update(status=comparison["decision"], correctness="pending", reason=comparison["reason"],
                   qualification_summary={"id": args.id, "scope": comparison["scope"],
                                          "performance": comparison["performance"],
                                          "exact_compressed_screen": "pass", "broader_validation": "not run"})
        row.setdefault("evidence", []).append({"label": "Repeated complete-cycle comparison",
            "url": f"evidence/{args.id}/report.json", "detail": comparison["reason"]})
        # Keep original cold-run timings and all global/active-run fields intact.
        runner.atomic_json(runner.STATUS, dashboard)
    return raw, public


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", required=True, help="Unique immutable comparison ID")
    parser.add_argument("--candidate-id", required=True, help="Existing candidate dashboard row")
    parser.add_argument("--baseline-runs", nargs="+", required=True)
    parser.add_argument("--candidate-runs", nargs="+", required=True)
    parser.add_argument("--excluded-runs", nargs="*", default=[])
    parser.add_argument("--warm-cache-cohort", action="store_true")
    parser.add_argument("--reject", action="store_true", help="Reject aggregate or repeated fixture-regression gate failure; no acceptance mode")
    parser.add_argument("--dry-run", action="store_true", help="Validate and summarize without writing files/status")
    args = parser.parse_args()
    run_ids = args.baseline_runs + args.candidate_runs + args.excluded_runs
    for identity in [args.id, args.candidate_id] + run_ids:
        require(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,95}", identity), "IDs must be safe directory names")
    require(len(set(run_ids)) == len(run_ids), "Scored and excluded run IDs must be unique and disjoint")
    baseline_pairs = [load_run(r) for r in args.baseline_runs]
    candidate_pairs = [load_run(r) for r in args.candidate_runs]
    frozen_path = runner.RESEARCH / "baseline-manifest.json"
    frozen = json.loads(frozen_path.read_text(encoding="utf-8-sig"))
    comparison = summarize([r for r, _ in baseline_pairs], [r for r, _ in candidate_pairs], source_hashes(frozen))
    original, original_provenance = load_run(args.candidate_id)
    require(original["binary_sha256"] == candidate_pairs[0][0]["binary_sha256"],
            "Candidate dashboard identity uses a different binary from the candidate cohort")
    patch = runner.RESEARCH / "runs" / f"{args.candidate_id}.patch"
    require(patch.is_file(), "Candidate source patch must be preserved")
    comparison["preserved_artifacts"].append({"path": str(patch), "sha256": runner.sha256(patch)})
    comparison["original_candidate_report"] = original_provenance
    excluded = []
    for identity in args.excluded_runs:
        report, provenance = load_run(identity)
        excluded.append({**provenance, "status": report["status"], "started_at": report["started_at"],
                         "results": [{k: r[k] for k in ("fixture_id", *TIMINGS)} for r in report.get("results", [])],
                         "reason": "Outside explicitly selected repeated cohort; retained separately, not erased or rescored"})
    p = comparison["performance"]
    failures = rejection_reasons(p)
    require(not args.reject or failures,
            "Rejection mode only supports failure of the registered aggregate or repeated fixture-regression gate")
    scope = "Repeated warm-cache compressed-storage complete-cycle screen" if args.warm_cache_cohort else "Repeated compressed-storage complete-cycle screen"
    reason = (f"{'Rejected' if args.reject else 'Qualification pending'}: {len(args.baseline_runs)} measurements per binary; "
              f"sum of fixture medians {p['baseline_full_cycle_ms']:.4f} -> {p['candidate_full_cycle_ms']:.4f} ms "
              f"({p['observed_gain_pct']:.4f}% observed gain). "
              + (" ".join(failures) + " " if args.reject else "No gain accepted by this helper. ")
              + "Exact complete-state fingerprints, exploitability bits and stopping iterations match on all three compressed fixtures. "
              + ("F32 storage and broader correctness suites were not run because the performance screen failed. " if args.reject else "F32 storage and broader correctness qualification remain pending. ")
              + "Timing spread is reported; no statistical significance or production deployment is claimed.")
    comparison.update(schema_version=1, id=args.id, created_at=runner.now(), candidate_id=args.candidate_id,
                      decision="rejected" if args.reject else "qualifying", accepted=False, deployed=False,
                      scope=scope, reason=reason, correctness={"status": "pending", "exact_compressed_screen": "pass",
                          "broader_validation": "not run", "f32_storage": "not run"},
                      input_reports=[p for _, p in baseline_pairs + candidate_pairs], excluded_runs=excluded,
                      frozen_manifest={"path": str(frozen_path), "sha256": runner.sha256(frozen_path)},
                      measurement_boundaries={"cargo_compilation": "Excluded from every run by the fixed evaluator; no Cargo build cost subtracted selectively",
                          "runtime_nvrtc_jit": "Included in every init_ms/full_cycle_ms, including warm-cache qualification; no runtime compile cost subtracted",
                          "warm_cache_cohort": args.warm_cache_cohort,
                          "cold_start_limit": "Warm-cache cohort does not qualify first-use/cold-start performance; separately retained initial runs disclose potential cache/compiler costs. Cache temperature was not experimentally reset or proved identical." if args.warm_cache_cohort else "Cache temperature was not experimentally controlled; review run order and initialization timings",
                          "other_exclusions": "Correctness fingerprint hashing, HTTP and disk saving; not part of the fixed complete-cycle score"})
    if not args.dry_run:
        raw, public = publish(args, comparison)
        comparison["output_paths"] = [str(raw), str(public)]
    print(json.dumps({k: comparison[k] for k in ("id", "decision", "scope", "reason", "performance")}, indent=2))


if __name__ == "__main__":
    main()
