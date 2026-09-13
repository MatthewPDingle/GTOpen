# C22: global rank products, separate producer and consumer

Registered before implementation/compilation, following D18 admission. Keep
C14/R03 unchanged. A test-only module first qualifies separate quadrature
products in global scratch, using one producer block per terminal. Rank-group
threads independently process the original sample sequence. A separate consumer
block performs each hand's original ordered sample and quadrature additions.
No per-sample block barriers; no subtotal reassociation, fast math, precision
change, sample reduction, range pruning, sorting or active-terminal queues.

First stage: compare every hand bit for bit with the extracted original narrow
helper. Cover five rank maps (all tied, all distinct, warp boundary, irregular,
real deck), three CDF patterns (zero, dense, staircase), zero/nonzero initial
accumulators, 2..8 opponents, starts 0/1/37/992 and counts 1/5/7/23/31/32:
5,040 cases. Rotate terminal counts/capacities 1/1, 2/1, 3/2, 5/4, 9/4.
Use nonzero terminal offsets, distinct and aliased opponent CDF bases, inactive
terminal holes, and poisoned scratch/output padding. Check every unwritten
sample, group, quadrature and tile slot, not just the final tail guards.
Inactive terminals must leave scratch untouched; consumer must not read it.
Exercise start-zero reset versus later-batch preservation. Synthetic maps may
need 169 groups; production D18 map bound is 104. Fixed Q stride is five in
this generalized test, even when actual Q is lower.

Require all exact comparisons, untouched-slot checks and unchanged original
kernel PTX entries. Candidate producer/consumer use no shared memory, no local
spill allocation and <=128 registers each. These resource gates only admit
integration; they do not demonstrate runtime savings. One guarded build/test,
300-second cap. Preserve sources, compiled PTX, resources and executable hash.

If admitted, separately integrate bounded scratch per D18 and repeat whole
solver arrays, 3..9 players, batch5/32, sparse/zero recovery, aliases/cohorts,
graphs, stop, allocation failure and both saved fixtures. Preserve accumulator
batch boundaries and inactive-node semantics. Actual device allocations and
launch inventory must reconcile with the declared plan. Only then run complete
large control/candidate pair: >=1% improvement admits three alternating pairs
per fixture; retention needs >=3% median large improvement, <=3% small regression,
exact saved checkpoints and full default/native regressions. Include cold
construction/compilation/allocation. Do not extend failed gates for more timings.

One run07-guarded workload at a time, no source edits while running; 56708 stays
read-only. A component gain would not prove the outstanding tenfold convergence
goal. No candidate is selected by a normal production constructor.
