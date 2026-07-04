# TODO

Work queue for FREEPIO. Items are written so a fresh contributor (human or
Claude) can execute them without prior context. Read `README.md` first for
the architecture; run `cargo test --release -p solver` (all green, ~5 min on
a laptop) before and after any change.

---

## 1. M5 — Calibrated equity-realization model (the big one)

**Goal.** Replace the hand-blind heuristic R in the Preflop Lab with factors
*measured from this engine's own postflop solves*, making preflop output
empirically grounded. Design agreed 2026-07-04.

**Background / current state.**
- The Preflop Lab (`crates/solver/src/preflop/`) prices flop terminals as
  `share = pot × multiway_equity × R`. R lives in
  `PreflopSolver::realization_weights()` (`preflop/mod.rs`):
  `R = 1 + 0.16 × pos_frac × min(SPR,8)/8`, pos_frac ∈ [-0.5, +0.5] by
  postflop acting order. Class-independent — 76s and Q2o get the same R.
  Selected by `PreflopConfig.realization` (serde default `"static"`;
  `"raw"` = R≡1 also supported). This makes the model too fond of offsuit
  junk and too cool on suited/connected playability hands.
- The postflop solver already exposes everything needed to MEASURE true
  realization: per-hand `ev` and `eq` at any node via
  `Solver::node_view()` (`query.rs`, `HandView.ev/.eq`, pot-share
  convention: EV_OOP + EV_IP = pot). Observed realization for hand h at the
  root of a solved postflop spot is simply
  `R_obs(h) = ev(h) / (pot × eq(h))`   (guard eq ≈ 0).
- Batch solving exists: `solve-cli batch spot.json boards.txt [iters]
  [target]` (`crates/solver/src/bin/solve_cli.rs`) writes
  `batch_results.json`; ~10–15 s/board on an RTX 3090, minutes/board on CPU.
- Spot inputs should come from real Preflop Lab exports
  (`POST /api/preflop/export {path}` → ranges/pot/eff-stack), so the fit
  covers the spots actually studied.

**Plan.**

*Phase A — observation extraction (laptop-friendly, ~1 session).*
Extend batch mode (or add `solve-cli realization <spot.json> <boards>`)
to emit, per board × player × 169-class, one JSON line:
`{board, player, pos_frac, spr, n_players: 2, class, reach, eq, ev, r_obs}`.
Aggregate combos→class with reach weighting (see `cellAgg` in
`web/js/browse.js` for the convention). Skip classes with reach < ~1% of the
class max (noise). Output: `realization_obs.jsonl`. SPR = eff_stack/pot at
the flop root. Include the tree-size config in a header line — R is
conditional on the bet-size menu used; calibrate with the menus you study.

*Phase B — data generation (desktop 3090, 1–2 overnights, no engineering).*
~20 exported spot configs (BTNvBB SRP, BBvUTG limped, 3-bet pots, lab-line
exports at several SPRs) × ~100-flop subset each ≈ 2,000 solves ≈ 7–8 GPU-h.
Pilot first: ~50 solves on CPU to validate the pipeline end to end.

*Phase C — fitting (~1 session).* Small weighted least-squares fit (no ML
stack needed; a ~200-line Rust or Python script): predict `r_obs` from
`(pos_frac, spr_bucket[≈6], class features: pair?, suited?, gap,
high_rank)` with reach×pot weights. Deliverable: a small table file, e.g.
`cache/realization_fit.json`. Sanity: R rises with pos_frac, spreads with
SPR, suited/connected > offsuit-junk at equal equity.

*Phase D — integration + validation (~1 session).*
- `realization: "calibrated"` in `PreflopConfig`: load the fit at solver
  construction (fall back to `"static"` with a warning if the file is
  missing). NOTE: R becomes class-dependent → `terminal_value()` must apply
  R per class h, not per seat only (today `nd.r[p]` is a per-seat scalar
  computed at build time; move the class-dependent part into the h-loop or
  precompute a per-seat 169-vector at build).
- Multiway stays heuristic (postflop engine is HU-only, so 3+-way R is
  unmeasurable): keep the positional shape, state the limitation in the UI.
- Expose raw/static/calibrated as a dropdown in the lab config panel
  (`web/js/preflop_lab.js` `config()` currently hardcodes `'static'`).
- Validation: HU push/fold anchors must not move (all-in terminals bypass
  R); re-run the BB-defend-vs-2.5x threshold example and report before/after
  vs GTO Wizard's BB defend range; add a regression test asserting the
  calibrated table's monotonicities.
- Optional round 2: re-export lab spots under calibrated R and refit once
  (fixed-point loop; expected to settle immediately — R shifts thresholds
  by ~1–2 equity points).

**Effort.** ~2–3 sessions of engineering + overnight desktop compute.

---

## 2. Raw/static realization toggle in the lab UI (tiny)

`web/js/preflop_lab.js` `config()` hardcodes `realization: 'static'`. Add a
select (static / raw — later calibrated, see item 1) so model sensitivity
can be A/B'd from the UI. If a decision survives both, the model isn't
deciding it. ~20 lines (config field, dropdown in `index.html` view-preflop
panel, els wiring in `app.js`).

## 3. Tier 2 — heads-up full-game preflop solver (desktop-class project)

True preflop solving for 2 players (SB vs BB): preflop street + flop chance
node fanning into a weighted canonical-flop subset (~50–95 boards), each
continuing into deliberately small postflop trees, solved as ONE game by the
existing 2-player DCFR engine (`cfr.rs`) — all convergence guarantees hold.
This is PioSolver's preflop module rebuilt on freepio. Blind-vs-blind limp
trees at any sizing, exact (no realization model). Big lift: the tree
builder (`tree.rs`) assumes a fixed board; needs a preflop street + flop
chance layer, and memory planning (each flop subtree ≈ a current spot;
×95 boards → needs small per-street size menus + the 128 GB desktop).
Validate against item 1's data and published HU charts.

## 4. UI consolidation — Browse as the only screen (design agreed 2026-07-02)

SETUP → GTO Wizard-style modal (tabs: New spot / Library of saves via
`/api/saves`); SOLVE → header strip + collapsible convergence drawer
(header solve buttons already exist); tabs removed. Pure frontend. Phase 2:
merge the preflop study panel and PREFLOP LAB ribbon into Browse's ribbon.

## 5. Smaller items

- **Preflop CUDA: VALIDATE ON THE DESKTOP** — implemented 2026-07-04
  (`preflop/gpu.rs` + `preflop/kernels.cu`: level-synchronous CFR
  mirroring the CPU exactly; server falls back to CPU + system RAM when
  the game exceeds free VRAM or CUDA errors, mid-solve included) but
  written on a GPU-less laptop: the kernels have NEVER RUN. On the 3090
  box, before trusting GPU output, run
  `cargo test --release --features gpu --test preflop_gpu -- --test-threads=1`
  (CPU-vs-GPU strategy equivalence + push/fold anchors). NVRTC compiles
  kernels at runtime, so kernel syntax errors surface there as a
  "GPU unavailable" fallback note with the compiler message.
- **Multiway all-in equity refinement**: product approximation is slightly
  pessimistic 3+-way; for POT_SHARE terminals with everyone all-in, an
  on-demand Monte-Carlo 3-way table (cached like the pairwise one in
  `preflop/equity.rs`) would make jam-heavy multiway trees near-exact.
- **EV heatmap mode for the lab grid**: per-class EVs fall out of
  `PreflopSolver::traverse(mode=1)`; wire into `paintGrid` like Browse's EV
  mode.
- **EXPLOIT mode hands panel**: the per-combo side panel in Browse still
  shows current-strategy data in EXPLOIT mode; feed it the
  `/api/exploit` payload instead.
- **Unequal stacks in the Preflop Lab**: `PreflopConfig.stack` is a single
  value (no side pots by design). Support per-seat stacks + side-pot-aware
  terminals if short-stack study becomes interesting.
- **GTO Wizard range import**: paste-parse GTOW's copy format into the
  range editor (mostly compatible with the existing text syntax already).
