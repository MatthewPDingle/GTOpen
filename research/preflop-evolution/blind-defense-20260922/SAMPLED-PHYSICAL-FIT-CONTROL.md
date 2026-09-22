# Physical observation fitting and engine reload

The fixed-data integration control passed. Actual physical-card traversal
records can now feed the 269-input network, and its fitted weights can be
loaded back into the Rust poker policy adapter with checked action probabilities.
This is a single fit to records from synthetic behavior, not a self-play run or
a strategically qualified poker model. The live application is unchanged.

## What was exercised

The registered BB-versus-BTN game keeps all private-hand support and its native
legal tree. Sixteen previously frozen physical deals are implementation fixtures,
not representative training coverage. Four seeded traversals per player per deal
produce 128 traversals and 2,828 records, covering preflop through river and all
three postflop entry branches. Both player passes use the same frozen synthetic
networks. No policy is changed between those passes.

The exporter produced 1,785 distinct canonical observable inputs. Features retain
the player's cards, visible board, acting player and full public action history.
The feature round-trip and legal-action checks run for exported inputs; earlier
hidden-card and global suit-symmetry controls remain prerequisites. Global suit
canonicalization is valid for this registered class-range context, not arbitrary
suit-specific locks.

Only positive-tag advantage records train that player's network. Negative-tag
opponent policy observations remain separately identifiable and are excluded
from the advantage fit. Every visit is retained: duplicate input keys contribute
their actual multiplicity rather than becoming one equally weighted example.
There were 908/184 advantage records for players 0/1, covering 650/171 distinct
observations. These small, unequal counts are not evidence of sufficient coverage.

## Gradient and serialization checks

The full per-visit objective and the grouped empirical-mean objective have the
same gradient. On these physical records, double-precision gradient differences
were at most 5.56e-17; the loss difference equals the omitted, parameter-independent
within-input variance within 1.67e-16. Legal-action masks exclude padded outputs.

Each network was then initialized independently and fitted for the registered
128 Adam steps at learning rate 0.003. Normalized grouped fitting loss fell:

| Player | Before | After |
|---|---:|---:|
| BB | 1.35103 | 0.05462 |
| BTN | 1.65297 | 0.01998 |

These are training residuals only. No held-out poker value or deviation gain was
measured, and lower fitting loss is not a claim of stronger play.

The saved 269-64-64-4 float32 networks reload through the existing Rust adapter.
Across all 1,785 inputs, maximum normalized-score disagreement with PyTorch was
3.82e-6 and maximum action-probability disagreement was 4.38e-6, within the frozen
2e-5 and 1e-4 tolerances. Positive per-player advantage normalization cancels in
regret matching; raw advantage scales are saved for accounting and diagnostics.

The CPU integration control took 4.91 seconds, using two threads and no GPU.
This is neither a GPU performance result nor CPU preflop optimization. All 13
input hashes and produced artifact hashes are retained under
`sampled-physical-fit-v1`. No model from this control is deployed.

## Next integration step

The small-game strategic comparisons still decide whether this learning method
is ready for a physical-poker pilot. Meanwhile, the next implementation check
is batched GPU inference and fitting on these same frozen physical observations.
It must preserve legal masking and match the CPU reference before any pilot.

For the pilot, generate a bounded batch of physical deals, enumerate observable
queries for that batch, evaluate networks in batches, and hold those policies
fixed across both player traversals. The query cache must be discarded or bounded
between batches; do not recreate the full board-by-history strategy forest that
failed the memory screen. Reuse the qualified joint-deal sampler and preserve
all private-hand support. Later accuracy claims require fresh independent
evaluation under the [evaluation contract](SAMPLED-EVALUATION-CONTRACT.md).
