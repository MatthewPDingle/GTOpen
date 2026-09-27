# Fixed-policy precision and cost pilot

Freeze the first audited stratified arm's played generation-77 policy before
observing any pilot outcome. No fitting, strategy selection or production
promotion occurs. This is an estimator feasibility diagnostic, not a new
playing-strength study or an equilibrium claim.

## Two estimators of the same class action values

- **Board-first:** 32 independently drawn uniform public runouts, seed 9279701.
  Draw five distinct cards uniformly, sort the first three (flop), preserve
  ordered turn and river. Integrate every supported compatible private holding
  and later action on each board. Use original private weights, original class
  entry denominators, and the verified conditional-board/proposal ratio.
- **Private-first:** 32 independent conditional deals per BB hand class,
  5,408 deals total, seed 9279702. Use the existing class-stratified physical
  sampler: original conditional private-pair weights, then uniform remaining
  cards. Integrate later actions on each sampled deal. Do not condition this
  sampler on the board-first boards.

Both estimate only the postflop-dependent contribution. Add the same exact
preflop terms when displaying action-value means; these constants do not alter
within-class variances. In particular, neither arm receives avoidable fold or
initial-shove sampling noise. The policy uses its trained weighted preflop
tables and exact BTN initial-shove response, with the same saved postflop nets.

## Fixed comparisons

Primary diagnostic: the entry-weighted mean of per-class estimated variance of
the raise-minus-call sample mean. Secondary diagnostics: call-minus-fold and
raise-minus-fold. Use unbiased sample variance with 31 degrees of freedom for
each estimator/class and divide by 32 for variance of its sample mean. Publish
all 169 class means and variances, including unfavourable classes and zeros.

Report the square root of entry-weighted mean variance as a descriptive RMS
standard error. Multiply that mean variance by the total summed worker wall
time for the corresponding estimator to compare variance per computation
budget. Report raw timing components and total elapsed time too. The two arms
have different information per observation; do not equate a board with a deal
or infer speed from sample counts. Interleave jobs to reduce timing drift.

Report differences between estimated class means alongside descriptive combined
standard errors. With only 32 boards, these are noisy pilot estimates: no
significance or equality claims, no winner declaration from a few selected
hands, and no confidence claims treating the 169 classes as independent.
Shared boards correlate class errors. This pilot is not a comparison against
the existing GPU trainer's measured throughput.

## Resources and evidence

Four hidden CPU workers, one math thread each, no GPU. Require production idle,
at least 28 GiB available RAM and 40 GiB free S space before starting; admit
further jobs only with production idle, 24 GiB RAM and 40 GiB S free. A job is
bounded to 180 seconds and the pilot to one hour. Completed evidence survives
failure; do not silently restart. The main registered study keeps priority.

Bind the model, controls, implementation, chance streams and sample counts in a
registration before starting workers. Preserve private deal/query/policy/value
transports for independent review. For board jobs retain requests, class values
and the deterministic native tree hash; do not archive a redundant 80 MiB tree
for every board. Final analysis must verify complete job coverage and native
source hashes. No partial-result analysis, optional stopping, sample extension
or training promotion is authorized by this plan.
