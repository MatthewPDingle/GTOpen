# E017: omit actor1 down-action blocks in the second E015 sweep

Candidate only; no performance or runtime correctness result is claimed here. Base is accepted E015 (`gpu/mod.rs` SHA256 `7de2cd46ef93742c603042306cfe2ad08a83ff52a2be1123efd9d201aca15f1a`). E016 is terminally rejected and its cross-iteration cache, validity state and third graph are absent. The sealed D027 design is preserved unchanged; its two-player/E016 counts do not apply to this narrower candidate.

Only `gpu/mod.rs`, `gpu/plan.rs`, and `gpu/continuation_capacity.rs` change. Base and candidate copies, `candidate.patch`, exact hashes and mechanical checks are alongside this document. The parent owns compilation, serialized CUDA execution and all acceptance decisions.

## Exact change

E015 already passes `down_nh1=0` during the second uninterrupted paired sweep. An actor1 `down_action` block consequently performs no reach writes in either the locked or regret-matching branch. E017 omits these blocks, preserving all actor0 IDs in their original within-level order. The first sweep, standalone continuation, downward evaluation, upward action traversal, hand counts and CUDA source remain unchanged. The same two graph variants capture immutable per-solver worklists; no new validity or invalidation mechanism is introduced.

If any action level contains both players, every filtered span indexes one compact actor0-only ID list. Otherwise the device list is absent: actor0 spans reuse original starts/counts and actor1/empty spans have zero count. This global pointer choice prevents mixing coordinate systems. Empty levels are handled without reading a first node. No node ID, child list, reach owner, CFV slot, learning-arena offset or kernel arithmetic changes.

## Cost and accounting

`counts.json` rederives structural counts from the preserved D001 census in D027, using E015's two aggregate down sweeps as the baseline. The unchanged frozen evaluator/config provides the workload identity. Rainbow omits 248,732 of 1,047,066 action blocks per iteration (23.7551%); two-tone omits 151,349 of 637,124 (23.7550%). Each adds one allocation/upload, respectively 1,099,204 and 668,852 device bytes, plus 112 retained host span bytes. Both go from 26 to 25 down-action launches per iteration. The river omits 6 of 24 blocks and goes from 14 to 11 launches, adds 64 host span bytes and **zero** device list bytes/allocations. These are structural counts, not speed measurements or estimates of end-to-end gain.

Construction adds two host passes over action IDs and optional host/device list storage. `staging_bytes()` now explicitly means traversal working storage (reach + CFV + optional list), preserving exact-budget callers without expanding source scope. Its arithmetic and constructor arena/reserve additions are checked. Other immutable metadata remains covered by the existing reserve. Continuation capacity independently includes the optional list's actual length in estimated/observed immutable payload and new retained host spans; it does not add staging_bytes again. Continuation's seven mutable workspace arrays and compact storage mapping do not acquire the new immutable list. All setup costs remain inside the existing complete-cycle metric.

## Validation prepared, not executed

- A CPU plan test checks stable filter membership/order with nonmonotonic IDs, mixed/uniform levels, both single-actor extremes and empty spans; real flop/turn/river plans also verify membership and exact additional staging bytes for both isomorphism modes.
- The existing eight-case raw-state lifecycle test now requires a real optional device list. It compares all learning/reach arrays against full-sweep reference through eager execution, graph capture/replay, evaluation, profiling, actor0 and actor1 locks/recapture, and warm reconstruction; both algorithms, both storage modes and compact/full action arenas remain covered. Launch counts must match aggregate plus selected levels. Existing poisoned standalone-p1 and independent full-down checks remain byte-identical.
- A separate uniform-river lifecycle test requires no extra CUDA list and exercises exact-budget rejection/admission, eager/capture/replay, evaluation, profiling, locks and warm reconstruction in F32/DCFR and compressed/CFR+.
- The feature-gated continuation-capacity test compares actual CUDA metadata against planned payload for an explicitly mixed turn and uniform river, including the absence/presence assertion and retained span capacity.

Syntax-only rustfmt parse and `git diff --check` passed. No Rust compilation, test execution, CUDA context, solver run, server request, deployment or commit was performed by the builder. Protected kernel/arena/store/evaluator hashes and byte-identical E015 graph/continuation/eval/upward bodies are recorded in manifest.json. Independent source critique is requested from menu_change_review; compilation and numerical/complete-cycle qualification are still required.
