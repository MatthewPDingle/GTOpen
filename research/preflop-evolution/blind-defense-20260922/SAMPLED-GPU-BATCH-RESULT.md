# Sampled GPU batch reference passed

The GPU reference now traverses sampled finite-game paths, emits regret and
average-strategy increments, combines duplicate information-set updates in a
fixed order, and computes the next ordinary regret-matching policy. It is an
isolated research example, not a poker trainer and not part of the server.

## Result

Across both rounds of both exact-control utility modes, the maximum absolute
error against the rational reference was **4.441e-16**, below the registered
1e-10 threshold. Checks covered:

- Instantaneous regret increments and average-strategy increments.
- Cumulative signed regrets and average accumulators across both rounds.
- The next regret-matching policy and the normalized average policy.
- Bit-identical output from two repeated launches of each unchanged batch.
- Unchanged input strategy, previous regrets and previous average state while
  computing each batch. New state is written to separate buffers.

The first round contains 768 nonzero sampling tapes and the second contains
864. All repeated information-set occurrences are retained: 5,376 and 6,048
respectively, with up to 216 occurrences for one information set. The same
zero-own-reach, re-entry, rare-hand, early-fold, all-in and hidden-information
controls from the exact oracle are included. Terminal utility modes cover
both dead money without rake and action-dependent rake.

## What the implementation does

One GPU thread walks a supplied sampled deal/opponent-action tape. It visits
every updating-player action, regardless of its current probability, and only
the sampled opponent action. The policy is frozen for the whole batch.
Own-node action values produce regret increments; visited opponent nodes
produce the average-strategy increments qualified by the exact oracle.

A separate reduction kernel groups updates by the complete information-set
key and adds them in stable sample/node order, with no floating-point atomic
addition. Only after reduction are cumulative state and next policies formed.
The fixture builder assigns distinct IDs to full public histories, private
cards and visible public cards. Hidden opponent cards and unrevealed boards
do not enter those keys. No lossy hashing or dropping of repeated keys occurs.

The implementation uses f64 with fused multiply-add disabled to establish a
reference. It must not be presented as a fast precision configuration. It
accepts an explicitly supplied acyclic public tree of at most 128 nodes and
at most three actions per node; this bound applies only to the engineering
control, not to the proposed full poker training target.

## Limits and next gate

The two policy rounds are deliberately supplied changing profiles, not a
self-play run that feeds the first computed next policy into the second batch.
The test qualifies the update operator and state accumulation, not convergence.
The fixture exhaustively enumerates random tapes and assigns their probability
weights; production sampling would generate tapes and use the appropriate batch
normalization instead. Random-number generation is not yet tested here.

The current fixture already contains the compact public tree, resolved key
IDs, terminal payoffs and grouping lists. Full poker traversal must generate
legal actions and chance outcomes, evaluate physical showdowns, preserve perfect
recall and group newly encountered keys without expanding every public node.
It must retain all supported hands and action branches from the wide BB study.
The reference's 128-node array is not a way to narrow that target.

Next implement and qualify that on-demand traversal against the actual poker
geometry, then measure state growth and update throughput. Independent
time-to-convergence remains required before claiming practical improvement.
Neither the 2.19-second guarded probe duration nor these finite-control sample
counts forecast the cost of a poker training run.

## Evidence

The registered fixture, kernel, executable identity, runner, logs and review are
stored under `sampled-gpu-batch-v1-*`; the kernel is `sampled_batch_v1.cu`.
Source examples/scripts are `hu_sampled_batch_probe.rs`,
`hu_sampled_gpu_fixture_20260922.py` and `hu_sampled_gpu_batch_run_20260922.py`.
All 11 registered source/input hashes were checked after the run. The existing
production-idle guard completed successfully. No production session, model,
server binary or user range was changed.
