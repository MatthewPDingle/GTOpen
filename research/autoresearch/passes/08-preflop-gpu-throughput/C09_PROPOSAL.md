# C09 proposal: partial terminal sample-loop unrolling

Continue from retained C07 plus test-only D06 tracing. C08 was exact but slower;
its shared-memory code is removed. D06 still identifies terminal evaluation as
the largest phase. The earlier pass03 terminal-sample-unroll proposal was never
compiled or measured, according to its README and recorded findings.

Try only factor TWO first. Generate an opt-in terminal-helper variant with
`#pragma unroll 2` on the local/sample_count loop. Retain a single sequential
float accumulator and identical q/t/sample ordering. Do not add a second sum,
prefetch buffer, layout change, extra shared memory, fast math or altered
particle count. Compile variants directly in the fresh C01/C07 research
constructors with separate cached PTX. Do not alter the production constructor
or replace functions after graph capture. Keep C07's global allocation plan.

Before implementation, register a protocol defining partial-count tests and
timing gates. Compare original/C01/C07/candidate terminal and arena bits. Add
focused tests for sample counts 1/7/23/31 and relevant nonzero sample offsets;
whole-solver tests still use original batch 5/32 and 1,024 samples. Cover all
2–8 opponent templates, zero-mass clearing/recovery, frozen/locked seats and
capture/replay. Inspect the generated kernel/PTX or function resources to
confirm what the compiler emitted; source intent does not prove unrolling or
an efficiency gain. Keep diagnostics outside timed runs.

Use the same frozen six-sweep paired benchmark against C07, first-pair >=0.99
rejection, then three alternating pairs per fixture and >=3% median large gain
with <=3% small regression and all required regressions for retention. Complete
time includes initialization, checks and synchronization. No CPU performance,
concurrent GPU workloads or edits during timing; run07 guard and immutable
provenance required. No writes/restarts/deployment to port 56708.

Risks: NVRTC may already unroll or decline the hint, additional live values
may spill or reduce occupancy, and compiler transformations may change bits.
Any of those can reject this attempt. Do not automatically layer factor four
onto a failed factor-two run without reviewing its evidence first.
