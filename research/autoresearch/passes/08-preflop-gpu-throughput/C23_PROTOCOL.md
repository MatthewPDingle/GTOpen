# C23: exact static rank-boundary CDF prototype

Registered before implementation/compilation after D19. Keep C14/R03 and56708
unchanged. Append a test-only compact CDF writer and direct compact reader.
Every original scan, carry, quadrature product and addition remains ordered
as before. Only prefix storage addresses and reader addresses change. Use
static prefix/group/sample-offset maps and D19's maximum up-to32-sample stride.
No value-dependent masks, popcounts, range pruning, precision change or samples
removed. Original exact-reuse module entries must remain byte-identical.

Stage1: GPU prefix and complete per-hand sum comparison over five rank tables
(all tied, all distinct, warp-crossing ties, irregular, real fixed deck), twelve
input patterns including dense/zero/recovery, sparse, one-hot, signed zeros,
subnormals, tiny positives and mixed magnitudes. Compact and noncompact source
slot modes; gates on/off; aliases, zero mass and poisoned inactive/padding rows.
Sample starts0/17/237/992, batch/count1/1,5/1,5/5,32/1,32/7,32/31,32/32:
6,720 prefix cases. For each, compare 2..8 opponents and zero/nonzero initial
accumulators (94,080 paired hand-vector cases). Use actual GPU-produced tables
for the readers. Compare all required prefixes against original170-value rows,
all169 hand sums bit-for-bit, and every unused compact slot/tail guard. No
reconstruction of unused original prefixes is needed or claimed.

Require no local spills/shared memory and <=64 registers in compact writer
and reader wrappers. Preserve original20 PTX entries and validate direct
addresses against independently reconstructed static maps. These gates admit
integration only. One run07-guarded build/test, cap300s, no edits while live.
Preserve all source/input/executable hashes, exact cases and compiler resources.

If admitted, integrate fresh private construction with original cohort/cache
choices. Release the private old CDF before new allocation when overlap exceeds
budget; publish no engine after a failure. Repeat exact full solver, prefix,
terminal, sparse/zero, graph/stop, saved continuation and allocation qualification.
Then first complete large pair requires >=1% benefit to extend; retention needs
three alternating pairs/fixture, >=3% median large improvement and <=3% small
regression, plus full default/native regressions. Count cold construction cost.
No speed or convergence claim follows from storage savings alone.
