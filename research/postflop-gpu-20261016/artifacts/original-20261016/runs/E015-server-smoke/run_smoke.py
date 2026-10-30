"""Isolated native API smoke; no disk saves or live-server mutations."""
import datetime as dt
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import socket
import subprocess
import time
import traceback
import urllib.request

ROOT = Path(r"S:\GTOpen-research\postflop-gpu-20261016")
OUT = Path(__file__).resolve().parent
APP = Path(r"X:\Dev\GTOpen")
BINARY = ROOT / "binaries/E015-gto-server.exe"
PORT = 43736
BASE = f"http://127.0.0.1:{PORT}"
LIVE = "http://127.0.0.1:43735"
spec = importlib.util.spec_from_file_location("runner", r"X:\Dev\GTOpen-gpu-research-20261016\tools\postflop_autoresearch.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def save(name, data):
    with (OUT / name).open("x", encoding="utf-8") as f:
        json.dump(data, f, indent=2, allow_nan=False)
        f.write("\n")


def request(path, body=None, base=BASE, timeout=10):
    if body is not None and base != BASE:
        raise RuntimeError("Mutations are restricted to the isolated server")
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(base + path, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.load(response)


def live_state():
    return {path: request(path, base=LIVE) for path in (
        "/api/status", "/api/preflop/status", "/api/reports/status")}


def port_free():
    with socket.socket() as probe:
        probe.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        probe.bind(("127.0.0.1", PORT))


def finite_tree(value):
    if isinstance(value, float):
        assert math.isfinite(value), value
    elif isinstance(value, dict):
        for child in value.values():
            finite_tree(child)
    elif isinstance(value, list):
        for child in value:
            finite_tree(child)


def check_node(node):
    finite_tree(node)
    assert node["node_type"] == "action", node["node_type"]
    assert len(node["board"]) == 5
    assert node["actions"] and len(node["players"]) == 2
    actor = node["player"]
    checked = 0
    max_sum_error = 0.0
    for player in node["players"]:
        assert player["hands"]
        for hand in player["hands"]:
            if hand["reach"] > 0 and hand["valid"] > 0:
                assert isinstance(hand["ev"], (int, float)) and math.isfinite(hand["ev"])
                assert isinstance(hand["eq"], (int, float)) and math.isfinite(hand["eq"])
    for hand in node["players"][actor]["hands"]:
        strategy = hand["strategy"]
        assert len(strategy) == len(node["actions"])
        assert all(-1e-7 <= x <= 1.0000001 for x in strategy)
        delta = abs(sum(strategy) - 1)
        assert delta < 1e-5, delta
        max_sum_error = max(max_sum_error, delta)
        checked += 1
    return {"acting_hands_checked": checked, "max_strategy_sum_error": max_sum_error,
            "actions": [a["label"] for a in node["actions"]], "player": actor}


def main():
    result = {"started_at": now(), "passed": False, "binary": str(BINARY),
              "binary_sha256": hashlib.sha256(BINARY.read_bytes()).hexdigest(),
              "port": PORT, "working_directory": str(APP),
              "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=APP, text=True).strip(),
              "scope": "Isolated API correctness smoke; not a performance qualification"}
    owned = None
    with runner.exclusive_lock(ROOT / "gpu-run.lock"):
        try:
            port_free()
            before = live_state()
            runner.refuse_active(before)
            save("live-before.json", before)
            env = os.environ.copy()
            env.update(PORT=str(PORT), SOLVER_GPU="1", SOLVER_COMPRESS="1")
            env["PATH"] = str(APP / ".cuda-nvrtc/nvidia/cuda_nvrtc/bin") + os.pathsep + env.get("PATH", "")
            with (OUT / "stdout.log").open("x", encoding="utf-8") as stdout, (OUT / "stderr.log").open("x", encoding="utf-8") as stderr:
                owned = subprocess.Popen([str(BINARY)], cwd=APP, env=env, stdout=stdout, stderr=stderr,
                                         creationflags=subprocess.CREATE_NO_WINDOW)
            result["owned_pid"] = owned.pid
            (OUT / "server.pid").write_text(str(owned.pid), encoding="ascii")
            save("launch.json", result)
            deadline = time.monotonic() + 60
            while True:
                assert owned.poll() is None, "Owned test server exited before readiness"
                try:
                    initial = request("/api/status", timeout=2)
                    break
                except (OSError, TimeoutError):
                    if time.monotonic() > deadline:
                        raise TimeoutError("Readiness exceeded 60 seconds")
                    time.sleep(.1)
            assert initial["state"] == "idle" and initial["tree"] is None
            listener_pid = subprocess.check_output([
                "powershell.exe", "-NoProfile", "-Command",
                "Get-NetTCPConnection -LocalPort 43736 -State Listen | Select-Object -ExpandProperty OwningProcess"
            ], text=True, creationflags=subprocess.CREATE_NO_WINDOW).strip()
            assert listener_pid == str(owned.pid), (listener_pid, owned.pid)
            result["listener_owner_verified"] = True
            save("initial-status.json", initial)
            size = {"bet": "50", "raise": "2.5x", "donk": ""}
            spot = {"board": "Ks7h2dQhTc", "range_oop": "AA,KK,QQ,JJ,TT,AKs,AQs",
                    "range_ip": "AA,QQ,JJ,99,AJs,KQs", "starting_pot": 20,
                    "effective_stack": 100, "rake_pct": 0, "rake_cap": 0,
                    "add_allin": False, "max_raises": 2,
                    "oop": [size, size, size], "ip": [size, size, size]}
            save("spot-request.json", spot)
            tree = request("/api/spot", spot, timeout=30)
            save("tree.json", tree)
            solve = {"max_iterations": 100, "target_exploit_pct": 0, "check_every": 100, "algorithm": "dcfr"}
            save("solve-request.json", solve)
            save("solve-response.json", request("/api/solve", solve))
            deadline = time.monotonic() + 120
            polls = []
            while True:
                status = request("/api/status")
                polls.append({"at": now(), "status": status})
                if status["state"] != "running":
                    break
                if time.monotonic() > deadline:
                    raise TimeoutError("GPU solve exceeded 120 seconds")
                time.sleep(.1)
            save("status-polls.json", polls)
            save("final-status.json", status)
            finite_tree(status)
            assert status["state"] == "done", status
            assert status["iteration"] == 100, status
            assert status["gpu"] is True, status
            assert not status["error"] and not status["gpu_note"], status
            for key in ("exploit_chips", "exploit_pct", "elapsed_secs"):
                assert isinstance(status[key], (int, float)) and math.isfinite(status[key]), key
            node = request("/api/node", {"path": []}, timeout=30)
            save("root-node.json", node)
            result["root_checks"] = check_node(node)
            child = request("/api/node", {"path": [{"type": "action", "index": 0}]}, timeout=30)
            save("check-child-node.json", child)
            result["child_checks"] = check_node(child)
            after = live_state()
            save("live-after.json", after)
            result["live_api_unchanged"] = before == after
            assert result["live_api_unchanged"], "Live API state changed during isolated smoke"
            result["final_status"] = status
            result["passed"] = True
        except BaseException as exc:
            result["error"] = repr(exc)
            result["traceback"] = traceback.format_exc()
        finally:
            if owned is not None:
                if owned.poll() is None:
                    owned.terminate()
                owned.wait(timeout=10)
                result["owned_process_exit_code"] = owned.returncode
                result["owned_process_stopped"] = owned.poll() is not None
            try:
                port_free()
                result["test_port_released"] = True
            except OSError as exc:
                result["test_port_released"] = False
                result["port_check_error"] = repr(exc)
                result["passed"] = False
            result["finished_at"] = now()
            save("result.json", result)
    print(json.dumps({key: result.get(key) for key in ("passed", "owned_pid", "binary_sha256", "error", "owned_process_stopped", "test_port_released", "live_api_unchanged")}), flush=True)
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
