# C24: static CDF storage for memory-constrained normal GPU games

Registered before GPU prototype work, against R04 commit 66f3747 and D20's
read-only layout audit. Target the user's seven-seat, four-sample schedule;
do not obtain a gain by reducing work or changing floating-point grouping.

1. Qualify a four-sample row stride independently on the GPU. Compare original
   and packed prefixes and terminal outputs bit-for-bit, including synthetic
   rank tables, real ranks, aliases, zero/subnormal masses, signed zero,
   inactive slots, partial batches, and nonzero continuation accumulators.
   Preserve sentinel padding. The existing 32-sample production map remains
   unchanged. Record source/PTX hashes and register/spill/shared-memory use.
2. Prototype the ordinary compact normalized writer/reader, without requiring
   cohort buffers or the exact-duplicate hash. Preserve native batch size,
   sample order/count, HU cache, precision, locks, policies and update order.
   New allocation and index bounds must be explicit. Use a fresh private
   engine; release replaced storage before allocating the replacement.
3. Match complete regrets, strategy, gaps and EVs against the ordinary engine
   at identical saved checkpoints. Include stop/reload continuation and
   allocation failure recovery. Recheck supported batch sizes and keep R04's
   32-sample path numerically unchanged. No production promotion yet.
4. Run a bounded same-problem timing screen, then three alternating complete
   workload pairs on retained witnesses and the user's frozen large game.
   Register the latter's workload/cap after measuring its baseline, before
   candidate timings. Require at least 1% screen benefit, at least 3% median
   complete runtime benefit for retention, no greater than 3% median regression
   on supported comparison fixtures, and exact checkpoints throughout.

Standalone build/test cap is 300 seconds under the existing live-idle guard.
Subsequent long workloads must be individually bounded and recorded. One
owned workload at a time; stop only research work if the user resumes a solve.
Storage savings alone never count as a retained performance improvement.
