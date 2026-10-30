"""Seal the one-run native control plan inside the permitted workspace."""
from pathlib import Path
from datetime import datetime, timezone
import ast
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = Path(r"S:\GTOpen-research\postflop-gpu-20261016")
RESEARCH = Path(r"X:\Dev\GTOpen-gpu-research-20261016")


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):
    return json.loads(p.read_text(encoding="utf-8"))


target = HERE/"native-execution-plan.json"
assert not target.exists() and not (ROOT/"runs/E070-direct-kernel-controls").exists()
components = ["up-action", "down-action", "up-action-eval", "up-fold", "continuation-raw", "continuation-resources"]
records = []
used = set()


def add(source, relative):
    relative = Path(relative).as_posix()
    assert relative not in used and ".." not in Path(relative).parts and not Path(relative).is_absolute()
    used.add(relative)
    records.append({"source": str(source.resolve()), "archive_relative": relative,
                    "sha256": sha(source), "bytes": source.stat().st_size})


for component in components:
    folder = HERE/component
    prep = read(folder/"preparation.json")
    receipt = read(folder/"rustc-exit.json")
    assert receipt["returncode"] == 0 and receipt["GPUexecutions"] == 0
    assert sha(folder/"probe.exe") == receipt["binary_sha256"]
    for name, expected in prep["input_sha256"].items():
        assert sha(folder/name) == expected
        add(folder/name, "inputs/"+component+"/"+name)
    for name in ["preparation.json", "rustc-exit.json", "probe.exe", "rustc.stdout.log", "rustc.stderr.log"]:
        add(folder/name, "inputs/"+component+"/"+name)
scripts = ["run_sealed_controls.py", "audit_helper_resources.py", "audit_raw.py", "helper_raw_audit.py"]
for name in scripts:
    ast.parse((HERE/name).read_text(encoding="utf-8"))
    add(HERE/name, "scripts/"+name)
host = HERE/"host-integration-r2"
m = read(host/"manifest.json")
for p, expected in m["candidate_source_sha256"].items():
    assert sha(host/"candidate"/p) == expected
for p in sorted(host.rglob("*")):
    if p.is_file() and "compiler-tmp" not in p.parts and p.suffix in {".json", ".rs", ".cu", ".log", ".patch", ".exe"}:
        add(p, "host-integration/"+p.relative_to(host).as_posix())
for p in sorted(HERE.iterdir()):
    if p.is_file() and p.suffix in {".py", ".json", ".rs"} and p.name not in scripts:
        add(p, "preparation/"+p.name)
existing = {}
for name in ["runs/E070-source/candidate.cu", "runs/E070-source/manifest.json",
             "runs/E070-resource/report.json", "runs/E070-resource/protocol.json",
             "runs/D114-node-metadata/report.json", "runs/D114-node-metadata/root-raw-replay.json",
             "runs/accepted-E051/baseline.json", "runs/accepted-E051/protected-main.json",
             "runs/accepted-E051/preexisting-target-artifacts.json"]:
    p = ROOT/name
    existing[str(p)] = sha(p)
policies = {"qualification-policy-20261017.md": "2b4f173b98863272279c39302017608aa8a0976074a709fe09e61af5a4b0735f",
            "resource-feasibility-policy-20261017.md": "eaa3f168c57a1f390510ac21454fcce3ac0bc454e1ef9a49f73876ec9cda393c"}
for name, digest in policies.items():
    p = RESEARCH/"research/postflop-gpu-20261016"/name
    assert sha(p) == digest, name
    existing[str(p)] = digest
for arm in ["baseline", "candidate"]:
    for arch in ["compute_120", "compute_75"]:
        p = ROOT/"runs/E070-resource/execution"/f"{arm}-{arch}.ptx"
        existing[str(p)] = sha(p)
assert existing[str(ROOT/"runs/E070-source/candidate.cu")] == "ffe6c46aa48fbae149ace1288ea512814da11b840c648e6a260759e427c54ec8"
assert existing[str(ROOT/"runs/E070-resource/report.json")] == "a9452fad3b7a5d4da8fe7915c5c7b5a7a74df1c166f48ca663f0e2d79cc19b8c"
bound = read(HERE/"continuation-raw/checkpoint.json")["raw_storage"]["conservative_bytes"]
archive_bytes = sum(r["bytes"] for r in records)
assert bound+archive_bytes < 8*1024**3
plan = {
    "id": "E070-seven-entry-native-execution-plan", "at": datetime.now(timezone.utc).isoformat(),
    "native_archive": str(ROOT/"runs/E070-direct-kernel-controls"),
    "candidate_cuda_sha256": existing[str(ROOT/"runs/E070-source/candidate.cu")],
    "archive_inputs": records, "existing_scientific_inputs": existing,
    "declared_cases": 5953, "planned_application_kernel_launches": 11906,
    "native_resource_processes": 1, "helper_NVRTC_compilations": 8,
    "native_numerical_processes": 5, "root_raw_replays": 5,
    "native_resource_timeout_seconds": 180, "numerical_process_timeout_seconds": 1800,
    "root_replay_timeout_seconds": 1800,
    "component_order": ["helper resource/ABI/driver gates", "up-action819", "down-action1196", "up-action-eval1638", "up-fold180", "continuation2120"],
    "unrounded_complete_solve_acceptance_cutoff_pct": 1,
    "sampling": "Exactly one frozen helper resource process and one paired numerical process per listed component. No timing samples, automatic retries, exclusions, extra cases, compiler-option/source rescue or pooled samples.",
    "admission": "Actual runtime permission to write S and read localhost; no permission edits or alternate executors. Verify source/Git/live/protected-PTX custody, idle app sessions, GPU UUID and S reserve. Checksum-copy all frozen inputs before any compiler/device work, hold existing exclusive GPU lock, seal generated helper PTX SHA256 before application kernel work.",
    "GPU_UUID": "GPU-a5459b5a-632b-3e73-d7f1-a06e167102ee",
    "minimum_free_before_admission_bytes": 66*1024**3,
    "minimum_free_during_controls_bytes": 58*1024**3,
    "peak_output_reservation_bytes": 8*1024**3,
    "conservative_full_raw_bytes": bound, "frozen_input_archive_bytes": archive_bytes,
    "limits": "Scoped correctness/resource campaign only. No solver activation, integrated build, complete-solver accuracy, material-tradeoff qualification or speed acceptance. A later integrated-source protocol must pass all existing qualification gates.",
    "native_execution_performed": False, "GPUexecutions": 0,
    "executor_sha256": sha(HERE/"run_sealed_controls.py"),
}
with target.open("x", encoding="utf-8") as f:
    json.dump(plan, f, indent=2)
print(json.dumps({"status": "sealed_preparation_only", "archive_files": len(records),
                  "archive_bytes": archive_bytes, "cases": 5953, "GPUexecutions": 0,
                  "execution_plan_sha256": sha(target)}))
