# AGENTS.md — working with GTOpen as a coding/analysis agent

GTOpen is a from-scratch NLHE solver: Rust workspace (`crates/solver` = CFR
engine + multiway Preflop Lab; `crates/server` = HTTP API that also serves the
`web/` UI). Read `README.md` for the architecture; this file is the agent
quickstart. Recent study outputs and a findings summary live in
`C:\Storage\dev\coinpoker\gtopen-studies\` (Windows) — read `FINDINGS.md` there
before redoing analysis that already exists.

## Build / run / test

```bash
cargo build --release            # CPU-only; GPU needs CUDA (not on this laptop)
./target/release/gto-server      # UI + API on http://127.0.0.1:3737 (run from repo root)
cargo test --release -p solver   # full suite, ~10 min on this laptop; keep green
```

- From Windows, the WSL server is reachable at `http://localhost:3737`.
  To start it from Windows: `wsl -d Ubuntu-22.04 -- bash -lc "cd ~/dev/gtopen && ./target/release/gto-server"`.
- This laptop: 8 solver threads, ~0.4–1.5 it/s on 0.5–1.5M-node preflop trees;
  a 400-iteration profile-exploit solve ≈ 3–10 min. Big trees may hit the
  dynamic RAM cap — set `PREFLOP_MAX_ARENA_MB=2600` when running batch studies
  (the dynamic cap never rebounds after a big session is freed; known issue).
- Only ONE preflop session lives at a time; building a new spot replaces it.
  Free a large session by building a tiny spot first, or restart the server.
- A cron autosyncs this repo to GitHub every 30 min (commits + pushes whatever
  is in the tree). Don't fight it; don't leave junk files in the repo.

## Preflop Lab HTTP API (the analysis workhorse)

All POST bodies/responses are JSON. Config shape (see `PreflopConfig` in
`crates/solver/src/preflop/mod.rs`):

```json
{"positions":["UTG","HJ","CO","BTN","SB","BB"],"stack":100.0,
 "posts":[0,0,0,0,0.5,1.0],"ante":0.0,"limp":true,
 "open_raises":[2.5],"raise_mults":[3.0],"max_raises":4,"add_allin":false,
 "rake_pct":5.0,"rake_cap":10.0,"no_flop_no_drop":true,
 "realization":"calibrated","call_only_seats":[],
 "open_raises_by_seat":null,"raise_mults_by_seat":null}
```

- `max_raises` counts ALL raises (open=1 … 5-bet=4). Re-raise TO = to_call ×
  mult, min-raise clamped; sizes ≥ 85% of stack become jams.
- Per-seat overrides: `open_raises_by_seat`/`raise_mults_by_seat` (len-6 lists
  of lists; empty inner list = use global). Lets one seat explore a size menu
  while others stay pinned. `call_only_seats` bans raising for listed seats.
- `realization`: "calibrated" (default, measured) / "static" (positional) /
  "raw". Calibrated embeds its training rake — the rake dial barely moves HU
  flop leaves under it (documented limitation).

Endpoints (prefix `/api/preflop/`): `estimate` (tree size preflight), `spot`
(build), `solve` `{"iterations":N}` (stops early at BR-gap target), `status`
(state/iteration/per-seat `gaps`+`evs` in bb/hand/`hero`/`frozen`), `stop`,
`node` `{"path":[i,j,...]}` (action indices; returns actor, actions+freqs,
`strategy` as na×169 action-major flat array, per-class reach), `generate`
`{"seat":i,"stats":{...},"name":"..."}` (stat-driven profile from the CURRENT
solved equilibrium — solve a baseline first; returns `profile` + `implied`
readback), `table` `{"seats":[{"frozen":bool,"profile":obj|null}...]}` (rule
seats; a table where all non-hero seats are ruled makes a plain solve = hero
max-exploit; 409 while running), `hero`, `lock`/`unlock`, `save`/`load`/`saves`
(named baselines — save solved baselines, reloading beats re-solving),
`export` (send a HU flop node to the postflop solver).

`HudStats` for `generate`: `vpip, pfr, threebet, fold_to_3bet, squeeze,
fourbet?, flatten` (naiveté 0..1), `raise_size` ("min"/"max"), and measured
overrides `cont_vs_raise?` / `cont_squeeze?` (use these — the VPIP-derived
blend can't express sticky pools). Class order for 169-vectors: index
`= lo*13+hi` off-diagonal suited above / offsuit below; see
`class_parts()` in `crates/solver/src/preflop/equity.rs`.

Archetypes (GET `/api/preflop/archetypes`) include measured CoinPoker types:
CP Pool (anon avg) 29/18/8.5, CP Reg, CP Sticky Limper (cont_vs_raise 75),
CP Aggro 3-Bettor.

## Postflop API (heads-up solver)

`/api/spot` (build; refuses over-budget trees), `/api/solve`, `/api/status`,
`/api/node` (per-hand strategy/EV/EQ; `valid` = blocker-adjusted opponent mass —
weight range aggregates by reach×valid or EV_OOP+EV_IP≠pot), `/api/exploit`
(best response), `/api/lock` (node locking), `/api/save`|`load`, `/api/runouts`,
`/api/reports/*` (batch flop reports). The web UI at :3737 drives all of it.

## The standard study recipe (used for everything in gtopen-studies)

1. Build the villain-realistic tree; solve a baseline (~400-500 iters); SAVE it.
2. `generate` per-seat profiles from the baseline (use per-seat measured stats —
   position-blind averages produce identical villains, a known trap).
3. `table` to rule all non-hero seats → `solve` (≈best response, fast) →
   read `status.evs[hero]` and walk `node` for ranges.
4. Iterate hero seats; reload the saved baseline before regenerating profiles.

Caveats to carry into any writeup: EVs vs frozen profiles are ceilings;
calibrated realization is pessimistic on no-initiative flatting (call ranges
are the soft numbers; folds and value-raises are robust); villain fold-vs-raise
is size-invariant per bucket (matches this pool's measured behavior, but is a
model property elsewhere).
