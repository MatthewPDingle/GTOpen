# Owned branch continuation: mechanics pass, small convergence screen rejected

Research only; no production deployment or mutation of port 56708. CPU work
was limited to state validation and conditional correctness evaluation.

## Implemented and tested

FixedUnitResearchState binds disjoint branch roots and learning-node ownership
to reference masses, local ages, retained global age, immutable per-node units
and one unmoved solver. A deterministic word checksum covers arena bit patterns,
tree geometry, configuration, constraints and model metadata; it detects
accidental changes and is explicitly not cryptographic. Runner artifacts carry
SHA-256 for source, executable and input files. State is invalidated before
GPU continuation work and cannot be reused after a device/admission failure.
Missing or mismatched persistent metadata cannot be guessed: there is no
persistent resume API. The existing ordinary .gtop format is unchanged.

Both raw and calibrated tests performed actual compact refinement of two
branches, verified all factor assignments and untouched copyback regions, then
continued globally. Two one-iteration calls matched a two-iteration call
bitwise, including native final evaluation. Rejection tests covered duplicate,
overlapped and invalid roots; changed history/configuration/tree/age; another
solver owner; cancellation; and poisoned state. Two tests passed in 86.109 s
including compilation (test body 2.28 s). The screen driver built successfully.

## Registered six-player screen

Each saved input was run as native full-GPU continuation control and as two
1,000-iteration compact refinements followed by fixed-unit full-GPU continuation.
The six historical paths were checked initially and every 25 added global
iterations, up to 250. All six paths and a <=0.005-bb summed global gap had to
pass at two consecutive checkpoints. Inputs, schedule and thresholds were
registered before learning in FIXED_UNIT_CONTINUATION_SCREEN.md.

| Input | Mode | Total seconds | Final global gap bb | Conditional passes after refinement / final |
|---|---|---:|---:|---:|
| Native save | Control | 18.388 | 0.00182326 | 2 / 2 |
| Native save | Fixed units | 25.852 | 0.00361805 | 4 / 2 |
| Sampled save | Control | 18.956 | 0.00210616 | 2 / 2 |
| Sampled save | Fixed units | 24.985 | 0.00398520 | 4 / 2 |

These totals include setup, learning, repeated engine construction, audits and
save validation after input loading; process totals are also recorded. They
are not persistent-engine throughput measurements. No candidate or control
qualified on combined quality. The candidates cost more and did not improve
final conditional coverage. All final saves round-tripped exactly, and separate
read-only saved-policy audits reproduced every final hand value/probability.
The independent verifier recomputed all 44 check gates and all branch factors.
No large trial was admitted.

## What changed during continuation

Both candidates initially passed the two selected branch roots and two other
paths, then lost the new conditional passes by the first 25-iteration check.
In the native-save BTN limped-pot branch [1,0,0], 99 initially raised with
99.9954% frequency: raising was worth +0.4682 bb versus +0.3128 for limping.
After 25 full iterations its average still raised 93.1976%, but those action
values became -0.1800 and +0.2570 bb. The target continuation changed; this
example alone does not establish that average-history inertia is the sole cause.

Final diagnostics narrow that hypothesis: current policies also failed the
same four one-action checks against average continuation values. Relevant hands
had no uniform fallback. For the native candidate the four failing current
worst bad-action masses were 0.7046, 0.5834, 0.6023 and 0.8079; the corresponding
average-policy masses were 0.8137, 0.3315, 0.7354 and 0.4965. These are one-action
deviations against the average continuation, not full current-policy BR audits.
Therefore replacing average output with current policy is not a qualified fix.

## Additional evidence / next discriminator

A previously missing conditional audit of archived gamma15, 64-particle dynamic
regret-normalization runs found 4/6 and 5/6 passes at 1,000 iterations, versus
2/6 for their controls. They still failed the global gate (0.009826 and 0.016286
bb) and retain their original rejection. No new learning occurred in this review.
The earlier global-only speed comparison did not establish equal conditional
quality, so it cannot support a qualified speed ranking.

Next test the sampling-noise explanation directly: compare normalized updates
with 64 versus all 1,024 particles under the same gamma15 schedule and original
1,000-iteration ceiling, with native-update controls and both global/conditional
gates. Keep full-particle checks canonical. Register the exact protocol first;
do not extend failed iteration caps or weaken quality. This may rule out the
optimizer, identify a variance problem, or motivate a different method. Large
0.005-bb and all-27 conditional qualification remains incomplete.
