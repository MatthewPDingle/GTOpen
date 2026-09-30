# Evaluation preparation during matched continuation training

The scientific training run is still in progress. These checks qualify parts of
the future evaluation software; they do not show that poker ranges improved.
The registered training inputs, models, budgets and comparison rules are unchanged.

## What is ready

`stack_context_matched_analysis_v1.py` implements the already registered final
comparison: 4,096 deals at each of seven depths, eight paired player gains, and
an error allowance of 0.05/7 per depth. It reports simultaneous bounded
intervals, equally weighted stack-normalized means, adverse-deal frequencies,
and signed paired-loss tails. An improvement requires all eight pooled lower
bounds to be positive and no negative per-depth point estimate. Exploratory
normal intervals cannot override that rule.

Its CPU check passed in 0.11 seconds. Synthetic payoffs matched independent
NumPy means, variances and quantiles across 56 contrasts. Positive, adverse and
inconclusive outcomes behaved as specified; seven incomplete or changed designs
were rejected. See `stack-context-matched-analysis-check-v1-result.json`.

`stack_context_preflop_export_v1.py` exports the complete averaged policy at
each preflop decision, together with the hand distribution actually arriving
there. It propagates compatible-card joint entry mass through both players'
actions. An action mix for a hand is therefore not presented as the probability
of that hand reaching the decision. Zero-reach decisions remain explicit.

Its CPU check passed in 1.05 seconds on retained native catalogs at 20 and
400 BB. An independent 1,326-by-1,326 physical-combination calculation agreed
with the 169-class export to within 2.78e-15. Both zero-reach and malformed
catalog cases were covered. The policies were artificial; no trained-model
accuracy was measured. See `stack-context-preflop-export-check-v1-result.json`.

`stack_context_evaluation_journal_v1.py` stores a durable claim before sampling
and an intent containing the exact batch before evaluation. A completion record
binds the batch, sampler continuation, source hashes, lossless archive receipt
and original native payoffs. Recovery accepts completed raw evidence or a
receipt-backed archive without calling the evaluator again. Partial sampling,
partial scientific outputs, and interrupted archive publication without a
receipt are preserved and refused for automatic retry.

Its CPU check passed in 3.031 seconds using 295,924 bytes of new evidence. Two
synthetic batches reproduced an independent sequential sampler and NumPy
statistics. Three interruption points recovered correctly, and 22 invalid or
corrupt cases were refused. The test used an artificial context and fake
payoffs: it did not draw the scientific comparison's test hands, invoke native
solves, read trained model outputs, fit networks, use CUDA, or delete files.
See `stack-context-matched-journal-check-v1-result.json`. Its evidence directory
is `S:\GTOpen-research\stack-context-matched-journal-check-v1`.

## Required consumer contract and remaining work

- Finish the evaluator controller and bind its source, complete banks, exact
  cache, native executables and all seven contexts before the first fresh draw.
  Do not run it before successful training completion and release of its owner.
- Select all 64 played generations 0 through 63 with weights 1 through 64 for
  each actor. Exclude the final unplayed generation 64. Preserve each model's
  own action reach and fitted local overrides; held-out depths have no local
  fitted tables. Do not select models using the test result.
- On reopening a journal, call `prefix(verify_archives=True)` before admitting
  more work. `prefix()` is the cheaper in-process path after that verification.
  The controller must own the study lock and enforce the registered resource
  bounds. The journal is not an admission scheduler.
- Call `recover_next()` before starting the next batch. Only `begin()` for a
  genuinely unstarted prefix may create new work. Its fixed batch size is 32.
  A failed partial batch must not be silently retried, skipped or replaced.
  Lossless raw-copy retirement is optional through the existing qualified
  archive owner and only follows a completed journal commit.
- The journal authenticates saved artifact identities and native/summary value
  agreement. It does not independently recompute poker payoffs or exact all-in
  labels. The final independent reader must verify those recorded inputs,
  complete model selection, chance stream and all predeclared comparisons.
- Qualify the combined evaluator on retained implementation evidence before
  running fresh scientific evaluation. The long 64-model bank's throughput
  has not yet been measured; previous bank parity checks used two models.
- Generate the seven-depth range exports and perform the final analysis only
  after their real inputs exist. The separate correctly targeted continuation
  prediction diagnostic still needs its own prospective protocol.

This remains fixed-entry, heads-up BB-versus-BTN continuation research. The
entry ranges originate from a retained 200 BB GTOpen approximation and are
held constant across stacks. Neither these software checks nor a later
positive fixed-opponent comparison establishes accurate all-position or
multiway preflop ranges. No production deployment or GitHub push was made.
