"""Record complete off-tree ABI preparation without native research admission."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil
import sys

HERE = Path(__file__).resolve().parent
HOST = HERE / "host-integration-r2"
ROOT = Path(r"S:\GTOpen-research\postflop-gpu-20261016")
DASH = HERE.parents[2] / "web/research/postflop-gpu-20261016"
sys.path.insert(0, str(ROOT / "runs/accepted-E051"))
import common_e051 as old


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):
    return json.loads(p.read_text(encoding="utf-8"))


def new_json(p, value):
    with p.open("x", encoding="utf-8") as f:
        json.dump(value, f, indent=2)


m = read(HOST/"manifest.json")
a = read(HOST/"abi-source-audit.json")
i = read(HOST/"syntax-and-integer-report.json")
r = read(HERE/"continuation-resources/rustc-exit.json")
assert a["status"] == "pass_source_abi_only" and a["site_count"] == 10 and a["kernel_entries"] == 7
assert i["original_u8_pair_cases"] == 65536 and i["Rust_files_parsed"] == 4 and i["all_owned_handles_terminal"]
assert r["returncode"] == 0 and r["terminal"] and r["GPUexecutions"] == r["NVRTC_processes"] == 0
assert sha(HERE/"continuation-resources/probe.exe") == r["binary_sha256"]
for p, h in m["candidate_source_sha256"].items():
    assert sha(HOST/"candidate"/p) == h
assert m["candidate_source_sha256"]["crates/solver/src/gpu/kernels.cu"] == "ffe6c46aa48fbae149ace1288ea512814da11b840c648e6a260759e427c54ec8"
prior = read(ROOT/"runs/accepted-E051/baseline.json")
for p, h in prior["source_sha256"].items():
    assert sha(Path(r"X:\Dev\GTOpen-gpu-research-20261016")/p) == h
main = read(ROOT/"runs/accepted-E051/protected-main.json")
for p, h in main["source_sha256"].items():
    assert sha(Path(main["root"])/p) == h
for p in main["absent_research_paths"]:
    assert not (Path(main["root"])/p).exists()
assert sha(Path(main["live_path"])) == main["live_sha256"]
assert not (ROOT/"gpu-run.lock").exists()
at = datetime.now(timezone.utc).isoformat()
checkpoint = {
    "id": "E070-complete-host-preparation-checkpoint", "at": at,
    "status": "prepared_off_tree_ABI_syntax_integer_checks_pass",
    "complete_patch_files": 7, "host_launch_sites_audited": 10, "CUDA_entries_requiring_controls": 7,
    "four_original_main_kernel_control_cases": 3833,
    "original_main_kernel_control_executions": 0,
    "additional_helper_entries": ["continuation_project", "continuation_transport", "continuation_storage_copy"],
    "helper_resource_host_probe_compiled": True, "helper_resource_native_executions": 0,
    "Rust_host_pack_byte_pair_cases": 65536, "Rust_candidate_files_syntax_parsed": 4,
    "discovery": m["compatibility_discovery"],
    "scope_correction": "Keep the four-entry core CUDA/resource result frozen. Add the three mandatory continuation compatibility entries and their own resource/numerical prerequisites before integrated activation. This is pre-execution caller coverage, with zero E070 GPU floating-result or timing outcomes.",
    "file_custody": {"main_source_files_exact": len(main["source_sha256"]),
                     "research_source_files_exact": len(prior["source_sha256"]),
                     "required_absences_exact": len(main["absent_research_paths"]),
                     "live_executable_exact": True, "gpu_run_lock_exists": False,
                     "scope": "File/hash checks only; linked research Git identity and protected PTX not rechecked by this workspace-only stage."},
    "preparation_errors_preserved": ["host-preparation-newline-error.json", "host-abi-parser-error.json"],
    "reports": {"host_manifest_sha256": sha(HOST/"manifest.json"), "source_ABI_audit_sha256": sha(HOST/"abi-source-audit.json"),
                "syntax_integer_report_sha256": sha(HOST/"syntax-and-integer-report.json"),
                "patch_sha256": sha(HOST/"candidate.patch"),
                "helper_resource_preparation_sha256": sha(HERE/"continuation-resources/preparation.json"),
                "helper_resource_rustc_receipt_sha256": sha(HERE/"continuation-resources/rustc-exit.json")},
    "next_permitted_work": "Prepare the three helper full-raw numerical probes and fixed admission/decoder scripts inside the allowed workspace.",
    "native_execution_pending": "Current chat still has on-request workspace-write access; bulk outputs require S and localhost verification is restricted. No further approval notifications requested, no settings changed or alternate executor used.",
    "integrated_Rust_typecheck": False, "new_NVRTC_executions": 0, "new_GPU_executions": 0,
    "new_performance_measurements": 0, "new_accepted_gain": False,
    "limits": "Source ABI, syntax and integer checks only. The three helper CUDA resource/numerical controls and all full solver exactness/material/performance gates remain pending. Candidate not activated or adopted.",
}
new_json(HOST/"checkpoint.json", checkpoint)
evidence = DASH/"evidence/E070-host-preparation"
evidence.mkdir(exist_ok=False)
for filename in ["manifest.json", "abi-source-audit.json", "syntax-and-integer-report.json", "candidate.patch", "checkpoint.json"]:
    shutil.copyfile(HOST/filename, evidence/filename)
for filename in ["preparation.json", "rustc-exit.json"]:
    shutil.copyfile(HERE/"continuation-resources"/filename, evidence/("helper-resource-"+filename))
for filename in checkpoint["preparation_errors_preserved"]:
    shutil.copyfile(HERE/filename, evidence/filename)
with old.ar.exclusive_lock(DASH/"status.lock", timeout=3):
    status = read(DASH/"status.json")
    before = status["accepted_complete_run"].copy()
    assert before["candidate_id"] == "E051"
    status.update(updated_at=at, state="waiting", goal_status="active", active_experiment="E070",
                  stage="E070 complete host ABI staged; continuation controls pending",
                  activity="Off-tree7file patch passes10launch-site ABI audit,4Rust syntax parses and65536host pack cases. Three continuation helpers also require packed metadata; their resource probe compiles, GPUchecks pending. No new GPUexecution/timing/gain; no approval prompts sent.")
    row = next(x for x in status["experiments"] if x["id"] == "E070")
    row.update(stage="Complete host ABI staged; three helper numerical controls next",
               fixture="Four main CUDAentries plus three continuation helpers",
               correctness="CPU encoding/host syntax/ABI pass; GPU numerical untested",
               reason="Host audit corrected D114's continuation caller labels: project, transport and storage-copy are three extra kernel ABIs.7file patch prepared,10sites audited,65536Rust pack cases pass; four original raw probes and helper resource probe compile. Source not activated. All GPU/resource/material/timing gates still required.")
    link = {"label": "Complete host ABI preparation and continuation coverage correction", "url": "evidence/E070-host-preparation/checkpoint.json"}
    row["evidence"].append(link); status["evidence"].append(link)
    assert status["accepted_complete_run"] == before
    old.ar.atomic_json(DASH/"status.json", status)
assert read(DASH/"status.json")["accepted_complete_run"] == before
assert sha(evidence/"checkpoint.json") == sha(HOST/"checkpoint.json")
new_json(HOST/"dashboard-publication.json", {"at": at, "disk_readback_verified": True,
         "HTTP_verified": False, "status_sha256": sha(DASH/"status.json"),
         "checkpoint_sha256": sha(HOST/"checkpoint.json"), "accepted_gain_unchanged": True})
print(json.dumps({"status": checkpoint["status"], "main_source_files_exact": 157,
                  "research_source_files_exact": 162, "new_GPU_executions": 0,
                  "dashboard_disk_readback": "pass", "HTTP_verified": False,
                  "checkpoint_sha256": sha(HOST/"checkpoint.json")}))
