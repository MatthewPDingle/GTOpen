# Wider test: a remaining BB decision leak is measurable

The complete population test and independent file audit passed. The candidate
still has a statistically detectable first-decision weakness: a response learned
on separate training deals improves BB's result by **0.293 bb per entry into
this fixed spot**, with a simultaneous interval of **0.106 to 0.479 bb**.
This is not a table-wide win rate, full best response, or accuracy certificate.

The earlier linear averaging result reduced the exact fold/shove and initial
BTN-response errors, but that narrower improvement did not establish that the
ordinary fold/call/raise/jam decision was accurate. This wider test now gives
positive evidence of a remaining error. Do not deploy the candidate as a
qualified preflop replacement or treat the small exact-all-in gains as its
total remaining exploitability.

## Fixed experiment

The candidate is the complete fresh 78-generation bank, using linear weights
1 through 78 for both players. The unplayed next generation is excluded.
The spot is BB versus a BTN 2bb open at 200bb, with fold, call to 2bb, raise to
6bb, and shove; configured rake is 5% capped at 2bb. Incoming ranges, omitted
folded-player cards, the limited action tree, and all later play remain fixed.
It does not reproduce the original eight-handed straddled Wizard comparison.

Response training used 256 deals for each of 169 BB classes: 43,264 deals.
Fold and shove values use the exact admitted physical-pair endpoints. Call and
raise values are sampled. The resulting class-based first-action rule was
frozen and hashed before constructing the separate 131,072-deal IID population
test stream. The registered evaluation had one final statistical look and five
fixed alternatives, with total family error probability 0.025.

| First-action alternative | Mean gain (bb/spot entry) | Simultaneous interval |
| --- | ---: | ---: |
| Trained class-based response | 0.29253 | [0.10589, 0.47917] |
| Always fold | -0.42052 | [-0.60395, -0.23710] |
| Always call | -0.28099 | [-0.48623, -0.07575] |
| Always raise to 6bb | -3.09155 | [-3.35969, -2.82340] |
| Always shove | -12.82359 | [-13.00702, -12.64017] |

These are gains relative to the same frozen candidate, not comparisons to
GTO Wizard. The upper interval endpoint bounds this one tested deviation's
gain; it is **not** an upper bound on the best possible deviation or on
full-game exploitability. The four deliberately crude always-action rules
losing does not establish that the baseline is good.

## What changed in the learned response

| Action | Candidate | Trained response |
| --- | ---: | ---: |
| Fold | 39.31% | 49.00% |
| Call | 39.71% | 41.67% |
| Raise | 18.86% | 9.32% |
| Shove | 2.12% | 0.00% |

Frequencies use the exact incoming BB population mass. The response selects
fold/call/raise for 69/83/17 classes respectively. This is a profitable fixed
response to these particular frozen later policies, not a new recommended
preflop chart. Copying it into a jointly changing game is not the tested result.

The total gain decomposes into -0.06248 bb of exact fold/shove offset and
+0.35501 bb of estimated call/raise residual. That supports studying ordinary
call/raise decisions as well as the all-in noise correction. It does not
identify the exact causal source of every hand's error.

The two training halves choose different actions for 83 of 169 classes,
covering 51.47% of incoming population mass. This predeclared diagnostic was
not used to choose the response. The positive aggregate test result remains
valid for the frozen response, but individual hand recommendations are too
unstable to describe as a reliable new chart.

## Verification and recovery

The independent readback reconstructed all 43,264 response-training draws,
131,072 population-test draws, 2,724 batches, 169 action choices, both stability
halves and all five intervals. Maximum scalar disagreement was 3.93e-12 bb.
The reader reconciles stored native payoffs; it does not independently rerun
the native poker engine or neural inference.

The original S-drive attempt stopped at its storage reserve. A separately
registered T-drive recovery reused 1,219 hash-verified completed batches,
replayed the original chance streams, verified the same frozen response and
preparation, and computed only the 1,505 missing test batches. Neither counts,
seeds, final-look rule nor candidate changed. The original failed attempt is
preserved. The recovery evaluation took 9,668.8 seconds and its audit 659.6
seconds. The completed evaluation store contains 75.24 GB of logical data.

Authoritative artifacts use prefix `later-average-wider-recovery-v1`:
`registration.json`, `evaluation.json`, `independent-review.json`, `result.json`
and `status.json`. Detailed native evidence remains in the registered T-drive
store. The full protocol and earlier failure are documented in
`WIDER-RESPONSE-RECOVERY-PLAN.md` and `WIDER-RESPONSE-STORAGE-OPERATIONS.md`.

## Next research decision

Finish the exact-initial training integration checks, then evaluate a fresh
candidate without assuming that lower all-in error fixes ordinary calling or
raising. Preserve a broader root-action test in the acceptance path. The new
correction has a specific mathematical justification and passing CPU/CUDA
integration checks, but has not yet demonstrated better poker performance.
The first CUDA single-model gate exposed a small rounding mismatch. Its
diagnosis and resolution are recorded in `EXACT-INITIAL-INFERENCE-PRECISION.md`;
that numerical finding does not explain the much larger measured poker leak.
