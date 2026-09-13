# C10 proposal: factor-four terminal unrolling against retained C09

C09 is retained: explicit factor-two unrolling changed the 4-8-opponent loops,
kept numerical bits exact and saved 4.2% complete large runtime. Two- and
three-opponent loops were already unrolled automatically. That evidence admits
one controlled factor-four experiment; it does not justify a broad sweep.

Keep C09 as the control. Add a distinct opt-in factor-four research constructor
with separate PTX caching and identical C01/C07 memory planning. Preserve the
single sequential accumulator and all operation/sample order. Do not add
independent accumulators, math approximations, layout changes or sample changes.

Before implementation register its protocol. Expand the direct helper cases
to counts 1/2/3/4/6/7/23/31/32 and nonzero offsets, checking all remainder classes
for O=2..8. Compare original/C01/C07/C09/C10 whole-solver outputs as well as
partial-helper bits, zero recovery and captured runs. Archive and inspect PTX
and loaded attributes; if practical, include actual generated alias-aware
terminal functions in the untimed compiler diagnostic to improve on C09's
base-terminal resource evidence. Code growth and register/local-memory changes
may outweigh reduced loop overhead. Do not interpret register counts alone
as performance proof.

Same six-sweep frozen first large pair: reject complete ratio >=0.99. A passing
screen enters three alternating pairs per large/small fixture, >=3% median
large gain and <=3% median small regression, exact outputs and required GPU/
default correctness regressions. Complete time includes initialization. Use
run07 guards, frozen inputs/executable and source hashes; no edits or other
build/test/GPU work during timing. No CPU performance or writes/restarts on56708.

If factor four fails, retain C09 and use its emitted-code evidence to choose
between a phase re-profile or a different terminal scheduling mechanism;
do not automatically progress to larger unroll factors. The broader quality
and time-to-convergence objective remains unproven.
