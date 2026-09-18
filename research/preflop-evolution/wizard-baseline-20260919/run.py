"""Isolated GPU baseline. Never sends a mutating request to production."""
import hashlib
import json
from pathlib import Path
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = "http://127.0.0.1:56710/api/preflop/"
PRODUCTION = "http://127.0.0.1:56708/api/preflop/"
SAVE = "wizard-nl25-baseline-20260919"


def dump(name, data):
    path = OUT / name
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")
    temp.replace(path)


def request(endpoint, data=None, production=False):
    if production and data is not None:
        raise ValueError("Production writes forbidden")
    url = (PRODUCTION if production else BASE) + endpoint
    body = None if data is None else json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as response:
        return json.load(response)


def configuration():
    cfg = json.loads((ROOT / "research/preflop-evolution/continuation/balanced-sb05-20260915/fixtures.json").read_text())["config"]
    cfg.update(rake_pct=4, rake_cap=6, max_raises=4, allin_threshold=.4)
    # Wizard's observed original opener 4-bets 18 -> 45; cold IP 4-bets
    # are 18 -> 40.5, and blind cold 4-bets are 18 -> 45.
    cfg["fourbet_mults_by_seat"] = [[2.5], [2.5], [2.25], [2.25], [2.25], [2.25], [2.5], [2.5]]
    return cfg


CASES = {
    "nl25-utg-open": ([], "UTG1"),
    "nl25-lj-vs-utg": ([1], "MP"),
    "nl25-sb-vs-utg": ([1, 0, 0, 0, 0], "SB"),
    "nl25-bb-vs-utg": ([1, 0, 0, 0, 0, 0], "BB"),
    "nl25-str-vs-utg": ([1, 0, 0, 0, 0, 0, 0], "UTG"),
    "nl25-utg-vs-lj-3bet": ([1, 2, 0, 0, 0, 0, 0, 0], "UTG1"),
}


def collect(prefix):
    nodes = {}
    for key, (path, actor) in CASES.items():
        node = request("node", {"path": path})
        assert node["actor_pos"] == actor, (key, node.get("actor_pos"))
        nodes[key] = node
    dump(prefix + "-nodes.json", nodes)
    return nodes


def solve(settings, prefix):
    started = time.perf_counter()
    request("solve", settings)
    history = []
    while True:
        status = request("status")
        status["wall_seconds"] = time.perf_counter() - started
        history.append(status)
        dump(prefix + "-progress.json", history)
        if status["state"] != "running":
            break
        if status.get("gpu_note") and not status["gpu"]:
            request("stop", {})
            raise RuntimeError("GPU required for this study: " + status["gpu_note"])
        time.sleep(10)
    if status.get("error"):
        raise RuntimeError(status["error"])
    dump(prefix + "-status.json", status)
    print(prefix, status["iteration"], status["gap_total"], status["wall_seconds"], flush=True)
    collect(prefix)
    request("save", {"name": SAVE + "-" + prefix})
    return status


if __name__ == "__main__":
    if (OUT / "initial-status.json").exists():
        raise RuntimeError("Outputs already exist; do not overwrite a completed run")
    prod = request("session", production=True)
    dump("production-before.json", prod)
    cfg = configuration()
    dump("config.json", cfg)
    dump("provenance.json", {
        "source_head": "fd7c2b27", "binary": "target/release/gto-server.exe",
        "binary_sha256": hashlib.sha256((ROOT / "target/release/gto-server.exe").read_bytes()).hexdigest(),
        "equity_sha256": hashlib.sha256((ROOT / "cache/preflop_eq169.bin").read_bytes()).hexdigest(),
        "realization_fit_sha256": hashlib.sha256((ROOT / "cache/realization_fit.json").read_bytes()).hexdigest(),
        "target_gap": .005, "iteration_limit": 3000, "check_every": 50,
        "refinement": "250 additional iterations, target disabled; check stability, not tuning",
        "settings_match": "Inspected stakes/posts/first actions only; known downstream differences remain",
    })
    dump("estimate.json", request("estimate", cfg))
    dump("build.json", request("spot", cfg))
    solve({"iterations": 3000, "check_every": 50, "target_gap": .005}, "initial")
    solve({"iterations": 250, "check_every": 50, "target_gap": 0}, "refined")
    dump("session.json", request("session"))
    prod_after = request("session", production=True)
    dump("production-after.json", prod_after)
    dump("production-preserved.json", {"same_session_response": prod == prod_after})
