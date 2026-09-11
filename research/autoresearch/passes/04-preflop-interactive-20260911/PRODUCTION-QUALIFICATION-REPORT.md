# Exact early-publication production qualification

**Status: compilation, selected tests, production API and private UI passed; session-preserving deployment completed.** All41 frozen test executables and the solver doctest invocation completed with exit0 at2026-09-11T02:30:48.975956Z. Actual counts are232 passed,0 failed,5 ignored and90 filtered. Zero-test binaries and the zero-doctest invocation are recorded, not counted as passing tests.

## Frozen candidate

| Item | Recorded value |
| --- | --- |
| Source commit | `53ce9dec08de9fa2f93f246d7f5efcccc8c22c68` |
| Production worktree | `T:/Dev/GTOpen/target/autoresearch/preflop-interactive-production-20260911` |
| Staged GPU runtime | `target/qualification/gto-server.exe` beneath that worktree |
| Runtime SHA256 | `7de6c8aaaef5daf840411218a27e13bfda41017571537fac26b76f3414f87bdc` |
| Build controller at preparation | Root-owned execution52749; completed exit0 |
| Build/test manifest | [Auditable summary](proposals/early-preview/production-qualification-a/summary.json) pins original manifest/result paths and SHA256 |
| Compiler-artifact/source provenance | Same summary retains compiler JSONL SHA/paths, exact commands and frozen artifact provenance |
| Final main integration commit | `5c978d6`, pushed; nine curated source blobs match53ce9de |
| Deployment and restore manifest | [Exact session-preserving deployment evidence](proposals/early-preview/production-qualification-a/deployment/summary.json) |

The counts/timings below were parsed from completed logs. The staged runtime and all41 executed frozen test EXE hashes were independently rechecked against the final records. Copied test logs total20,116bytes; the compact summary is90,272bytes. No binary or large Cargo JSONL was copied. CPU builds use the shared Cargo cache after GPU staging; the shared target's later EXE must not replace this qualified staged runtime.

Scope is exact full-reference early publication, detached GPU work with coherent host snapshots, lifecycle cancellation/accuracy hardening and corresponding UI. No reduced-particle model, conditional refinement or warmstart research feature is included. The nine-file curated patch applied cleanly in a read-only check against main9989fea; those paths' original blobs matched the curated parent exactly.

## Compilation and tests

| Gate | State at preparation | Evidence still required |
| --- | --- | --- |
| GPU server compile | PASS,110.860s | Completed compiler log/hash pinned in summary |
| GPU solver selected test compilation | PASS,73.828s | Frozen EXE hashes and compiler log pinned |
| GPU server test compilation | PASS,27.656s | Frozen EXE hash and compiler log pinned |
| Non-GPU solver library/bin/integration compilation | PASS,111.907s | Completed compile result |
| Non-GPU server test compilation | PASS,43.828s | Covers the non-GPU main cfg path |
| Detached GPU snapshot exactness test | PASS,1 test |81 unrelated GPU library tests filtered |
| GPU equivalence integration suites `gpu` and `preflop_gpu` | PASS,6 +13 tests | Actual preflop count13, correcting the earlier projected14 |
| GPU server publication/lifecycle tests | PASS,12 tests |9 unrelated server tests filtered |
| Full CPU solver library/bin/integration tests | PASS,181 tests;5 ignored | All selected binaries logged, including zero-test targets |
| CPU server tests | PASS,19 tests | Complete CPU server test executable |
| Solver doctests | PASS command,0 doctests | No doctest was present to execute |
| Frontend helper tests and syntax | PENDING final qualification linkage | Link exact-source checks |

A redundant standalone CPU runtime build is omitted: non-GPU server test compilation already exercises that cfg path. Full CPU tests and doctests remain required. The unchanged broad GPU H/I suite is prior supporting evidence, not a new run against this runtime; the targeted new test and both GPU integration suites are the current production gates.

## API and UI acceptance

| Gate | State | Required result |
| --- | --- | --- |
| Private-server ownership and cache identity | PASS | All3 cases use staged7de6c8… runtime;20,000-sample cache/header/fit unchanged through load/roundtrip/end; no live guard failures |
| Early publication disabled/enabled reference pair | PASS | Native header and both264,950,257-element arenas exact; whole native SHA6162be… matches golden; final gaps/EV/iteration metadata exact |
| Stop/cancel and coherent save/reload | PASS small lifecycle | Running evaluate rejected; stop178 clears accuracy and notes interrupted sweep; immediate evaluation gives nonzero summed gap0.00010788245; exact paused roundtrip then resume228 and roundtrip |
| Capability/model boundary | PASS | `early_preview_v1` true; only `coupled_deck_v1`; invalid queries preserve existing session |
| First published strategy / first accuracy timing | PASS availability measurement | First published305.360→12.234s; first export305.641→12.469s (24.512x earlier). Preview iteration2 accuracy unmeasured. Both stop50 at gap1.49551663, not target0.005 |
| 1280px private UI | PASS root browser review and screenshot inspection | Own readable publication row; checked early option/no experimental selector; full-model export source/fixed-range warning; zero console errors/warnings |
| Native session-preserving private restore smoke | PASS; live restore also PASS | Fresh preflop102/postflop210 headers and all arena hashes exact, no solve |

Research approximation results are separate. A learned snapshot at iteration2 means an available intermediate strategy; it is not a quality certificate, nor evidence of global or local convergence. Published iteration and measured-accuracy iteration must remain distinct in reporting.

## Final completion record (root fills after evidence exists)

- Completed build/test artifacts: [summary and all42 test/doctest logs](proposals/early-preview/production-qualification-a/README.md). Original result and manifest hashes, all47 job records and frozen artifact hashes are retained in the JSON summary.
- Production API: [compact validation including small lifecycle](proposals/early-preview/production-qualification-a/api-validation.json), pinned to the original completed summary SHA. All3 cases passed on the staged runtime. Full-case times333.781s control/338.344s preview; small lifecycle2.797s. One fixed pair does not establish a timing confidence interval or faster convergence.
- Production UI: [archived screenshots, snapshots and compact evidence](proposals/early-preview/production-qualification-a/ui/README.md). Runtime/source match. Root completed browser checks before owned300-second cleanup; exact helper result retains timeout/child-exit1, with no token-triggered cleanup claim.
- Failures, exclusions or unresolved risks: **PENDING review**, not assumed empty.
- Fresh native backups and exact restores verified: preflop102 stopped, postflop210 done/Kd6s5c, including config/profiles/locks and all arenas. These are freshly saved session values, not reused earlier snapshots.
- Deployment completed03:01:47UTC: oldPID108484 → newPID99900, runtime7de6c8… on56708/main cwd. [Archived compact manifests](proposals/early-preview/production-qualification-a/deployment/README.md) retain ownership, fresh backups, exact restore and rollback executable. No solve started.

Production API controller61683 (`production-api-a`) completed all3 cases. Private UI controller92800 completed its bounded lifetime after successful browser review; deployment subsequently completed after the remaining research queue ended. Remaining gates must be updated only from completed logs. No build, test, private-server launch, live POST, process action or deployment was performed by the template author.
