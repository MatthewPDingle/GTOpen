"""Verify the retained source, frozen workloads and final accuracy evidence."""
from pathlib import Path
import datetime as dt
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
config = json.loads((HERE / "run.json").read_text(encoding="utf-8"))
lab = Path(config["lab"])
results = {r["id"]: r for r in json.loads((HERE / "results.json").read_text(encoding="utf-8"))}
checks = []

def verified(name, condition):
    if not condition:
        raise AssertionError(name)
    checks.append(name)

for name, expected in config["main_source_hashes"].items():
    data = (ROOT / name).read_bytes()
    verified("main source: " + name, hashlib.sha256(data).hexdigest() == expected and data == (lab / name).read_bytes())
for name, expected in config["harness"].items():
    verified("frozen workload: " + name, all(hashlib.sha256((root / name).read_bytes()).hexdigest() == expected for root in [ROOT, lab]))

verified("preflop time-to-target complete original state", results["B013"]["checks"] == results["F001"]["checks"])
verified("CPU and lifecycle original fingerprints", results["B014"]["checks"] == results["F002"]["checks"])
verified("24 complete postflop saved states and evaluation bits", results["B010R"]["checks"] == [c for c in results["F007"]["checks"] if "states" in c])
for run in ["E020", "E020R", "E020R2", "E020R3"]:
    verified("CPU complete state: " + run, results[run]["checks"] == results["B020"]["checks"] == results["B014"]["checks"][:1])
for run in ["E019R", "E019R2"]:
    verified("profile/report/save fingerprints: " + run, results[run]["checks"] == results["B014"]["checks"][1:])
verified("512 raking cases", results["E019"]["checks"] == results["B009"]["checks"])
fingerprints = lambda run: [c["preflop"].split("arena_hash=", 1)[1] for c in results[run]["checks"] if "preflop" in c]
verified("2/6/8-seat original arenas, gaps and EVs", fingerprints("B001") == fingerprints("F006"))
verified("warm loader preserves exploitability and iteration", all(results["B017"]["checks"][0][k] == results["F005"]["checks"][0][k] for k in ["exploitability", "iteration"]))
if "F008" in results:
    values = lambda run: [c["postflop"].split("exploit_chips=", 1)[1] for c in results[run]["checks"] if "postflop" in c]
    verified("postflop repeat evaluation values", values("F007") == values("F008"))
if "F009" in results:
    verified("final preflop target repeat original state", results["F009"]["checks"] == results["B013"]["checks"])

tests = {}
for name, expected in [("cpu", (124, 0, 4)), ("gpu", (40, 0, 0)), ("server", (1, 0, 1))]:
    filename = "raw/final-main-" + name + "-v2.log"
    log = (HERE / filename).read_text(encoding="utf-8")
    counts = [tuple(map(int, match)) for match in re.findall(r"test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored", log)]
    totals = tuple(map(sum, zip(*counts)))
    verified("final main " + name + " regression suite", totals == expected and "test result: FAILED" not in log)
    tests[name] = dict(zip(["passed", "failed", "ignored"], totals), log=filename)

verified("all measured trials have decisions", all(r["status"] != "candidate" for r in results.values()))
summary = {
    "verified_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
    "baseline_commit": config["baseline_commit"],
    "retained_commit": config["final_kept_commit"],
    "recorded_runs": len(results),
    "metrics": len({m for r in results.values() for m in r["metrics"]}),
    "checks": checks,
    "tests": tests,
}
(HERE / "validation.json").write_text(json.dumps(summary, indent=2), encoding="utf-8", newline="\n")
print(f"PASS: {len(checks)} final checks; {len(results)} recorded runs; {summary['metrics']} metric graphs.")
