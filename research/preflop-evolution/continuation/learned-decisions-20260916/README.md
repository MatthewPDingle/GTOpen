# Frozen candidate: experimental preflop decisions

This is option 1 from the follow-up: test the already trained candidate in
actual preflop traversals. The production app on 56708 remains unchanged.
This experiment does not train a new candidate or deploy one.

## Protocol, fixed before inspecting strategy outcomes

- Use the exact config from `saves/preflop/balanced-sb05-continuation-20260915.gtop`:
  the user's zero-rake half-small-blind straddle comparison. Start both arms
  fresh, with no player models or saved regret history inherited.
- Compare Balanced against the frozen `shape`, ridge 0.1 candidate from the
  completed 3,200-reference experiment. `candidate.cu` records its SHA256.
- Replace only zero-rake heads-up continuation terminals with SPR 1 through
  20. All-ins, out-of-support SPRs and multiway continuations retain existing
  pricing. Zero-arrival range contexts also retain ordinary pricing.
- Recompute candidate inference from the ranges in each GPU downward pass,
  including read-only evaluation. Do not hold terminal ranges fixed while
  learning. Exact heads-up compatible-class counts and frozen feature scaling,
  coefficients and centering match Python; no prediction clipping or tuning.
- Inspect the first 50 iterations for execution problems, then compare matched
  250, 500 and 1,000-iteration checkpoints. If the 1,000-iteration strategy is
  not stable, extend both arms to 2,000 without changing the model or tree.
- Capture unopened decisions at successive seats, responses to the first
  opener and responses to a BTN open, including SB, BB and the straddler.
  Cross-price both final policies with both continuation models and inspect
  conditional action EVs as well as probabilities. A direction of change
  alone is not proof of improved poker accuracy.
- Check independent prediction parity, finite values, strategy normalization,
  repeatable read-only action evaluation and checkpoint stability. Record
  unsupported terminal counts and model/accounting limitations. Retain
  regressions, not only favorable hands. Do not tune to Wizard's grid colors.

## Interpretation limits

The preflop engine's chance model does not implement full joint card removal.
The learned heads-up model uses compatible range masses, whereas preflop
aggregation uses the engine's existing chance weights. Monitor total player
EVs as well as individual decisions: a pot-conserving predictor alone does not
prove a pot-conserving full preflop game under that mismatch.

Range-dependent leaf payoffs also change the meaning of the reported gap.
The GPU best-response pass holds the current range-conditioned predictions
fixed. It is a diagnostic surrogate gap, not a full-game exploitability bound
or a standard CFR convergence guarantee. A stable average policy is necessary
but does not resolve that theoretical limitation.

This original comparison source belongs to an earlier training family. This
is a targeted integration/decision study, not a new independent generalization
test. Reliable claims of improved decisions need supporting postflop reference
checks or an independent higher-fidelity benchmark.

## Isolation

Only the `preflop-research` build exposes the learned GPU hook. The ordinary
server has no route to enable it. The executable is built under
`target/learned-decisions`, not over the running server.

**Do not load this directory's experimental `policy.gtop` files in the app.**
They preserve research solver state for controlled resumes, but ordinary save
metadata still says Balanced. The sidecar JSON selects the research payoff;
these files are local and excluded from Git.

## Structural gate found at the 50-iteration execution check

The candidate's total player EV was +0.06151 bb/hand at zero rake, versus
-0.000000257 bb/hand for Balanced. Independently reweighting the 32 original
fixtures confirmed the incompatibility: compatible-mass prediction sums
balance to roundoff, but independent weighting can deviate by 4.38895% of pot.
The predictions themselves are unchanged. This is a structural accounting
failure, not a reason to tune the candidate or run more convergence iterations.

Both arms will finish a matched 250-iteration diagnostic checkpoint and undergo
read-only cross-pricing. The originally planned 500/1,000/2,000 extension is
withheld pending a consistent chance/value interface. No decision-improvement
or full-game convergence claim can pass this gate, irrespective of grid colors.
The source family being in training and sparse-hand prediction errors remain
separate limitations after that interface problem is fixed.
