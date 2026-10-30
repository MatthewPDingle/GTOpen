# Decision after the river-bounds pilot

The fixed 4,096-deal pilot and independent readback completed. All eight paired
mean gains were positive, ranging from 0.0000373 to 0.0011646 bb per entry to
the restricted 200bb BB-versus-BTN subtree. All registered simultaneous bounded
intervals include zero. Four descriptive approximate intervals exclude zero,
all in Run B; those are neither a separate acceptance gate nor the registered
finite-sample guarantee. Preserve all eight comparisons.

The correction is numerically qualified and reduces impossible value
predictions. This pilot does not qualify it for production, establish a stronger
preflop equilibrium, or explain the broad opening/calling discrepancies. The
preflop tables were deliberately held fixed. A later retraining experiment could
have different effects, but this test supplies no evidence for their size.

## Do not spend a large confirmation budget here yet

The prospectively requested three-standard-error planning calculation returned
89 deals for a half-width of 0.01 bb per entry. That number is **not** the sample
size needed to confirm these much smaller gains. The pilot already has more
precision than that coarse planning target. Its observed gains are below the
target, and the simultaneous bounded intervals remain much wider because they
allow worst-case 200bb outcomes without distributional assumptions.

Do not extend the pilot or choose a favorable run/role. Keep the correction as
a research candidate and prioritize the previously written conditional-river
diagnostic. No new production setting, model replacement, or coadaptation run
is justified by this pilot alone.

## Next concrete work

Implement and qualify the native visible-history exporter in
`BOARD-RIVER-OPPONENT-REACH-PLAN.md`, then evaluate its 80 already fixed cases
against each complete original opponent bank. Use exact entry weights, card
removal, and the opponent's action likelihoods. Preserve flop/turn/river order
from the observation keys: the separate uniform-equity helper sorts all five
board cards and must not be used to reconstruct earlier-street histories.

This asks whether single sampled opponent outcomes are hiding larger
decision-value errors that can be reduced through better training targets.
It is a local reference calculation against fixed opponents, not a full best
response or proof that another preflop range is correct. Mark zero hero reach
as off-path and zero opponent reach as unsupported rather than inventing a
range. If the diagnostic finds a useful error pattern, design a bounded
training or variance-reduction comparison before collecting a larger dataset.

## Resource evidence

The resumed pilot completed 4,064 remaining hands in 898.922 seconds, including
startup inventory and model loading. A separate first invocation had saved the
initial 32-hand checkpoint, and an actual process restart replayed the same
sampler/statistics prefix. Independent readback checked 128 archives and
1,860,751 queries in 47.75 seconds using eight CPU workers.

Retained pilot files: 66.70 MB. Peak own CUDA tensors: 0.270 GB; allocator
reservation: 0.336 GB. The original fixed 10 GB free-memory check unnecessarily
blocked this workload. Execution v2 uses a hard 4 GB tensor-allocator budget
plus 2 GB external headroom, shares light desktop activity, and still yields
to heavy GPU activity or active production solves. The revision preserved the
fixed seed, policy calculations, transport, sample count and scoring.

Recorded batch stages totalled 28.752 seconds of native query generation,
438.492 seconds of policy averaging, and 31.981 seconds of native evaluation.
The averaging timer includes CPU preparation and GPU work; it is not GPU busy
time. Remaining wall time includes source checks, startup, serialization,
archive work, checkpoints and resource checks. Do not infer the next bottleneck
from utilization percentage alone.

No historical archives were deleted and no production server was changed.
Both research locks were released after verification. The broader preflop
research goal remains active.

Evidence:

- `weighted-complete-river-bounds-pilot-v1-result.json`
- `weighted-complete-river-bounds-pilot-v1-independent-review.json`
- `weighted-complete-river-bounds-pilot-v1-analysis.json`
- `BOARD-RIVER-BOUNDS-POLICY-PILOT-FINDINGS.md`
- `board-river-opponent-reach-v1-selected-cases.json`
