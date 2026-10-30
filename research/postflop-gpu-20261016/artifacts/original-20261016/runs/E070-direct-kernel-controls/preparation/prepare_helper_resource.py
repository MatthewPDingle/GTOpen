"""Compile the resource probe's Rust bindings only. Never start that probe."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
HOST = HERE / "host-integration-r2"
OUT = HERE / "continuation-resources"
ROOT = Path(r"S:\GTOpen-research\postflop-gpu-20261016")
REL = "crates/solver/src/gpu/"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


assert not OUT.exists()
m = json.loads((HOST / "manifest.json").read_text(encoding="utf-8"))
OUT.mkdir()
shutil.copyfile(HERE / "helper_resource_probe.rs", OUT / "probe.rs")
for suffix, filename in [("projection", "continuation_projection.cu"), ("storage-copy", "continuation_storage_copy.cu")]:
    for arm in ["baseline", "candidate"]:
        source = HOST / arm / REL / filename
        expected = m["staged_baseline_sha256" if arm == "baseline" else "candidate_source_sha256"][REL+filename]
        assert sha(source) == expected
        shutil.copyfile(source, OUT / (arm+"-"+suffix+".cu"))
p = json.loads((ROOT / "runs/E070-resource/protocol.json").read_text(encoding="utf-8"))
resource = ROOT / "runs/E070-resource"
command = [str(OUT/"probe.rs") if x == str(resource/"probe.rs") else
           str(OUT/"probe.exe") if x == str(resource/"probe.exe") else x for x in p["rustc_command"]]
plan = {"id": "E070-continuation-helper-resource-preparation", "status": "unexecuted_native_prerequisite",
        "input_sha256": {x.name: sha(x) for x in OUT.iterdir() if x.is_file()},
        "rustc_command": command, "host_manifest_sha256": sha(HOST/"manifest.json"),
        "kernel_entries": ["continuation_project", "continuation_transport", "continuation_storage_copy"],
        "architectures": ["compute_120", "compute_75"], "planned_NVRTC_compiles": 8,
        "planned_driver_resource_rows": 6, "planned_application_kernel_launches": 0,
        "prerequisite_gates": ["Both module/arm/architecture PTX sets compile with architecture-only default options.",
                               "All3entry parameter lists replace only the adjacent player/arity pair with one packed-u16 pointer; retain expected rest of ABI.",
                               "Both metadata decodes remain source-reversible; PTX uses a narrow u8/u16 global load for the metadata.",
                               "No increase in driver local/spill bytes, dynamic shared memory, or loss of maximum supported block threads. Default limits fit and64/128/256thread theoretical residency stays positive.",
                               "Register/residency warnings disclosed under D108; they do not waive measured material/performance gates."],
        "native_admission_pending": True, "frozen_core_E070_CUDA_changed": False,
        "no_rescue": "One frozen helper source pair; failure closes the form, no compiler-option/width/sampling rescue.",
        "GPUexecutions": 0, "limits": "Rust host compiler preparation only. No NVRTC, driver-resource or GPU numerical result yet."}
with (OUT/"preparation.json").open("x", encoding="utf-8") as f:
    json.dump(plan, f, indent=2)
temporary = OUT/"compiler-tmp"
temporary.mkdir()
env = os.environ.copy()
env["TMP"] = env["TEMP"] = str(temporary)
process = None
error = None
started = datetime.now(timezone.utc).isoformat()
try:
    with (OUT/"rustc.stdout.log").open("xb") as stdout, (OUT/"rustc.stderr.log").open("xb") as stderr:
        process = subprocess.Popen(command, cwd=OUT, env=env, stdout=stdout, stderr=stderr,
                                   creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            process.wait(timeout=180)
        except subprocess.TimeoutExpired:
            process.kill(); process.wait(timeout=30); raise
except BaseException as exc:
    error = repr(exc)
    raise
finally:
    receipt = {"started": started, "finished": datetime.now(timezone.utc).isoformat(),
               "pid": process.pid if process else None, "returncode": process.returncode if process else None,
               "terminal": process is not None and process.poll() is not None,
               "error": error, "GPUexecutions": 0, "NVRTC_processes": 0,
               "preparation_sha256": sha(OUT/"preparation.json")}
    if (OUT/"probe.exe").exists():
        receipt["binary_sha256"] = sha(OUT/"probe.exe")
    with (OUT/"rustc-exit.json").open("x", encoding="utf-8") as f:
        json.dump(receipt, f, indent=2)
assert process.returncode == 0, (OUT/"rustc.stderr.log").read_text(encoding="utf-8", errors="replace")[-2500:]
print(json.dumps({"compiled": "continuation resource probe", "returncode": 0,
                  "binary_sha256": receipt["binary_sha256"], "GPUexecutions": 0, "NVRTC_processes": 0}))
