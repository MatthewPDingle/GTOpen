# Bounded replay to physical neural fitting

The physical reservoir now connects to a fitter that accumulates a complete
retained-data gradient in bounded chunks. Its fixed-data control passed, including
engine reload on all 7,277 exported observations. This is integration evidence,
not a self-play result or a stronger poker policy.

## Fitting calculation

The fitter groups only identical canonical observations within the current
reservoir. It verifies that each repeated key has the same visible features and
legal action menu. Counts preserve every retained visit's weight; different
hands or histories are never merged because they look similar. Signed advantages
are scaled by one positive RMS value per player, with a 0.01 floor. The scale
includes all four padded output slots, consistently with the earlier physical
fit control. Positive common scale cancels in regret matching.

The objective is squared error over all retained legal action targets. Grouped
mean targets and visit counts give the same gradient as individual visits; the
omitted within-observation variance is independent of model parameters. Dense
269-feature rows and activations are materialized one chunk at a time. Every
chunk contributes to the gradient before the optimizer takes a single step.
Splitting the data does not turn full-gradient fitting into minibatch SGD.

Grouping uses temporary arrays bounded by reservoir size, not a persistent
dictionary of all visited information sets. The caller must freeze the reservoir
during fitting and supplies an activity/resource guard. Empty inputs and
inconsistent repeated keys fail closed. Each fit starts a newly seeded
269–64–64–4 model without consuming the caller's random-generator state. It
exports normalized signed advantages through the existing weight format.

## Registered fixed-data result

Three copies of the bridge fixture fed a capacity-257 buffer per player. This
deliberately exercises replacement and duplicates; repeated data does not add
training coverage. BB retained 257 visits across 213 observations; BTN retained
96 visits across 32 observations. Both networks fit for 64 Adam steps at 0.003,
with chunks of 31 observations and CPU float32 fitting.

| Check | Maximum error |
|---|---:|
| Full per-visit vs grouped/chunked gradient, float64 | 8.33e-17 |
| Chunked vs single-chunk gradient, float64 | 5.56e-17 |
| Loss plus within-observation variance identity | 2.23e-16 |
| Reloaded Rust vs tensor scores on 7,277 observations | 1.44e-6 |
| Reloaded Rust vs tensor legal action probabilities | 4.64e-6 |

Normalized grouped fitting loss fell from 1.6081 to 0.2313 for BB and from
1.5981 to 0.0246 for BTN. Reservoir arrays and sampling RNGs were unchanged;
the caller's tensor RNG was also preserved. Both malformed fitting inputs were
rejected. Sixteen registered inputs and output artifact hashes were verified.
The control took 3.16 seconds, used no GPU and left production untouched.

## What remains

The same implementation accepts CUDA, but this combined chunked fitter still
needs its CUDA execution and gradient checks. The earlier separate GPU fitter
does not substitute for that test. After the active GPU strategic comparison
releases the device, check the full query/inference/traversal/storage/fitting
path together. Then review the method gates before a physical self-play pilot.

Nothing here measures unseen-board performance, exploitability or agreement with
Wizard. Those require separately frozen training and independent evaluation.

Evidence prefix: `sampled-physical-stream-fit-v1`.
