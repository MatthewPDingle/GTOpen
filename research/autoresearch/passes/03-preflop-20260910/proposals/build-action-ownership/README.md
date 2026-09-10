# Build action ownership proposal

`PreflopSolver::build` currently generates a legal-action vector, clones it into
the parent node, and retains the original solely for recursion. `PAction` owns
two Strings (`kind` and `label`), so the measured six-seat tree clones 3,691,038
nonempty Strings unnecessarily across 1,845,519 action edges. The associated
861,384 temporary action vectors also coexist with their stored clones during
construction.

The patch moves the generated vector into the node. Each child's owned
BuildState is computed using a short immutable borrow of that node's action,
then the borrow ends before the recursive builder can grow/reallocate nodes.
It keeps the parent fully populated throughout recursion. Node insertion order,
action order, child layout, action text, floating-point calculations, arena
offsets and native save format are unchanged.

The Vec is converted through a boxed slice before transfer to trim spare
capacity to its exact length, as the old Vec clone did. This may involve an
allocator resize, but still removes both String clones per edge. Original
formatted labels may retain spare capacity that their clones did not. Report
that retained-byte delta explicitly rather than assuming identical memory use.

This is a proposal only: no source edits, compilation or hardware measurements
were performed. `git apply --check` passed against the isolated source at the
recorded hash. The worktree can change between proposal and adoption.

## Independent acceptance gate

1. Before applying, augment the benchmark with `fingerprint.rs` and freeze that
   harness on both revisions. Hashes cover every node scalar, exact float bits,
   action kind/text/amount and actual child index. Capacity metrics are separate.
   Run the fingerprint AFTER timing; do not include it in build/load timings.
2. Compare identical fresh configurations for 3/6/7/8 seats, plus the real
   six-seat modeled native save. Require identical topology hashes, config and
   typed profiles, initial iteration and native arena fingerprints. The modeled
   save exercises load+rebuild; its existing strategy bytes must remain exact.
3. Run existing CPU preflop/build/save/variant tests, including per-seat menus,
   equal blinds, all-in clamps, legacy/coupled saves, hero state and locks. Do not
   change expected outputs or numerical tolerances for an ownership-only change.
4. Alternate baseline/candidate fresh-process runs on the same input and pinned
   caches: at least five matched pairs for the large modeled tree, plus smaller
   controls. Time `PreflopSolver::new` separately from native load. A warm-cache
   load improvement alone is weak evidence; require a repeatable >2% build gain
   without material small-tree or memory regression. Keep raw paired timings.
5. Report action Vec/String retained bytes and measured process peak memory.
   No save-throughput claim is expected: writing/syncing 2.5 GB is untouched.
   Normal fixed-state arena/gap checks should remain bit-identical.

If retained String capacity matters materially, reject or propose a separate
label-compaction experiment. Do not bundle allocator tuning, unsafe memory,
arena-zeroing changes, serialization changes or header parsing into this patch.
