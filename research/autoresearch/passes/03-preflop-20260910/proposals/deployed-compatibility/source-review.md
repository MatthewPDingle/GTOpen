# Second source review of layered minimal/deployed patches

Read-only review against the full proposed sources and installed cudarc0.19.7. No hardware or compilation was performed. One test defect was found and corrected before execution: the HU cached/direct test manually replaced reaches/masses but did not refresh d_eq_cache. The proposal now explicitly launches f_equities on the all-seat work span before comparing. Normal production paths populate HU caches in down(), so this was not a production defect. Both layered patches were regenerated after the fix.

## Allocation and pointer paths

Minimal construction sets prepared=false, normalized=false, compact=0; resets physical capacity to union slots; uses original fixed metadata; and chooses the original reference batch/cache. Active, probability, normalized, and compact buffers use stream.null() with zero lengths. Installed cudarc implements this using a zero-byte driver allocation, no read/write events and len0. Actual driver acceptance must be established by the focused minimal GPU test; source review alone cannot establish that.

The null buffers are not read: prepare/clear/normalize launches are skipped; direct CDF sees gate0 and compact0; the minimal terminal receives d_reach_mass in the probability argument position and never reads d_mw_prob. Its compact-pointer branch is disabled. The original slot map, reach-source map, CDF allocation, terminal list and rank data remain present. The preferred entry/kernel body remains unchanged. Removing all four extra allocations avoids hiding placeholder bytes in an allegedly exact minimum-memory fallback.

Actual allocator rounding, module loading and device fragmentation can still affect a fit. The planner includes the same existing base/headroom model rather than an exact driver-residency proof; preserve actual CUDA allocation measurements for low-memory tests.

## Graph and state lifetime

All layout choices, kernel-function selection and batch sizes are fixed at construction. Capture/replay uses stable device addresses. Minimal probability recomputes every terminal/batch in original ascending q order, includes folded opponents and excludes own reach; there is no stale probability buffer. Positive-zero-positive recovery and zero-own reach therefore require no mask state and are explicitly tested. The unused null arguments are passed only into branches that cannot read them.

The existing synthetic tests clear captured graphs before replacing reach/value/CDF buffers. Production does not replace these buffers inside capture. A context/kernel allocation failure propagates through existing Result paths; no partial solver publication is introduced by the planner.

## Numerical reference and budgeting

literal_reference_base_mb is captured immediately before forced reservation; no other intervening need adjustment exists. Original EquityCachePlan construction and its bytes/metadata computations are unchanged except opt-in logging. Thus the target mirrors literal pre-pass B/cache choices, while all physical fits use accurately reserved forced bytes. The captured base is not reconstructed by floating-point subtraction.

Literal targets try preferred then minimal storage; a physically unsupported target returns None, not a fabricated smaller batch. Corrected reference is tried only afterward. Overflow/invalid accounting remains Err. Capacity extension is labeled separately. The public constructor always allows the preferred layout; the private force-minimal test switch may restrict feasible choices intentionally.

HU plan.bytes includes its slots/blocks/work metadata in addition to equity entries. Literal and corrected cache decisions both use that whole cost. Cache-on is reserved before optional normalization; cache-off stays off. The new fixed-state cache-dispatch test now refreshes the cache correctly and supplements source review that dot-product/division order is intended to match.

## Remaining meaningful gates

1. Compile and run all host planner tests, then focused minimal graph/zero tests and fixed-state HU parity. Driver support for stream.null() is a concrete gate, not an assumption to waive.
2. Run the ignored actual integer-MB union boundary test. It now finds its fixture using the deployed selector, matching constructor semantics; require identical B/cache and exact arenas against compact at that budget.
3. Re-run original internal graph/cache/stop tests and retained direct/normalized, compact/union, active-zero and forced-policy tests. Existing tests that synthesize a specific greedy batch budget may need a correctly derived new fixture; do not loosen their parity assertions.
4. Compare original literal source and candidate full native arenas/effective policies at matching 19/21/23GB iterations. Existing corrected-reference exactness does not cover this claim.
5. Keep the frozen corrected protocol and results unchanged. Add literal controls as a separate evidence family, with fresh named outputs and source/binary identities. Confirm preferred-case performance after compilation because adding a CUDA entry can alter code layout even if preferred source arithmetic is unchanged.

No additional production defect was identified in this review. That is a source assessment, not a compilation/runtime guarantee.
