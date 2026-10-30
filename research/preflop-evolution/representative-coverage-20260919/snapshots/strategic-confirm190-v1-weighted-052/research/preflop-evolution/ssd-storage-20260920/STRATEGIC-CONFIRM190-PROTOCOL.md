# Independent 190-flop confirmation of the frozen policy comparison

## Question and fixed scope

The completed 95-board comparison favors weighted-112 over equal-112 by 0.023555 bb and over the old 47-board reference by 0.113553 bb in summed full deviation. Paired single-board omissions can reverse either ordering. Test whether the ranking replicates on a larger, disjoint sample before changing training or choosing a production policy.

Keep the same three frozen source policies, subtree, evaluator executable, helpers, incoming ranges, rake, postflop action menus, precision and omitted-folded-card treatment. No additional preflop training, range edits, chance-weight fitting or new model selection occurs in this run. The old-reference comparison retains its known training-update confound.

## New sample, selected before its outcomes

Select exactly 190 canonical flop orbits using the existing integer-arithmetic systematic probability-proportional-to-physical-mass sampler and fixed seed `stored-confirm190-independent-20260922-v1`. Exclude all 128/112/96 candidate training panels, the old 164 comparison boards, and all 95 just-evaluated reserved boards. Freeze the resulting manifest, eligible population, source policies, runner, protocol and executable identities before evaluating any new board. Do not change the seed or redraw in response to outcomes.

Use equal sample weights as defined by that sampler, suit-orbit treatment, the 50% postflop bet menu and the plain explicit evaluator. This new eligible population differs from the first panel's population. Report this panel separately; do not compare absolute gap levels across the two panels as if they shared the same chance distribution, and do not concatenate their samples with arbitrary equal weights. Within each panel, all policies face the same boards and distribution. This is confirmation on a new sample, not a full-deck equilibrium claim.

## Evaluation, safeguards and stopping

Run every source on every board: 190 times three = 570 sequential workers, board order from the manifest and source order weighted, equal, report47. Each worker runs exactly 2,000 postflop iterations with all preflop probabilities preserved bit-for-bit. Retain reached and off-path values. No retry, early strategy-based stopping, omitted difficult board or automatic iteration extension.

The previous 285 guarded workers took 14,128.577 seconds in total; maximum worker time was 53.125 seconds. Doubling that observed workload suggests approximately eight hours, not a runtime guarantee. Register the same 900-second per-worker maximum and a 43,200-second invocation ceiling. Before each worker require disk capacity for remaining workers at 256 MiB each plus a 32 GB reserve. Preserve the existing 20 GB RAM / 3 GB VRAM reserves and production-idle guard. Never restart or mutate production. A worker or validation failure retains partial evidence and stops for review.

## Validation and interpretation

Require the preceding evaluator controls to remain valid and recheck their inputs and outputs. Verify all fixed identities throughout the run. Each worker must pass exact preflop import, private-pair and hand-summary accounting, probability and chip/rake checks. Preserve raw JSON, verified gzip copies, reviews, logs, resource records and source snapshots with hashes.

Aggregate terminal counterfactual values over all 190 boards before maximizing any preflop action. Report each source's full deviation, both player gaps, postflop residual, EV and expected rake separately. Require each aggregate postflop residual below 0.01 bb before interpreting the comparison as settled responses. An unmet criterion means an underconverged comparison, not a winner or automatic extension.

The principal comparison is weighted versus equal weighting; comparison with the earlier 47-board policy is a secondary baseline. Report exact differences and paired leave-one-board-out sensitivity after completion. A rank reversal or a small unstable difference is an inconclusive finding to retain, not a reason to tune this validation set. Keep this new panel out of subsequent fitting unless its role is explicitly changed to development data and a separate test is reserved.

No result here alone authorizes production promotion, a full multiway claim, or GTO Wizard equivalence. Use the result to choose the next separately designed coverage, training-update ablation or context-transfer experiment.
