# Integrated sampled poker: correctness passed, capacity remains open

The complete registered 15-node BB-versus-BTN preflop subtree now runs through
on-demand GPU postflop traversal, physical seven-card showdown evaluation and
an exact sparse strategy lookup. Six small frozen-policy batches passed against
a separate recursive scalar reference. This is an integrated algorithm check,
not an independently evaluated BB strategy or a production deployment.

## What ran

The fixture draws 8,192 physical deals from the previously qualified joint law
over all 112 weighted flops and the full supported incoming ranges. Each deal
uses a shared uniformly selected suit permutation and an ordered turn/river
draw without replacement from the remaining 45 cards. The sampler checks its
board probabilities and compatible pair masses against the earlier exhaustive
oracle. NumPy PCG64 seed 2026092201 and the generated deals are frozen.

All 112 boards and all 24 suit permutations appeared. The sample visited all
169 BB classes and 86 of the 96 supported BTN classes; the other ten retain
positive sampling support but did not appear in this finite fixture. This is
not a range cutoff. The largest standardized board-count deviation was 2.36;
that is a sanity screen, not proof of a sampling distribution or accuracy.

Each batch contains 2,048 deals, with one traversal for each updating player.
The six batches use fixture starts 0, 0, 2048, 4096, 6144, 6144. Repeated deals
exercise lookup and changed strategies; they do not create independent extra
chance observations. All three postflop branches and all five preflop decision
nodes were visited. Fold utilities and the 0.25 bb continuation adjustments
come from the qualified exported context.

The updating player's actions are all enumerated. The other player's action is
sampled with a separately seeded SplitMix64 stream; both sides use the same
frozen table during a batch. Missing entries use uniform legal probabilities.
Signed regrets and opponent-pass strategy sums are reduced in deterministic
sample/preorder order on the host only after the batch completes. This first
prototype intentionally retains the scalar oracle and host work for checking.
It is not an optimized persistent GPU trainer.

## Results

| Measure | Result |
|---|---:|
| Sampled traversals | 24,576 |
| Decision/update records | 653,847 |
| Maximum GPU/reference value or update difference | **0** |
| Largest records in one traversal | 113 (capacity 512) |
| Final distinct strategy entries | 521,394 |
| Final packed key/regret/average payload | 45,882,672 bytes |
| Allocated output record buffers | 109,051,904 bytes |

Each cumulative regret and average entry was also checked against a separately
updated reference table, with a 1e-8 tolerance. The first GPU batch repeated
bit-for-bit. Input keys and probabilities remained unchanged. An intentionally
insufficient one-record capacity returned overflow; it did not modify the
strategy table or silently drop updates. All six normal batches retained
repeated information-set occurrences (roughly 11,000 per batch).

Keys compare the complete 128-bit observation identity, not only a hash. They
contain the exact own private cards, sorted visible flop, ordered visible
turn/river, actor, and full betting history/continuation. Preflop node IDs are
unique public histories in this tree. No hidden opponent cards, future public
cards, or suit-permutation index enters a policy key. Controls check hidden
card invariance, private/flop listing-order invariance, and distinctions for
own cards, public street, action history and continuation. This representation
does not yet combine strategically equivalent suit relabelings.

## What the timing and growth mean

Warm GPU traversal plus root readback took about 5.5–5.8 ms per batch. Full
validation rounds grew from roughly 0.15 seconds to 0.27 seconds as the table
grew. Those rounds include table preparation/upload, record readback, scalar
validation and deterministic host reduction. They **exclude fixture generation**
and initial CUDA compilation (0.355 seconds).

The frozen result's `limits` text incorrectly says CPU deal generation is
included in round time. This paragraph corrects that descriptive error without
rewriting registered evidence. The fixture is generated in a separate process.
Kernel timing alone is not end-to-end training throughput, and packed payload
excludes B-tree overhead, oracle copies, temporary records and device workspace.

On the three fresh batches after the first two rounds, only about 9–11% of
records found an existing entry. Distinct entries grew from 179,289 to 454,700.
Even the final repeated-deal batch added another 66,694 entries because changed
opponent choices revealed different histories. This is a concrete storage and
sample-reuse concern. The short check does not establish that a useful policy
will converge before the table exceeds resource limits.

Next: measure longer fresh-deal state growth by street and end-to-end cost,
with explicit memory stops. Then test time to an independently measured gap on
a tractable control before admitting the full BB study. Do not infer convergence
from this six-batch check, tune to the already inspected 190-flop panel, shrink
the incoming hands, or erase stored regrets to force a fit.

## Reproducibility

Sources: `hu_sampled_poker_fixture_20260922.py`, `hu_sampled_poker_gpu.rs`,
`poker_reference_v1.rs`, `sampled_poker_v1.cu`, and the guarded runner
`hu_sampled_poker_run_20260922.py`. Existing qualified betting and evaluator
headers remain unchanged. Evidence uses prefix `sampled-poker-v1`.

Registration SHA256:
`3fd881e395a7619c26b4bcee92180f3a1f88e11fea677eab3422bf5c1685e48c`.
Result SHA256:
`0893147b292a5da0ffcb134e47e74449ecaf9c514a3c2c15c7e416c776d3ac59`.
All 19 registered inputs matched afterward. The fail-closed idle/resource guard
exited successfully in 2.171 seconds. Production sessions and port 56708 were
untouched. The preview still contains the previously evaluated UTG/LJ study.
