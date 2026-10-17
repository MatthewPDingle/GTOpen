# CPU postflop convergence

[Issue #1](https://github.com/MatthewPDingle/GTOpen/issues/1), reported by
SergMartidi, supplies a deep-SPR `AdAc9h` game where adding an all-in option
leaves compressed DCFR near 3.5% pot exploitability. Two CPU learning details
matter in this case.

## Strategy averaging at zero opponent reach

A zero opponent reach vector makes counterfactual values zero, but does not
make the traverser's own realization-weighted strategy average zero. Skipping
the entire branch during learning omitted these average updates and regret
discounts. The resulting stale averages could remain exploitable even with
full-precision storage.

The learning traversal now visits these branches. It can still skip terminal
CFV calculations, which have no learning state. Best-response and other
read-only CFV traversals can still skip complete zero-opponent-reach subtrees.
This does more CPU work on previously skipped learning branches; it does not
add an arena or change the tree.

## Compressed updates below a quantization step

Repeated nearest rounding can discard a small regret or strategy-sum update
on every iteration. CPU compressed traversal updates now use reproducible
stochastic rounding: the lower and upper integer are selected according to
the fractional part. The threshold depends on node, iteration and arena, with
one shared threshold per block so hand permutations and equal values are
treated consistently. Quantization extrema remain exact.

Save/load and GPU-transfer encoders retain their existing deterministic
roundtrip behavior and format. Compressed storage remains approximate; a
memory saving is not a universal bound on convergence error.

## Reproduction and regression checks

The supplied CLI JSON uses `allin_threshold: 0.85` as a fraction. To match the
older report's exact 1,075,938-node tree, also set
`tree.carry_aggressor_through_checks: true`. Fresh trees default to clearing
the aggressor after a check-through street, so their node counts differ.

`crates/solver/tests/deep_allin_precision.rs` checks that a zero-frequency
opponent bet still accumulates the responder's own average. It also uses a
fast river reduction of the reported game (`AdAc9h2c3h`, same broad ranges,
55-chip pot, 975-chip stack, 50% bets, 100% raises and all-in option) to check
compressed convergence against a full-precision reference.

On the original legacy-tree reproduction, baseline compressed DCFR gives
3.542% pot exploitability at iteration 200 and 3.359% at iteration 300. With
both corrections it gives 0.683% at iteration 200 and reaches the requested
0.5% target at iteration 240 (0.494%). Tree size and the 773.6 MB compressed
arenas are unchanged. These are convergence observations, not timing benchmarks.

```sh
cargo test --release -p solver --test deep_allin_precision
cargo test --release -p solver
cargo test --release --features gpu --test gpu --test preflop_gpu -- --test-threads=1
```
