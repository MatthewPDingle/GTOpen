# D12: partial opponent-product caching rejected

There is too little reusable work under the fixed proposal to justify a GPU
prototype. Even optimistic selection misses both admission thresholds. Keep
C14/R03 unchanged; do not tune this inventory's budget or gate after the result.

| Fixture / operation | Selected keys across sequential groups | Consumer tasks covered | Source arithmetic saved | Logical terminal traffic saved |
| --- | ---: | ---: | ---: | ---: |
| Small learning | 132 | 945 | 3.12% | 1.40% |
| Small checks | 646 | 3,229 | 5.85% | 1.94% |
| Large learning | 16,394 | 107,136 | 3.64% | 1.70% |
| Large checks | 30,464 | 188,365 | 2.97% | 1.30% |

Required large-case reductions were 20% arithmetic and 10% logical terminal
traffic in both learning and checks. Counts include cache construction, product
reads and writes. They exclude lookup/selection overhead, so this is already
optimistic. Probability-table construction would remain unchanged.

The cache holds at most 12,021 ordered identity pairs at one time. Learning
seats and average-strategy cohorts run sequentially, so the summed selected-key
counts in the table are not simultaneous capacity. Two large check groups fill
the capacity; learning groups do not. The proposal reserved 512 MiB additional
memory, including 16 MiB for maps/metadata, but did not allocate GPU storage.

Two independent decoders agree on every eligible pair Counter and terminal
histogram in both hashed D10 witnesses. Inputs reconcile with D11's work census;
the separate checker verifies run provenance, hashes and arithmetic/traffic
accounting. The guarded host-only run completed successfully in 6.11 seconds.
No solver learning, kernel build, GPU prototype or production mutation occurred.

This rejects caching the first two opponents for Q=2 under the registered
budget. It does not rule out every algebraic or structural optimization. Snapshot
reuse also cannot establish reuse throughout a changing learning trajectory.
Logical traffic is not measured DRAM traffic, and source operation counts are
not executed-instruction counts. No performance graph point is added.

[Protocol](D12_PROTOCOL.md), [census](raw/d12-prefix-census.json),
[extractor](d12_prefix_census.py), [independent record/accounting checker](check_d12.py),
[verification](raw/d12-verified.json).
