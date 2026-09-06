"""Cross-exploit study: how much EV does hero (BTN) lose by playing the
max-exploit strategy for player type A against a table of type B?

For each game and each type A (plus GTO = an unruled equilibrium):
  build tree -> villains = A on every seat but BTN -> solve N iterations
  -> hero's EV vs A (diagonal) -> for each B: swap villains to B keeping the
  learned sums (table keep_learned) -> /evaluate -> hero's EV vs B.
loss[A][B] = EV[B][B] - EV[A][B]  (bb/100, >= 0 up to solve noise)

Usage: python xev_study.py [iters] [game ...]   games: 2-2, 2-5
"""
import json, sys, time, urllib.request, os

BASE = "http://127.0.0.1:3737"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "xev_results.json")

def call(path, body=None):
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(BASE + path, data=data, method="POST" if data is not None else "GET",
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=1800) as r:
        return json.loads(r.read().decode())

POS8 = ["UTG", "UTG1", "MP", "HJ", "CO", "BTN", "SB", "BB"]
def cfg8(stack, opens, mults, rake_pct, rake_cap, allin=False):
    return dict(positions=POS8, stack=stack, posts=[0, 0, 0, 0, 0, 0, 0.5, 1.0], ante=0.0, limp=True,
                open_raises=opens, raise_mults=mults, max_raises=2, add_allin=allin, allin_threshold=0.85,
                rake_pct=rake_pct, rake_cap=rake_cap, no_flop_no_drop=True, realization="calibrated",
                call_only_seats=[], open_raises_by_seat=None, raise_mults_by_seat=None)
GAMES = {
    "2-2": ("8-max 150bb $2/2: limps, opens 7.5/10, 10% rake cap 8.5", cfg8(150, [7.5, 10.0], [2.0, 4.0], 10.0, 8.5)),
    "2-5": ("8-max 200bb $2/5: limps, opens 3/4, 5% rake cap 2.2", cfg8(200, [3.0, 4.0], [2.5, 4.0], 5.0, 2.2)),
}
HERO = POS8.index("BTN")

def wait_done():
    while True:
        st = call("/api/preflop/status")
        if st["state"] in ("done", "error", "stopped", ""):
            return st
        time.sleep(1.5)

def solve(iters, check):
    call("/api/preflop/solve", {"iterations": iters, "check_every": check, "target_gap": 0.0})
    st = wait_done()
    if st.get("error"):
        raise RuntimeError(st["error"])
    return st

def main():
    iters = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    games = sys.argv[2:] or list(GAMES)
    archs = [a for a in call("/api/preflop/archetypes") if a["name"].startswith("Data") and a["name"].count("·") == 1]
    types = [a["name"].split("·", 1)[1].strip() for a in archs]
    print("types:", types)
    results = json.load(open(OUT)) if os.path.exists(OUT) else {}
    for g in games:
        label, cfg = GAMES[g]
        print(f"\n=== {label} ===")
        built = call("/api/preflop/spot", cfg)
        print("  tree:", {k: built.get(k) for k in ("action_nodes", "arena_mb", "engine", "gpu")})
        solve(5, 5)  # the generator needs a solved baseline (iteration > 0)
        n = len(POS8)
        # profiles per type per seat (position-aware), generated once on the fresh tree
        profiles = {}
        for a, t in zip(archs, types):
            profiles[t] = {}
            for seat in range(n):
                if seat == HERO:
                    continue
                profiles[t][seat] = call("/api/preflop/generate", {"seat": seat, "stats": a["stats"], "name": t})["profile"]
        def table(villain_type, keep=False):
            seats = []
            for seat in range(n):
                if seat == HERO or villain_type is None:
                    seats.append({"frozen": False, "profile": None})
                else:
                    seats.append({"frozen": False, "profile": profiles[villain_type][seat]})
            call("/api/preflop/table", {"seats": seats, "keep_learned": keep})
        ev = {}     # ev[A][B]: hero strategy learned vs A, evaluated vs B (bb/hand)
        gaps = {}
        for A in ["GTO"] + types:
            t0 = time.time()
            call("/api/preflop/spot", cfg)            # fresh regrets for a fresh hero
            table(None if A == "GTO" else A)
            st = solve(iters * (2 if A == "GTO" else 1), 100)
            ev[A] = {}
            gaps[A] = st["gaps"][HERO]
            ev[A][A] = st["evs"][HERO]
            row = f"  hero vs {A:20s} solved {st['iteration']} it, hero gap {st['gaps'][HERO]:.4f}, EV vs self {100*st['evs'][HERO]:+.1f} bb/100 ({time.time()-t0:.0f}s) |"
            for B in types:
                if B == A:
                    continue
                table(B, keep=True)                    # swap villains, keep hero's learned strategy
                ev[A][B] = call("/api/preflop/evaluate")["evs"][HERO]
                row += f" vs {B.split()[0]} {100*ev[A][B]:+.1f}"
            print(row)
        results[g] = {"label": label, "hero": "BTN", "iters": iters, "types": types, "ev_bb_per_hand": ev, "hero_gap": gaps}
        json.dump(results, open(OUT, "w"), indent=1)
        # loss matrix
        print(f"\n  loss (bb/100) of playing the counter-strategy for ROW type against COLUMN type:")
        print("  " + " " * 20 + "".join(f"{B.split()[0]:>10s}" for B in types))
        for A in ["GTO"] + types:
            cells = []
            for B in types:
                best = ev[B][B]
                cells.append(f"{100*(best - ev[A][B]):10.1f}")
            print(f"  {A:20s}" + "".join(cells))
    print(f"\nwrote {OUT}")

if __name__ == "__main__":
    main()
