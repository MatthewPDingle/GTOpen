# A practical way to remove one source of noisy preflop values

The BTN shove-response diagnosis found unstable conditional hand values. This
bounded control asks a narrower question: how much error comes from using one
future board to label an all-in for a fixed pair of private hands?

For the 16 private-card pairs in an existing numerical fixture, enumerate all
1,712,304 possible remaining five-card boards. Compare these exact equities with
32 independently sampled board sequences per pair, using shared prefixes of
1, 16, 64, 256 and 1,024 boards. These are conditional-equity calculations, not
trained policies, independent poker-strength tests or population accuracy claims.

| Boards per sampled label | RMS equity error on the fixture | RMS error in a 200 bb call value |
|---|---:|---:|
| 1 | 44.47 percentage points | 177.21 bb |
| 16 | 11.73 points | 46.75 bb |
| 64 | 5.49 points | 21.87 bb |
| 256 | 2.91 points | 11.58 bb |
| 1,024 | 1.33 points | 5.30 bb |

The value conversion uses the existing 400.5 bb pot minus 2 bb rake. It does not
mean a trained strategy loses 177 bb per hand: these are individual noisy labels
before averaging, fitted-model approximation or regret updates.

All 19 cases, including player-swap, suit-permutation and identical-pair symmetry
controls, enumerated 32,533,776 boards. The native enumeration took about 1.89
seconds on this fixture; complete orchestration and validation took 12.4 seconds.
Treat timing as a local engineering observation under the current workload,
not a solver speedup. Sampled-board generation, serialization and validation are
included only in the larger end-to-end figure.

Independent seven-card enumeration checked 1,216 sampled results. Player swaps
reversed every sampled outcome and exact win/loss counts; suit permutation left
them unchanged; the identical-pair case had exactly 50% equity. Independent
readback verified artifacts, card legality and all scalar error statistics.

## Exact cache rather than a new approximation

The existing 39,936-deal training schedule contains 38,651 distinct physical
private-card pairs and 23,891 keys after preserving player roles and identifying
suit permutations and card order within a hand. This makes a bounded exact cache
worth preparing. The cache job enumerates every board for each key on one CPU
worker, checks a sampled winner independently for every key, and preserves
integer win/tie/loss counts. It does not change the currently running hybrid
trial. At admission the cache is incomplete; its own result and audit must
establish completion before any training path uses it.

Exact conditional all-in values remove future-board sampling error for that
terminal calculation. Opponent private-card sampling, opponent action sampling,
neural postflop approximation and changing training strategies remain. Also,
replacing one component of a regret target can change its covariance with other
components. Lower all-in label variance alone does not prove lower variance in
every full regret vector or faster convergence. A future integration must test
those effects and preserve the correct expected game values.

Only preflop all-ins qualify for averaging over all future boards. Once public
cards are observed, averaging them away would be wrong. This experiment does not
alter those postflop calculations, any policy, the production build or the range
preview.

Evidence: `sampled-physical-allin-board-control-v1-result.json`, its independent
review, and `sampled-physical-allin-training-cache-v1-registration.json`.
