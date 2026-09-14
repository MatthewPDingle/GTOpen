# D20: why the current game misses retained optimizations

The live R03 server reports a stopped iteration-53, seven-player game with
5,704,840 nodes and 7,712.94 MB CPU arenas. Its log selects the normal GPU
path: the reference numerical schedule uses four-sample batches, whereas
retained cohorts explicitly require 32. It is still using GPU computation.

The log has 2,688,434 union rows, 1,292,228 compact rows, normalized storage,
the HU cache enabled, and about 20,268 MB total planned device allocation.
The original CDF scratch is exactly 3,514,860,160 bytes. There are 256 sample
batches per traversal instead of 32; this is a scheduling count, not an 8x
runtime claim. The game also has much more total work than the frozen fixtures.

Simply removing the cohort gate is unsafe. Its planner and allocation checks
hardcode 32. C23 also sizes compressed rows for 32 samples: retaining that
stride would allocate 11,164,849,920 bytes here, increasing memory. The
existing exact-duplicate hash needs 21,946,128 bytes, exceeding its separate
16 MiB cap. Neither cap should be silently relaxed.

The proposed C24 prototype applies static boundary storage directly to the
ordinary compact normalized path, without cohorts or the duplicate hash.
For four samples the maximum packed row stride is 333 floats, versus 680
originally. CDF storage would become 1,721,247,696 bytes, a 51.03% reduction.
After 1,392,644 bytes of immutable mapping data, net savings are 1,792,219,820
bytes. This does not predict whole-solve runtime or justify changing batches.

`audit_d20.py` cross-checks the independently generated D19 maps against C23's
GPU qualification maps, validates 173,056 hand boundaries and 32,768 windows
across batch widths 1 through 32, and records the live configuration and log
hash. See `raw/d20-verified.json`. No solve, restart, or user state change was
performed. A shell write was rejected before execution; the audit file was
then created with the patch tool and executed successfully.

Next: qualify four-sample packed GPU prefixes and terminal hand results,
then implement a research-only ordinary-path constructor. Full unchanged
schedule comparisons, memory failure recovery, saved continuation and paired
timings are required before normal integration. R04 remains release ready;
56708 remains R03.
