# First test outcome and investigation

The initial two-tone test failed the registered independent-trajectory value
gate: maximum average/best-response CFV discrepancy per unit opponent mass
was 0.0137996 bb (required <0.002). Root average-strategy discrepancy was
0.001126945 (required <0.01). A single step starting from the same state
agreed with uncompressed CPU within 0.000117965 bb; immediate root averages
within 5.96e-8. Input rejection tests passed.

The initial binary/source hashes and log are retained. Do not loosen the
acceptance criteria or treat the wrapper as validated on this evidence.

Next diagnostic run preserves all thresholds and fixtures, but reports all
three boards before failing. It also compares selected single steps against
an uncompressed GPU initialized from the same state, and evaluates one final
policy with both quotient and fully materialized CPU traversals. These help
distinguish a semantic orbit error from floating-point trajectory separation.

## All-fixture outcome

The strict gates still fail; rainbow is identical. The two-tone same-state
GPU replay differs by 0.0000356 bb, while the monotone case differs by
0.0035262 bb. Evaluating the same materialized monotone policy with and
without orbit reuse differs by 0.0058582 bb. This is not explained solely by
two separately evolving runs choosing different strategies.

An added policy audit found that the internally stored strategies do not
retain exact stabilizer symmetry. Root average asymmetry is small
(0.0000153 two-tone, 0.000231 monotone), but some descendants reach almost
unit differences. The latter is a maximum over nodes, including poorly
reached ones; do not interpret it as an aggregate strategy error.

This exposes a missing condition in the new wrapper: symmetric input reaches
alone do not guarantee that floating-point updates preserve symmetry inside
the postflop strategy. The next isolated experiment should explicitly tie
regret/average storage under each node's board-fixing suit group, then compare
against a fully enumerated reference with the SAME hand-symmetry projection.
Keep the original unprojected comparisons as diagnostics and preserve the
failed gates. A canonical-orbit averaging pass requires race-free two-stage
GPU handling (reduce each orbit, then broadcast), not in-place unsynchronized
averaging. Verify same-policy full enumeration first, then whole-game values.

This candidate is on `codex/continuation-symmetry-research`. No production
kernel, fixed-range solve path or deployed binary was changed. The candidate
has deliberately failing research tests and must not be merged to master or
used for larger strategic claims until addressed.

## Explicit projection and transport

Projection over each node's stabilizer removes all measured current/average
policy asymmetry. Independent CPU group averaging and recursive public-card
materialization agree exactly with both GPU operations on flop and turn
fixtures (`projection-transport-unit.log`). Same-state CPU/GPU comparisons
and evaluating the same policy through full versus quotient chance now pass.

The abrupt-changing-range fixture still fails its strict independent-path
value gate even after both implementations use matching public transport:
0.022339 bb two-tone and 0.016563 bb monotone, against the unchanged 0.002
threshold. Root strategy differences remain below 0.001. Preserve that failed
test; a separately evolving, poorly converged stress trajectory is not an
equivalence certificate.

Registered fixed-range 2,000-iteration diagnostics pass. Full versus compact
aggregate EV differences are 0.00004234 bb and 0.00001249 bb, with combined
deviation gains about 0.0022 bb and 0.0004 bb. The largest per-hand two-tone
value difference is still 0.002297 bb per unit opposing mass, recorded as a
diagnostic rather than hidden behind the aggregate.

The two-board connected diagnostic also passes its registered gates. Both
total gains are about 0.0021 bb; maximum aggregate EV difference is
0.000005687 bb and common-entry-prior root policy TV is 0.000008969. Independent
pair normalization, frequencies, hand summaries, terminal probabilities and
cash conservation pass. See `connected-two-review.json`. The ten-board
connected comparison is pending. This work remains research-only.
