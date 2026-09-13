# D12: exact partial-product reuse inventory

Registered before extracting partial-product counts. Diagnostic only, no GPU or
server mutation. Retained C14/R03 runtime and D11 timing evidence remain baseline.
Do not change precision, samples, policies, update order or accuracy targets.

## Fixed proposal

For terminal tasks with two or three opponents (quadrature Q=2), cache the two
products after the first two opponents in their existing order. Key by ordered
normalized-distribution identity pair, with no reordering. Reuse within one
learning seat, or within a retained average-strategy cohort. IDs are local to
learning seats; never combine them across seats. Average IDs are shared.
Keep the existing CDF producer and allocations. This is partial multiplication
reuse, distinct from full terminal tuple reuse and from C03's no-tie calculation.

Cache budget: 512 MiB additional, of which 16 MiB is reserved for mapping and
metadata. Each pair needs 32*169*2*4 bytes for two products across a sample batch.
Use at most floor(496 MiB / bytes_per_pair) pairs per seat/cohort. Minimum reuse
four tasks; rank by descending use count, then lexicographic identity pair.
This optimistic host selection excludes dynamic selection overhead; a successful
inventory only admits a separate prototype, not a runtime change. Any prototype
must account all buffers and remain below 23 GB total planned GPU allocation.

## Gate and accounting

Require both large learning and large accuracy checks to save at least 20% of
D11 terminal source arithmetic AND at least 10% of logical terminal CDF-gather
traffic after including cached-product reads and writes. Both conditions must
pass; do not retune budget, thresholds, prefix length or Q after seeing counts.
Small case is descriptive; any prototype still needs exact results and small
complete-time nonregression under normal research gates.

For each selected key with N consumers: producer costs 14 source FP operations,
4 CDF float reads and 2 cached float writes per hand/sample. Each consumer reads
2 cached floats and saves 14 original operations and 4 original CDF float reads.
Thus savings are 14*(N-1) operations and (2*N-6) floats of logical traffic.
Compare with full D11 terminal operation/gather totals, including unselected and
higher-opponent tasks. This does not reduce CDF construction itself. Multiplication
by initial one may be compiler-eliminated; these remain source-level counts.

Decode hashed D10 witnesses through two independent methods (struct records and
array-index records). Reconcile histograms, baseline identities and D11 totals;
compare complete ordered-pair Counters. Verify selected counts/savings through
independent formulas and archive compact summaries plus source hashes. Bound host
execution to one task; no model or solver training. Snapshot reuse does not prove
reuse persists through learning, nor does logical traffic imply DRAM traffic.

If admitted, exact cached-prefix kernel tests and full arena comparisons must
precede timing. If rejected, leave runtime untouched and record the result.
