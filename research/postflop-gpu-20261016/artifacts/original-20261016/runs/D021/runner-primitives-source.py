#!/usr/bin/env python3
"""Run one serialized native test and publish measurements, never acceptance.

Example: python tools/postflop_autoresearch.py --id B001 --title Baseline \
    --kind baseline --binary S:\\path\\postflop_perf.exe --test bench --fixture rainbow
Use --not-ignored for ordinary tests; --test '*' selects the whole test binary.
The live application's APIs are read only. Raw evidence is never overwritten.
"""
from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import queue
import re
import shutil
import signal
import subprocess
import sys
import threading
import time
import urllib.request
import uuid


REPO = Path(__file__).resolve().parents[1]
APP = Path(r"X:\Dev\GTOpen")
RESEARCH = Path(r"S:\GTOpen-research\postflop-gpu-20261016")
DASHBOARD = APP / "web/research/postflop-gpu-20261016"
STATUS = DASHBOARD / "status.json"
NVRTC = APP / ".cuda-nvrtc/nvidia/cuda_nvrtc/bin"
LIVE = "http://127.0.0.1:43735"
HEARTBEAT_SECONDS = 10
MAX_DASHBOARD_LOG = 512 * 1024
REQUIRED_RESULT = {
    "fixture_id", "board", "storage", "build_ms", "init_ms", "solve_ms",
    "readback_ms", "full_cycle_ms", "iteration", "exploit_bits", "fingerprint",
    "target_pct", "check_every",
}


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.{uuid.uuid4().hex}.tmp")
    try:
        with tmp.open("x", encoding="utf-8", newline="\n") as f:
            json.dump(value, f, indent=2, ensure_ascii=False, allow_nan=False)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        # Windows readers (the HTTP server or antivirus) can briefly hold the
        # destination without delete sharing. Keep the old complete JSON visible
        # and retry the atomic rename; never truncate the published status file.
        deadline = time.monotonic() + 2.0
        while True:
            try:
                os.replace(tmp, path)
                break
            except PermissionError:
                if time.monotonic() >= deadline:
                    raise
                time.sleep(.05)
    finally:
        tmp.unlink(missing_ok=True)


@contextlib.contextmanager
def exclusive_lock(path, timeout=0):
    deadline = time.monotonic() + timeout
    while True:
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            break
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise RuntimeError(f"Lock exists: {path}; inspect its owner before retrying")
            time.sleep(.1)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump({"pid": os.getpid(), "created_at": now()}, f)
        yield
    finally:
        path.unlink(missing_ok=True)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_command(command, timeout=10):
    try:
        done = subprocess.run(command, cwd=REPO, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=timeout,
                              creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        return {"command": command, "returncode": done.returncode,
                "stdout": done.stdout.strip(), "stderr": done.stderr.strip()}
    except (OSError, subprocess.TimeoutExpired) as e:
        return {"command": command, "error": str(e)}


def source_identity():
    paths = {REPO / name for name in ("Cargo.toml", "Cargo.lock", "bench_spot.json",
             "crates/solver/Cargo.toml", "crates/solver/build.rs",
             "research/postflop-gpu-20261016/program.md", "tools/postflop_autoresearch.py")}
    for folder in (REPO / "crates/solver/src", REPO / "crates/solver/tests"):
        paths.update(p for p in folder.rglob("*") if p.suffix in {".rs", ".cu", ".cuh", ".h"})
    hashes = {p.relative_to(REPO).as_posix(): sha256(p) for p in sorted(paths) if p.is_file()}
    benchmarks = {k: v for k, v in hashes.items() if k == "bench_spot.json" or k.startswith("crates/solver/tests/")}
    return {"source_sha256": hashes, "benchmark_sha256": benchmarks,
            "source_manifest_sha256": hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest(),
            "git_head": read_command(["git", "rev-parse", "HEAD"]),
            "git_status": read_command(["git", "status", "--short", "--untracked-files=no"]),
            "binary_source_relationship": "Current source snapshot; binary build provenance is supplied by the experiment operator."}


def build_manifest_identity(path, binary_hash):
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict) or str(data.get("binary_sha256", "")).lower() != binary_hash:
        raise RuntimeError(f"Build manifest binary_sha256 does not match executed binary: {path}")
    return {"path": str(path), "sha256": sha256(path), "data": data,
            "binary_hash_verified": True}


def telemetry():
    return {"at": now(), "gpu": read_command([
        "nvidia-smi", "--query-gpu=name,uuid,driver_version,memory.total,memory.used,memory.free,utilization.gpu,temperature.gpu,power.draw,clocks.sm",
        "--format=csv,noheader,nounits"], timeout=5),
        "compute_processes": read_command(["nvidia-smi", "--query-compute-apps=pid,process_name,used_memory", "--format=csv,noheader,nounits"], timeout=5)}


def live_status():
    snapshots = {}
    for endpoint in ("/api/status", "/api/preflop/status", "/api/reports/status"):
        with urllib.request.urlopen(LIVE + endpoint, timeout=5) as response:
            body = json.load(response)
        if not isinstance(body, dict):
            raise RuntimeError(f"Unexpected live-server status at {endpoint}")
        snapshots[endpoint] = body
    return snapshots


def refuse_active(snapshots):
    for endpoint, value in snapshots.items():
        state = str(value.get("state", "")).lower()
        if value.get("running") is True or state in {"running", "building", "stopping", "solving", "iterating", "measuring"}:
            raise RuntimeError(f"Live workload active at {endpoint}; benchmark refused")
        if endpoint != "/api/reports/status" and state not in {"", "idle", "ready", "done", "stopped", "error", "failed"}:
            raise RuntimeError(f"Unrecognized live state {state!r} at {endpoint}; benchmark refused")


def parse_marker(line):
    match = re.search(r"AUTORESEARCH_(STAGE|RESULT)\s+", line)
    if not match:
        return None
    data = json.loads(line[match.end():].strip())
    if not isinstance(data, dict):
        raise ValueError("Autoresearch marker must contain a JSON object")
    if match[1] == "RESULT":
        missing = REQUIRED_RESULT - data.keys()
        if missing:
            raise ValueError(f"Missing result fields: {sorted(missing)}")
        for key in ("build_ms", "init_ms", "solve_ms", "readback_ms", "full_cycle_ms", "target_pct"):
            value = data[key]
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
                raise ValueError(f"Invalid result metric: {key}={value!r}")
        for key in ("iteration", "check_every"):
            if type(data[key]) is not int or data[key] < (1 if key == "check_every" else 0):
                raise ValueError(f"Invalid result field: {key}")
        for key in ("fixture_id", "fingerprint", "exploit_bits"):
            if data[key] is None or data[key] == "":
                raise ValueError(f"Empty result field: {key}")
    return match[1], data


def copy_evidence(run_dir):
    destination = DASHBOARD / "evidence" / run_dir.name
    destination.mkdir(parents=True, exist_ok=True)
    report = json.loads((run_dir / "report.json").read_text(encoding="utf-8"))
    atomic_json(destination / "report.json", report)
    source = run_dir / "stdout.log"
    truncated = source.stat().st_size > MAX_DASHBOARD_LOG
    with source.open("rb") as inp:
        if truncated:
            inp.seek(-MAX_DASHBOARD_LOG, os.SEEK_END)
        data = inp.read()
    tmp = destination / f".stdout.{os.getpid()}.tmp"
    tmp.write_bytes((b"[Tail only; complete raw log is in the run artifact directory.]\n" if truncated else b"") + data)
    os.replace(tmp, destination / "stdout.log")
    return [{"label": f"{run_dir.name} report", "url": f"evidence/{run_dir.name}/report.json", "detail": "Measurement and provenance; acceptance is a separate decision."},
            {"label": f"{run_dir.name} log", "url": f"evidence/{run_dir.name}/stdout.log", "detail": "Last 512 KiB; full raw log retained on S:." if truncated else "Complete native stdout/stderr."}]


def update_dashboard(report, evidence=None):
    with exclusive_lock(STATUS.with_suffix(".lock"), timeout=3):
        dashboard = json.loads(STATUS.read_text(encoding="utf-8-sig"))
        experiments = dashboard.setdefault("experiments", [])
        row = next((r for r in experiments if r.get("id") == report["id"]), None)
        if row is None:
            row = {"id": report["id"]}
            experiments.append(row)
        results = report["results"]
        measured = results[0] if len(results) == 1 else {}
        full_suite = len(results) == 3 and {r["fixture_id"] for r in results} == {"rainbow", "two-tone", "river"}
        timings = {key: sum(r[key] for r in results) if full_suite else measured.get(key)
                   for key in ("full_cycle_ms", "solve_ms")}
        row.update({"at": report["started_at"], "title": report["title"], "kind": report["kind"],
                    "status": report["status"], "started_at": report["started_at"], "updated_at": now(),
                    "finished_at": report.get("finished_at"), "fixture": "All three fixtures" if full_suite else report.get("fixture") or measured.get("fixture_id"),
                    "stage": report["stage"], "results": results, **timings,
                    "timing_aggregation": "Serialized sum of three complete fixture cycles" if full_suite else "Single fixture" if measured else None,
                    "correctness": "pending", "reason": report.get("error") or
                    ("Measurement only; repeated comparison and correctness qualification pending." if report["status"] == "measured" else report["stage"])})
        if evidence:
            row["evidence"] = evidence
        dashboard.update({"updated_at": now(), "stage": report["stage"],
                          "activity": f"{report['id']} · {report['title']} · {row['reason']}",
                          "active_experiment": report["id"] if report["status"] == "running" else None})
        # The runner never changes accepted_complete_run, validation, deployment,
        # accepted_history, fixture best values, or final baseline decisions.
        if report["status"] == "measured" and report["kind"] == "baseline":
            for result in results:
                fixture = next((f for f in dashboard.get("fixtures", []) if f.get("id") == result["fixture_id"]), None)
                if fixture is None:
                    continue
                baseline = fixture.setdefault("baseline", {})
                if baseline.get("full_cycle_ms") is None:
                    baseline.update({**result, "run_id": report["id"], "status": "single_measurement",
                                     "provisional": True, "repetitions": 1, "measured_at": report.get("finished_at"),
                                     "detail": "First measurement only; repeated final baseline not qualified."})
                if evidence:
                    existing = fixture.setdefault("evidence", [])
                    existing.extend(e for e in evidence if not any(x.get("url") == e["url"] for x in existing))
        atomic_json(STATUS, dashboard)


def cleanup_child(proc):
    if proc is None or proc.poll() is not None:
        return None
    if os.name == "nt":
        outcome = read_command(["taskkill", "/PID", str(proc.pid), "/T", "/F"], timeout=8)
    else:
        os.killpg(proc.pid, signal.SIGTERM)
        outcome = {"signal": "SIGTERM", "process_group": proc.pid}
    try:
        proc.wait(timeout=3)
    except subprocess.TimeoutExpired:
        if os.name == "nt":
            proc.kill()
        else:
            os.killpg(proc.pid, signal.SIGKILL)
        proc.wait(timeout=3)
    return outcome


def stream_output(proc, logfile, events):
    try:
        with logfile.open("ab", buffering=0) as out:
            for line in iter(proc.stdout.readline, b""):
                out.write(line)
                events.put(line.decode("utf-8", errors="replace"))
    except Exception as error:
        events.put(error)
    finally:
        events.put(None)


def run(args, run_dir):
    command = [str(args.binary)] + ([] if args.test == "*" else [args.test])
    command += ["--nocapture", "--test-threads=1"] + ([] if args.not_ignored else ["--ignored"])
    env = os.environ.copy()
    env.update({"RAYON_NUM_THREADS": "16", "PATH": str(NVRTC) + os.pathsep + env.get("PATH", "")})
    if args.fixture:
        env["POSTFLOP_AUTORESEARCH_FIXTURE"] = args.fixture
    else:
        env.pop("POSTFLOP_AUTORESEARCH_FIXTURE", None)
    env.setdefault("POSTFLOP_AUTORESEARCH_STORAGE", "compressed")
    env.setdefault("POSTFLOP_AUTORESEARCH_PROFILE", "0")
    report = {"schema_version": 1, "id": args.id, "title": args.title, "kind": args.kind,
              "fixture": args.fixture, "started_at": now(), "status": "running", "stage": "Preflight",
              "command": command, "cwd": str(REPO), "run_directory": str(run_dir), "results": [], "stages": [],
              "environment": {"RAYON_NUM_THREADS": "16", "nvrtc_path": str(NVRTC),
                              **{key: env.get(key) for key in ("POSTFLOP_AUTORESEARCH_FIXTURE", "POSTFLOP_AUTORESEARCH_STORAGE", "POSTFLOP_AUTORESEARCH_PROFILE")}},
              "accepted": False, "qualification": "Not evaluated by this runner"}
    proc = reader = None
    raw_log = run_dir / "stdout.log"
    raw_log.touch(exist_ok=False)
    try:
        update_dashboard(report)
        report["live_status_before"] = live_status()
        refuse_active(report["live_status_before"])
        if not args.binary.is_file():
            raise RuntimeError(f"Binary not found: {args.binary}")
        if not NVRTC.is_dir():
            raise RuntimeError(f"NVRTC directory missing: {NVRTC}")
        report["disk_free_bytes"] = shutil.disk_usage(RESEARCH).free
        if report["disk_free_bytes"] < 64 * 1024 * 1024:
            raise RuntimeError("Insufficient free space for durable run evidence")
        report["binary_sha256"] = sha256(args.binary)
        if args.build_manifest:
            report["binary_build_manifest"] = build_manifest_identity(args.build_manifest, report["binary_sha256"])
        report["provenance"] = source_identity()
        if args.build_manifest:
            report["provenance"]["binary_source_relationship"] = "Binary matches supplied build manifest; manifest records build-time source provenance. Current source snapshot is separate."
        report["telemetry_before"] = telemetry()
        report["live_status_at_launch"] = live_status()
        refuse_active(report["live_status_at_launch"])
        report["stage"] = "Running native test"
        atomic_json(run_dir / "report.json", report)
        update_dashboard(report)
        options = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {"start_new_session": True}
        proc = subprocess.Popen(command, cwd=REPO, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, **options)
        report["pid"] = proc.pid
        report["process_started_at"] = now()
        process_start = last_update = time.monotonic()
        events = queue.Queue()
        reader = threading.Thread(target=stream_output, args=(proc, raw_log, events), daemon=True)
        reader.start()
        output_done = False
        test_count = None
        while not output_done or proc.poll() is None:
            try:
                line = events.get(timeout=.2)
            except queue.Empty:
                line = ""
            if line is None:
                output_done = True
            elif isinstance(line, Exception):
                raise line
            elif line:
                summary = re.search(r"test result: ok\. (\d+) passed;", line)
                if summary:
                    test_count = int(summary[1])
                marker = parse_marker(line)
                if marker:
                    kind, payload = marker
                    if kind == "STAGE":
                        report["stages"].append({"at": now(), "data": payload})
                        report["stage"] = str(payload.get("stage") or payload.get("phase") or "Benchmark progress")
                    else:
                        if args.fixture and payload["fixture_id"] != args.fixture:
                            raise RuntimeError(f"Expected fixture {args.fixture}, received {payload['fixture_id']}")
                        report["results"].append(payload)
                        report["stage"] = f"Measured {payload['fixture_id']}; test still running"
                    atomic_json(run_dir / "report.json", report)
                    update_dashboard(report)
                    last_update = time.monotonic()
            if time.monotonic() - last_update >= HEARTBEAT_SECONDS:
                report["elapsed_process_seconds"] = round(time.monotonic() - process_start, 3)
                atomic_json(run_dir / "report.json", report)
                update_dashboard(report)
                last_update = time.monotonic()
        report["returncode"] = proc.wait()
        report["process_wall_ms"] = (time.monotonic() - process_start) * 1000
        report["test_pass_count"] = test_count
        if report["returncode"] != 0:
            raise RuntimeError(f"Native test exited with {report['returncode']}")
        if test_count == 0:
            raise RuntimeError("Test filter matched no executed tests")
        if args.kind in {"baseline", "candidate"} and not report["results"]:
            raise RuntimeError("No AUTORESEARCH_RESULT records; no performance measurement")
        if not report["results"] and test_count is None:
            raise RuntimeError("No structured result or successful native test summary")
        if sha256(args.binary) != report["binary_sha256"]:
            raise RuntimeError("Binary changed during execution")
        report["status"] = "measured"
        report["stage"] = "Measurement complete; qualification pending"
    except BaseException as error:
        report["status"] = "invalid"
        report["stage"] = "Run invalid"
        report["error"] = f"{type(error).__name__}: {error}"
        try:
            report["child_cleanup"] = cleanup_child(proc)
        except Exception as cleanup_error:
            report["child_cleanup_error"] = str(cleanup_error)
    finally:
        if reader:
            reader.join(timeout=3)
        if proc and proc.stdout:
            proc.stdout.close()
        report["finished_at"] = now()
        report["telemetry_after"] = telemetry()
        report["stdout_sha256"] = sha256(raw_log)
        atomic_json(run_dir / "report.json", report)
        try:
            evidence = copy_evidence(run_dir)
            update_dashboard(report, evidence)
        except Exception as error:
            report["status"] = "invalid"
            report["stage"] = "Run invalid: evidence/status publication failed"
            report["publication_error"] = str(error)
            atomic_json(run_dir / "report.json", report)
            try:
                copy_evidence(run_dir)
                update_dashboard(report)
            except Exception as retry_error:
                report["status_update_error"] = str(retry_error)
                atomic_json(run_dir / "report.json", report)
    print(json.dumps({"id": args.id, "status": report["status"], "report": str(run_dir / "report.json"),
                      "results": len(report["results"]), "error": report.get("error") or report.get("publication_error")}))
    return 0 if report["status"] == "measured" else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--kind", choices=("baseline", "candidate", "diagnostic", "validation"), required=True)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--build-manifest", type=Path, help="Build-time JSON provenance; binary_sha256 must match the supplied executable")
    parser.add_argument("--test", required=True, help="Rust test filter, or '*' for all tests")
    parser.add_argument("--not-ignored", action="store_true", help="Run ordinary tests instead of ignored benchmark tests")
    parser.add_argument("--fixture")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,95}", args.id) or args.id.upper().split('.')[0] in {"CON", "PRN", "AUX", "NUL", *[f"{p}{i}" for p in ("COM", "LPT") for i in range(1, 10)]}:
        parser.error("id must be a safe unique run-directory name")
    args.binary = args.binary.expanduser().resolve()
    if args.build_manifest:
        args.build_manifest = args.build_manifest.expanduser().resolve()
    RESEARCH.mkdir(parents=True, exist_ok=True)
    run_dir = RESEARCH / "runs" / args.id
    run_dir.parent.mkdir(parents=True, exist_ok=True)
    def interrupted(signum, _frame):
        raise InterruptedError(f"Signal {signum}")
    for name in ("SIGTERM", "SIGBREAK"):
        if hasattr(signal, name):
            signal.signal(getattr(signal, name), interrupted)
    try:
        with exclusive_lock(RESEARCH / "gpu-run.lock"):
            dashboard = json.loads(STATUS.read_text(encoding="utf-8-sig"))
            if any(r.get("id") == args.id for r in dashboard.get("experiments", [])):
                raise RuntimeError(f"Experiment ID already appears in dashboard: {args.id}")
            run_dir.mkdir(exist_ok=False)
            return run(args, run_dir)
    except (OSError, ValueError, RuntimeError, InterruptedError, KeyboardInterrupt) as error:
        print(f"Refused: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
