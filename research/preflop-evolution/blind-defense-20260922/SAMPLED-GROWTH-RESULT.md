# Sparse sampling: fast traversal, very little late-street reuse

The bounded fresh-deal probe completed 91 accepted batches, 186,368 deals and
372,736 player traversals. It retained 9,294,315 decision updates in 7,944,848
distinct strategy entries. The next batch would have exceeded the registered
8-million-entry screening limit, so it was rejected **before any of its updates
were applied**. No rows were evicted and no incoming hands or actions removed.

This was a deliberate experiment limit, **not an out-of-VRAM failure**. The
last resource sample still showed about 22.2 GB free device memory and 101 GB
free host memory. It would be possible to allocate more. The concern is how
much useful repeated learning that larger allocation would buy.

## Main result: new states dominate after the flop

Here is the last ten accepted batches' fraction of visited decision records
whose exact strategy key already existed before that batch:

| Street | Existing-key visits / decision records | Existing-key fraction |
|---|---:|---:|
| Preflop | 99,310 / 99,314 | 99.996% |
| Flop | 20,787 / 149,932 | 13.864% |
| Turn | 396 / 277,821 | 0.143% |
| River | 4 / 490,487 | **0.000816%** |

These are record counts, not range-weighted measures of exploitability or
equilibrium quality. A missing key uses the registered uniform legal policy.
Thus the measurements flag poor late-street sample reuse; they do not prove an
asymptotic impossibility or measure the number of samples needed to converge.
The preflop decisions are being revisited while almost every detailed river
decision is still new. A changing preflop chart would therefore be weak evidence
of improved continuation values at this stage.

Final state occupancy:

| Street | Distinct entries |
|---|---:|
| Preflop | 5,104 |
| Flop | 1,124,697 |
| Turn | 2,431,189 |
| River | 4,383,858 |

The complete signed-regret and average-strategy checkpoint is 699,146,656 bytes
at `target/research-sampled/sampled-growth-v1-state.bin`. Its SHA256 is
`20e26112f480683f3e57de679a9b4310f2bd5a58b51e67a94c1da0effa362b6a`.
It is retained locally, outside Git. Header counts, sorted unique keys, finite
regrets, nonnegative averages, padded action slots and per-street counts were
audited across the entire file. This checkpoint is research state, not a
validated range model for the application.

## Timing

- Fresh 262,144-deal fixture generation: 27.937 seconds; only the accepted
  186,368-deal prefix was applied. The sample retains all 169/96 supported
  classes; 169/95 classes appeared in the entire generated fixture.
- Training/resource measurement: 37.700 seconds, including the rejected final
  attempt, transfers, host lookup census/reduction and scalar spot checks.
- Initial CUDA compilation: 0.041 seconds; checkpoint write: 0.695 seconds.
- Last accepted batch: 0.701 seconds total, including 0.527 seconds preparing
  and uploading its growing table. GPU traversal plus root readback was
  0.006 seconds; traversal plus all output readback was 0.028 seconds.

This prototype is now mostly occupied by table handling rather than GPU
traversal. Eliminating repeated uploads could improve throughput, but would
not by itself make unseen river observations share what has been learned.
Do not interpret traversal speed as speed to a useful strategy. No independent
best-response/convergence evaluation was performed on this checkpoint.

All 728 complete scalar spot traversals (eight per accepted batch) matched GPU
keys, action counts, root values and per-record updates with zero numeric error.
The rejected attempt also ran its spot checks. This is in addition to the
earlier complete six-batch integration test, not a fresh exhaustive equivalence
proof for every row in the larger run. The unchanged qualified kernel and
reference sources were hash-checked before and after.

## Would equivalent suits fix the storage problem?

A separate read-only census canonicalized each stored observation across all
24 global suit relabelings. It preserved ranks, actor, own-card/board roles,
ordered turn/river and the complete betting history. It did not merge or retrain
the saved regrets or averages. All 6,144 orbit-invariance controls passed and
the checkpoint hash was unchanged.

| Street | Original entries | Occupied suit orbits |
|---|---:|---:|
| Preflop | 5,104 | 695 |
| Flop | 1,124,697 | 535,623 |
| Turn | 2,431,189 | 2,391,079 |
| River | 4,383,858 | 4,383,216 |
| Total | 7,944,848 | 7,310,613 |

This occupied-key reduction is only **1.087x**, about 8% fewer entries, and
almost no reduction on the river. Suit sharing can still help, particularly on
the flop. Its theoretical maximum orbit size must not be advertised as a 24x
observed saving. Training with canonical keys would change trajectories, so
these census numbers are not a performance forecast for that different run.

## Decision and next gate

Do not scale this exact-key tabular prototype into an overnight wide study yet.
First establish an independent convergence benchmark on a tractable control,
then test a representation that can share learned values across related
observations while retaining the full target's hand and action support. Compare
quality at matched wall time and memory, not only training loss or range width.
The [bounded-model candidate note](SAMPLED-FUNCTION-APPROXIMATION.md) records
the next option and the requirements that prevent it from becoming another
unvalidated range heuristic. Neither the small control nor an approximate model
will count as completion of the full BB/BTN question.

Evidence prefixes: `sampled-growth-v1` and `sampled-suit-census-v1`. The GPU run
used the continuous fail-closed production-idle/resource guard; the read-only
census used four CPU threads with a 120-second timeout. No production code,
sessions, player models, preview ranges or port 56708 were changed.
