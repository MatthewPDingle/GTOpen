# Wide-support state maturity and lossless compression

The full-support resident probe completed 2,000 iterations / 4,000 player
sweeps. It retained all 169 BB classes and 96 entering BTN classes, with the
unchanged call-branch action tree on KsQd9d. Its iteration-four exported state
matched the preceding independently checked stored-GPU checkpoint byte for byte.
All returned counterfactual values were finite.

This is an engineering trajectory with registered, changing incoming weights,
including zero BB reach at iteration two followed by re-entry. It is not a
fixed-game equilibrium, connected preflop training, or a new blind-defense policy.

## Runtime and state

- 293.255 seconds native runtime: 281.400 for sweeps and 11.827 for four exports.
- Each canonical checkpoint: 3,440,369,296 payload bytes plus 72 header bytes.
- Four checkpoints at iterations 4, 100, 500 and 2,000; all are retained locally.
- Reference identity, source identities and the production-idle guard passed.
- No production solver code or session was changed.

The measured resident runtime excludes the repeated loading and unloading needed
for a forest larger than device memory. It must not be extrapolated as an actual
full-panel runtime or compared directly with the cold-recovery timing.

## All-record lossless compression

Both Zstandard levels processed every byte in every registered record using
1 MiB chunks, with 64 bytes per chunk plus the original header budgeted for
framing. Each chunk decoded exactly. All source SHA-256 hashes matched before,
during and after processing. No encoded copies or modified states were written.

| Iteration | Level 1 ratio | Level 3 ratio | Level 3 framed size |
|---|---:|---:|---:|
| 4 | 2.107x | 2.292x | 1.501 GB |
| 100 | 1.338x | 1.431x | 2.405 GB |
| 500 | 1.322x | 1.411x | 2.438 GB |
| 2,000 | 1.326x | 1.415x | 2.431 GB |

The complete screen took 203.343 seconds. At iteration 2,000, measured codec
time alone was 22.518 seconds encoding and 5.689 seconds decoding at level 3.
These Python chunk measurements exclude solver integration, transfer, disk
writes and framing implementation. They are not native end-to-end throughput.

The apparent advantage of the initial state disappears as the state develops.
The mature wide fixture compresses less well than the previously measured narrow
trained states (1.665x), rather than revealing an overlooked large storage gain.
No full-forest admission follows from this single-board measurement.

## Preserved failed attempt

The first compression checker required every stored float to be nonnegative.
That assertion was wrong for this implementation's CFR+ state: the GPU matches
using positive regret parts, discards old negative regret at the next update,
and then stores the new signed increment. After projection, negative regrets
can therefore remain in a completed snapshot.

The first checkpoint has 97,588,034 negative entries in player 0's regret array
and 41,574,312 in player 1's. All four arrays are finite; both strategy-sum arrays
are nonnegative. The original checkpoint also matches the previous checked
reference exactly. No solve was rerun or changed to repair this checker.

Version 2 preserves every signed bit, requires all arrays finite and strategy
sums nonnegative, and records negative counts. The original registration, failed
log, exact script copy and failure review are retained alongside v2 results.

Evidence: `wide-maturity-v1-review.json`, `wide-maturity-v1-registration.json`,
`wide-maturity-compression-v2-registration.json`,
`wide-maturity-compression-v2-result.json`, their logs and source files.

## Positive-regret storage screen

A separate experiment measured the size obtained after replacing negative regrets
with zero **after complete symmetry projection**, preserving all positive regret
and strategy-sum bits. This is not lossless compression of the original state.
Its possible validity comes from the update rule, and requires resumed-GPU
trajectory checks before use. DCFR, predictive updates, and clipping before
projection are explicitly excluded. A size improvement alone cannot qualify it.

| Iteration | Transformed level 3 ratio | Framed size | Smaller than exact signed-state encoding |
|---|---:|---:|---:|
| 4 | 2.931x | 1.174 GB | 21.8% |
| 100 | 1.742x | 1.975 GB | 17.9% |
| 500 | 1.706x | 2.016 GB | 17.3% |
| 2,000 | 1.720x | 2.001 GB | 17.7% |

All transformed chunks round-tripped, all original hashes stayed unchanged, and
100,000 scalar update comparisons passed. Two negative controls demonstrate why
this transformation cannot be moved before symmetry projection or applied to
DCFR. No transformed checkpoint was written or resumed. The screen took 161.484
seconds. Evidence: `wide-positive-regret-screen-v1-registration.json` and
`wide-positive-regret-screen-v1-result.json`.

This modest reduction does not solve the capacity problem. Do not implement a
new production codec or launch another full-state GPU qualification solely on
this result. Keep it as a possible later optimization, with its correctness gate
still open. The next investigation is a sampled-update algorithm that avoids
allocating and moving full hand arrays at every public history. It must retain
the target hand support, betting menu and counterfactual updates for currently
unused own actions; sampling is not permission to prune them permanently.
