"""Standalone rustc/NVRTC resource inspection, serialized with the existing GPU lock."""
from pathlib import Path
import datetime
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
REPO = Path(r"X:\Dev\GTOpen-gpu-research-20261016")
ROOT = Path(r"S:\GTOpen-research\postflop-gpu-20261016")
DEPS = ROOT / "build/release/deps"
SOURCE = REPO / "crates/solver/src/gpu/kernels.cu"
EXPECTED = "8fe86cb859124592f9df13821f4a300450045620e6947e99466e4228b78c20d0"

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(name, data):
    (HERE / name).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

if (HERE / "report.json").exists() or (HERE / "probe.exe").exists():
    raise SystemExit("Refusing to overwrite D021 execution evidence")
original = SOURCE.read_bytes()
assert hashlib.sha256(original).hexdigest() == EXPECTED
assert b"__launch_bounds__" not in original
start = original.index(b'extern "C" __global__ void up_action(')
end_signature = original.index(b"{", start)
signature = original[start:end_signature].replace(b"void up_action(", b"void up_action_3(", 1)
original_call = re.search(rb"else if \(na == 3\) (up_action_impl<3>\([^\n]+;)", original).group(1)
wrapper = signature + b"{\n    if (blockIdx.x >= (u32)count) return;\n    " + original_call + b"\n}\n"
candidate = original + b"\n// D021 resource-only entry point; original implementation above is unchanged.\n" + wrapper
(HERE / "baseline.cu").write_bytes(original)
(HERE / "candidate.cu").write_bytes(candidate)
(HERE / "direct3-wrapper.cu").write_bytes(wrapper)
shutil.copyfile(ROOT / "runs/E006-postflop_register_resources.rs", HERE / "source-E006-resource.rs")
shutil.copyfile(ROOT / "runs/D016-direct3-design/audit.md", HERE / "source-D016-audit.md")
shutil.copyfile(REPO / "tools/postflop_autoresearch.py", HERE / "runner-primitives-source.py")
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("d021_runner", HERE / "runner-primitives-source.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
runner.REPO = REPO

def one(pattern):
    found = list(DEPS.glob(pattern))
    assert len(found) == 1, (pattern, found)
    return found[0]
cudarc = one("libcudarc-*.rlib")
serde = one("libserde_json-*.rlib")
command = ["rustc", "probe.rs", "--edition=2021", "-C", "opt-level=3", "-C", "codegen-units=1", "-C", "lto=thin",
           "-L", "dependency=" + str(DEPS), "--extern", "cudarc=" + str(cudarc),
           "--extern", "serde_json=" + str(serde), "-o", "probe.exe"]
commands = []
def execute(args, name, env=None):
    before = time.perf_counter()
    at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    child = subprocess.Popen(args, cwd=HERE, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    try:
        out, err = child.communicate(timeout=120)
    except BaseException:
        child.kill()
        out, err = child.communicate()
        (HERE / (name + ".stdout.log")).write_bytes(out)
        (HERE / (name + ".stderr.log")).write_bytes(err)
        raise
    (HERE / (name + ".stdout.log")).write_bytes(out)
    (HERE / (name + ".stderr.log")).write_bytes(err)
    commands.append({"args": args, "cwd": str(HERE), "started_at": at,
                     "elapsed_seconds": time.perf_counter()-before, "returncode": child.returncode})
    save("commands.json", commands)
    if child.returncode: raise RuntimeError(name + " failed; inspect preserved logs")
    return out.decode("utf-8")

manifest = {"id": "D021", "source_path": str(SOURCE), "source_sha256": sha(SOURCE),
            "baseline_sha256": sha(HERE / "baseline.cu"), "candidate_sha256": sha(HERE / "candidate.cu"),
            "original_prefix_byte_identical": candidate[:len(original)] == original,
            "dispatcher_signature_reused": True, "template3_argument_list_reused": True,
            "probe_sha256": sha(HERE / "probe.rs"), "runner_sha256": sha(HERE / "run.py"),
            "resource_template_sha256": sha(HERE / "source-E006-resource.rs"),
            "preflight_template_sha256": sha(HERE / "runner-primitives-source.py"),
            "dependency_rlibs": {str(p): sha(p) for p in [cudarc, serde]},
            "rustc": subprocess.check_output(["rustc", "-Vv"], text=True),
            "checkout_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip(),
            "nvrtc_options": "architecture only; all other cudarc CompileOptions default",
            "resource_block_threads": 128, "kernel_launches": 0, "solver_executions": 0,
            "scope": "Resource diagnostic only; no speed or numerical correctness claim"}
save("manifest.json", manifest)
with runner.exclusive_lock(ROOT / "gpu-run.lock"):
    live = runner.live_status()
    runner.refuse_active(live)
    save("preflight.json", {"live_status": live, "telemetry": runner.telemetry(), "lock": str(ROOT / "gpu-run.lock")})
    execute(command, "rustc")
    env = os.environ.copy()
    env["PATH"] = str(runner.NVRTC) + os.pathsep + env.get("PATH", "")
    env["RAYON_NUM_THREADS"] = "16"
    live = runner.live_status()
    runner.refuse_active(live)
    save("launch-preflight.json", live)
    output = execute([str(HERE / "probe.exe")], "probe", env)
    after = runner.telemetry()
rows = [json.loads(line.removeprefix("METRIC_JSON ")) for line in output.splitlines() if line.startswith("METRIC_JSON ")]
assert len(rows) == 3
assert [(r["source_variant"], r["kernel"]) for r in rows] == [("baseline","up_action"),("candidate","up_action"),("candidate","up_action_3")]
keys = ["registers", "local_bytes_per_thread", "static_shared_bytes", "occupancy_blocks_per_sm_128"]
assert all(rows[0][k] == rows[1][k] for k in keys), "Appending entry point changed dispatcher resources"
assert SOURCE.read_bytes() == original

def entry(source, name):
    match = re.search(r"\.visible\s+\.entry\s+" + name + r"\(", source)
    assert match, name
    begin = source.index("{", match.start())
    level = 1; end = begin+1
    while level:
        if source[end] == "{": level += 1
        elif source[end] == "}": level -= 1
        end += 1
    return source[match.start():end]
baseline_ptx = (HERE / "baseline.ptx").read_text()
candidate_ptx = (HERE / "candidate.ptx").read_text()
dispatcher = entry(baseline_ptx, "up_action")
control = entry(candidate_ptx, "up_action")
direct = entry(candidate_ptx, "up_action_3")
for name, text in [("baseline-up_action.ptx", dispatcher),("candidate-up_action.ptx",control),("candidate-up_action_3.ptx",direct)]:
    (HERE / name).write_text(text+"\n", encoding="utf-8")
proof = {"original_source_prefix_exact": True, "dispatcher_ptx_exact": dispatcher == control,
         "entry_source": "direct3-wrapper.cu", "unchanged_impl": "candidate.cu retains complete baseline.cu prefix byte-for-byte",
         "ptx_entry_lines": {"baseline_dispatcher": len(dispatcher.splitlines()), "direct3": len(direct.splitlines())}}
report = {"id": "D021", "status": "measured_diagnostic", "manifest": manifest,
          "results": rows, "code_proof": proof, "commands": commands, "telemetry_after": after,
          "resource_change": {k: {"dispatcher": rows[0][k], "direct3": rows[2][k]} for k in keys},
          "kernel_launches": 0, "performance_measurement": False,
          "numerical_validation": "not executed", "candidate_accepted": False,
          "artifact_sha256": {p.name: sha(p) for p in HERE.iterdir() if p.is_file()}}
save("report.json", report)
print(json.dumps({"results": rows, "code_proof": proof}, indent=2))
