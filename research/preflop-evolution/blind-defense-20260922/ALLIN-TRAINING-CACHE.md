# Exact training-pair cache completed and reviewed

The cache finished successfully in 2,799.5 seconds, about 46.7 minutes, using
one CPU worker alongside the existing hybrid GPU trial. It made no changes to
that trial, production or the range preview.

| Coverage | Completed |
|---|---:|
| Scheduled physical training deals | 39,936 |
| Training batches | 624 |
| Role-preserving suit-canonical private pairs | 23,891 |
| Remaining boards per pair | 1,712,304 |
| Total private-pair / board evaluations | 40,908,654,864 |
| Sampled outcomes checked with separate five-card enumeration | 23,891 |

For each pair, the native reference enumerates all five-card subsets of the
remaining 48-card deck and stores integer wins, ties and losses. Canonical keys
identify equivalent suit permutations and card order within each player's hand;
they do not exchange the players. These labels contain no learned policy or
opponent-behavior assumptions.

The independent audit reconstructed the key set from every original training
deal, verified all native batch identities and count totals, and rebuilt the
complete cache. It did not repeat the full 40.9-billion enumeration. Earlier
small-fixture controls separately checked native equity symmetry and outcomes
against independent hand evaluation.

A second read-only check loaded the completed cache through the actual new
training adapter. All 624 batches mapped successfully, with **zero missing
private-pair keys**. Card identities, deal/action seeds, batch identifiers and
query limits were preserved. The cached equity enters only preflop all-in
terminal calculations; it never becomes a neural input feature.

Cache SHA-256:
`bf68ef78ac5102b3bb8736a513aa666bba672d799cb1a3820a7e5e8a66a3bf3c`

The local immutable cache is
`S:/GTOpen-research/sampled-physical-allin-training-cache-v1/cache.json`.
It covers this scheduled experiment, not every possible private pair in every
future setup. Missing keys are an error; the trainer cannot silently substitute
an approximation.

This completes a prerequisite for the separately prepared conditional-all-in
trial. It is not completed training or evidence that the resulting ranges will
be better. The next GPU trial still waits for the existing hybrid experiment,
its fresh evaluation and its independent readback to finish.

Evidence: `sampled-physical-allin-training-cache-v1-{registration,result,status,independent-review}.json`
and `sampled-physical-allin-cache-adapter-v1-review.json`. Native inputs/outputs
and source training batches are individually hashed in those records.
