# C06: shared cohort CDFs in average checks

Registered after D05 admission and before implementation/benchmarking. Baseline
is retained C01 with D03 optional tracing off. D04 and D05 are diagnostic only.

## Mechanism and allocation

Compute static player-membership histograms from the engine's multiway work
spans on the host. Enumerate partitions of groups1-4 and choose minimum static
union work under the D05 full23GB budget, then total memory and lexical masks.
Use the same deterministic selection as the independent D05 checker. This
selection must not read current strategy arrays or require a GPU download.

Add an explicit opt-in research constructor/allocation plan. It must allocate
the final enlarged CDF/normalized/classification buffers directly, without
coexisting old/new CDF arrays. Include group maps/worklists, up to three full
value arenas and probability buffers, all existing engine buffers and256MiB
reserve. Reject an over-budget plan before allocating its large arrays. Keep
batch32, stride170, all1024 particles and the original HU cache. Report exact
device-buffer byte totals. D05 large plan22.924GB leaves little registered
headroom; do not silently reduce the baseline cache to make the prototype fit.

## Dispatch and invariants

Keep learning dispatch and all solver updates unchanged. Evaluation performs
the original one common average down sweep. For each cohort, construct its
normalized union and exact169-bit aliases once. Prepare each player's original
terminal counterfactual probabilities and ordinary terminal results. Keep each
player's complete terminal value accumulation in a separate d_val buffer.

For each original32-particle batch, construct the cohort's representative CDFs
once, then run each player's original multiway terminal arithmetic against that
CDF and its own values/probabilities. Preserve per-hand particle and batch
addition order. After all batches, perform each player's existing constrained
or unrestricted BR up sweep, average up sweep and root copy. Restore the main
value-buffer identity before returning. Graph capture must retain valid stable
addresses; no host download/synchronization in a captured evaluation path.

Do not reuse average CDFs across learning updates/checks, alter zero-mass guards,
merge opponent multiplicity, change quadrature or introduce approximate identity.
All maps must cover exactly the same per-player sources as the original spans.

## Qualification and timing

Before performance screening, validate static grouping/mapping and memory plans
against D05 on both saves. Unit tests cover odd seats/singletons, all supported
player counts, empty/zero slots, overflow, allocation rejection and deterministic
ties. Compare original/C01/C06 prefix and terminal outputs plus full learning
arenas, gaps/EVs, locks, frozen/forced seats, zero own/opponent reach, recovery,
stop/sync and repeated checks. Exercise eager/captured execution and batch5/32
in small tests; real timing uses unchanged32. Errors must leave an owned engine
consistent or fail before use, never publish half-initialized research state.

Use the existing six-iteration frozen benchmark, two warmups, check each sweep.
Every paired checkpoint and final full arena fingerprint must match bit for bit.
First large control/candidate pair: reject if complete-time ratio>=0.99. If it
passes, run three large and three small paired comparisons with alternating
order. Retain only at least3% median complete-time gain on large, consistent
direction and no material small regression (3% threshold), plus required native
GPU and default solver regression suites. All startup/allocation/synchronization
cost counts; kernel-only or eager-profiler gains are insufficient. Optional
diagnostic timing must be separately labeled and excluded from the graph.

Build/test cap240s; each benchmark cap180s; numerical suite cap240s. run07 serial
guard, one workload at a time, no edits while timing. Source/input/executable
hashes frozen; retain failures and rejected source artifacts. No deployment or
restart on56708. A passing throughput candidate does not prove the broader
large-game conditional convergence objective has been achieved.
