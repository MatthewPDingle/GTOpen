# Early usable preflop strategy publication

Implementation worktree: target/autoresearch/preflop-interactive-20260911, baseline ff54279. User live56708 is untouched.

## Minimum path

The tree already builds before solving. Main delay before navigation is GPU publication: the live counter advances every iteration, but CPU strategy/regret arenas remain at the last checkpoint until a full BR accuracy pass at iteration50. The frontend used that live counter to repeatedly request unchanged nodes.

Add early_preview=true as an explicit opt-in solve request, advertised by capabilities.early_preview_v1; absent remains false. The UI checkbox defaults unchecked pending quality review. It schedules real, transactional full-arena downloads after completed pass2 and every10 passes. Pass1 is excluded because initial accumulated strategy can still be uniform. Accuracy remains on the existing check_every schedule; CFR updates, model, samples, math, targets and native format are unchanged.

Each node/export response includes coherent publication metadata from the same solver lock: published_iteration, accuracy_iteration, optional measured gap and target, and a target-reached flag. The status counter remains live and the frontend refreshes only published changes. Preview labels explicitly distinguish unmeasured accuracy or an older measurement. Reaching the iteration limit is not labeled target convergence. An imported Setup spot retains the publication metadata and a visible source note; its ranges remain a fixed import while the preflop solve continues.

Native saves already require stopping. The check is repeated inside the solver lock to prevent a solve-start race. Stop finalization synchronizes and tags the actual native iteration; if final GPU sync fails, CPU arenas keep their prior snapshot and native iteration is restored to that tag. Saved snapshots do not store measured gap metadata, so reload labels accuracy as unmeasured rather than inventing a target claim.

Model/hero/lock changes invalidate the previous gap claim. Node queries and exports reject a traversed unlearned ancestor (previously only the current node's note guarded export), so uniform fallback at an unsolved earlier decision cannot silently become an exported reaching range.

## Files

- crates/server/src/main.rs: request/capability, publication schedule and state, coherent node/export metadata, stop/save guards.
- crates/server/src/preflop_preview_tests.rs: opt-in schema/cadence, state publication, accuracy invalidation, additive JSON.
- web/js/preflop_preview.js and tools/test_preflop_preview.mjs: pure status/display rules.
- web/js/preflop_lab.js, api.js, app.js and CSS: optional preview control, published-counter polling, honest labels, Setup provenance.

## Acceptance gates requested from parent

1. Compile server with/without GPU, run five focused Rust tests and current server suites. JS pure tests and syntax checks have passed locally.
2. On isolated tiny/large same-input cases, compare early_preview=false/true at identical final iteration: complete native arenas and policy comparator exact, same measured checkpoint gaps/EVs, no target change.
3. Observe first published iteration2, node response populated only for learned/model paths, BR accuracy_iteration remains null until normal check; query another branch while running.
4. Snapshot save rejected while running, stop/save/reload native exact with correct published tag; test loaded/frozen/hero/point-lock profiles and rejected unlearned ancestor export.
5. Browser inspect the checkbox, preview range/percentages, stale-gap caption, disabled unavailable exports, and imported Setup note. Verify maximum-iteration completion wording.

No speedup or early-policy quality claim yet. A two-iteration preview is a rough intermediate solver policy; the separate fast-model research must establish any stronger quality/speed claims. Extra full-arena downloads have a throughput cost that must be measured. More ambitious per-node GPU row reads or construction-only inferred ranges are outside this bounded path.

## Explicit fresh-build model selector

The server additionally accepts the strict query `multiway_model=coupled_preview64_v1` on `/api/preflop/spot`. Absent or `coupled_deck_v1` keeps the reference game. Unknown models (including32/legacy fresh modes), duplicate model keys and unknown query fields fail before any stop/session/cache access. The posted JSON config stays unchanged. The solver's native model setter runs only on the newly constructed zero-iteration game. Loaded saves and RE-SOLVE keep their native model.

The compact UI selector defaults Reference; Fast estimate (experimental) is enabled only by explicit server capability. Changing it on a built game announces that it affects the next BUILD GAME; RE-SOLVE uses the active native model and does not rebuild merely because the dropdown differs. Fast active games automatically opt into early publication. Node/export publication metadata includes the active model ID; fast Preview/Target labels explicitly say Reference error not measured, including the imported Setup note.

Two additional Rust tests cover strict query parsing and invalid-model rejection against a deliberately poisoned session sentinel, proving validation returns before entering the stop/session path. Pure JS tests cover query URL allowlist and fast-model provenance labels. Those JS tests pass. Root owns the64-particle payoff/GPU implementation and quality validation; this selector is experimental and does not certify its quality.
