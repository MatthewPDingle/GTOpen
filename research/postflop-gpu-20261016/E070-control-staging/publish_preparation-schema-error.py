"""Publish compiler-only progress to the existing workspace dashboard."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil
import sys

HERE = Path(__file__).resolve().parent
ROOT = Path(r"S:\GTOpen-research\postflop-gpu-20261016")
DASH = HERE.parents[2] / "web/research/postflop-gpu-20261016"
sys.path.insert(0, str(ROOT / "runs/accepted-E051"))
import common_e051 as old


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def new_json(path, value):
    with path.open("x", encoding="utf-8") as f:
        json.dump(value, f, indent=2)


assert sha(ROOT / "runs/E070-source/candidate.cu") == "ffe6c46aa48fbae149ace1288ea512814da11b840c648e6a260759e427c54ec8"
assert sha(ROOT / "runs/E070-resource/report.json") == "a9452fad3b7a5d4da8fe7915c5c7b5a7a74df1c166f48ca663f0e2d79cc19b8c"
names = ["up-action", "down-action", "up-action-eval", "up-fold"]
raw_bounds = [105982480, 265445940, 211964860, 152543620]
families = []
for name, raw_bound in zip(names, raw_bounds):
    folder = HERE / name
    prep = json.loads((folder / "preparation.json").read_text(encoding="utf-8"))
    receipt = json.loads((folder / "rustc-exit.json").read_text(encoding="utf-8"))
    corpus = json.loads((folder / "corpus.json").read_text(encoding="utf-8"))
    assert receipt["returncode"] == 0 and receipt["GPUexecutions"] == prep["GPUexecutions"] == 0
    assert receipt["all_owned_compiler_handles_terminal"]
    assert len(corpus["cases"]) == prep["cases"]
    assert [x["id"] for x in corpus["cases"]] == list(range(prep["cases"]))
    for filename, expected in prep["input_sha256"].items():
        assert sha(folder / filename) == expected, (name, filename)
    assert sha(folder / "probe.exe") == receipt["binary_sha256"]
    families.append({"family": name, "cases": prep["cases"],
                     "planned_kernel_launches": 2 * prep["cases"],
                     "compiler_returncode": 0,
                     "compiler_pid": receipt["compiler_pid"],
                     "binary_sha256": receipt["binary_sha256"],
                     "preparation_sha256": sha(folder / "preparation.json"),
                     "compiler_receipt_sha256": sha(folder / "rustc-exit.json"),
                     "conservative_raw_bytes": raw_bound,
                     "ABI": prep["ABI"],
                     "planned_raw_directory": str(ROOT / "runs/E070-direct-kernel-controls" / name / "raw")})
at = datetime.now(timezone.utc).isoformat()
manifest = {
    "id": "E070-four-kernel-compiler-preparation", "at": at,
    "status": "pass_host_probe_compilation_only",
    "families": families, "cases": sum(x["cases"] for x in families),
    "planned_kernel_launches": sum(x["planned_kernel_launches"] for x in families),
    "GPUexecutions": 0, "solver_executions": 0, "performance_measurements": 0,
    "candidate_cuda_sha256": sha(ROOT / "runs/E070-source/candidate.cu"),
    "resource_report_sha256": sha(ROOT / "runs/E070-resource/report.json"),
    "root_decoder_sha256": sha(HERE / "audit_raw.py"),
    "source_sha256": {p.name: sha(p) for p in HERE.iterdir() if p.is_file()},
    "all_owned_compiler_handles_terminal": True,
    "new_app_source_activation": False,
    "host_integration_implemented": False,
    "resource_warning": "Down-action40to46registers;128thread theoretical residency12to10blocks/SM. No measured tradeoff qualification yet.",
    "raw_storage_plan": {"physical_root": str(ROOT), "conservative_raw_bytes": sum(raw_bounds),
                         "peak_reservation_bytes": 8*1024**3, "minimum_free_before_admission_bytes": 66*1024**3,
                         "free_bytes_observed_preparation_only": shutil.disk_usage(ROOT).free,
                         "must_recheck_before_native_admission": True},
    "planned_sequence": ["Seal checksum-verified source/binary copy and final execution protocol on S before admission.",
                         "Acquire the existing serialized GPU lock; recheck custody, idle server sessions and reserve.",
                         "Execute each declared family once, in listed order. Retain all five full raw files and owned-process receipts.",
                         "Replay all3833declared pairs with the frozen root decoder; no speed claims from these correctness controls.",
                         "Only after all numerical controls pass: integrate every host ABI/caller and actual metadata accounting, then ordinary/exact checks and registered timing gates."],
    "no_rescue": "Frozen E070 CUDA and cases. Any candidate numerical failure closes this form; no width, threshold, arithmetic, ABI or extra-sample rescue.",
    "unused_control_inputs": "Both arms retain old i32 metadata and packed attrs to capture complete immutable images. Each arm consumes only its declared ABI. These probes do not measure memory or speed.",
    "blueprint_note": "up-action/corpus.json retains its E054 descriptor-source labels. Its819case descriptors are reused; no old numerical result is reused. Other three blueprints are explicitly unexecuted E070 preparations.",
    "permissions": {"effective_chat_mode": "on-request workspace-write", "saved_host_default": "full-access",
                    "user_authorization": "Routine research authorized; user requests no repeated approval notifications.",
                    "native_requests_sent_after_latest_instruction": 0,
                    "native_execution_state": "Held pending actual current-chat runtime permissions; no security settings altered."},
    "limits": "Successful host Rust compilation and source/hash checks only. GPU floating results, full solver equivalence, host integration, no-tradeoff checks and performance are untested. Final native admission protocol is still required.",
    "candidate_accepted": False, "accepted_complete_run_gain_changed": False,
}
assert manifest["cases"] == 3833 and manifest["planned_kernel_launches"] == 7666
new_json(HERE / "compiler-preparation-manifest.json", manifest)
evidence = DASH / "evidence/E070-control-preparation"
assert not evidence.exists()
evidence.mkdir()
shutil.copyfile(HERE / "compiler-preparation-manifest.json", evidence / "compiler-preparation-manifest.json")
for name in names:
    for filename in ["preparation.json", "rustc-exit.json"]:
        shutil.copyfile(HERE / name / filename, evidence / (name + "-" + filename))
shutil.copyfile(HERE / "audit_raw.py", evidence / "audit_raw.py")
with old.ar.exclusive_lock(DASH / "status.lock", timeout=3):
    status = json.loads((DASH / "status.json").read_text(encoding="utf-8"))
    accepted_before = status["accepted_complete_run"].copy()
    assert accepted_before["candidate_id"] == "E051"
    status.update(updated_at=at, state="waiting", goal_status="active", active_experiment="E070",
                  stage="E070 four correctness probes compiled; GPU execution pending",
                  activity="All4host probes compile:3833declared cases/7666planned kernel launches. No GPUexecution, new timing or accepted gain. Native execution is held while the current chat remains on-request; no further approval prompts sent.")
    row = next(x for x in status["experiments"] if x["id"] == "E070")
    row.update(stage="3833case correctness probes compiled; native execution pending",
               correctness="CPU encoding/resources pass; GPU numerical untested",
               reason="All four Rust/CUDA-ABI probes compile against frozen E070 PTX. Full raw controls, host/caller integration and qualification remain pending. Down-action register/residency warning retained. No new performance claim.")
    link = {"label": "Four compiled correctness probes; no GPU execution", "url": "evidence/E070-control-preparation/compiler-preparation-manifest.json"}
    row["evidence"].append(link); status["evidence"].append(link)
    assert status["accepted_complete_run"] == accepted_before
    old.ar.atomic_json(DASH / "status.json", status)
readback = json.loads((DASH / "status.json").read_text(encoding="utf-8"))
assert readback["accepted_complete_run"] == accepted_before and readback["stage"] == status["stage"]
assert sha(evidence / "compiler-preparation-manifest.json") == sha(HERE / "compiler-preparation-manifest.json")
new_json(HERE / "dashboard-publication.json", {"at": at,
         "manifest_sha256": sha(HERE / "compiler-preparation-manifest.json"),
         "status_sha256": sha(DASH / "status.json"), "disk_readback_verified": True,
         "HTTP_verified": False, "HTTP_limit": "Current restricted network profile prevents localhost socket verification.",
         "accepted_complete_run_unchanged": True, "GPUexecutions": 0})
print(json.dumps({"status": manifest["status"], "cases": 3833, "GPUexecutions": 0,
                  "dashboard_disk_readback": "pass", "HTTP_verified": False,
                  "manifest_sha256": sha(HERE / "compiler-preparation-manifest.json")}))
