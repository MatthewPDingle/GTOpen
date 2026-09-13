# C16: fuse local CDF construction and terminal consumption

Proposed next experiment; not implemented, measured or admitted as a speedup.
C15 was reserved by D09 for the narrowed-writer prototype and was not admitted.
Use retained C01+C07+C09+C14 at 53288a0 as reference. GPU only; 56708 read-only.

## Mechanism

Avoid materializing and rereading the global rank-CDF scratch for the selected
multiway terminal evaluator. Within each terminal block, stage each ordered
opponent's already-normalized 169-hand distribution once. For each original
sample, build the same 170-entry CDF using the original warp scan and carry
order in shared memory, consume it for all hero classes, then reuse shared
storage for the next sample. Keep the original sample/quadrature/opponent
addition order, floating-point operations and batch boundaries.

This repeats prefix construction across terminals that share a distribution.
The intended tradeoff is more arithmetic for fewer global-memory writes/reads.
Unlike rejected C08, it does not copy already-materialized global CDF rows into
shared memory; the global producer and its traffic are bypassed. Barriers,
shared-bank conflicts, recomputation and occupancy may still make it slower.
This is a hypothesis, not a bandwidth or stall measurement.

## Prototype boundaries

Research-only opt-in with direct construction of selected kernel modules;
avoid the duplicate startup penalty exposed by C13. Keep all existing global
allocations and grouping unchanged for this first comparison, even if a buffer
is unused; memory reclamation is a separate future experiment. Ordinary GPU
and unsupported modes keep the retained evaluator. No change to production
selection or the immutable qualified server binary.

Use 192-thread terminal blocks as before. Every thread must participate in all
block barriers, including threads above hand 168. Warp-prefix work may stride
across 2-8 opponents; inactive terminals can exit only on block-uniform tests.
Use the same current/average aliases and ordered opponent maps. Keep zero
reach, frozen/locked/hero states, captured graph replay and stop behavior.

## Qualification and timing

First prove every local prefix and terminal result bit-identical to retained
kernels for 2-8 opponents, dense/sparse/zero/recovery distributions, early/late
sample offsets, batch 5/32 and odd/partial counts. Include guards and all 169
hands. Then expanded full-arena, roots, gap/EV and graph/stop tests, followed by
immutable small/large saved-state complete-work comparisons. Verify constructor
allocation plans and preserved batch/HU-cache settings.

First large alternating pair must be <0.99 candidate/reference to proceed.
Retention needs three alternating pairs at both fixture sizes, >=3% median
large complete-work benefit and <=3% small complete-work regression. Include
startup, all six original learning sweeps/checks and synchronization. Every
checkpoint and final arena fingerprint must match. No retries to seek a pass.
If rejected, restore only candidate runtime while preserving source and raw
records. Full default/native GPU regressions are required before retention.

Use run07 live guards, serial workloads, bounded caps and immutable outputs.
No hardware-counter permission changes or new 10-hour deadline. Update the
live dashboard and push research results. This cannot by itself establish
full convergence or the user's desired order-of-magnitude improvement.
