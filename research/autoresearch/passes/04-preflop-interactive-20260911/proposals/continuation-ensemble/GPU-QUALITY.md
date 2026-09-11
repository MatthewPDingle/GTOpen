# Large-tree full-reference policy audit

Source-only implementation, awaiting root-controlled compilation and execution:

- `crates/solver/src/preflop/preview_quality_gpu.rs`
- `crates/solver/examples/preflop_preview_quality_gpu.rs`

Root must declare the GPU-gated module and example before building. Run:

```text
preflop_preview_quality_gpu CANDIDATE.gtop REFERENCE.gtop EQUITY_CACHE GPU_BUDGET_MB
```

The intended full reference is the previous pass's `extended-convergence-eight-compatible-a.gtop`, iteration1,024; root independently verifies its hash, configuration and prior convergence. This harness recomputes reference gaps and EVs and requires a full1,024-particle model. Prior convergence is not accepted as a substitute for the recomputed result.

The procedure evaluates the saved reference, then a fresh full-payoff workspace containing the candidate's average-strategy sums, then each learning seat's candidate strategy against all other seats' reference strategies. Each evaluation creates and destroys its own GPU engine, rebuilding effective profile and lock inputs. Signed unilateral losses are all reported; aggregate mean/max losses use positive losses so improvements cannot cancel another seat's degradation. The global gates remain the previously registered0.005 reference gap,0.02 excess gap,0.01 mean positive loss and0.03 maximum positive loss, in bb.

Before evaluation it checks complete tree metadata, configuration, seat profiles, frozen flags, hero/pre-hero flags, point locks, shared equity-table Arc, realization fit, finite raw arenas, normalized effective policies, and equal frozen effective policies. The workspace copies full-reference constraints; its regrets remain unused zeros. Hero undo backups remain in the immutable inputs and are not duplicated: evaluation never changes hero/table settings or saves.

Limits are2million nodes and3GiB combined regret/strategy arenas per input; the command rejects native files above3GiB before loading. Host memory holds two immutable solvers and one workspace: up to9GiB of arenas, plus tree/profile metadata and existing hero backups. No full-arena snapshots or per-seat block-index vectors are created by the large evaluator. Only one GPU allocation set exists at a time; the requested budget is enforced by the normal constructor. Repeated engine initialization is deliberately included in audit timing, not claimed as optimized quality-check throughput.

Source inputs are never resumed, relabelled, synchronized from GPU or saved. The command checks native size/mtime and exact equity-cache bytes before/after. These checks are **not native content hashes**; pin native SHA256 externally and retain that evidence. Cancellation is checked during validation and before/after each GPU evaluation; an in-flight GPU check completes before the cancellation is observed. No partial numeric result is published after cancellation.

The unit test `gpu_policy_quality_same_policy_is_zero_and_inputs_remain_unchanged` uses a tiny game to check exact zero same-policy loss, all learning-seat comparisons, GPU/CPU root agreement and input immutability, plus rejection of a pending stop.

This is global policy evaluation under the existing latent model. It does not validate physical-deal equity or local strong-action tails, and its runtime is not the user's time to a usable preview.
