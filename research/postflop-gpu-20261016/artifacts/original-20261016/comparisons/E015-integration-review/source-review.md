# E015 independent source and integration review

**PASS: no actionable source regression or integration conflict found.** This review is read-only with respect to both checkouts, sealed evidence and the live application. No build, GPU run, test execution, live API request, process action or deployment was performed. Only this new review directory was written.

## Source reasoning

E015 changes only GPU host dispatch in `crates/solver/src/gpu/mod.rs` plus two unit tests in that file. Kernel math, launch sizes, discount values, arena layout, budgets and save format are unchanged. The second sweep of an uninterrupted ordinary or profiled iteration passes `nh1=0` only to `copy_root`, `down_action` and `down_chance`. This makes player 1's down-loop bodies empty while preserving player 0's real hand width and recomputation. Up kernels retain both real widths.

Reusing player 1 reach is sound under the present paired call contract: the first down sweep has computed it; player 0's up sweep updates only player 0's regrets/strategy and CFV scratch, and neither changes player 1 policy/root weights/locks nor writes reach buffers. Player 1 reach contains its own action probabilities and board-card masking, independent of player 0 policy. The refreshed player 0 reach incorporates its newly updated regrets for the second traversal. Zero-width down pointers are formed safely and not dereferenced by the skipped player 1 loops.

Ordinary eager execution and graph execution both launch player 0 then player 1 on the same stream. Capture records the same dependency and first resumes at a nonzero iteration still launch the full player 0 graph first. Every new pair recomputes both reaches before reuse, including after evaluation, lock invalidation or a warm constructor. The generic standalone `sweep` wrapper explicitly disables reuse, preserving continuation/custom-root/workspace-swap refresh semantics. The reviewed call sites do not expose reuse to arbitrary standalone player 1 calls.

The added tests compare all raw device regrets, strategy and reaches against full sweeps across both algorithms, both host storage modes, explicit/compact arenas, eager/captured/profiled iterations, evaluation, both lock owners and warm graph recreation. An independent legacy down-dispatch oracle checks player 1 preservation and standalone refresh after changed roots and poisoned reach buffers. Existing immutable broader control evidence separately covers save/load/query state and menus. These are bounded tests, not a proof for every possible tree or future caller.

## Evidence verified here

Rehashed **79 unique inputs** listed by the primary and cumulative independent audits: all match their recorded SHA256 values. The complete list is in manifest.json. All twelve raw stdout result sets match their report results. Recomputed both three-repeat cohort statistics and compared all non-timing result fields across all six runs of each cohort, including full state fingerprints, exploitability bits, stopping iterations, configuration and accuracy targets. Environments match within each cohort; no runs were excluded.

| Comparison | Baseline | Candidate | Observed full-cycle gain |
|---|---:|---:|---:|
| E004 vs E004+E015 | 11262.8874 ms | 10814.3093 ms | 3.9827984% |
| Original baseline vs E004+E015, fresh cohort | 10740.3699 ms | 9707.2344 ms | 9.6191799% |

The statistic is the sum of the three fixture full-cycle medians, using three repetitions per binary. All fixture medians improve in both cohorts and the sealed audits report no repeated material fixture-regression failure. The cumulative figure is directly measured; it is not an addition or product of earlier percentages. Its river median gain is only 0.6671%, and its first river pair is 1.8203% slower, below the registered material-regression guard. Absolute times differ between cohorts; cross-cohort subtraction or an explanation of that shift is unsupported.

The reviewed broader audit records 160 ordered exact state/menu/resume snapshots, exact non-timing results for all three F32 fixtures, 84 passing units (four ignored), and six passing GPU tests. Both newly added raw-device tests executed. This review reverified their preserved artifact identities and reviewed the audit/source, but did not execute those tests again. The old primary summary intentionally predates the cumulative review and still describes that gate as pending; final cumulative reporting should cite cumulative-validation.json rather than reinterpret or overwrite the sealed primary summary.

## Main integration identity

At the start of this review, main's mod.rs was byte-identical to the research baseline (SHA256 0df4108ec3ccb81151782a667beb9906ed61f99c876d26d16bcf8957e4b9c82b), so the change had no source conflict. The parent integrated it while the review continued. The final observed main commit is `bf0d15c4` (full ID in manifest.json). Main and research mod.rs now both match the qualified candidate SHA256 **7de2cd46ef93742c603042306cfe2ad08a83ff52a2be1123efd9d201aca15f1a**. arena.rs, kernels.cu, plan.rs, continuation_capacity.rs, cfr.rs and store.rs also match byte-for-byte across the two checkouts. The checked main tracked working state was clean. Untracked research/dashboard evidence was not modified or integrated by this reviewer.

## Safe acceptance scope

Accept the paired GPU host-dispatch optimization with retained E004 under the measured native RTX 5090 three-fixture compressed postflop protocol. The evidence supports approximately **3.98% incremental** full-cycle improvement over E004, and **9.62% cumulative** full-cycle improvement over the original baseline from the separately measured fresh cohort, with exact tested numerical state and passed recorded correctness controls.

Do not generalize those percentages to F32 performance, arbitrary trees/hardware, cold-start behavior, preflop solving or live server latency. No statistical-significance or universal exactness claim is established. Solve spans include accuracy checks; component timings do not isolate the precise kernel contribution. The frozen complete-cycle metric includes runtime JIT/setup, solving, checks and readback, while Cargo compilation, fingerprint hashing, HTTP and disk saves remain outside its boundary. Continuation receives no new reach-reuse optimization. Source acceptance and integration are separate from a rebuilt server's native smoke validation and application deployment; this review establishes neither a live binary update nor session restoration.
