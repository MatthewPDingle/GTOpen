# Regular class coverage: sampler control passed

The research sampler guarantees three or four BB observations per supported hand
class in each 512-deal batch. In the fixed 16-batch control, it left no classes
empty; the existing sampler left an average of 18.375 classes empty per batch.
This establishes coverage and sampling correctness, not improved learning or
poker strength. The sampler is not connected to training or production.

Direct enumeration of compatible private-card pairs confirmed that the weighted
proposal reproduces the original joint distribution, with maximum absolute
probability discrepancy 1.91e-21. The tested batch's weights ranged from 0.3653
to 1.6235 and summed to 512. All 8,192 generated deals had legal, distinct cards,
matching native hand classes and normalized weights. The five public cards use
the same uniform without-replacement procedure as the original full-deck sampler.

Exact checkpoint replay passed. Eight negative controls rejected invalid batch
sizes/types, checkpoint identities/counters and changed game context. No frozen
research sources were changed during the run. The whole control took 1.58 seconds.
Sampler-only timings were 0.516 seconds for 14 stratified batches and 0.640 for
16 ordinary batches; these are small local measurements, not a training speed claim.

Without its weights, the tested proposal differs from the intended private-pair
distribution by **24.48% total variation**. Simply plugging the deals into the
existing unweighted trainer would be an incorrect implementation of the intended
experiment. Keeping three observations per class also does not cure high variance
within a class, changing opponents, or insufficient postflop modeling.

## Integration audit and next gate

The existing joint training path currently discards sampler metadata and takes
only `sample(...)["deals"]` in `later_action_training_v1.update`. It uses 32-deal
subbatches, so the new allocation must be made once per full 512-deal generation
and then sliced with weights and original deal identities kept aligned. A
32-deal stratified call correctly refuses because it cannot cover 169 classes.

| Component | Existing behavior | Required treatment before a weighted pilot |
| --- | --- | --- |
| BB root accumulator | Adds raw per-deal advantages | Separately typed weighted sums; physical sample counts remain distinct from weighted mass |
| Later-action records | Trace identifies each record's source deal | Preserve and validate that mapping when attaching its deal weight |
| Replay reservoir | Algorithm R uniformly retains visits; no weight field | Store source weight with each retained visit, including checkpoints and exact restore |
| Network fitting | Grouped ordinary squared-error objective | Weighted grouped means and weighted loss, with a direct ungrouped-gradient equivalence control |
| Preflop lookup tables | Means over retained observations | Weighted sums/masses consistent with the fitted objective |
| Exact BTN initial update | Full-population matrix update once per generation | Keep unchanged; do not multiply a population-integrated update by a sampled-deal weight |
| Held-out evaluation | Original physical-deal distribution | Keep unchanged; use ordinary game payoffs |

Multiplying targets and also weighting their loss would double-apply the weight.
Multiplying only targets is not the same finite regression objective as weighting
the original squared errors. These paths require explicit numerical controls;
weighted targets must not be silently inserted into old unweighted checkpoints.

The next bounded implementation step is a separate weighted reservoir/objective
control on synthetic and previously inspected observations, including grouping,
direct gradients, all-ones equivalence, invalid-weight rejection and restart.
Only after those pass should a small fixed-budget training pilot be considered.
Its comparison must charge all preparation, sampling and fitting costs and retain
the baseline. No large training run is justified by this sampler result alone.

Evidence: `class-stratified-sampler-control-v1-registration.json` and
`class-stratified-sampler-control-v1-result.json`. Existing training/evaluation
modules and the production app were not modified.
