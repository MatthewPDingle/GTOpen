# River targets: weighted insertion and compact transport

2026-09-28. Research only; no live model or production change.

The posterior64 river estimator now passes actual weighted training insertion
checks. Native exports can travel through memory with exactly the same output
bytes and target values, retaining about 98% less conditional intermediate data.
These are integration and storage results, not evidence of better poker ranges.

## Actual weighted insertion

Created one valid 384-deal stratified TRAIN generation, then used its first four
physical deals under both generation-77 policies. The candidate substitutes only
visited river rows after the existing full-action target derivation. It retains
the exact initial targets and all original flop/turn targets. Deal weights enter
once, through the original weighted insertion/fitting contract.

The first control failed its final coverage gate: resetting capacity-7 reservoirs
for every one-deal case never exercised actor 1's replacement sampling. All eight
case outputs and the failure remain retained. Version 2 keeps separate continuous
reservoirs per model across the same four deals, with unchanged target draws,
policies, data and capacity. It does not weaken the gate.

Version 2 passed in 21.281 seconds:

- 131 positive visits; 54 river rows, 50 numerically changed vectors.
- All 11 preflop, 26 flop and 40 turn rows unchanged.
- Both actors exercised Algorithm R: 95 and 8 overflow insertions.
- Visit order, keys, features, weights, counters and random-generator state
  match baseline; every staged target matches an independent insertion oracle,
  including events ultimately discarded by the reservoir.
- Save/reload preserves the result. Seventeen malformed or mismatched inputs
  reject before changing real reservoir arrays, counters or random state.

The target generator binds the current model, context, query, trace, complete
source generation and selected records. Unsupported posterior mass rejects;
there is no invented fallback distribution. Four unchanged river vectors are
valid coincidences, not missing substitutions.

## Memory transport

The new research-only native example accepts a bounded stdin request and emits
the same bounded JSON bytes on stdout. The Python generator retains request
hashes, output lengths/hashes, compressed current-policy arrays, posterior draw
evidence and target rows. It avoids writing the large conditional exports.

All eight qualified cases replayed with exact overlay/policy agreement; all 16
native history/selected outputs matched the old bytes and decoded structure.
Fourteen malformed-input controls rejected without stdout output. The complete
control took 17.297 seconds, including independent replays.

Conditional evidence folders fell from 34,171,727 to 675,122 bytes: 98.024% less
storage (about 50.6 times smaller). This applies to conditional intermediates,
not the entire training archive. Historical exports were not removed.

## What this establishes, and what remains

The estimator's earlier 64-draw unbiasedness and native equivalence checks now
connect to real weighted insertion without changing source weights or sampling.
The next experiment must compare fitted policies from identical training states,
with fresh evaluation deals and complete elapsed costs. The old baseline already
averages future actions at one sampled opponent hand; posterior64 adds averaging
over opponent hands. It still costs more than that baseline. Keep K=64 fixed and
judge policy quality per elapsed time, not just target noise or GPU utilization.

Do not propagate targets selected by sampled visits to full-action ancestors.
Preserve board-root and exact BTN updates, played-policy banks and atomic joint
checkpoint publication. Broader stack/rake/sizing validation remains outstanding.

Evidence: river-weighted-overlay-control-v1-failure.json,
river-weighted-overlay-control-v2-result.json,
river-stream-transport-control-v1-result.json, and
river-weighted-stream-evidence-review-v1.json. Registrations bind executed sources.
