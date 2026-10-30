"""Compile staged host-side probes, without starting a GPU process."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


for name in sys.argv[1:]:
    assert name in {"down-action", "up-action-eval", "up-fold"}, name
    folder = HERE / name
    preparation = json.loads((folder / "preparation.json").read_text(encoding="utf-8"))
    for filename, expected in preparation["input_sha256"].items():
        assert sha(folder / filename) == expected, filename
    assert not (folder / "probe.exe").exists()
    assert not (folder / "rustc-exit.json").exists()
    temporary = folder / "compiler-tmp"
    temporary.mkdir(exist_ok=False)
    env = os.environ.copy()
    env["TMP"] = str(temporary)
    env["TEMP"] = str(temporary)
    for key in ["RUSTFLAGS", "CARGO_ENCODED_RUSTFLAGS", "RUSTC", "RUSTC_WRAPPER"]:
        assert not env.get(key), key
    proc = None
    started = now()
    fault = None
    try:
        with (folder / "rustc.stdout.log").open("xb") as stdout, (folder / "rustc.stderr.log").open("xb") as stderr:
            proc = subprocess.Popen(preparation["rustc_command"], cwd=folder, env=env,
                                    stdout=stdout, stderr=stderr,
                                    creationflags=subprocess.CREATE_NO_WINDOW)
            clock = time.monotonic()
            while True:
                try:
                    proc.wait(timeout=20)
                    break
                except subprocess.TimeoutExpired:
                    print(name, "compiler running", proc.pid, int(time.monotonic() - clock), flush=True)
                    if time.monotonic() - clock > 180:
                        raise TimeoutError(name)
    except BaseException as exc:
        fault = repr(exc)
        if proc is not None and proc.poll() is None:
            proc.kill()
            proc.wait(timeout=30)
        raise
    finally:
        receipt = {"id": "E070-" + name + "-compiler-receipt", "started": started,
                   "finished": now(), "compiler_pid": proc.pid if proc else None,
                   "returncode": proc.returncode if proc else None, "error": fault,
                   "all_owned_compiler_handles_terminal": proc is not None and proc.poll() is not None,
                   "GPUexecutions": 0, "preparation_sha256": sha(folder / "preparation.json"),
                   "compiler_command": preparation["rustc_command"],
                   "child_only_TMP_TEMP": str(temporary)}
        if (folder / "probe.exe").exists():
            receipt["binary_sha256"] = sha(folder / "probe.exe")
        with (folder / "rustc-exit.json").open("x", encoding="utf-8") as f:
            json.dump(receipt, f, indent=2)
    assert proc.returncode == 0, (folder / "rustc.stderr.log").read_text(encoding="utf-8", errors="replace")[-3000:]
    print(json.dumps({"compiled": name, "returncode": 0, "GPUexecutions": 0,
                      "binary_sha256": receipt["binary_sha256"]}), flush=True)
