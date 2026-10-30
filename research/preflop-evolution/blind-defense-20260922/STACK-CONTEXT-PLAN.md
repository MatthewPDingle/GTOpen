# Stack-aware preflop research: required extension

User requirement, 2026-09-23: stack sizes are essential to deciding which hands
continue preflop. This is part of the flexible-model objective, not an optional
cosmetic input. The 200 bb representation trial is a fixed-depth diagnostic.
It cannot qualify transfer to other depths.

## Current verified behavior

The native game uses configured stack, committed chips, action history and
remaining stacks for legal actions and payoffs. Observation v1 represents cards,
actor, phase, public node and history in a single frozen context. Stack and pot
are implicit in that context/history; there is no explicit cross-depth numeric
stack input. Context hashes prevent accidentally reusing a model with a different
configuration. The 33 appended visible summaries only describe cards/boards.

Do not feed identical public-node IDs from different trees into one model and
assume it learns stack depth. Direct-table keys and histories also need context
separation. The current equal-stack heads-up study does not establish behavior
for unequal stacks, side pots or multiway stacks.

## Next extension, after the isolated representation test

1. Add a versioned public-state encoder with starting and remaining chips for
   both players, effective remaining stack, pot, amount to call, chips already
   committed, and stack-to-pot ratio. Use consistent bb units with bounded or
   logarithmic transforms where useful. Include actual legal raise-to amounts,
   all-in indicators and action masks; action index alone is not a sizing input.
   Only public information may be used. Preserve exact context metadata.
2. Independently reconstruct these numbers from native histories; test preflop,
   each postflop street, calls, raises, all-ins and zero-call checks. Ensure no
   collisions across stack depths. Context-aware table/checkpoint/cache lookup
   must reject a mismatched tree, even when node IDs and hole cards coincide.
3. Establish small fixed-context reference solves at 20, 40, 100, 200 and 400 bb
   under matched game rules. Fix the incoming priors where possible to isolate
   continuation effects, and explicitly distinguish that diagnostic from a
   full preflop solution in which opening/3-betting priors must change too.
4. Train across contexts with balanced sampling and explicit budgets, then hold
   out entire depths (for example 60 and 150 bb) from fitting and tuning. Compare
   a shared model with separately trained context models under the same budget.
   Split by context as well as deals; a held-out board is not a held-out stack.
5. Report calibration/decision errors, restricted deviation tests and uncertainty
   by depth, seat and hand group. Do not require arbitrary monotonic hand rules:
   stack depth changes implied odds, domination risk, jam pressure and sizing
   incentives together. Similar aggregate frequencies do not prove portability.

A useful eventual model must respond to changes in stack and price. No current
fixed-depth result should be presented as satisfying that requirement. Production
and the existing range preview remain unchanged until separately validated.
