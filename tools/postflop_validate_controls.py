#!/usr/bin/env python3
"""Compare preserved state/menu/resume controls; never execute or accept anything.

--id UNIQUE --baseline-runs STATE MENU RESUME --candidate-runs STATE MENU RESUME
Writes immutable raw/public comparison JSON, including failures; exits nonzero
on invalid inputs or mismatches. --dry-run validates without publishing evidence.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import re

import postflop_autoresearch as runner

SUITES = {
    "state": {"test": "postflop_states", "file": "postflop_state_perf.rs", "records": 12,
              "snapshots": 24, "field": "states",
              "harness_sha256": "7d6f51618d0fe5b0fa431351c31cc0775f4a3bd7e816a2e93ecda9bbafa49d47"},
    "menu": {"test": "postflop_action_menus", "file": "postflop_action_menus.rs", "records": 12,
             "snapshots": 24, "field": "menu_states",
             "harness_sha256": "4a518cbc449668a3221737815507e8ffc1f0434f1c387809736ce31b3cad5cc3"},
    "resume": {"test": "postflop_resume_state", "file": "postflop_resume_state.rs", "records": 16,
               "snapshots": 112, "field": "resume_states",
               "harness_sha256": "eb15af135a357f9ceb8e21d3fe8f2a616a0d562ee9468cc6ada6113ca27617a4"},
}
STAGES = ("initial", "first_sync", "materialized", "strategy_resync", "full_resync", "locked_sync", "resumed")
SUMMARY = re.compile(r"^test result: (\w+)\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out; finished in [0-9.]+s$")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def valid_hash(value):
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{16}", value) is not None


def valid_bits(value):
    return type(value) is int and 0 <= value < 2**64


def reject_constant(value):
    raise ValueError(f"Nonfinite JSON constant {value}")


def parse_records(stdout, suite):
    spec = SUITES[suite]
    summaries = [SUMMARY.fullmatch(line) for line in stdout.splitlines() if line.startswith("test result:")]
    require(len(summaries) == 1 and summaries[0] is not None
            and summaries[0].groups() == ("ok", "1", "0", "0", "0", "0"),
            f"{suite}: expected exactly one passing, executed test with no failures/filtering")
    require([line for line in stdout.splitlines() if re.fullmatch(r"running \d+ tests?", line)] == ["running 1 test"],
            f"{suite}: absent or unexpected executed-test count")
    records = []
    for number, line in enumerate(stdout.splitlines(), 1):
        if "METRIC_JSON" not in line:
            continue
        prefix, marker, payload = line.partition("METRIC_JSON ")
        require(bool(marker) and (not prefix.strip() or re.fullmatch(r"test " + re.escape(spec["test"]) + r" \.\.\.\s*", prefix)),
                f"{suite}: malformed metric prefix at line {number}")
        record = json.loads(payload, object_pairs_hook=unique_object, parse_constant=reject_constant)
        require(isinstance(record, dict) and record.get("metrics") == {},
                f"{suite}: metrics must be explicitly empty; no timing fields are silently ignored")
        records.append(record)
    validate_records(records, suite)
    return records


def validate_records(records, suite):
    spec = SUITES[suite]
    require(len(records) == spec["records"], f"{suite}: expected {spec['records']} records, found {len(records)}")
    if suite == "state":
        configs = [{"board": b, "iso": i, "rake": r} for b, i, r in
                   itertools.product(("KsQs2d", "Qs7h2dKh", "AsKsQsJsTs"), (False, True), (0.0, 0.05))]
    elif suite == "menu":
        configs = [{"bets": b, "algorithm": a, "root_actions": len(b.split()) + 1} for b, a in
                   itertools.product(("", "50", "33 75", "25 50 100", "20 40 60 100", "10 20 30 40 50 60 70 80 90 100"), ("Dcfr", "CfrPlus"))]
    else:
        configs = [{"board": b, "storage": s, "iso": i, "warm": w} for b, s, i, w in
                   itertools.product(("KsQs2d", "KsQs2dJd"), ("F32", "Compressed"), (False, True), (False, True))]
    total = 0
    for index, (record, config) in enumerate(zip(records, configs)):
        label = f"{suite} record {index}"
        allowed = set(config) | {"metrics", spec["field"]}
        if suite == "resume":
            allowed |= {"inactive", "queries", "exploit_bits", "resumed_exploit_bits"}
        require(set(record) == allowed, f"{label}: missing/extra fields")
        require(canonical({key: record[key] for key in config}) == canonical(config), f"{label}: changed or reordered fixed configuration")
        require(record["metrics"] == {}, f"{label}: nonempty metrics are not supported")
        states = record[spec["field"]]
        require(isinstance(states, list) and len(states) == (7 if suite == "resume" else 2), f"{label}: snapshot count differs")
        total += len(states)
        if suite != "resume":
            for locked, state in zip((False, True), states):
                require(set(state) == {"locked", "hash", "exploit_bits"} and state["locked"] is locked
                        and valid_hash(state["hash"]) and valid_bits(state["exploit_bits"]), f"{label}: invalid ordered snapshot")
        else:
            require(type(record["inactive"]) is int and record["inactive"] >= 0
                    and isinstance(record["queries"], list) and len(record["queries"]) == 2
                    and all(valid_hash(v) for v in record["queries"])
                    and valid_bits(record["exploit_bits"]) and valid_bits(record["resumed_exploit_bits"]),
                    f"{label}: invalid query/exploitability fields")
            initial = 4 if record["warm"] else 0
            iterations = [initial + n for n in (0, 7, 7, 7, 7, 16, 21)]
            for stage, iteration, state in zip(STAGES, iterations, states):
                require(set(state) == {"stage", "iteration", "raw_hash", "save_hash"}
                        and state["stage"] == stage and type(state["iteration"]) is int and state["iteration"] == iteration
                        and valid_hash(state["raw_hash"]) and valid_hash(state["save_hash"]), f"{label}: invalid resume stage/iteration/hash")
    require(total == spec["snapshots"], f"{suite}: total snapshot count differs")


def read_run(identity, suite):
    directory = runner.RESEARCH / "runs" / identity
    path, log = directory / "report.json", directory / "stdout.log"
    report = json.loads(path.read_text(encoding="utf-8-sig"))
    require(report["id"] == identity and report["status"] == "measured"
            and report["returncode"] == 0 and report["test_pass_count"] == 1,
            f"{identity}: invalid, failed or unexecuted test run")
    require(report["command"][1:] == [SUITES[suite]["test"], "--nocapture", "--test-threads=1", "--ignored"],
            f"{identity}: unexpected test/filter or runner arguments")
    manifest = report["binary_build_manifest"]
    require(manifest["binary_hash_verified"] is True and
            manifest["data"]["binary_sha256"].lower() == report["binary_sha256"].lower(), f"{identity}: unverified binary build source")
    artifacts = []
    for artifact, expected in ((log, report["stdout_sha256"]), (Path(report["command"][0]), report["binary_sha256"]),
                               (Path(manifest["path"]), manifest["sha256"])):
        digest = runner.sha256(artifact)
        require(digest == expected.lower(), f"{identity}: preserved artifact hash changed: {artifact}")
        artifacts.append({"path": str(artifact), "sha256": digest})
    hashes = manifest["data"].get("source_sha256", manifest["data"].get("hashes", {}))
    hashes = {k.replace("\\", "/"): v.lower() for k, v in hashes.items()}
    harness = "crates/solver/tests/" + SUITES[suite]["file"]
    require(hashes.get(harness) == SUITES[suite]["harness_sha256"]
            and report["provenance"]["benchmark_sha256"][harness].lower() == SUITES[suite]["harness_sha256"],
            f"{identity}: control harness changed from registered source")
    records = parse_records(log.read_text(encoding="utf-8-sig"), suite)
    return {"id": identity, "suite": suite, "records": records, "environment": report["environment"],
            "source_sha256": hashes, "binary_sha256": report["binary_sha256"],
            "report": {"path": str(path), "sha256": runner.sha256(path)}, "artifacts": artifacts,
            "started_at": report["started_at"], "finished_at": report["finished_at"]}


def compare(baseline, candidate):
    require([r["suite"] for r in baseline] == list(SUITES) and [r["suite"] for r in candidate] == list(SUITES),
            "Exactly state, menu and resume controls are required in order")
    environment = baseline[0]["environment"]
    cohorts = []
    for name, runs in (("baseline", baseline), ("candidate", candidate)):
        sources = []
        for run in runs:
            require(run["environment"] == environment, f"Environment changed: {run['id']}")
            validate_records(run["records"], run["suite"])
            sources.append({k: v for k, v in run["source_sha256"].items()
                            if k.startswith("crates/solver/src/") or k in ("Cargo.toml", "Cargo.lock", "crates/solver/Cargo.toml")})
        require(bool(sources[0]) and all(s == sources[0] for s in sources), f"{name}: controls built from differing solver sources")
        cohorts.append({"name": name, "source_sha256": sources[0], "run_ids": [r["id"] for r in runs]})
    suites = []
    for b, c in zip(baseline, candidate):
        for index, (br, cr) in enumerate(zip(b["records"], c["records"])):
            require(canonical(br) == canonical(cr), f"Exact control mismatch: {b['suite']} record {index} ({b['id']} vs {c['id']})")
        payload = canonical(b["records"])
        spec = SUITES[b["suite"]]
        suites.append({"suite": b["suite"], "status": "pass", "baseline_id": b["id"], "candidate_id": c["id"],
                       "record_count_each": spec["records"], "snapshot_count_each": spec["snapshots"],
                       "ordered_records_sha256": hashlib.sha256(payload.encode()).hexdigest(),
                       "matched_records": b["records"]})
    bs, cs = cohorts[0]["source_sha256"], cohorts[1]["source_sha256"]
    return {"status": "pass", "suites": suites, "total_snapshots_each": sum(s["snapshots"] for s in SUITES.values()),
            "environment": environment, "cohorts": cohorts,
            "source_changes": [{"path": k, "baseline": bs.get(k), "candidate": cs.get(k)}
                               for k in sorted(set(bs) | set(cs)) if bs.get(k) != cs.get(k)]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", required=True)
    parser.add_argument("--baseline-runs", nargs=3, required=True, metavar=("STATE", "MENU", "RESUME"))
    parser.add_argument("--candidate-runs", nargs=3, required=True, metavar=("STATE", "MENU", "RESUME"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    identities = args.baseline_runs + args.candidate_runs
    for identity in [args.id] + identities:
        require(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,95}", identity), "IDs must be safe directory names")
    require(len(set(identities)) == 6, "Baseline/candidate run IDs must be unique and disjoint")
    raw = runner.RESEARCH / "comparisons" / args.id / "report.json"
    public = runner.DASHBOARD / "evidence" / args.id / "report.json"
    require(not raw.exists() and not public.exists(), "Comparison exists; refusing overwrite")
    output = {"schema_version": 1, "id": args.id, "created_at": runner.now(), "status": "invalid",
              "scope": "Exact ordered saved-state, action-menu and resume controls only; no performance or full validation claim",
              "baseline_runs": args.baseline_runs, "candidate_runs": args.candidate_runs,
              "ignored_fields": [], "metrics_policy": "Every metrics object must be explicitly empty; all other fields compare exactly",
              "qualification": "pending", "accepted": False, "deployed": False, "input_evidence": []}
    try:
        cohorts = []
        for ids in (args.baseline_runs, args.candidate_runs):
            runs = []
            for suite, identity in zip(SUITES, ids):
                run = read_run(identity, suite)
                output["input_evidence"].append({k: v for k, v in run.items() if k not in ("records", "source_sha256", "environment")})
                runs.append(run)
            cohorts.append(runs)
        output.update(compare(*cohorts))
    except (ValueError, KeyError, TypeError, OSError) as exc:
        output["error"] = str(exc)
    if not args.dry_run:
        (runner.RESEARCH / "comparisons").mkdir(parents=True, exist_ok=True)
        with runner.exclusive_lock(runner.RESEARCH / "comparisons" / f"{args.id}.lock", timeout=3):
            require(not raw.exists() and not public.exists(), "Comparison exists; refusing overwrite")
            runner.atomic_json(raw, output)
            runner.atomic_json(public, output)
    print(json.dumps({k: output[k] for k in ("id", "status", "scope", "qualification")}
                     | {"snapshots_each": output.get("total_snapshots_each"), "error": output.get("error"),
                        "raw_report": str(raw), "public_report": str(public)}, indent=2))
    return 0 if output["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
