"""Run the final pass-2 regressions against the actual shared checkout."""
from pathlib import Path
import datetime as dt
import hashlib
import json
import os
import subprocess
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
config = json.loads((HERE / "run.json").read_text(encoding="utf-8"))
def snapshot():
    return {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in config["main_source_hashes"]}
source = snapshot()
assert source == config["main_source_hashes"]
env = os.environ.copy()
env["PATH"] = str(ROOT / ".cuda-nvrtc/nvidia/cuda_nvrtc/bin") + os.pathsep + env["PATH"]
env["RAYON_NUM_THREADS"] = env["SOLVER_THREADS"] = "16"
# Content-identical files need no change; touching implementation inputs once
# here ensures the main checkout cannot reuse artifacts from preserved mtimes.
for name in source:
    if name.endswith((".rs", ".cu", "Cargo.toml")):
        (ROOT / name).touch()
commands = {
    "cpu": ["cargo", "test", "--release", "-p", "solver"],
    "gpu": ["cargo", "test", "--release", "-p", "solver", "--features", "gpu", "--lib", "--test", "gpu", "--test", "preflop_gpu", "--test", "preflop_budget", "--", "--include-ignored", "--test-threads=1"],
    "server": ["cargo", "test", "--release", "-p", "server", "--features", "gpu", "--", "--test-threads=1"],
}
manifest = {"started_utc": dt.datetime.now(dt.timezone.utc).isoformat(), "source": source, "suites": {}}
for name, command in commands.items():
    filename = "raw/pass2-main-" + name + ".log"
    print("Running main " + name, flush=True)
    with (HERE / filename).open("w", encoding="utf-8") as log:
        result = subprocess.run(command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
    manifest["suites"][name] = {"command": command, "log": filename, "returncode": result.returncode}
    (HERE / "gpu-main-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    if result.returncode:
        raise SystemExit("Main " + name + " failed; inspect " + filename)
assert snapshot() == source
manifest["completed_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
(HERE / "gpu-main-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print("Main regression suites passed", flush=True)
