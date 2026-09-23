# Full candidate admitted for a wider fixed-budget evaluation

23 September 2026. The complete 78-model linear output passed its numerical and
resource control after the fresh averaging study and both audits completed.

A separate 64-deal control exercised 29,025 visible observations across preflop,
flop, turn and river, including 28,766 rows with own-action histories. CPU/CUDA
probabilities differed by at most 1.35e-13 and own-reach weights by 5.92e-12.
Integrated native root payoffs differed by at most 2.85e-14 bb. No control deals
will enter the forthcoming response-training or population-test streams.

CPU averaging took 26.0 seconds and GPU averaging 4.28 seconds in this control.
The GPU batch plus native evaluation and output took approximately 5.83 seconds
after excluding the deliberately added CPU comparison. This suggests several
hours for the full 174,336-deal plan, not a guaranteed completion time. The
registered limit is 12 hours for evaluation and two hours for its readback.

The control produced 27.6 MB of logical GPU artifacts using about 10.7 MB on
disk after flushing compressed output. Scaling allocation with a 50% margin
requires 43.8 GB above the 40 GB reserve. Initial free space narrowly missed
that admission requirement. The completed, independently audited training store
was therefore compressed losslessly: all 2,970 file hashes, lengths, paths and
last-write times stayed unchanged. Allocation fell to 2.87 GB from 9.41 GB
logical size, and free disk space rose to 89.6 GB. No live store was changed.

The broader study can now retain its planned sample counts. Its controller
freezes sources, bank identity, seeds, physical bounds, confidence rules and
resource caps before launch. It preserves failure evidence and has no automatic
retry or deployment path. See WIDER-RESPONSE-FULL-PLAN.md for the fixed protocol.

Evidence: `later-average-wider-admission-v1-{registration,result,status}.json`
and `later-average-completed-compression-v1-{registration,result,manifest}.json`.
These are execution/resource controls, not additional poker-strength results.
