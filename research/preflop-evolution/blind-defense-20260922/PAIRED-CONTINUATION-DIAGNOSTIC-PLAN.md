# Same-card comparison of learned continuations

25 September 2026. Prospective diagnostic after the negative matched
action-integrated training study. No new training, responder selection,
production change or range-quality qualification is authorized by this plan.

## Question and fixed scope

The two completed trials assign different actions to many hands. Compare their
complete played, linear-weighted continuation policies on identical physical
deals. Evaluate all four combinations: BB first / BTN first (AA), BB first /
BTN repeat (AB), BB repeat / BTN first (BA), and BB repeat / BTN repeat (BB).
The actor's entire later behavioral policy comes from the selected bank. Each
bank preserves its original own-reach averaging, including zero-reach fallback.
Force only the initial BB action to call or raise; integrate all later actions.

Use generations 0–77, weights 1–78, from both audited action-integrated trials;
exclude the unplayed generation 78. Preserve the context: BB versus BTN 2 bb,
200 bb effective, 5% rake capped at 2 bb. This is not an equilibrium solve of
the crossed profiles. Neither seed is presumed correct.

Use the first 64 complete rounds of the existing, already inspected,
class-balanced `root-retained-wider-study-v1/evaluation/training-deals.json`:
10,816 physical deals, 64 for each of all 169 BB classes. Compare the source
prefix against the authenticated original batch records before evaluation.
This is reused diagnostic data, not a new holdout. There is no optional
stopping or choice of attractive hands, checkpoints, seeds or sample counts.
The fixed initial batch size is 32, giving 338 complete batches.

## Measurements and limitations

Retain every per-deal call/raise payoff for all four profiles. For call, raise,
and call minus raise, report every class's means, sample variances, descriptive
standard errors, and first/second 32-deal half means. On the paired deals form:

- diagonal difference: BB − AA;
- BB-policy effect: ((BA − AA) + (BB − AB)) / 2;
- BTN-policy effect: ((AB − AA) + (BB − BA)) / 2;
- interaction: BB − BA − AB + AA.

Report incoming-mass-weighted RMS class means and RMS class standard errors for
these differences, plus weighted signed means. Verify the first two effects
sum to the diagonal difference on every deal. Keep unfavorable and ambiguous
results. No simultaneous confidence bound or full exploitability claim is made.
Within-profile variation describes remaining private-card/board uncertainty;
paired effects describe sensitivity to learned continuation policies. These
cannot establish which continuation is erroneous, nor fully separate all
learning and chance effects. Large uncertain differences justify more samples;
large stable differences justify examining continuation training rather than
merely extending root sampling. No arbitrary significance cutoff is imposed.

Also retain each bank's zero-own-reach query counts by actor and street, root
probabilities and policy/support hashes. Off-path fallback can affect forced
root deviations and must remain visible in interpretation.

## Verification and resources

Before evaluation, the bulk-feature bank must produce byte-identical averaged
probabilities and own-reach support to the historical CUDA bank for both full
78-model banks on two authenticated full-history query batches from the earlier
evaluation (train-000000 and train-010752). The first control attempt used
training queries, which lack own-history links, and failed before comparing
policies; preserve that attempt. Keep float64 inference,
float32 stored weights, TF32 disabled, ordered accumulation and chunk size 8.

Freeze the controller, reducer, reader and source identities before the run.
Preserve compact authenticated batch archives and independently reconstruct
crossed policy transport, all per-deal output values, paired effects, per-class
statistics and weighted reductions using a separate scalar reader. Native
forward/reverse cashflow checks remain required; neither this reader nor the
equivalence control independently implements all poker traversal or inference.

Admit at most 4 GB of new output plus the existing 2 GB reserve within the
800 GB combined research allocation ceiling. Measure fresh admission. Maximum
worker duration 7,200 seconds, with production-idle guards, exclusive research
ownership, at least 40 GB free on T:, 20 GB available RAM and 3 GB available
VRAM. Preserve failures; do not enlarge the fixed experiment silently. Use the
already verified owned-batch archive lifecycle, retaining all original files.
