# Bounded class-coverage sampler qualification

Purpose: isolate a candidate way to remove random gaps in BB root hand-class
coverage. This is not a training run or a change to the completed showdown study.
The original physical sampler and all production/evaluation paths stay unchanged.

For a 512-deal batch with 169 supported classes, allocate three deals per class
and one additional deal to five classes chosen uniformly without replacement.
Shuffle the resulting class schedule. Within each class, sample BB's physical
private pair using its original blocker-adjusted marginal conditional on the
class. Sample BTN conditional on that private pair from the original compatible
range, then draw the five board cards uniformly without replacement.

Let p(c) be the original physical class mass and n(c) the realized allocation.
Each deal carries weight w(c)=512*p(c)/n(c). Conditional on the allocation, its
random-slot proposal is q(i,j)=n(c)/512 * p(i,j|c). Thus w(c)*q(i,j)=p(i,j).
Uniform board sampling is unchanged. Weighted sums estimate the original game;
unweighted stratified observations generally estimate a different distribution.

Controls use direct enumeration of the compatible private-pair joint law to
check weighted proposal identities, exact checkpoint continuation, all-card
legality, complete class coverage, weight normalization, malformed input rejection,
and changed-context rejection. Use 16 batches of 512, seed 9271001. Time the
sampler alongside the existing sampler; report these as sampler-only timings.
No native payoff evaluation, model fitting, GPU work or strength conclusions.
Maximum runtime 180 seconds and compact metadata only.

Before training integration, audit every root accumulator, BTN exact target,
later-action target, replay-reservoir selection and fitting-loss weight. Carry
the source-deal weights consistently, or isolate a root-only side stream while
explicitly charging its extra compute. The current unweighted pipeline must
reject or remain disconnected from this sampler until that work is qualified.
Any next study must compare coverage and target variance per wall-clock cost;
regular counts alone do not resolve within-class runout noise or policy drift.
