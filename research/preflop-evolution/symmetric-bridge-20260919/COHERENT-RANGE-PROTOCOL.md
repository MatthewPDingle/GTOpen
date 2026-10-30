# Additional coherent-range diagnostic (not yet run)

Registered19 September2026. Preserve the original abrupt-input test and
its failure. Do not change its thresholds, fixtures or verdict. No production
change and no GPU execution alongside the active47-board accuracy run.

Code review confirms the original stress calls player p with own weights
`reaches(p,t)` and opposing weights `reaches(1-p,t+13)`. The other player's
pass therefore receives a different pair. Every17th iteration sets each
pass's own range to zero while leaving its opposing input positive. This
is a valid adversarial input test of the API, but not a single fixed pair
of entering ranges shared across both passes. It does not make the failed
independent-trajectory equivalence test irrelevant or permit promotion.

Add two diagnostics using the same three boards, entering hand support,
postflop menus, rake, algorithm,100 iterations and matched full/compact
projection/transport implementations:

1. Abrupt coherent pair: choose both seats' weights once at t, use the same
   pair in both player passes; every17th iteration zero one whole seat,
   alternating which seat. The other pass sees that same empty range.
2. Smooth coherent pair: linearly interpolate each seat's weights from
   reaches(p,31) to reaches(p,47) over100 iterations, shared across passes.

Record same-state CPU versus compact CFVs, immediate root averages,
independent-trajectory CFVs/root averages, independent final average/BR
values, and evaluating the same compact policy with full/quotient traversal.
Keep comparable original tolerances:0.002bb per opposing mass for same-state
and final average/BR values,0.002 immediate root difference,0.01 root drift,
0.0001 same-policy evaluation. A zero opposing range must return zero CFVs
in all paths. Independent trajectory CFV maxima remain descriptive, as in
the original test. These diagnostics do not repeat or replace the earlier
all-node stabilizer audit, which remains part of the overall qualification.

Print every board/mode result before the final assertion so any failures
are preserved. Passing additional controls would narrow the cause; it would
not turn the original stress result green, prove full precision equivalence,
or solve the host-memory allocation issue. Compact GPU storage still keeps
full host arrays in the current implementation.

Compile-only preflight is allowed now in a separate target directory.
Before future execution, verify production idle and no owned reference GPU
worker; freeze the executable, source and kernel hashes in a separate bounded
run. Do not interrupt or extend the current overnight queue. Tests are in
`crates/solver/tests/continuation_coherent_symmetry.rs`.
