# Exact early publication: curated production integration review

Source-only review, main `be04cd1` versus lab `6a7b484` (build J). Read `AGENTS.md`. No build, hardware test, app mutation or deployment performed by this reviewer. Main may advance; recheck its implementation diff before applying this checklist.

## Recommended scope

Integrate early **publication of the unchanged full-reference solve**, detached GPU computation, and stop/error lifecycle hardening. This improves first strategy access and navigation; it does not establish that the early strategy is accurate. Keep the same default `coupled_deck_v1`, pairwise cache, realization fit, solve target and accuracy cadence. API `early_preview` remains opt-in/default false; the capability-gated Lab checkbox can default checked as in `cfbdb8e` once paired exactness/latency qualification passes.

Do not merge the research branch wholesale. The initial publication commit `5ee500a` bundles quality research; `43200db` bundles64-sample model changes. Use curated file/hunk integration. `8c37f18` supplies detached snapshot publication and `6a7b484` adds lifecycle finalization. The latter commits require the earlier publication helpers/status fields; they are not independent cherry-picks onto unmodified main.

## Minimal production file set

| File | Include | Exclude or adapt |
|---|---|---|
| `crates/server/src/main.rs` | Publication/accuracy metadata, strict `early_preview` request field, publication cadence, coherent GPU transaction helper, private device iteration counter, unlocked device iterate/accuracy work, generation-correct fallback, terminal cancellation/accuracy finalizer, node/export publication metadata, load/table/HERO/lock accuracy invalidation, early-preview capability | Do not expose compressed models. If retaining strict fresh-build query validation, accept only `coupled_deck_v1` and reject64/32/128 before stopping the session. Capabilities advertise only Reference. Keep JSON config unchanged. |
| `crates/server/src/preflop_preview_tests.rs` | Cadence, coherent publication, failure retention, running mutation guards, generation labels, stop/error waiting-reader tests, normal completion | Adjust fresh-build tests to reject all research models while accepting Reference. Keep the poisoned-session rejection sentinel. |
| `crates/solver/src/preflop/gpu.rs` | Only `try_iterate_counter` extraction and the existing `try_iterate` adapter; exact detached/host/stop/resume test | Keep production fixed1024 particle sizing/planning unchanged. Restrict new detached test model loop to Reference (and optionally existing legacy separately); do not import references to absent preview constants. No sample-count/planner/preview test hunks needed. |
| `web/js/preflop_lab.js` | Capability-gated checked early-preview checkbox, publication-based refreshing, displayed/measured iteration labels, target-vs-limit wording, approximation banner, export guard/label | Remove the Multiway-values selector, compressed-model choice state, query selection and automatic fast-mode override. Default full Reference alone is insufficient if capability enables the experimental option. |
| `web/js/preflop_preview.js` | Pure publication key/iteration/label/completion helpers | No callable fresh-build helper selecting compressed models. Experimental-name recognition can remain defensive labeling only; it must not enable creation or silently reinterpret a loaded save. |
| `web/js/api.js` | Capability request wrapper | Preserve existing `pfBuild(cfg)` URL/body; no model-selection import or query is required for exact early publication. |
| `web/js/app.js`, `web/css/app.css` | Carry preflop preview provenance into Setup and style its banner/checkbox | No experimental selector styling needed. |
| `tools/test_preflop_preview.mjs` | Publication/helper tests, stale accuracy, target/limit, opt-in compatibility | Adapt any fresh-model URL tests to production's Reference-only contract. |

Keep main's `crates/solver/src/preflop/mod.rs`, `multiway.rs`, `save.rs`, `Cargo.toml`, CUDA kernel source and native format unchanged. Do not import research quality/warmstart/conditional modules or their module registrations into the minimal production build. Their tools/results can remain research artifacts, separate from production implementation. Existing main save-model validation then continues to reject unsupported research native saves rather than silently resuming them as Reference. If later supporting research-save loading is desired, that requires a separate reviewed opt-in model feature, not this publication integration.

The main GPU already has transactional pinned-buffer download support; its ownership/staging is unchanged by the minimal `8c37f18` extraction. Copying all of lab `gpu.rs` would unnecessarily import variable-particle memory-plan changes and model tests. Curated integration should have no changed payoff arithmetic, sample corpus, precision, batch grouping or discount schedule.

## Final qualification before installation

1. Inspect the resulting diff and prove model/kernel/cache/native-schema files remain unchanged. Pin curated source and executable hashes; the lab J hash does not identify a new curated binary.
2. Run server publication/lifecycle tests and JS helper tests. Verify both GPU and non-GPU builds compile. Suggested commands: `cargo test --release -p server preflop_preview_tests -- --test-threads=1`; `node tools/test_preflop_preview.mjs`.
3. Complete AGENTS-required appropriate solver suites: `cargo test --release -p solver`; `cargo test --release -p solver --features gpu --test gpu --test preflop_gpu -- --test-threads=1`. Run the focused detached exactness test on the curated code. Root owns scheduling and deciding which already-completed unchanged suites need repeating.
4. Retain paired API-c evidence at actual20,000-sample pairwise cache, exact input/fit and GPU budget. Require uninterrupted Reference control/preview native arenas and final metadata to match exactly; report first published/usable response latency separately from solve quality and total solve duration. API-a/b/c evidence is version-specific: do not attribute J stop hardening to the earlier c frozen binary.
5. Qualify final curated runtime on a small isolated API case: read nodes during compute; reject table/HERO/lock/evaluate/save while running; stop, immediately evaluate real values, save/reload exact native state, preserve counter but clear accuracy after interrupted work; resume correctly. Check invalid compressed-model request causes no session stop/replacement. No real-server writes during qualification.
6. Browser smoke: early checkbox capability fallback, zero/unlearned suppression, real readable preview, measured-vs-displayed iteration, target versus limit, stop/error note, retained Setup export provenance, and absence of experimental model controls. A small gap or completed iteration2 is not a quality claim.

## Session-preserving installation gate

Wait for all owned qualification work and any user solves/reports to finish. Inspect current live sessions afresh; do not reuse earlier iteration/board assumptions. Follow AGENTS's existing desktop-maintenance authorization: create unique backups of both sessions, record current config/model/profiles/locks/board and native iteration, verify target process identity and executable hash, stage and smoke-test an isolated hidden child, then switch the owned runtime and restore both exact sessions. Preserve rollback executable and native backups. Confirm restored native semantics and latest user state. Root owns this process; this checklist neither launches nor claims deployment.


## Implemented curated source handoff

Commit **`53ce9dec08de9fa2f93f246d7f5efcccc8c22c68`**, branch `codex/preflop-interactive-production-20260911`, base main `be04cd171403c325cccead2c3002a9f61f737801`. Isolated worktree: `T:/Dev/GTOpen/target/autoresearch/preflop-interactive-production-20260911`. No main/lab/live session changes, builds, GPU execution, deployment or push were performed by this integration agent.

Changed files:

- `crates/server/src/main.rs`
- `crates/server/src/preflop_preview_tests.rs`
- `crates/solver/src/preflop/gpu.rs`
- `tools/test_preflop_preview.mjs`
- `web/css/app.css`
- `web/js/api.js`
- `web/js/app.js`
- `web/js/preflop_lab.js`
- `web/js/preflop_preview.js`


Implementation follows the curated scope above. Server accepts only Reference in the strict optional fresh-build query and advertises no compressed-model capability. Frontend `pfBuild` retains its original no-query URL, and all experimental model selectors/helpers are omitted. Existing unsupported research-save rejection remains intact because native/model source files are unchanged. Canonical content hashes of solver `mod.rs`, `multiway.rs`, `save.rs`, `Cargo.toml` and `kernels.cu` were checked against the base commit and matched.

The early preview checkbox is checked by default but disabled until explicit `early_preview_v1 === true` capability support. The shared request helper strips unsupported/stale preview fields and never mutates caller options. Both the running generation and its measured accuracy remain visible. Export provenance explicitly warns that imported ranges remain fixed while the preflop solve continues. The publication badge now sits in a separate full-width compact block above the actor/evidence row; that row has flexible wrapping for the reported1280px layout. Root should visually verify it with the final full-reference fixture; this agent inspected the prior screenshot and made source changes only.

Checks executed here: `node tools/test_preflop_preview.mjs`, JS syntax checks for `preflop_lab.js`, `app.js` and `api.js`, and staged `git diff --check`; all passed. The JS tests cover capability absence/false/malformed values, no unsupported request fields, opt-in behavior, nonmutating options, stale accuracy labels, target-versus-limit, and exported preview provenance. Rust tests were added but not compiled or run by this agent.

Root's next commands, serialized with the research queue:

```
cargo test --release -p server preflop_preview_tests -- --test-threads=1
cargo test --release -p server --features gpu preflop_preview_tests -- --test-threads=1
cargo test --release -p solver --features gpu detached_iterations_preserve_exact_trajectory_stale_host_stop_and_resume -- --test-threads=1
```

Then apply the appropriate broader AGENTS suites, build and freeze the actual curated runtime, perform final Reference-only API/lifecycle and1280px browser smoke, and only then follow the session-preserving installation gate. The production detached test intentionally exercises only the existing full-reference model. The server tests include Reference-only capability/query gates, rejection before even accessing a poisoned session, transactional snapshot publication, running-state guards, and real canceled-versus-noncanceled evaluation under a waiting reader after stop/error completion.
