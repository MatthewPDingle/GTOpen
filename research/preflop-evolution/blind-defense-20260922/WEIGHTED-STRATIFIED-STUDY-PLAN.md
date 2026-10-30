# Fixed-budget class-stratified training comparison

Test whether complete BB starting-class coverage reduces training instability
without changing the intended physical poker distribution. This remains the
restricted 200bb BB-versus-BTN spot, not a full preflop solver or deployment.

Use the completed, independently read-back baseline arms 9266201-baseline and
9266301-baseline from showdown-matched-training-v1. Train two stratified arms
with the same seed identities, 78 generations, 512 deals per generation, eight
64-deal subbatches, 262144 retained visits per player, 512 Adam steps, chunk4096,
learning rate .003, initial architecture, exact initial all-in targets and
postflop conditional-action targets. Omit the unsuccessful showdown correction.
Seed identities are matched, but different samplers do not give identical deals
or identical subsequent action histories. Baseline results were already known;
this is a prospectively fixed candidate comparison against historical controls.

The candidate guarantees at least three deals per class each generation, with
five extra allocations. Source-deal importance weights flow through the loss,
root regrets and preflop tables; actual visit counts remain distinct. Do not
silently drop weights or reinterpret equal class sampling as natural frequency.
The checked two-worker pipeline and V2 shared CUDA stream preserve the ordered
algorithm. Fitting and inference keep their established numerical precisions.

## Fixed outcomes and gates

- All generations must pass source, target, checkpoint and reservoir readback
  before any strength claim. Validate resumed state and registered source bytes.
- Compare every hand class, aggregate frequencies, class coverage, and movement
  between consecutive policies. Primary descriptive stability is cross-seed BB
  root total variation weighted by the unchanged original entry distribution.
- Average all played generations 0 through 77 using weights 1 through 78 and
  each player's own-action reach, as in the prior final evaluation. Exclude
  unplayed generation78. Do not select a favorable intermediate checkpoint.
- Conduct a new fixed 65536-deal common-sample crossed-policy evaluation using
  unchanged poker payoffs. For each seed, compare new versus old BB against both
  old/new BTN, and new versus old BTN against both old/new BB (eight contrasts).
  Predeclare evaluation seed9278101. Reuse the prior bounded empirical-Bernstein
  simultaneous95% method with Bonferroni across all eight contrasts, one final
  look. Preserve ordinary paired standard errors as secondary descriptions.
- Less cross-seed variation alone is not better play. Report all gains and
  uncertainty, including unfavorable or inconclusive outcomes. This study cannot
  establish accuracy across other positions, stack depths, or multiway games.

## Resources, restarts, and evidence

Check competing workloads before launch. Require production idle/closed, no other
research lock, low CPU/GPU use, at least6GB free VRAM,20GB free RAM and50GB free
space on T. During work retain4GB VRAM and the RAM/disk headroom; stop on production
activity. Two bounded CPU workers overlap preparation with GPU inference, then
join before fitting. Keep helpers hidden. No production state is modified.

Use a new NTFS-compressed T research directory. Cap logical evidence at80GB with
2GB pre-generation reserve; free-volume checks also protect against allocation
overhead and unrelated use. Save complete state after each generation. A stopped
or failed partial generation is retained and retried in a uniquely named folder
from the last complete checkpoint. The12-hour per-invocation cap is operational,
not outcome-based stopping. The fixed78-generation endpoint remains unchanged.

First run two real-budget generations and resume at the saved boundary before
continuing. This checks the larger reservoir/fit settings without a separate toy
study. The coordinator records progress and source hashes; final training does
not imply independently verified training or a successful strength result.
