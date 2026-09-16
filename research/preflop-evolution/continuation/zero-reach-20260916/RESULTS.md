# Current versus average zero-reach audit (N31)

Read-only reconstruction of all terminal reaches in the two N19 final saves and
six N27 final saves. No payoffs, training labels or solver state were changed.
All input hashes remained unchanged. The reconstructed current and average
prefix masses match the existing independent N28 diagnostic exactly at all 17
selected large-case decisions. One regret-normalization test passed.

| Saved policy | Eligible HU leaves | Current positive live ranges | Average positive live ranges | Zero current own range with positive opponents |
|---|---:|---:|---:|---:|
| Eight-player ordinary | 6,585 | 4,463 | 6,585 | 922 |
| Eight-player learned | 6,585 | 4,939 | 6,585 | 446 |
| Heads-up 40 bb, each of three paths | 5 | 5 | 5 | 0 |
| Heads-up 100 bb, each of three paths | 6 | 6 | 6 | 0 |

Eligible means two live players, pot-share terminal and SPR from 1 through 20.
The last column counts terminal/traverser pairs, not unique leaves or dealt-hand
frequency. The ordinary policy is a control: it does not actually enable learned
values; its counts describe what the learned guard would do on those reaches.

The large learned case does switch to Balanced on some zero-own-range branches
that still matter for counterfactual action evaluation. Its largest reconstructed
opponent reach among switched branches is 0.0100351. This is an independent-class
diagnostic quantity, not blocker-adjusted reach or an additive contribution to
the reported gap. All inspected saves have zero ante; this diagnostic's SPR
calculation has not been qualified for nonzero-ante inputs.

No such switch appears in the small heads-up fixtures at this checkpoint, so it
cannot explain their remaining gaps. Nor does this audit establish that removing
the switch is correct. N32 separately tests a fixed uniform prior when own reach
is zero, keeping all positive-range predictions unchanged.
