# Card-compatible heads-up reference

19 September 2026. Research only; production on 56708 is unchanged.

**The small GPU implementation passed all three independent correctness gates.**
Both players adapt in a deliberately restricted fold/jam versus fold/call game.
The same physical hole-card probabilities apply to folds and showdowns, avoiding
the mistake of correcting only the displayed equity or one terminal value.

| Fixture | Independent minimax value (bb) | GPU best-response gap (bb) | GPU value error (bb) |
|---|---:|---:|---:|
| Uniform ranges, 10bb | 1.112265 | 0.00000934 | 0.00000302 |
| Saved 200bb entering ranges, zero rake | 2.562292 | 0.00009637 | 0.00003337 |
| Overlapping premium ranges | 0.732484 | 0.00000987 | 0.00000987 |

Primal and dual linear programs independently certify the values. Direct physical
combo-pair enumeration checks random-policy payoffs, and exact counting identities
check the chance matrix. CPU and GPU CFR+ policies pass the preregistered 0.001bb
gap threshold after 1,000 iterations. Maximum CPU/GPU action-probability difference
is 0.00000809. Zero-weight classes are included in the premium fixture.

For the saved-range fixture, solving the independent-class game very accurately
still leaves a **1.1503bb best-response gap when evaluated in the card-compatible
game**. This is a conditional result in this restricted, zero-rake test; it is not
the original full game's exploitability or an estimate of a production improvement.

## Limits and next step

The equity cache still supplies sampled class-versus-class showdown values. Exact
compatible hole-card counts do not make those equities exact. There is no postflop
betting, no non-all-in raise, no limping/calling before the jam, no rake, and no
third player. These ranges must not be substituted for the original Wizard case.

The GPU kernel took 9.7ms for three independent blocks, excluding compilation
(69ms). This is a correctness prototype, not a full-tree speed measurement.

The [existing engine comparison](NATIVE-RESULTS.md) now independently reproduces
all eight exported policies. More iterations converge the independent-class game
but leave the physical-chance discrepancy. The [existing research interface](INTERFACE-RESULTS.md)
also passes the independent equilibrium check on all four two-player fixtures,
without changing its kernel or enabling learned pricing. This reuses the September
16 implementation rather than introducing a second integration path.

Any production integration must retain consistent chance weights through fold values,
showdowns, regret updates, best responses, and reported frequencies. Multiway
folded-card conditioning and postflop range interaction need separate work.

## Reproducibility

- [Protocol](PROTOCOL.md), [GPU protocol](GPU-PROTOCOL.md)
- [Independent LP and CPU results](results.json)
- [Frozen GPU inputs and source hashes](gpu-fixtures.json)
- [GPU output](gpu-policies.json), [independent review](gpu-review.json)
- [CUDA reference kernel](reference.cu)
- Python reference: `tools/research/card_compatible_hu.py`
- GPU runner/reviewer: `tools/research/card_compatible_hu_gpu.py`
- Rust GPU driver: `crates/solver/examples/card_compatible_hu_gpu.rs`

Runners refuse to overwrite completed evidence. The GPU runner checks production
is idle before executing. No application engine or UI code changed.
