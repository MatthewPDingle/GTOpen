# Next prototype: explicit fixed units for research history updates

The numerical conversion identity passed; naive array rescaling failed policy
preservation at the existing 1e-12 normalization floor. Test an alternative
representation, not a silent change to the original compact copyback API.

Keep stored local regret and average arrays unchanged after a compact solve.
Associate each learning node with two positive fixed units:

- regret_unit = product of incoming branch masses for opponents of its actor;
- average_unit = the actor's incoming branch mass.

During subsequent full-tree GPU learning, add `global_regret_increment /
regret_unit` and `global_average_increment / average_unit` to those arrays.
Nodes outside refined branches have both units 1. Preserve native value
propagation and probability normalization, including full evaluation. Units
are fixed between explicit refinements, not recalculated from each iteration's
reach (which would repeat the rejected dynamic-normalization experiment).

Do not modify histories at forced/frozen nodes. Reject invalid dimensions,
nonfinite/zero units, underflow/overflow-prone values, overlapping ownership or
unsupported research combinations before mutation. Explicitly record branch
roots, reference incoming masses, local/global iteration ages and units. Keep
the existing parent and untouched-neighbor histories, so later full GPU passes
can adapt ancestors and neighboring continuations together.

This is a synthetic warm start, not a reconstruction of one true historical
CFR run. Local and global discount ages differ. An initial implementation must
declare that limitation, use a pre-registered schedule, and not mark ordinary
saved-game resume as supported. A read-only saved-policy audit is still useful,
but continuing a research save requires its checked unit metadata; no silent
fallback when that metadata is absent or does not match the save.

Before learning trials: unit-one bitwise native equality; unequal-unit GPU
increments against an independent arithmetic reference; value/average policy
preservation; frozen/locked nodes; all affected depths; zero/invalid admission;
and captured/eager execution with full native final evaluation. Include the
tiny-history example without changing its stored probabilities. Quantify extra
GPU memory and keep operations serial and guarded from live user work.

Then register a small saved-game refinement-plus-full-continuation screen,
including a matched control, global and conditional outcomes, runtime and
maximum-iteration gates, before executing it. Do not promote this based merely
on the scaling identity. Large 0.005-bb global and all-27 conditioned quality
requirements remain unchanged. Port 56708 remains excluded.

## Kernel proof stage (registered before execution)

Test the standalone research kernel before exposing any continuation API. Use
the existing four-seat, 526-node raw and calibrated fixtures with signed regrets,
a frozen seat and a point lock. Reset histories for every traverser. Cover all
11 levels, unit-one bitwise native equality, unequal per-node units and graph
replay versus eager execution. Units are 1 for fixed nodes; selected learning
nodes use dyadic/non-dyadic units in [0.001, 1]. Compare unequal-unit increments
to independently transformed native increments with absolute tolerance 0.002
(the subtraction reference loses precision before division); propagated values
must agree within 0.0002 bb. This is a kernel arithmetic test, not a convergence
or accuracy result. The standalone kernel has no public admission/resume API;
validation, metadata and integration remain required before learning trials.

## Full-iteration integration proof (registered before execution)

Initial internal admission accepts one immutable unit pair per node, each
finite and in [1e-8, 1]. The reciprocal scale is thus at most 1e8; this is an
admission limit, not a guarantee against every possible future f32 overflow.
Reject dimensions, non-unit fixed/terminal nodes, an already configured unit
engine, prior learning/evaluation, sampled/scheduled research, masks, custom
roots and all other optimizer experiments before publishing new state. Both
configuration orders must reject combinations. No public saved-game continuation
API is enabled by this stage. Unit allocation must fit an explicit extra-byte
budget. Stable buffers persist for the engine lifetime.

Test raw/calibrated four-seat fixtures at global iteration 17 through 21,
unit-one equality to native, unequal captured/eager complete iterations,
finite histories and unchanged frozen/locked histories. Compare native final
evaluation to a fresh ordinary GPU loaded with the resulting histories.
Independently check the existing native DCFR discount arithmetic after one
manual sequential sweep with fixed units. No discount age reset: preserve
the global counter. This tests mechanics only; branch ownership, save hashes,
local-age declarations and matched convergence screens remain required.

### v1 integration test correction

The first integrated run rejected two test assumptions about native discount,
not the up-kernel arithmetic: `pf_discount_nodes` decays all regret arrays,
including frozen/forced nodes, and preserves average sums only for frozen
src=1. Forced src=2 actions use separate immutable forced metadata. Correct
the full-iteration invariant to matching native fixed-node bookkeeping and
unchanged fixed policies. Do not alter the production discount kernel or
weaken unit-one native equality. Host discount checks must include every
action node, excluding only frozen averages from decay. Preserve the failed
v1 evidence and add both-order and late-admission coverage in v2.

### v2 arithmetic correction

Admission and independent host discount passed. Unit-one full iterations
differed from native by approximately 1e-9 bb in evaluation, despite the
single-sweep identity. The extra division changes available compiler fusion
for the average accumulation. v3 explicitly uses the native expressions when
the corresponding unit equals 1; retain bitwise full-iteration equality as
the gate rather than relaxing it. Re-run standalone arithmetic tests too.

### v3 diagnosis and v4 correction

The explicit arithmetic expressions did not remove the unit-one discrepancy;
compiler fusion alone was not established as its cause. Source comparison
shows native pf_up dispatches action-count-specialized pf_up_impl<2/3/4>,
whereas the prototype had a runtime action loop. For nodes with both units 1,
v4 calls those exact native implementation specializations. Unequal nodes
retain explicit scaled updates. Keep the failed v3 evidence.
