# Read-only planning instrumentation specification

No instrumentation has been applied or run. Suggested opt-in flag:
`PREFLOP_MW_TERMINAL_REUSE_STATS`. Add only around construction of existing
multiway term/source plans; do not alter their layout or launch behavior.

Process one traverser at a time to limit host memory. For each original live
multiway terminal in original term order, build this key:

```rust
let key: Vec<u32> = (0..s.n)
    .filter(|&q| q != p && (node.live >> q) & 1 != 0)
    .map(|q| sources[node_index * s.n + q])
    .collect();
```

Use a `HashMap<Vec<u32>, usize>` (full equality, not a raw hash-only key) to
count multiplicity. Report for each seat:

- Live tasks T, unique keys U, keys with >=2 members D, repeated task savings
  `T-U`, maximum multiplicity, and histogram by multiplicity/opponent count.
- Percentage avoided arithmetic `(T-U)/T`; this is not a runtime speedup.
- One-batch duplicate sum scratch `D * 169 * 4`, with checked arithmetic.
- Several representative duplicate groups with node IDs and full source tuple
  so any unexpected same-seat collision can be checked against the tree path.

After releasing those per-seat maps, optionally build the cross-seat union
map for a frozen average check. Include `seat_mask` for each key, task count,
first/last traverser, and per-seat multiplicity. Report total tasks, unique keys,
keys reused only across seats, and duplicates within seats separately. Keep the
tuple in original seat order. If source IDs make key ownership implicit, do not
add hero p to this key: that would hide valid anonymous-hero cross-seat reuse.

A full union map may have millions of entries. It is optional diagnostic host
memory and must be freed before GPU allocation. The low-memory alternative is
to enumerate fixed-size `(len, [u32;8], seat, node)` records, sort lexicographically
by `(len,sources)`, and stream equal runs. Unused array entries must be explicitly
zeroed and length retained. This is instrumentation only, not a sort of the
opponent multiplication order within a key.

For an optional later runtime study, activity statistics must be evaluated on
the captured reach snapshot: group active iff some member probability is >0.
Fresh uniform strategy counts can substantially overstate mature-learning reuse.
Do not run CPU CDF/equity computations just to count keys, and do not access the
live HTTP session. Existing eight-seat constructor input and frozen fixtures
are sufficient once the parent chooses to run this diagnostic.
