"""Audit pass-2 retained experiments, final workloads, and actual main suites."""
from pathlib import Path
import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
config = json.loads((HERE / "run.json").read_text(encoding="utf-8"))
from workspace import ensure_workspace
lab = ensure_workspace()
recorded = "--recorded" in sys.argv
source_root = lab if recorded else ROOT
rows = json.loads((HERE / "results.json").read_text(encoding="utf-8"))
results = {r["id"]: r for r in rows}
checks = []
def verified(name, condition):
    if not condition: raise AssertionError(name)
    checks.append(name)
def selected(run, key):
    return [c for c in results[run]["checks"] if key in c]
for name, expected in config["main_source_hashes"].items():
    data = (source_root / name).read_bytes()
    verified("main source: " + name, hashlib.sha256(data).hexdigest() == expected and data == (lab / name).read_bytes())
for name, expected in config["harness"].items():
    verified("frozen workload: " + name, all(hashlib.sha256((root / name).read_bytes()).hexdigest() == expected for root in [ROOT, lab]))
references = {
    "states": selected("B010R", "states"),
    "resume_states": selected("E022R", "resume_states"),
    "menu_states": selected("B025", "menu_states"),
    "variant_states": selected("E024F", "variant_states"),
    "memory_checks": selected("B026", "memory_checks") + selected("B029", "memory_checks"),
    "check_board": selected("B030", "check_board"),
    "check_seats": selected("B031", "check_seats"),
    "arena_hash": selected("B013", "arena_hash"),
}
preflop = [c["preflop"].split("arena_hash=", 1)[1] for c in selected("B022", "preflop") + selected("B033", "preflop")]
postflop = [c["postflop"].split("exploit_chips=", 1)[1] for c in selected("E026A", "postflop")]
def without_seconds(s): return re.sub(r"seconds=[0-9.]+ ?", "", s)
convergence = [without_seconds(c["convergence"]) for c in selected("E026R", "convergence")]
reports = [without_seconds(c["report"]) for c in selected("B028", "report")]
final_ids = config.get("pass_final_runs", [])
verified("final combined research runs registered", bool(final_ids))
for commit in sorted({results[i]["commit"] for i in final_ids}):
    for name, expected in config["main_source_hashes"].items():
        data = subprocess.check_output(["git", "show", commit + ":" + name], cwd=lab)
        verified("final run source " + commit[:8] + ": " + name,
                 hashlib.sha256(data).hexdigest() == expected)
control_files = ["crates/solver/src/gpu/mod.rs", "crates/solver/src/gpu/kernels.cu",
                 "crates/solver/src/gpu/plan.rs", "crates/solver/src/preflop/gpu.rs",
                 "crates/solver/src/preflop/kernels.cu"]
for run in ["B034", "B035"]:
    for name in control_files:
        original = subprocess.check_output(["git", "show", config["pass_baseline_commit"] + ":" + name], cwd=lab)
        measured = subprocess.check_output(["git", "show", results[run]["commit"] + ":" + name], cwd=lab)
        verified(run + " original implementation: " + name, measured == original)
final_types = set()
retained = [r for r in rows if r["status"] == "keep" and r["utc"] >= config["pass_started_utc"]]
for row in retained + [results[i] for i in final_ids if results[i] not in retained]:
    run = row["id"]
    verified(run + " completed successfully", row["returncode"] == 0)
    for i, c in enumerate(row["checks"]):
        for key, reference in references.items():
            if key in c:
                verified(f"{run} exact {key} case {i}", c in reference)
                if run in final_ids: final_types.add(key)
        if "preflop" in c:
            verified(f"{run} exact preflop fingerprint {i}", c["preflop"].split("arena_hash=", 1)[1] in preflop)
            if run in final_ids: final_types.add("preflop")
        if "postflop" in c:
            verified(f"{run} exact postflop evaluation {i}", c["postflop"].split("exploit_chips=", 1)[1] in postflop)
            if run in final_ids: final_types.add("postflop")
        if "convergence" in c:
            verified(f"{run} same target stopping {i}", without_seconds(c["convergence"]) in convergence)
            if run in final_ids: final_types.add("convergence")
        if "report" in c:
            verified(f"{run} same report stopping {i}", without_seconds(c["report"]) in reports)
        if "all_arena_gap_ev_bits_equal" in c:
            verified(f"{run} tight cache fallback {i}", c["all_arena_gap_ev_bits_equal"] is True)
required = {"states", "resume_states", "menu_states", "variant_states", "memory_checks", "check_board", "check_seats", "arena_hash", "preflop", "postflop", "convergence"}
verified("final combined source covers all accuracy families", required <= final_types)
manifest = json.loads((HERE / "gpu-main-manifest.json").read_text(encoding="utf-8"))
verified("main suites used final source", manifest["source"] == config["main_source_hashes"])
verified("main suites completed during this pass", manifest.get("completed_utc", "") >= config["pass_started_utc"])
tests = {}
for name, minimum in [("cpu",124),("gpu",42),("server",1)]:
    suite = manifest["suites"][name]
    log = (HERE / suite["log"]).read_text(encoding="utf-8")
    counts = [tuple(map(int, match)) for match in re.findall(r"test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored", log)]
    totals = tuple(map(sum, zip(*counts))) if counts else (0,0,0)
    verified("main " + name + " regression suite", suite["returncode"] == 0 and totals[0] >= minimum and totals[1] == 0 and "test result: FAILED" not in log)
    tests[name] = dict(zip(["passed", "failed", "ignored"], totals), log=suite["log"])
verified("all trials have decisions", all(r["status"] != "candidate" for r in rows))
patch = (HERE / "patches/gpu-pass-retained.patch").read_bytes()
expected_patch = subprocess.check_output(["git", "diff", "--binary", config["pass_baseline_commit"],
    config["final_kept_commit"], "--", "crates/solver/src", "crates/server/src"], cwd=lab)
verified("retained source patch matches final implementation", patch == expected_patch)
summary = {
    "verified_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
    "pass_baseline_commit": config["pass_baseline_commit"],
    "retained_commit": config["final_kept_commit"],
    "recorded_pass_runs": sum(r["utc"] >= config["pass_started_utc"] for r in rows),
    "retained_pass_runs": len(retained),
    "metrics": len({m for r in rows for m in r["metrics"]}),
    "retained_patch_sha256": hashlib.sha256(patch).hexdigest(),
    "checks": checks, "tests": tests, "final_runs": final_ids,
}
output = ROOT / "target/autoresearch/gpu-validation.json"
output.parent.mkdir(parents=True, exist_ok=True)
summary["scope"] = "recorded evidence" if recorded else "current source and recorded evidence"
output.write_text(json.dumps(summary, indent=2), encoding="utf-8", newline="\n")
print(f"PASS ({summary['scope']}): {len(checks)} accuracy/source checks; {summary['metrics']} metric graphs; main CPU/GPU/server suites passed.")
