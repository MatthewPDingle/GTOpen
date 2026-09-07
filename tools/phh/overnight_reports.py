"""Overnight flop-report queue: the heads-up flop spots Matthew faces most,
with ranges from the preflop lab's max-exploit solves against the measured
player types, each run three ways across 184 flops — GTO postflop, villain
= station, villain = folder.

Per (game, villain type, hero seat): build the saved scenario, generate the type's
profiles on every seat but hero, solve hero (300 it, GPU), walk to each spot
node and export the two ranges + pot + stack; then queue the reports in
value order and poll each to completion. Reloads the saved lab session at
the end of preflop preparation (also on failure). Saved game files are never overwritten.

Usage: python -u tools/phh/overnight_reports.py [--games 2-2,2-5] [--flops 184]
"""
import json, sys, time, urllib.request, argparse, traceback, re, os, subprocess
from pathlib import Path
from contextlib import contextmanager, redirect_stdout, redirect_stderr
from datetime import datetime
from uuid import uuid4

BASE = "http://127.0.0.1:" + os.environ.get("PORT", "3737")

def call(path, body=None, timeout=3600):
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(BASE + path, data=data, method="POST" if data is not None else "GET",
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{path}: HTTP {e.code} {e.read().decode()[:300]}")

def log(msg):
    print(time.strftime("%H:%M:%S"), msg, flush=True)

POS8 = ["UTG", "UTG1", "MP", "HJ", "CO", "BTN", "SB", "BB"]
ROOT = Path(__file__).resolve().parents[2]
SETTINGS = ROOT / "saves/overnight/settings.json"


def scenario_config(scenario):
    """Use the same field conversion as the Preflop Lab setup form."""
    if scenario["players"] != 8:
        raise ValueError("The overnight spot recipes currently require eight seats")
    def nums(value):
        return [float(v.strip()) for v in str(value).split(",") if v.strip() and float(v) > 0]
    return dict(positions=POS8, posts=[0, 0, 0, 0, 0, 0, .5, 1],
                stack=scenario["stack"], ante=scenario["ante"], limp=scenario["limp"],
                open_raises=nums(scenario["opens"]), raise_mults=nums(scenario["mult"]),
                max_raises=scenario["maxRaises"], add_allin=scenario["allin"],
                rake_pct=scenario["rakePct"], rake_cap=scenario["rakeCap"],
                no_flop_no_drop=True, realization=scenario.get("realization", "calibrated"))


def saved_games(games):
    if os.name == "nt":
        subprocess.run(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                        str(ROOT / "tools/recover-scenarios.ps1")], check=True, stdout=sys.stderr)
    saved = call("/api/preflop/scenarios")
    choices = json.loads(SETTINGS.read_text(encoding="utf-8")) if SETTINGS.exists() else {}
    selected = {}
    for game in games:
        if game not in ORDER:
            raise ValueError(f"Unsupported game {game}")
        name = choices.get(game)
        matches = [s for s in saved if s["name"] == name] if name else [
            s for s in saved if re.search(r"(?<!\d)" + game.replace("-", r"[/\-]") + r"(?!\d)", s["name"])]
        if len(matches) != 1:
            raise ValueError(f"Expected one saved {game} scenario; found {len(matches)}. "
                             f"Select its exact name in {SETTINGS}. No solve has started.")
        selected[game] = (matches[0]["name"], scenario_config(matches[0]))
    return selected


@contextmanager
def preserve_lab(backup):
    # An unsolved but built lab is idle; only an absent session has an empty state.
    exists = bool(call("/api/preflop/status").get("state"))
    if exists:
        # A failed backup must stop the queue before the first replacement.
        call("/api/preflop/save", {"name": backup})
        log(f"Saved current lab as {backup}")
    try:
        yield
    finally:
        if exists:
            call("/api/preflop/load", {"name": backup})
            log(f"Restored lab from {backup}")


@contextmanager
def keep_awake():
    """Prevent automatic sleep while this queue is active; no power-plan edits."""
    if os.name == "nt":
        import ctypes
        power = ctypes.windll.kernel32.SetThreadExecutionState
        power.argtypes = [ctypes.c_uint]
        power.restype = ctypes.c_uint
        if not power(0x80000001):
            raise RuntimeError("Could not keep the computer awake for the overnight queue")
    try:
        yield
    finally:
        if os.name == "nt":
            power(0x80000000)


@contextmanager
def queue_lock():
    directory = ROOT / "saves/overnight"
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / "queue.lock").open("a+b") as f:
        if f.tell() == 0:
            f.write(b"0"); f.flush()
        f.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise RuntimeError("An overnight queue is already running") from exc
        yield
        # Closing the handle releases the lock, including after a crash.


STD = [{"bet": "33 75", "raise": "60", "donk": ""}, {"bet": "75", "raise": "60", "donk": ""}, {"bet": "75", "raise": "60", "donk": ""}]
FISH, TAG = "Loose-passive fish", "TAG"
F = "fold"; C = "call"; R = "raise_min"
fold_to = lambda seats: [(s, F) for s in seats]
# key, title, villain type, hero seat, path, villain side (0 OOP / 1 IP), preflop aggressor side
SPOTS = [
    ("A", "BTN iso-raises MP limper who calls", FISH, "BTN",
     fold_to(["UTG", "UTG1"]) + [("MP", C)] + fold_to(["HJ", "CO"]) + [("BTN", R)] + fold_to(["SB", "BB"]) + [("MP", C)], 0, 1),
    ("B", "BTN opens BB calls", FISH, "BTN",
     fold_to(["UTG", "UTG1", "MP", "HJ", "CO"]) + [("BTN", R), ("SB", F), ("BB", C)], 0, 1),
    ("D", "BTN opens hero BB calls", FISH, "BB",
     fold_to(["UTG", "UTG1", "MP", "HJ", "CO"]) + [("BTN", R), ("SB", F), ("BB", C)], 1, 1),
    ("E", "CO opens hero BTN calls", TAG, "BTN",
     fold_to(["UTG", "UTG1", "MP", "HJ"]) + [("CO", R), ("BTN", C)] + fold_to(["SB", "BB"]), 0, 0),
    ("C", "CO opens BTN 3-bets CO calls", FISH, "BTN",
     fold_to(["UTG", "UTG1", "MP", "HJ"]) + [("CO", R), ("BTN", R)] + fold_to(["SB", "BB"]) + [("CO", C)], 0, 1),
    ("F", "CO opens BTN 3-bets CO calls", TAG, "BTN",
     fold_to(["UTG", "UTG1", "MP", "HJ"]) + [("CO", R), ("BTN", R)] + fold_to(["SB", "BB"]) + [("CO", C)], 0, 1),
    ("G", "BTN opens BB calls", TAG, "BTN",
     fold_to(["UTG", "UTG1", "MP", "HJ", "CO"]) + [("BTN", R), ("SB", F), ("BB", C)], 0, 1),
    ("H", "BTN opens hero BB calls", TAG, "BB",
     fold_to(["UTG", "UTG1", "MP", "HJ", "CO"]) + [("BTN", R), ("SB", F), ("BB", C)], 1, 1),
]
ORDER = {"2-2": ["A", "B", "D", "E", "C", "F", "G", "H"], "2-5": ["A", "B", "D", "E"]}

def wait_lab_idle(max_s=3600):
    t0 = time.time()
    while time.time() - t0 < max_s:
        st = call("/api/preflop/status")
        if st["state"] != "running":
            return st
        time.sleep(10)
    raise RuntimeError("lab solve still running after an hour")

def solve(iters, check=100):
    call("/api/preflop/solve", {"iterations": iters, "check_every": check, "target_gap": 0.0})
    while True:
        st = call("/api/preflop/status")
        if st["state"] != "running":
            if st.get("error"):
                raise RuntimeError(st["error"])
            return st
        time.sleep(2)

def pick(view, want, seat):
    assert view["actor_pos"] == seat, f"expected {seat} to act, got {view['actor_pos']}"
    acts = view["actions"]
    if want == F:
        return next(i for i, a in enumerate(acts) if a["kind"] == "fold")
    if want == C:
        return next(i for i, a in enumerate(acts) if a["kind"] in ("call", "check"))
    raises = [(a["to"], i) for i, a in enumerate(acts) if a["kind"] == "raise"]
    return min(raises)[1]

def export_spot(path_spec):
    path = []
    view = call("/api/preflop/node", {"path": path})
    for seat, want in path_spec:
        path.append(pick(view, want, seat))
        view = call("/api/preflop/node", {"path": path})
    return call("/api/preflop/export", {"path": path})

def prepare_queue(args, games, selected, archs, run_id):
    def postflop(tname, mod):
        a = archs.get(f"Data · {tname} · {mod}") or archs[f"Data · {tname}"]
        return a["postflop"], a["name"]
    queue = []  # (name, body)
    for g in games:
        glabel, cfg = selected[g]
        spots = {k: s for s in SPOTS for k in [s[0]] if k in ORDER[g]}
        combos = []
        for k in ORDER[g]:
            s = spots[k]
            key = (s[2], s[3])
            if key not in combos:
                combos.append(key)
        exported = {}
        for (tname, hero) in combos:
            try:
                log(f"[{g}] table of {tname}, hero {hero}: build + generate + solve")
                built = call("/api/preflop/spot", cfg)
                solve(5, 5)
                hero_i = POS8.index(hero)
                seats = []
                for i, pos in enumerate(POS8):
                    if i == hero_i:
                        seats.append({"frozen": False, "profile": None})
                    else:
                        prof = call("/api/preflop/generate", {"seat": i, "stats": archs[f"Data · {tname}"]["stats"], "name": tname})["profile"]
                        seats.append({"frozen": False, "profile": prof})
                call("/api/preflop/table", {"seats": seats})
                st = solve(args.iters)
                log(f"    solved {st['iteration']} it, hero gap {st['gaps'][hero_i]:.4f}, hero EV {100*st['evs'][hero_i]:+.1f} bb/100")
                for k in ORDER[g]:
                    s = spots[k]
                    if (s[2], s[3]) != (tname, hero):
                        continue
                    ex = export_spot(s[4])
                    exported[k] = ex
                    log(f"    spot {k} {s[1]}: OOP {ex['oop_pos']} IP {ex['ip_pos']} pot {ex['pot_bb']:.1f} stack {ex['eff_stack_bb']:.1f} "
                        f"OOP range {len(ex['range_oop'].split(','))} classes, IP range {len(ex['range_ip'].split(','))} classes")
            except Exception as e:
                log(f"    FAILED: {e}")
                raise
        for k in ORDER[g]:
            if k not in exported:
                continue
            key, title, tname, hero, _, vside, aggr = spots[k]
            ex = exported[k]
            spot = {"board": "Ks7h2d", "range_oop": ex["range_oop"], "range_ip": ex["range_ip"],
                    "starting_pot": round(ex["pot_bb"], 2), "effective_stack": round(ex["eff_stack_bb"], 2),
                    "rake_pct": ex["rake_pct"], "rake_cap": ex["rake_cap"], "allin_threshold": 85.0,
                    "add_allin": False, "max_raises": 3, "oop": STD, "ip": STD}
            short = "fish" if tname == FISH else "TAG"
            base = f"{run_id} {glabel} {key} {title} vs {short}"
            queue.append((f"{base} - GTO postflop", {"name": f"{base} - GTO postflop", "spot": spot, "flops": args.flops, "max_iterations": 600, "target": 0.35}))
            for mod in ("station", "folder"):
                pf, aname = postflop(tname, mod)
                queue.append((f"{base} - {short} {mod}", {"name": f"{base} - {short} {mod}", "spot": spot, "flops": args.flops, "max_iterations": 600, "target": 0.35,
                              "villain": {"player": vside, "name": aname, "stats": pf, "aggressor": aggr}}))
    return queue


def run_reports(queue):
    log(f"{len(queue)} reports queued")
    failures = []
    for name, body in queue:
        t0 = time.monotonic()
        try:
            call("/api/reports/run", body)
            while True:
                st = call("/api/reports/status")
                if st.get("name") != name:
                    raise RuntimeError("Report ownership changed; stopping this queue")
                if not st.get("running"):
                    break
                time.sleep(15)
            report = call("/api/reports/get", {"name": name})
            if st.get("error") or not report.get("complete"):
                raise RuntimeError(st.get("error") or "Report stopped before completion")
            log(f"report done: {name} ({(time.monotonic()-t0)/60:.1f} min)")
        except Exception as exc:
            failures.append(f"{name}: {exc}")
            log(f"report FAILED: {name}: {exc}")
            # Do not launch another report after an unknown timeout/ownership change.
            current = call("/api/reports/status")
            if current.get("running") or current.get("name") != name:
                raise
    if failures:
        raise RuntimeError(f"{len(failures)} reports failed; see this run's log")


def main():
    ap = argparse.ArgumentParser(description="Run reports from the current saved scenarios")
    ap.add_argument("--games", default="2-2,2-5")
    ap.add_argument("--flops", type=int, default=184)
    ap.add_argument("--iters", type=int, default=300)
    ap.add_argument("--dry-run", action="store_true", help="Read/validate saved scenarios without changing sessions")
    args = ap.parse_args()
    if args.flops < 1 or args.iters < 1:
        ap.error("flops and iters must be positive")
    games = args.games.split(",")
    selected = saved_games(games)
    if args.dry_run:
        print(json.dumps(selected, indent=2))
        return
    run_id = datetime.now().strftime("overnight-%Y%m%d-%H%M%S-") + uuid4().hex[:6]
    directory = ROOT / "saves/overnight" / run_id
    with queue_lock(), keep_awake():
        directory.mkdir(parents=True)
        with (directory / "run.log").open("w", encoding="utf-8", buffering=1) as logfile:
            with redirect_stdout(logfile), redirect_stderr(logfile):
                try:
                    log(f"Starting {run_id}")
                    (directory / "scenarios.json").write_text(json.dumps(selected, indent=2), encoding="utf-8")
                    wait_lab_idle()
                    if call("/api/reports/status").get("running") or call("/api/status")["state"] == "running":
                        raise RuntimeError("Another solve/report is active; no sessions changed")
                    archs = {a["name"]: a for a in call("/api/preflop/archetypes")}
                    with preserve_lab(run_id + "-before"):
                        queue = prepare_queue(args, games, selected, archs, run_id)
                    (directory / "queue.json").write_text(json.dumps(queue, indent=2), encoding="utf-8")
                    run_reports(queue)
                    log("All reports completed successfully")
                    (directory / "complete.json").write_text(json.dumps({"reports": len(queue)}), encoding="utf-8")
                except BaseException:
                    traceback.print_exc()
                    raise


if __name__ == "__main__":
    main()
