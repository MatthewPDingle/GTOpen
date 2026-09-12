# Regret matching+ screen: rejected

The new native-payoff regret matching+ baseline passed its numerical tests but
failed the registered combined convergence target in all three candidate runs.
Neither full-particle nor sampled large-game exploration is admitted.

| Mode | Samples | Seed | Iterations | Complete seconds | Global gap bb | Branches |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Normalized-pair gamma15 control | 64 | 42 | 1300 | 18.823612 | 0.003363617 | 6/6 |
| Native-payoff RM+, linear average | 1024 | 42 | 3000 | 198.479789 | 0.000807556 | 3/6 |
| Native-payoff RM+, linear average, pair correction | 64 | 42 | 3000 | 47.285344 | 0.000804865 | 2/6 |
| Native-payoff RM+, linear average, pair correction | 64 | 314159 | 3000 | 46.528159 | 0.000788604 | 2/6 |
| Normalized-pair gamma15 control | 64 | 314159 | 825 | 12.348984 | 0.003671788 | 6/6 |

Complete example times include setup, all global/conditional checks and save
roundtrip validation. They are executable-recorded durations, separate from
connection delays. Failed candidates are not equal-quality speed comparisons.
Their tiny global gaps cannot substitute for the missing conditional coverage.

The GPU implementation clips each learning actor's regrets after its native
counterfactual update, with no opponent-reach normalization or regret discount.
Linear averaging is implemented at iteration end. It adds no persistent device
arrays, only one clipping kernel per traverser. It is gated by preflop-research,
has no server entry point, and rejects ordinary learned histories or mixed
incompatible research modes. The full and sampled cases use the same model.

Verification:

- Independent host clipping and explicit linear average arithmetic match every
  regret/strategy entry across four alternating iterations, raw/calibrated HU,
  and full/corrected sampled particles. Nonzero frozen and locked histories
  exercise preservation; graph capture matches eager execution.
- Average/BR evaluation leaves histories unchanged, matches a detached native
  GPU engine exactly, and agrees with the CPU correctness reference within
  0.005 bb. Invalid admissions reject. Numerical v1 passed; v2 strengthened
  the constrained histories to nonzero values and passed too.
- Native GPU equivalence suites passed (6 postflop and 13 preflop tests).
- The full default release solver suite passed (132.859 seconds including
  compilation and all subprocess work); its log is retained.
- Every learning checkpoint was independently recomputed against all six fixed
  paths and all relevant hands. All five final saved audits match the recorded
  per-hand records exactly; save roundtrips match both arenas.
- Both disabled controls exactly replay earlier normalized-pair-tail gaps,
  EVs, conditional records, stopping ages and final saved-history hashes.
  All five cases used the same executable, solver source and pinned inputs.
- The Cargo manifest subsequently gates this new example behind the research
  feature for normal builds; no measured kernel or example logic changed.

See RM_PLUS_PLAN.md, RM_PLUS_SCREEN_PLAN.md, check_rm_plus_screen.py and
raw/rm-plus-screen-verified.json. Raw logs retain process timings, source,
executable and input hashes. The default release suite is recorded separately
as rm-plus-default-compat-v1 and completed successfully before publication.

Next: retain this as a tested algorithm baseline, not a speed improvement.
Investigate a separately specified predictive update and compressed prediction
storage. The dense-layout bound is in PREDICTION_STORAGE_INVENTORY.md. No large
RM+ rerun, longer budget, deployment, or relaxed acceptance gate follows.
