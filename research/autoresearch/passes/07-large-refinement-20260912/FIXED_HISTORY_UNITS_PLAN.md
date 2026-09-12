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
