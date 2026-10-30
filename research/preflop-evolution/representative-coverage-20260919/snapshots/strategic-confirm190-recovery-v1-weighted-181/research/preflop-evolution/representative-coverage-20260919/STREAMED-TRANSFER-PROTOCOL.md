# Streamed evaluation of frozen preflop policies

The coupled reference solve must revisit every board as preflop ranges
change. Once every preflop policy is frozen, however, separate flop
continuations have no shared learned parameters. They can be trained one
board at a time, retaining only their final counterfactual values for the
preflop evaluation. This is restricted to frozen-policy evaluation, never
an alternative way to train the connected preflop game.

Use the same fully enumerated resident GPU bridge, CFR+ schedule, constant
unnormalized private reaches and source policy at every preflop node. Preserve
the same alternating-player and called-pot order within each board. Compute
all requested postflop training checkpoints and keep the source probabilities
bitwise unchanged. Holding two called-pot games for one board in GPU memory
avoids the repeated host transfers needed by the coupled 47-board reference.

Store per-terminal, per-private-combo counterfactual values for average and
postflop best-response play, including preflop folds and all-ins. Aggregate
these vectors across boards with the frozen chance weights BEFORE taking
any preflop best response. Averaging independently maximized per-board
preflop values would leak the future flop and is forbidden.

Validation before reserved use:

1. Run the deterministic river controls from TRANSFER-CONTROLS.md and apply
   the same conservation, policy-preservation and restricted-BR checks.
2. Compare two independently streamed old development boards, each at 2,000
   iterations, with the existing two-board frozen-policy evaluator at 2,000.
   Require maximum player EV, postflop gap and full gap differences <0.0001
   bb; root frequencies <1e-7; exact source policy identity. Independently
   audit the aggregated physical-pair normalizer, hand summaries and cashflow.
3. Keep final leaf-value files or compressed equivalents with hashes so the
   aggregation is reproducible without rerunning the board solves.

Record the cost per board before scheduling either reserved panel. A single
low sampled-game gap still does not establish full-deck robustness. Preserve
the original ten-board stress panel and the separately frozen 95-board
validation sample; do not choose boards based on their strategy outcomes.
