# Next bounded diagnostic: where do the prediction errors come from?

The completed 302-versus-314 input comparison did not meet its threshold.
Mean postflop validation error rose 0.36%; only one of four datasets improved.
Do not integrate these inputs into a full training run on that evidence.
Longer and shorter fitting also failed to improve the original 512-step fit.

Before choosing another fit experiment, read back the four saved 512-step
baseline networks and existing generation-77 datasets. Do not generate new
deals, retrain networks, change targets, or score the final-test partition.
This is an exploratory descriptive audit of reused data, not confirmation.

## Questions and fixed outputs

1. On validation rows, partition weighted squared prediction error by street,
   current pot size (under 10, 10-50, 50-100, 100-200, 200+ bb) and starting
   postflop pot. Compare each bucket's row/source-weight share with its error
   share and target-energy share. Report loss relative to predicting zero.
   Public chip values must come from the existing native-state catalog.
2. Report the share of weighted error concentrated in the largest-error 1%
   of rows, separately for each street. This is descriptive concentration,
   not a reason to discard those examples or a prediction interval.
3. On training rows only, count repeated identical inputs/legal menus and
   measure their target disagreement. Repeat grouping with training iteration
   included to distinguish some policy drift from same-iteration variation.
   Report coverage and effective counts alongside the disagreement.
   Singletons contain no repeat evidence. Sparse, selected duplicate inputs
   cannot establish an irreducible noise floor or represent all hands.
4. Reconstruct each saved baseline validation loss from the audit's raw-row
   totals, with CPU inference agreeing within a declared numerical tolerance.
   Bucket totals must reproduce the overall/street totals. Test these
   accounting identities on a small hand-calculated fixture first.

## Bounds and interpretation

Use up to four independent CPU workers with one numerical thread each after
checking other workloads and available RAM. This readback needs no GPU; it
should not wait for a video or local image-generation application. Keep shared
research-lock, production-activity and allocated-storage checks. Retain at most
5 MB of summary outputs, and stop after 10 minutes if the readback does not
finish. Preserve failure evidence. Do not retain another copy of the dataset.

If large-pot rows dominate the objective, investigate a separately registered
public-state target-scale/weighting comparison. A positive common rescaling
of a state's action scores preserves regret matching, but changing training
weights and scales still requires explicit policy and fallback checks.

If repeated-input coverage is adequate and targets disagree substantially,
consider averaging more action rollouts at sampled information sets before
collecting a wider dataset. Policy changes, correlated samples and hidden-card
variation remain distinct explanations. If coverage is sparse, say that the
noise question is unresolved; do not infer a noise floor from singletons.

Any promising regression change still needs complete policy training and
fresh-deal evaluation. Production remains unchanged. The broader goal is
accurate, flexible preflop ranges, and this diagnostic does not achieve it.
