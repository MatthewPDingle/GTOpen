# Completed 47-flop reference: numerical pass, accuracy pending

Completed at approximately 02:58 Adelaide on 20 September 2026. The original
fully enumerated, losslessly paged reference reached 2,000 iterations in
28,832.0 seconds (8 hours). It passed the registered combined within-game
deviation threshold: **0.00742383 bb**, below 0.01 bb.

The independent accounting audit passed every recorded checkpoint. Maximum
chip/rake conservation error was 0.0000001955 bb; terminal-probability error
was 0.0000000140. The previously reviewed iteration-500 record is unchanged:
canonical SHA-256
`15c9ec969cf539d672fd769f582ba78fe7262dd10282f2a0ecad9a6805f41e52`.
The complete source file SHA-256 is
`a1dbdd97d585e7603b8e117c2055c4be3b19804208b11c406e7ecf3c5c3afc22`.

## Strategy sensitivity

After reweighting both completed sources onto the same full-deck entering
private-card distribution, their action mixes are:

| Training flops | Fold | Call | 4-bet | Jam |
|---|---:|---:|---:|---:|
| 10 | 70.76% | 12.79% | 16.45% | 0.000% |
| 47 | 80.88% | 0.055% | 9.94% | 9.13% |

Prior-weighted policy variation is **26.72%**. This measures redistributed
action probability, not the percentage of hands that changed. AKo, 99, QQ
and KK make the largest contributions. The larger panel has more balanced
chance coverage, but this substantial strategic change does not by itself
prove greater accuracy or a desirable calling range.

The current queue is evaluating both frozen strategies on the same original
ten reserved flops, then on the independently selected 95-flop panel. Those
comparisons must complete their numerical checks before interpreting transfer.
No result here is a recommendation to replace production player ranges.

## Rare continuation caveat

The 47-flop source calls the initial 3-bet only about 0.055% of the time in
its own training game. The diagnostic finds 41.81% of OOP's counterfactual
hand mass has call probability at most one in a million; 86.13% has call
probability at most 0.1%. Those percentages are **not** the distribution of
hands actually arriving on the flop. They identify portions of a conditional
postflop evaluation that receive very little weight from this player's own
strategy. A small aggregate residual does not certify every rare hand or
counterfactual action value.

The called 4-bet branch occurs 3.06% of the time. Its corresponding extremely
low-own-reach shares are 51.33% for OOP and 13.68% for IP. No diagnostic threshold
prunes these hands or changes the registered validation gates.

Both entering ranges remain fixed from the saved baseline; earlier folded
cards are omitted. This remains one conditional heads-up branch, with a
limited postflop size menu, rather than a solved complete preflop game.

Evidence: `report47-full-result.json`, `report47-full-review.json`,
`report47-full-status.json`, `transfer-sources-freeze.json`,
`ab-vs-report47-common-prior.json`, and `report47-reach-diagnostics.json`.
