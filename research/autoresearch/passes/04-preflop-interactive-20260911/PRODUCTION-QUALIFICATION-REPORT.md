# Exact early-publication production qualification

**Status: compilation and selected tests passed; API/UI/deployment pending.** All41 frozen test executables and the solver doctest invocation completed with exit0 at2026-09-11T02:30:48.975956Z. Actual counts are232 passed,0 failed,5 ignored and90 filtered. Zero-test binaries and the zero-doctest invocation are recorded, not counted as passing tests.

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
| Final main integration commit | PENDING |
| Deployment and restore manifest | NOT DEPLOYED by this qualification |

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
| Private-server ownership and cache identity | PENDING | Correct staged EXE SHA, private cwd/port, pinned actual cache header/hash |
| Early publication disabled/enabled reference pair | PENDING | Final native config/profiles/locks/iterations/arenas exact; publication at completed checkpoints |
| Stop/cancel and coherent save/reload | PENDING | Published state corresponds to saved native; interrupted accuracy invalidated; stop flag detached before idle evaluation |
| Capability/model boundary | PENDING | `early_preview_v1` true; fresh model list only `coupled_deck_v1`; invalid models leave session intact |
| First published strategy / first accuracy timing | PENDING | Actual API latency with recorded cache, fixture, iteration/check interval; do not reuse research-mode timing |
| 1280px private UI | PENDING | Own publication row; actor/evidence readable; capability-aware control and export warning |
| Native session-preserving private restore smoke | PENDING, after queue/test completion | Both freshly saved user sessions resave with exact headers and every arena SHA |

Research approximation results are separate. A learned snapshot at iteration2 means an available intermediate strategy; it is not a quality certificate, nor evidence of global or local convergence. Published iteration and measured-accuracy iteration must remain distinct in reporting.

## Final completion record (root fills after evidence exists)

- Completed build/test artifacts: [summary and all42 test/doctest logs](proposals/early-preview/production-qualification-a/README.md). Original result and manifest hashes, all47 job records and frozen artifact hashes are retained in the JSON summary.
- Production API protocol/result links and exact runtime hash match: **PENDING**.
- Production UI screenshot/check links: **PENDING**.
- Failures, exclusions or unresolved risks: **PENDING review**, not assumed empty.
- Fresh preflop native iteration/config/profiles/locks and postflop iteration/board/locks: **PENDING latest backups**. Earlier status101/native102 and postflop210 are not restoration inputs.
- Deployment decision: **PENDING**. If executed, record new ownerPID/create time/EXE/SHA/cwd, fresh backup/restore/cutover records, main asset identity and rollback executable path.

Production API controller61683 (`production-api-a`) is still pending at this report update. Remaining gates must be updated only from completed logs. No build, test, private-server launch, live POST, process action or deployment was performed by the template author.
