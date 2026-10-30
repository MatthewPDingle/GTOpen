# Direct preflop policy trial: training and replay complete

The hybrid trial completed all 78 registered updates and 39,936 fresh physical
deals. Training took 5,049 seconds, approximately 84 minutes. Its independent
training replay passed in 445 seconds. Fresh evaluation is running; no range-
quality result or deployment decision follows from the training audit alone.
The original evaluation later stopped on a numerical control; its separately
registered [precision repair](HYBRID-NUMERICAL-REPAIR-STATUS.md) is now running.

This experiment keeps the dense candidate's game and training recipe, but uses
retained mean advantages directly at observed preflop information sets. Postflop
decisions still use the neural networks. This removes one source of preflop
fitting error while retaining sampling noise and imperfect continuation play.
It is a separate BB-versus-BTN study, not an update to the UTG/LJ preview.

The completed replay verified:

- All 39,936 dealt hands, action random-number streams and 79,872 updater
  traversals, together with their recorded native reference checks.
- Every generated preflop table and every queried policy row supported by those
  tables, including consistent use of the frozen policy across each update.
- The final retained arrays and sampling states: 262,144 BB records and 108,502
  BTN records, drawn from 951,156 and 108,502 observed records respectively.
- All 78 played generations, 0 through 77. The unused generation 78 is excluded
  from the strategy to be evaluated.

The review reconstructs sampling, stored tables and checkpoint progression; it
does not independently repeat neural optimization. Its passed status establishes
execution integrity, not convergence or agreement with GTO Wizard.

The reserved 8,192 response-training deals and 16,384 held-out deals have now
completed, with a passing independent evaluation audit after the documented
numerical repair. The [completed findings](SAMPLED-PHYSICAL-HYBRID-FINDINGS.md)
retain all 169 classes and both candidates' intervals. Improved accuracy was
not established; different streams do not provide a paired improvement estimate.

Evidence: `sampled-physical-hybrid-pilot-v1-result.json`, its terminal
`status.json` and `independent-review.json`, and the unchanged
[registered plan](SAMPLED-PHYSICAL-HYBRID-PLAN.md). The source policies remain on
S: with their hashes recorded in the result and review. Production and the
experimental range preview are unchanged.
