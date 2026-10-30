"""Compile and run only the standalone CPU diagnostic in this directory."""
from pathlib import Path
import collections
import datetime
import hashlib
import json
import statistics
import subprocess
import time

HERE = Path(__file__).resolve().parent
manifest = json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))
if (HERE / "report.json").exists():
    raise SystemExit("Refusing to overwrite completed report.json")

commands = []
def run(args, output, errors=None):
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    before = time.perf_counter()
    proc = subprocess.run(args, cwd=HERE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (HERE / output).write_bytes(proc.stdout)
    (HERE / (errors or output + ".stderr")).write_bytes(proc.stderr)
    entry = {"args": args, "cwd": str(HERE), "started_at": started,
             "elapsed_seconds": time.perf_counter() - before, "returncode": proc.returncode,
             "stdout": output, "stderr": errors or output + ".stderr"}
    commands.append(entry)
    (HERE / "commands.json").write_text(json.dumps(commands, indent=2) + "\n", encoding="utf-8")
    return proc

command = ["rustc", "prototype.rs", *manifest["compile_flags"],
           "--emit=link=prototype.exe,asm=prototype.s"]
compiled = run(command, "compile.stdout.log", "compile.stderr.log")
if compiled.returncode:
    raise SystemExit("Compilation failed; inspect compile.stderr.log")
exe = str(HERE / "prototype.exe")
guard = run([exe, "--inject-failure", "--proof-only"], "injected-failure.stdout.log", "injected-failure.stderr.log")
assert guard.returncode != 0 and b'"exact":true' not in guard.stdout and b'"stage":"timing"' not in guard.stdout
measured = run([exe], "stdout.jsonl", "stderr.log")
if measured.returncode:
    raise SystemExit("CPU proof/benchmark failed; inspect stderr.log")
rows = [json.loads(line) for line in measured.stdout.decode().splitlines() if line]
proof = [r for r in rows if r.get("stage") == "proof"]
assert len(proof) == 1 and proof[0]["exact"]
assert rows[-1] == {"stage": "complete", "diagnostic_only": True, "end_to_end_claim": False}
groups = collections.defaultdict(list)
for row in rows:
    if row["stage"] == "timing":
        groups[(row["type"], row["mode"], row["length"])].append(row)
summary = []
for key, group in sorted(groups.items()):
    variants = {v: [r["ns_per_block"] for r in group if r["variant"] == v]
                for v in ["baseline", "sse41"]}
    assert all(len(v) == 9 for v in variants.values())
    med = {k: statistics.median(v) for k, v in variants.items()}
    paired = []
    for pair in range(9):
        sample = {r["variant"]: r["ns_per_block"] for r in group if r["pair"] == pair}
        assert len(sample) == 2
        paired.append(100 * (1 - sample["sse41"] / sample["baseline"]))
    summary.append({"type": key[0], "mode": key[1], "length": key[2], "pairs": 9,
                    "median_ns_per_block": med,
                    "range_ns_per_block": {k: [min(v), max(v)] for k, v in variants.items()},
                    "gain_pct_from_medians": 100 * (1 - med["sse41"] / med["baseline"]),
                    "paired_gain_pct": paired})
assert len(groups) == 56
for name in ["oracle", "corpus", "corpus_constants"]:
    item = manifest[name]
    original = Path(item["source"]).read_bytes()
    assert hashlib.sha256(original).hexdigest() == item["source_sha256"]
    assert original[item["start_byte"]:item["end_byte_exclusive"]] == (HERE / item["output"]).read_bytes()
parent = json.loads((HERE / "d014-report.json").read_text(encoding="utf-8"))
assert proof[0] == parent["proof"], "D014 corpus/output identity changed"
assert any(r.get("stage") == "feature_gate" and r["sse4_1"] for r in rows)
import re
assembly = {}
for path in HERE.glob("*.s"):
    text = path.read_text(encoding="utf-8")
    for symbol in ["d015_baseline_i16", "d015_baseline_u16", "d015_sse41_i16", "d015_sse41_u16"]:
        match = re.search(r"(?ms)^" + symbol + r":.*?^\s*\.seh_endproc", text)
        if match:
            body = match.group(0)
            (HERE / (symbol + ".asm.txt")).write_text(body + "\n", encoding="utf-8")
            assembly[symbol] = {"file":path.name, "lines":len(body.splitlines()),
                                "rintf_call_sites":len(re.findall(r"callq\s+rintf",body)),
                                "roundps":len(re.findall(r"\broundps\b",body)),
                                "roundss":len(re.findall(r"\broundss\b",body))}
assert len(assembly) == 4, assembly
(HERE / "assembly-review.json").write_text(json.dumps(assembly,indent=2)+"\n",encoding="utf-8")
hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in HERE.iterdir()
          if p.is_file() and p.name not in ["report.json"]}
report = {"id": "D015-host-sse41-proof", "status": "diagnostic_pass", "proof": proof[0],
          "injected_failure_guard": {"caught": True, "returncode": guard.returncode,
                                     "timings_emitted": False},
          "timing_groups": summary, "commands": commands, "manifest": manifest, "assembly": assembly,
          "artifact_sha256": hashes, "end_to_end_claim": False,
          "limits": ["Single-thread standalone CPU microbenchmark with reused small input blocks.",
                     "No GPU, solver complete-cycle, Rayon scaling, or production acceptance measurement.",
                     "Default x86_64-pc-windows-msvc target; SSE4.1 only on runtime-guarded candidate functions; no target-cpu=native or fast-math flags.",
                     "Alternate baseline/candidate order each pair; no CPU affinity or power-state control.",
                     "Adversarial finite corpus is evidence, not exhaustive enumeration of all float inputs."]}
(HERE / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"proof": proof[0], "failure_guard": report["injected_failure_guard"],
                  "timing_groups": len(summary), "assembly": assembly,
                  "positive_groups": sum(r["gain_pct_from_medians"] > 0 for r in summary)}, indent=2))
