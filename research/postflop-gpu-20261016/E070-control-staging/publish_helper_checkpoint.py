"""Publish the seven-entry control preparation, without running GPU code."""
from pathlib import Path
from datetime import datetime, timezone
import ast
import hashlib
import json
import shutil
import sys

HERE = Path(__file__).resolve().parent
OUT = HERE/"continuation-raw"
ROOT = Path(r"S:\GTOpen-research\postflop-gpu-20261016")
DASH = HERE.parents[2]/"web/research/postflop-gpu-20261016"
sys.path.insert(0, str(ROOT/"runs/accepted-E051"))
import common_e051 as old


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):
    return json.loads(p.read_text(encoding="utf-8"))


def new_json(p, value):
    with p.open("x", encoding="utf-8") as f:
        json.dump(value, f, indent=2)


prep = read(OUT/"preparation.json")
receipt = read(OUT/"rustc-exit.json")
corpus = read(OUT/"corpus.json")
assert receipt["returncode"] == 0 and receipt["terminal"] and receipt["GPUexecutions"] == receipt["NVRTC_processes"] == 0
assert sha(OUT/"probe.exe") == receipt["binary_sha256"]
assert [x["id"] for x in corpus["cases"]] == list(range(2120))
for n, h in prep["input_sha256"].items():
    assert sha(OUT/n) == h
for p in HERE.glob("*.py"):
    ast.parse(p.read_text(encoding="utf-8"))
mainprep = read(HERE/"compiler-preparation-manifest.json")
for f in mainprep["families"]:
    assert sha(HERE/f["family"]/"probe.exe") == f["binary_sha256"]
assert sum(f["cases"] for f in mainprep["families"]) == 3833
host = read(HERE/"host-integration-r2/manifest.json")
for p, h in host["candidate_source_sha256"].items():
    assert sha(HERE/"host-integration-r2/candidate"/p) == h
baseline = read(ROOT/"runs/accepted-E051/baseline.json")
for p, h in baseline["source_sha256"].items():
    assert sha(Path(r"X:\Dev\GTOpen-gpu-research-20261016")/p) == h
protected = read(ROOT/"runs/accepted-E051/protected-main.json")
for p, h in protected["source_sha256"].items():
    assert sha(Path(protected["root"])/p) == h
for p in protected["absent_research_paths"]:
    assert not (Path(protected["root"])/p).exists()
assert sha(Path(protected["live_path"])) == protected["live_sha256"]
assert not (ROOT/"gpu-run.lock").exists()
at = datetime.now(timezone.utc).isoformat()
checkpoint = {
    "id": "E070-seven-entry-control-preparation", "at": at,
    "status": "pass_host_compilation_and_preparation_only",
    "main_kernel_cases": 3833, "continuation_helper_cases": 2120,
    "combined_declared_cases": 5953, "combined_planned_kernel_launches": 11906,
    "planned_numerical_processes": 5, "CUDA_entries": 7,
    "all_numerical_probe_host_compilation_complete": True,
    "all_GPU_numerical_controls_executed": False,
    "new_GPU_numerical_executions": 0, "new_NVRTC_executions": 0,
    "new_timing_samples": 0, "accepted_gain_changed": False,
    "helper_corpus_sha256": sha(OUT/"corpus.json"),
    "helper_probe_source_sha256": sha(OUT/"probe.rs"),
    "helper_probe_binary_sha256": sha(OUT/"probe.exe"),
    "helper_compiler_receipt_sha256": sha(OUT/"rustc-exit.json"),
    "helper_preparation_sha256": sha(OUT/"preparation.json"),
    "helper_root_decoder_sha256": sha(HERE/"helper_raw_audit.py"),
    "helper_resource_probe_binary_sha256": read(HERE/"continuation-resources/rustc-exit.json")["binary_sha256"],
    "source_sha256": {n: sha(HERE/n) for n in ["helper_raw_probe.rs", "prepare_helper_raw.py", "helper_raw_audit.py", "helper_resource_probe.rs"]},
    "CPU_oracles": corpus["CPU_oracle"],
    "coverage_limits": corpus["limits"],
    "raw_storage": {"conservative_bytes": prep["conservative_full_raw_bytes"]+sum(f["conservative_raw_bytes"] for f in mainprep["families"]),
                    "peak_reservation_bytes": 8*1024**3, "minimum_S_free_before_admission_bytes": 66*1024**3,
                    "current_S_free_observed_bytes": shutil.disk_usage(ROOT).free,
                    "must_recheck_native_admission": True},
    "source_file_custody": {"main": len(protected["source_sha256"]), "research": len(baseline["source_sha256"]),
                            "live_executable_exact": True, "required_absences": len(protected["absent_research_paths"]),
                            "scope": "Source and live file hashes only; not linked Git/protected PTX/native idle-state revalidation."},
    "all_owned_new_compiler_handles_terminal": True,
    "research_or_main_solver_source_activated": False,
    "remaining_before_any_native_kernel_work": ["Finish/seal the helper resource decoder and bounded native admission/execution scripts.",
                                               "Current runtime must actually permit S writes and localhost idle-session checks; no repeat approval notifications.",
                                               "Checksum-archive all frozen inputs/binaries to S, recheck source/Git/live/PTX custody and free-space reserve, and acquire the existing serialized GPU lock.",
                                               "Run the frozen helper resource process once and require its source/ABI/narrow-load/driver resource gates before sealing generated PTX inputs.",
                                               "Run each of the five declared numerical processes once, then replay all complete raw arrays with their frozen root decoders."],
    "remaining_before_speed": "Only after all7entry numerical controls pass: integrate complete host ABI, build/check ordinary/equivalence/continuation/state/save/resume/capacity paths, then registered initial3paired complete solves. Acceptance remains unrounded>=1% with no repeatable fixture slowdown or material tradeoff; no rescue or extra timing samples.",
    "limits": "Host probe compilation/source preparation only. No CUDA numerical result, integrated solver typecheck, no-tradeoff qualification or new performance evidence.",
}
assert checkpoint["raw_storage"]["conservative_bytes"] == 4041845680 < 8*1024**3
new_json(OUT/"checkpoint.json", checkpoint)
evidence = DASH/"evidence/E070-seven-entry-preparation"
evidence.mkdir(exist_ok=False)
for n in ["checkpoint.json", "preparation.json", "rustc-exit.json"]:
    shutil.copyfile(OUT/n, evidence/n)
shutil.copyfile(HERE/"helper_raw_audit.py", evidence/"helper_raw_audit.py")
with old.ar.exclusive_lock(DASH/"status.lock", timeout=3):
    status = read(DASH/"status.json")
    before = status["accepted_complete_run"].copy()
    assert before["candidate_id"] == "E051"
    status.update(updated_at=at, state="waiting", goal_status="active", active_experiment="E070",
                  stage="E070 seven-entry probes compiled; native admission preparation",
                  activity="All7CUDAentry host probes compile:5953fixed cases/11906planned launches. Three helper comparisons add full raw guards and CPU oracles. About3.8GiB raw bound within8GiB reserve. Zero new GPU/NVRTC execution or timing; no approval prompts sent.")
    row = next(x for x in status["experiments"] if x["id"] == "E070")
    row.update(stage="5953case probes compiled; native execution not started",
               correctness="CPU encoding/host source ABI pass; seven-entry GPU numerical untested",
               reason="Four main-kernel raw probes and one three-helper raw probe compile.10host launch-site ABIs audited;65536Rust packing cases pass. Helper driver resource/narrow-load gates and all5953GPUcase pairs are still unexecuted. Frozen core CUDA unchanged; no new speed result.")
    link = {"label": "All seven entries: compiled5953case control preparation", "url": "evidence/E070-seven-entry-preparation/checkpoint.json"}
    row["evidence"].append(link); status["evidence"].append(link)
    assert status["accepted_complete_run"] == before
    old.ar.atomic_json(DASH/"status.json", status)
assert read(DASH/"status.json")["accepted_complete_run"] == before
assert sha(evidence/"checkpoint.json") == sha(OUT/"checkpoint.json")
new_json(OUT/"dashboard-publication.json", {"at": at, "disk_readback_verified": True, "HTTP_verified": False,
         "status_sha256": sha(DASH/"status.json"), "checkpoint_sha256": sha(OUT/"checkpoint.json"),
         "accepted_gain_unchanged": True, "GPUexecutions": 0})
print(json.dumps({"status": checkpoint["status"], "compiled_cases": 5953,
                  "new_GPU_executions": 0, "dashboard_disk_readback": "pass", "HTTP_verified": False,
                  "checkpoint_sha256": sha(OUT/"checkpoint.json")}))
