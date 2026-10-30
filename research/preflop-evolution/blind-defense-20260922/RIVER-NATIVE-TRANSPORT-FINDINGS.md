# Native river substitution controls

Completed 2026-09-28: all 24 configurations passed in 6.42 seconds, CPU only.
This qualifies one target substitution per fixture, not a complete trainer,
simultaneous nested replacements, improved preflop ranges or faster convergence.

The separate candidate traverses the same branches and consumes the same RNG
draws as `policy_walk_allin_v1.rs`. After descendants have been recorded, it can
replace an updater river decision's complete action vector. The common policy
mean centers the regret vector and supplies the returned value to ancestors.
No source-deal importance weight is inserted into payoffs or regret targets.

## Evidence

- Twelve frozen native situations, each with a positive fixture policy and a
  zero-own-history variant: 24 configurations. The hand-dependent fixture
  probabilities are fully specified on exported keys and uniform elsewhere.
  These are engineering control policies, not the played learned policies.
- 576 preflop-root passes compared the old sampler, the candidate with no
  replacement and the candidate with replacement enabled, across both seats.
  Disabled values and records were exactly equal to the old sampler. All
  14,851 sampled decision records, policy query sequences and final RNG states
  matched between enabled and disabled traversal.
- Twenty replacements were actually reached from the preflop root. Some deep
  histories were not sampled by these 12 seeds per fixture. An additional 288
  target-root passes guaranteed direct coverage for every configuration.
  This is not a claim of complete preflop-root coverage for every deep case.
- The independent parent-graph calculation matched all action values, regret
  vectors and ancestor returns within 3.56e-15 bb. Descendants were retained;
  opponent records and decisions outside the affected ancestor path matched.
- Finite sums over all 990 legal opponent pairs matched source-weighted action
  and regret expectations within 2.23e-15, using both entry-proportional and
  unequal proposals. All 12 zero-own variants retained their counterfactual
  targets. Applying the importance ratio twice was detected in 12 nontrivial
  unequal-proposal controls. Entry-proportional weights are one on support, so
  those controls cannot distinguish applying that ratio twice.
- Seven malformed requests were rejected: arity, illegal vector padding,
  mismatched context, mismatched policy identity, duplicate keys, negative
  probabilities and nonfinite values. No rejected request produced an output.

The fixture uses a shared 0.5 preflop all-in equity solely to compare unchanged
leaf handling; it does not substitute that value into any learned game.
All native source and input hashes were verified after the run (134 inputs).
Retained evidence was 17.28 MB. No GPU, historical cleanup, training, production
changes, application restart or GitHub push occurred.

## Remaining integration

The callback deliberately does not invent an unsupported target. The next
transport layer must bind every supplied vector to its current model and
context, omit unsupported vectors explicitly, and preserve the old sampled
behavior where no qualified vector exists. The current fixture controls have
positive opponent support; the preceding learned-policy pilot retained one
unsupported case separately.

Next measure a bounded actual-current-policy batch: keep the original trainer's
exact initial/board-root overrides, discover sampled river visits, group common
visible states, reuse query preparation and inference, and replay identical
deals/seeds. Qualify multiple nested targets before enabling them together.
Measure complete preparation, export, inference and update cost against the
unchanged sampler, not just the replacement hook. Source weights still enter
once at the original ingestion step. Only then register matched self-play and
a fresh full-policy evaluation. Frozen final deals remain unavailable for tuning.

Evidence: `river-native-transport-control-v1-registration.json`, matching
`-result.json`, and per-configuration inputs/native outputs under
`river-native-transport-control-v1/`. Executed sources are immutable.
