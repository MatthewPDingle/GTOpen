"""Explicit verified cutover after private smoke; rollback restores both backups."""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import subprocess
import time
from types import SimpleNamespace
import uuid

import psutil
import session_guard as guard


def launch(executable, expected_hash, manifest, log_path):
    guard.require(guard.sha(executable) == expected_hash, "launch executable hash changed")
    env = os.environ.copy()
    for key in list(env):
        if key.startswith(("PREFLOP_MW_", "PREFLOP_GPU_", "PREFLOP_PHASE_")):
            env.pop(key)
    for key, value in manifest["old_owner"]["environment"].items():
        if value is None:
            env.pop(key, None)
        else:
            env[key] = value
    env["PORT"] = str(manifest["port"])
    env["PATH"] = str(guard.ROOT / ".cuda-nvrtc/nvidia/cuda_nvrtc/bin") + os.pathsep + env["PATH"]
    with log_path.open("x", encoding="utf8") as log:
        child = subprocess.Popen([str(executable)], cwd=guard.ROOT, env=env,
                                 stdout=log, stderr=subprocess.STDOUT,
                                 creationflags=subprocess.CREATE_NO_WINDOW)
    try:
        deadline = time.monotonic() + 120
        while time.monotonic() < deadline:
            guard.require(child.poll() is None, "new server exited during startup")
            try:
                owner = guard.owner(manifest["port"])
                if owner["pid"] == child.pid and owner["sha256"] == expected_hash:
                    if guard.api(manifest["port"], "/api/status")["state"] == "idle":
                        return child, owner
            except (OSError, ValueError):
                pass
            time.sleep(.3)
        raise ValueError("new server startup timed out")
    except BaseException:
        if child.poll() is None:
            child.terminate()
            child.wait(timeout=30)
        raise


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    guard.require(args.execute, "explicit --execute required")
    manifest = json.loads(args.manifest.read_text())
    folder = args.manifest.parent
    guard.require((folder / "smoke-passed.json").is_file(), "private smoke has not passed")
    guard.queues_clear()
    candidate = manifest["candidate"]
    old = manifest["old_owner"]
    guard.require(guard.sha(candidate["path"]) == candidate["sha256"], "candidate changed since smoke")
    guard.require(guard.sha(manifest["rollback_executable"]) == old["sha256"], "rollback copy changed")
    guard.check_live(SimpleNamespace(execute=True, queues_complete=True, manifest=str(args.manifest),
                                   port=manifest["port"], expected_pid=old["pid"], expected_sha256=old["sha256"]))
    guard.check_owner(manifest["port"], old)
    guard.snapshot(manifest["port"])
    previous = psutil.Process(old["pid"])
    guard.require(previous.create_time() == old["created"], "old PID reused")
    previous.terminate()
    previous.wait(timeout=30)
    child = None
    record = {"started_utc": dt.datetime.now(dt.timezone.utc).isoformat(), "old_owner": old}
    token = uuid.uuid4().hex[:8]
    try:
        child, current = launch(candidate["path"], candidate["sha256"], manifest, folder / ("live-" + token + ".log"))
        guard.restore(SimpleNamespace(execute=True, queues_complete=True, manifest=str(args.manifest),
                                      port=manifest["port"], expected_pid=child.pid, expected_sha256=candidate["sha256"]))
        record.update(status="deployed", new_owner=current, finished_utc=dt.datetime.now(dt.timezone.utc).isoformat())
        guard.write_new(folder / ("cutover-" + token + ".json"), record)
        print(json.dumps(record))
    except BaseException as error:
        record["error"] = repr(error)
        if child is not None and child.poll() is None:
            child.terminate()
            child.wait(timeout=30)
        rollback, restored_owner = launch(manifest["rollback_executable"], old["sha256"], manifest,
                                           folder / ("rollback-" + token + ".log"))
        guard.restore(SimpleNamespace(execute=True, queues_complete=True, manifest=str(args.manifest),
                                      port=manifest["port"], expected_pid=rollback.pid, expected_sha256=old["sha256"]))
        record.update(status="rolled_back", restored_owner=restored_owner)
        guard.write_new(folder / ("cutover-" + token + ".json"), record)
        raise


if __name__ == "__main__":
    main()
