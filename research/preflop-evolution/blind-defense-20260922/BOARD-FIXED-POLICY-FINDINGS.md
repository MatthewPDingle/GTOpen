# Fixed-board policy propagation

The compact card-removal method now reproduces complete postflop branch values
for a saved trained policy. This extends the earlier terminal-only control.
It remains research code and has not changed production or current training.

## What was checked

The native exporter uses the registered postflop state transitions for all
three branches of the BB-versus-BTN context. Each decision emits one observation
per acting player's own holding. Inputs retain the native visible-board prefix,
full public betting history and suit canonicalization; the policy never sees
opponent cards or unrevealed board cards.

The candidate propagates opponent reach vectors down the tree, averages the
hero's actions at hero decisions, and reduces compatible hand values at leaves.
The independent reference instead propagates a dense matrix of hand-pair path
probabilities forward and pays terminals from actual investments, dead money
and rake. That reference does not use the candidate's reverse recursion,
sorted terminal reduction, exported offsets or exported payouts. Both share
native transitions and evaluator ranks; this is not an independent validation
of those underlying implementations.

The first control used 128 BB and 96 BTN holdings on two boards, uniform play
and the first fully audited arm's played generation-77 postflop network. All
12 branch/profile/board cases passed; maximum per-hand unnormalized value error
was 5.01e-12. Changing the future turn and river while keeping the same flop
left 2,016 flop observations unchanged. Runtime was 4.63 seconds, CPU only.

The full-support control then included every supported holding on board
`[0,5,10,15,20]`: 1,081 BB holdings and 566 BTN holdings. It used the same saved
network with the original range weights. All three branches passed. Maximum
per-hand value error was 8.01e-11; terminal probability error was below 9e-16
and cashflow conservation error below 1.37e-13.

## Timing and resource limits

| Fixed-board component | Seconds |
| --- | ---: |
| Native topology and visible observation export | 3.313 |
| Feature construction and saved-policy evaluation | 5.516 |
| Compact propagation, all three branches | 1.329 |
| Dense forward reference, all three branches | 7.795 |
| Complete control including both paths and evidence | 20.281 |

Compact propagation was about 5.9 times faster than the explicit pair reference
in this one run. This is **not** a speedup over the live sampled trainer or the
production solver. It is not an isolated repeated benchmark, and the two paths
also serve different validation roles. Policy preparation and native transport
remain significant costs. CPU math was limited to one thread and no GPU was
used, so this bounded control could overlap the current four-worker audit.

The full native export is about 80.7 MiB and is retained on S, with hashes in
the result. Avoid exporting one such JSON per board in a larger experiment;
stream or reuse topology and retain compact sufficient evidence instead.

## What remains before an accuracy experiment

1. Add preflop branch reach and forced root-action accounting. Keep exact fold
   and initial all-in values instead of adding board noise to them.
2. Apply the correct board proposal and private-hand importance weights,
   retaining the original entry-hand denominator. The earlier small-deck
   identity control establishes the formula, not this real-poker adapter.
3. Check the combined estimator against existing native action-integrated
   values on common physical deals, including rare and zero-reach histories.
4. At a fixed policy, compare variance and elapsed time against the existing
   sampled estimator. Freeze sample counts and comparisons before observing
   results. More work per board is worthwhile only if it buys enough precision.
5. Only after those gates consider using board integration in training. The
   ongoing stratified study and its evaluation remain unchanged.

These controls use one saved network, not the 78-policy own-reach average and
not a newly trained or improved strategy. They demonstrate value arithmetic,
not agreement with Wizard, equilibrium accuracy or improved playing strength.

Evidence: `board-fixed-policy-control-v1-result.json`,
`board-full-support-control-v1-result.json`. Both bind inputs by SHA-256;
native transport and per-hand full-support values are retained locally.
