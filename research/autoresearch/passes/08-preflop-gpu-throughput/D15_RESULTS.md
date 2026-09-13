# D15: zero-scan shortcut cannot accelerate the large accuracy check

The proposal to accelerate both learning and accuracy checks fails its 20%
work-volume admission gate. All 692,628 distinct averaged distributions in the
large saved snapshot have nonzero weight on all 169 classes. Consequently no
sampled scan tile in those distributions is entirely zero. An exact empty-tile
shortcut cannot remove their scan chains.

Learning is different: its support counts permit a substantial optimistic
bound. This remains an unmeasured possibility, not an admitted GPU prototype.

| Saved fixture | Learning: maximum possible empty tiles | Check: maximum possible empty tiles |
| --- | ---: | ---: |
| Small | 80.08% | 36.86% |
| Large | 78.88% | 0.00% |

These percentages are **upper bounds**, not observed savings. For learning,
each distribution with K positive classes needs at least ceil(K/32) nonempty
tiles. The bound allows the most favorable ordering separately for every
sample; actual rank orders may spread positives across more tiles. It covers
the five full tiles and the final nine-lane tile without assuming random ranks.

Checks also account for retained cross-player cohorts. The witness gives exact
identity membership and the histogram gives support counts, but their original
per-ID association is not saved. Pairing the most favorable support counts
with the most frequently rebuilt identities gives an optimistic rearrangement
bound. This is not the observed association. In the large check this ambiguity
does not matter: every distribution has support 169, so every allowance is zero.

The host census completed in 11.234 seconds. Independent struct/array decoding,
all 169 exhaustive tile-capacity cases, a second histogram-transport bound,
D10 hashes and D11 retained row counts pass. No GPU extraction, code change,
new timing or production mutation was performed.

## What this changes next

Do not add the unconditional shortcut to the common writer: it would add zero
detection to a large accuracy-check workload that has no empty tiles. A
**separate learning-only dispatch** could avoid that cost and remains worth
screening. It requires its own proposal, actual-count or conservative lower-
bound evidence, exactness tests and complete timings. D15 does not admit it.

Do not turn small positive values into zeros to make the check sparse. That
would change the evaluated policy. These observations apply to the immutable
test snapshots; learning support changes over time, and the small check is
already different. Probability loads, output stores and terminal evaluation
remain even when a zero scan can be skipped.

[Protocol](D15_PROTOCOL.md), [census](d15_zero_bound.py),
[independent audit](check_d15.py), [verified results](raw/d15-verified.json).
