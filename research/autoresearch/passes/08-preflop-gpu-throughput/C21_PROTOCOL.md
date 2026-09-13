# C21: predicate-driven scan inside the exact-zero bypass

Registered before compilation. C20 preserved all outputs but added 25.93%
static PTX instructions. This changes the nonempty branch implementation:
reuse the up-shuffle's source-valid predicate to guard each round-to-nearest
addition. Preserve C20's warp-wide exact-zero vote and all original carry,
load, store, index, sample, precision and alias behavior. No positive cutoff.

C12 already tested predicate-driven addition alone and found no repeatable
complete-work gain (0.16%). This is not a repeat of that standalone proposal:
the hypothesis is that it removes C20's duplicated lane tests/selects enough
to make skipping empty tiles worthwhile. No C12 gain is assumed or chained.

Append a separate sparse-predicate kernel. All 20 original entries, including
the accuracy-check writer, must remain identical. Later integration selects
the candidate only for learning, before graph capture, with no new GPU arrays.

Stage1 cap300 seconds: same 1,008 exact GPU prefix/guard cases as C20, including
negative/mixed zeros and positive subnormals; compare against retained C14.
Require zero spills/shared memory, <=48 registers, candidate static PTX count
<=120% of original, six real zero-vote branches bypassing all five scans, and
30 shuffle-valid-predicate round-to-nearest additions. No arithmetic
reassociation or fast math. Stage1 only admits full solver qualification.

If admitted, repeat whole solver arenas/roots/terminal outputs, 3..9 seats,
batch5/32, fixed/learning, zero recovery, graph/eager, stop and constructor error
recovery. Audit original-check versus sparse-learning function selection and
unchanged small/large allocations. First complete large pair must improve
>=1%; retention needs three alternating pairs/fixture, >=3% median large gain,
<=3% small regression, exact saved checkpoints and full default/native tests.
Include cold module/compile/allocation costs. No extra timing of a failed gate.

One run07-guarded workload at a time. Port 56708 remains read-only. No source
edits during workload execution. This component does not resolve the tenfold
complete-solve/convergence goal by itself.

Instruction semantics checked against NVIDIA's PTX ISA: the optional shuffle
predicate is true when its source lane is in bounds. Up-shuffle clamp0 and
steps1/2/4/8/16 reproduce lane>=step. Inline PTX uses a read/write float operand
and scoped registers, as in the separately validated C12 implementation.
Sources: https://docs.nvidia.com/cuda/parallel-thread-execution/index.html#data-movement-and-conversion-instructions-shfl-sync
and https://docs.nvidia.com/cuda/inline-ptx-assembly/index.html .
