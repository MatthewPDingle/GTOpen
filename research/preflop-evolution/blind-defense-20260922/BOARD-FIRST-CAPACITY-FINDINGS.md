# Actual-game board-first capacity preflight

The current restricted BB-versus-BTN game has **455 decision histories per
complete public runout**: five preflop decisions and 450 postflop decisions
across three continuation branches. A native read-only traversal counted the
histories and matched the existing visible-query builder exactly on two physical
deals. No strategy arena was allocated and no solve was run.

Three illustrative full runouts were then measured using the original frozen
entry ranges and the existing support cutoff. These are capacity fixtures, not
a representative board sample or a payoff evaluation.

| Runout, native card indices | BB hands | BTN hands | Compatible private pairs | Raw policy rows, upper bound |
| --- | ---: | ---: | ---: | ---: |
| 0, 5, 10, 15, 20 | 1,081 | 566 | 560,340 | 374,950 |
| 48, 49, 50, 0, 4 | 1,081 | 471 | 466,290 | 353,385 |
| 0, 4, 8, 12, 16 | 1,081 | 571 | 565,290 | 376,085 |

The policy rows count actor/history/holding combinations before suit-canonical
deduplication. They include only holdings compatible with that complete runout;
each decision's policy input must still contain only the board prefix visible
at that street. Excluding a holding incompatible with the sampled future cards
does not authorize revealing those future cards to a surviving holding's policy.

## Memory implications

A dense double-precision private-pair matrix for one runout is about 3.9–4.7 MiB.
One such value for every decision history totals about 1.73–2.09 GiB. That is
**one scalar field only**, not the complete memory required by an evaluator.
Values for both players, action branches, reach weights, temporaries, model-bank
activations and training state would add to it. Do not call this a demonstrated
fit on the 24GB card.

A raw float32 matrix of all 302 policy features would be another 407–433 MiB
before inference activations. Streaming observation chunks and private-pair
tiles is preferable to retaining every dense field for every node. The next
performance question is time per useful root estimate, including these larger
policy batches, rather than time per board alone.

## Probability checks

Dense private-pair marginals match the original sampler. On each fixture,
an independent card-subtraction calculation agrees with dense masked pair sums
to at most 1.71e-13 per holding. The true board marginal divided by a uniform
board proposal is respectively **1.103, 0.858 and 1.112**. These nonconstant
weights demonstrate why independently normalizing compatible hands on each
board would change this real context's chance law.

The ratio uses `C(52,5)/C(48,5)` times the surviving pair-mass fraction. The same
ratio applies to a sorted flop with ordered turn and river because both counts
gain the same factor of 20. This check does not enumerate all real boards or
evaluate their expected poker payoffs.

## Status and next gate

The probe compiled with four build workers in about seven seconds; the count
and probability measurement took about 0.11 seconds and used no GPU. The
existing training process continued. [Bound results](board-first-capacity-readback-v1-result.json)
include the context, source and executable hashes.

This makes a bounded streamed prototype plausible to investigate, but does not
establish that it will be faster or produce better ranges. A fixed-policy native
payoff equivalence check and measured GPU memory/throughput must precede any
training integration. The active stratified study and its registered evaluation
still take priority.
