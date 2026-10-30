# AGENTS.md — working with GTOpen as a coding/analysis agent

GTOpen is a from-scratch NLHE solver: Rust workspace (`crates/solver` = CFR
engine + multiway Preflop Lab; `crates/server` = HTTP API that also serves the
`web/` UI). Read `README.md` for the architecture; this file is the agent
quickstart. Recent study outputs and a findings summary live in
`C:\Storage\dev\coinpoker\gtopen-studies\` (Windows) — read `FINDINGS.md` there
before redoing analysis that already exists.

## Current workspace (user cleanup, 2026-10-30)

- Keep one working checkout at `X:\Dev\GTOpen` and one local research data folder
  at `X:\Dev\GTOpen-research`. The running app uses the main checkout.
- Useful source, benchmark tools, the dashboard and bounded reports belong in Git.
  Raw dumps, saved research fixtures, build outputs and preserved checkout files
  stay in the research data folder. Do not upload raw dumps or commit runtime caches.
- The previous `GTOpen-fix` and `GTOpen-gpu-research-20261016` checkouts were
  preserved on GitHub before retirement. The unfinished adaptive-HERO changes
  are archived at `archive/unfinished-hero-fix-20261030`; they are not an accepted
  application fix. The active local and GitHub branch is `master`.
- Read `research/postflop-gpu-20261016/workspace-layout.json` before continuing
  GPU research. Historical inputs, hashes and absolute paths remain immutable.
  Do not rewrite frozen custody records to make an old run appear current.
- New bulk output goes to X:. Keep the old S: archive read-only and do not
  access the retired T: drive. These current rules supersede the historical
  storage and old desktop-path notes below. Research is stopped after E127;
  workspace cleanup does not resume experiments or change the accepted E080 solver.

## Build / run / test

```bash
cargo build --release -p server --features gpu   # the desktop: native Windows + CUDA (see README "Windows")
GTOpen.cmd                                       # Windows launcher: builds, puts nvrtc on PATH, serves :3737, opens the browser
cargo test --release -p solver                   # full suite; keep green
cargo test --release --features gpu --test gpu --test preflop_gpu -- --test-threads=1   # GPU equivalence suites
```

- Home desktop (2026-09): Windows 11, Ryzen 5950X (16 solver threads), 128 GB,
  RTX 3090 (24 GB). Repo at `T:\Dev\GTOpen`; nvrtc DLLs in `.cuda-nvrtc/`
  (pip wheel, gitignored). Everything runs on the GPU: postflop solves,
  reports, the Preflop Lab with calibrated realization, profiles/locks/hero.
  Current performance: `research/autoresearch/gpu-pass.md`. On the measured
  RTX 3090 cases, preflop 6/8 uses 503/1309 MB and compressed postflop
  rainbow/two-tone uses 5906/3624 MB. These are workload-specific device
  allocations; UI VRAM is a conservative estimate and the final plan may be
  smaller. Actual fit is checked at solve time; oversized or unavailable
  CUDA falls back to CPU and reports retain the chosen engine.
- Laptop notes (kept for the road): WSL server reachable at
  `http://localhost:3737` via `wsl -d Ubuntu-22.04 -- bash -lc "cd ~/dev/gtopen && ./target/release/gto-server"`;
  8 threads, ~0.4–1.5 it/s on 0.5–1.5M-node preflop trees; set
  `PREFLOP_MAX_ARENA_MB=2600` for batch studies (the dynamic cap never
  rebounds after a big session is freed; known issue).
- Only ONE preflop session lives at a time; building a new spot replaces it.
  Free a large session by building a tiny spot first, or restart the server.
- Desktop maintenance authorization (user, 2026-09-08): perform routine local
  rebuilds, server starts/restarts and session restoration without asking again.
  Preserve current work: wait for active solves, save both sessions, verify the
  target process and check restored results. This does not authorize bypassing
  tool/system restrictions; report a continuing block if no permitted route exists.
- The laptop had a cron autosyncing this repo to GitHub every 30 min; the
  desktop pushes by hand (SSH remote). If both machines are live, make sure
  the cron is off or it will fight the desktop's pushes.

## Preflop Lab HTTP API (the analysis workhorse)

All POST bodies/responses are JSON. Request bodies reject unknown keys with
a 422 (a misspelled field used to be silently defaulted into a different
game). Config shape (see `PreflopConfig` in
`crates/solver/src/preflop/mod.rs`):

```json
{"positions":["UTG","HJ","CO","BTN","SB","BB"],"stack":100.0,
 "posts":[0,0,0,0,0.5,1.0],"ante":0.0,"limp":true,
 "open_raises":[2.5],"raise_mults":[3.0],"max_raises":4,"add_allin":false,
 "rake_pct":5.0,"rake_cap":10.0,"no_flop_no_drop":true,
 "realization":"calibrated","call_only_seats":[],
 "open_raises_by_seat":null,"raise_mults_by_seat":null}
```

- The UI/scenario fields `smallBlind` and `bigBlind` are stake denominations;
  convert to `posts` in bb before calling the engine (2/2 = SB 1, BB 1;
  2/5 = SB 0.4, BB 1). API config remains normalized. Old saves retain their
  original posts. Call action `to` remains the total, while UI labels show
  the incremental call/completion, excluding antes.
- `max_raises` counts ALL raises (open=1 … 5-bet=4). Re-raise TO = to_call ×
  mult, min-raise clamped; sizes ≥ 85% of stack become jams.
- Per-seat overrides: `open_raises_by_seat`/`raise_mults_by_seat` (len-6 lists
  of lists; empty inner list = use global). Lets one seat explore a size menu
  while others stay pinned. `call_only_seats` bans raising for listed seats.
- `realization`: new UI scenarios use "balanced" (relative class priors,
  pot-conserving HU shares, explicit configured rake). It is not a newly
  trained rake-free model. "calibrated" retains embedded training rake;
  "static" (the API omission default) and "raw" retain legacy behavior.
  See `docs/preflop_balanced_model.md`. Optional `fourbet_mults` and
  `fourbet_mults_by_seat` split later raises from the 3-bet menu; omission
  retains the original all-round multiplier inheritance. These features
  save as v4, which older binaries refuse.
- New games use `coupled_deck_v1` for 3+ live-player leaves: 1,024 deterministic
  latent-strength samples (seed 90210), whole-pot shares net configured rake,
  no positional realization multiplier. This is not a shared physical deal;
  overlapping premium ranges still expose large card-removal errors. Do not
  claim full multiway postflop solving or exact equity. Legacy saves retain
  `legacy_product`; RE-SOLVE preserves that model. Build a fresh game to change
  models. V2 saves require model metadata and are refused by old binaries.

Endpoints (prefix `/api/preflop/`): `estimate` (tree size preflight), `spot`
(build), `solve` `{"iterations":N}` (stops early when `gap_total` — the BR
gaps summed over the seats still LEARNING; a frozen/ruled seat's gap is its
bleed and never converges — drops below `target_gap`), `status`
(state/iteration/per-seat `gaps`+`evs` in bb/hand/`hero`/`frozen`;
`realization_note` is non-empty when "calibrated" could not load its fit and
the HU game was priced with the static model; `multiway_equity_model` identifies
the active continuation version), `session` (GET: the live game —
config, seats, iteration, hero/frozen, state), `stop`,
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
`= hi*13+lo` for suited, `lo*13+hi` for offsuit, and `rank*14` for pairs; see
`class_parts()` in `crates/solver/src/preflop/equity.rs`.

Archetypes (GET `/api/preflop/archetypes`) include the built-in generated
ones and the measured "Data · <type>" entries from `cache/archetypes.json`
(seven preflop types × optional `· station` / `· folder` postflop
modifiers; see `docs/player_types.md`). `HudStats` also takes the first-in
rates `open_raise?` / `open_limp?` and the vs-limpers rates `iso_raise?` /
`limp_behind?` (percent); blank falls back to PFR and VPIP − PFR, which
over-limps regs. Range ORDER comes from `preflop/reference.rs` (a clean
9-max reference solve: open / call / 3-bet propensity per class, regenerate
with `cargo run --release -p solver --example reference_order`), blended
toward raw card appeal by naiveté — never from the current solve.

### Range Lab reference charts

The Preflop Lab shows the canonical charts from Pan's Range Lab trainer under
the solve grid (`web/js/rangelab_ref.js`, `crates/server/src/rangelab.rs`). The data
is private and is NEVER committed (this repo is public): the
server reads `data.js` / `cash-data.js` / crawl JSON from `cache/rangelab/`
(gitignored) and `../Range Lab/` (`X:\Dev\Range Lab`), or the `;`-separated
folders in `GTOPEN_RANGELAB_DIR`, and reloads when those files change.
Endpoints: GET `/api/preflop/rangelab` (files, games, open sizes/stages with
their depths), POST `rangelab/situations {tag, variant, depth}`, `rangelab/spot
{id}` (actions, `strategy` na×169 in GTOpen class order, `ev_loss` in bb,
`reach`), `rangelab/match {tag, players, line:["F","R",…], stack, open_to?}`
(same kind-only action history, then nearest open size and depth),
`rangelab/node {tag, variant, depth, path, extend?}` (the charts walked as a
preflop tree, shaped like `/api/preflop/node`; seats without a chart fold when
later charts assume it, `extend` follows those folds and returns the longer
`path`) and `rangelab/export {…, rake_pct, rake_cap}` (a heads-up flop in the
`/api/preflop/export` shape). The Preflop Lab's "Ranges from: Range Lab charts"
switch uses these instead of a build and solve. Charts are
8-max cash (10% live rake; straddle game), 9-max chip-EV and 8-max ICM
tournaments, so they are a shape reference, not the same game as a GTOpen solve.

## Postflop API (heads-up solver)

`/api/spot` (build; refuses over-budget trees), `/api/solve`, `/api/status`,
`/api/node` (per-hand strategy/EV/EQ; `valid` = blocker-adjusted opponent mass —
weight range aggregates by reach×valid or EV_OOP+EV_IP≠pot), `/api/exploit`
(best response), `/api/lock` (node locking), `/api/save`|`load`, `/api/runouts`,
`/api/reports/*` (batch flop reports; `/api/reports/lines {name, line}` reads a
finished report at any node — `a<i>` per action, `c` per any-card step). The
web UI at :3737 drives all of it.

## Full game (heads-up preflop to river, GPU)

`solver::fullgame` (feature `gpu`) solves SB vs BB from the preflop root to
the river as one CFR+ game over a weighted flop panel; `fullgame-cli` runs it
from a `FullGameConfig` JSON (`docs/fullgame/sb-vs-bb-100.json`). See
`docs/fullgame/README.md`. Continuations stay resident in VRAM, so only a few
flops fit with limps on; there are no server endpoints or saves yet.

## The standard study recipe (used for everything in gtopen-studies)

1. Build the villain-realistic tree; solve a baseline (~400-500 iters); SAVE it.
2. `generate` per-seat profiles from the baseline (use per-seat measured stats —
   position-blind averages produce identical villains, a known trap).
3. `table` to rule all non-hero seats → `solve` (≈best response, fast) →
   read `status.evs[hero]` and walk `node` for ranges.
4. Iterate hero seats; reload the saved baseline before regenerating profiles.

Caveats to carry into any writeup: EVs vs frozen profiles are ceilings;
calibrated HU realization is pessimistic on no-initiative flatting (call ranges
are the soft numbers; folds and value-raises are robust); ordinary villain fold-vs-raise remains fixed per bucket/band. New app-generated
profiles learn responses from 25% of stack, so keep HERO off for joint solves.
Adaptive-seat gaps respect their fixed actions; fully fixed/frozen gaps remain
bleed. Historical fully fixed results and old saves keep their original model.
See `docs/preflop_modeling_fix.md`; the Data sample is online, not live casino.


## Research storage

- Research storage (user, 2026-10-03): keep at least 50 GiB
  (53,687,091,200 bytes) free on T:. Prefer `S:\GTOpen-research` for new
  bulk research output. Check actual free space and conservative peak output
  reservations before admitting work; defer writes that would breach the T:
  reserve. Keep useful research and verify full copies before retiring the T:
  copies. Preserve frozen scientific inputs and record any relocation explicitly.


- Research relocation (user, 2026-10-05): all remaining T:\GTOpen-research
  data was checksum verified and relocated to S:\GTOpen-research. T:\GTOpen-research
  is now a compatibility junction; keep bulk research physically on S. Inventory
  S once, avoiding double counting through the T alias. Relocation identities
  are recorded in S:\GTOpen-research\T-TO-S-RELOCATION-20261005.json; strict
  frozen identity checks must handle them explicitly before future admission.
  This storage-only request does not authorize resuming stopped research.
