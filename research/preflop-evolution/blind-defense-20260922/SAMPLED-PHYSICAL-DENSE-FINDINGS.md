# More training data: encouraging root result, not an accurate-range certificate

The 39,936-deal candidate completed its registered 8,192-deal response training
and 16,384-deal fresh held-out test. Independent readback passed all 1,536 batches,
both chance streams, the frozen response, 81,920 paired differences, numerical
controls and final interval arithmetic. Evaluation took about 21.5 minutes,
including CPU controls; independent readback took another 6.1 minutes.

## What improved in this test

The test asks how much BB can gain by changing only its first decision against
the candidate's frozen BTN strategy, keeping later behavior fixed. The alternative
response is selected on the separate response-training stream before any test
deals are drawn. Values are bb per entry to this BB-versus-BTN spot.

| Candidate | Training deals | Measured response gain | Conservative interval |
|---|---:|---:|---:|
| Original physical pilot | 4,992 | +2.080 bb | +0.080 to +4.080 bb |
| Larger-data candidate | 39,936 | +0.389 bb | -0.990 to +1.768 bb |

These are the registered bounded intervals, controlling error at 5% across each
trial's five comparisons. They are not a paired confidence interval for the
difference between candidates: test seeds and both players' strategies differ.
The lower point estimate is encouraging, but the intervals are broad. Failure
to demonstrate a profitable deviation does not establish approximate equilibrium.
This test is not an upper bound on exploitability and does not test all of BTN's
decisions or postflop improvements.

All 169 root classes met the response-training support threshold in the dense
test; no held-out deal required the unchanged-policy fallback. In the original
test, 167 classes met it and 94 held-out deals used the fallback.

## The actual action mixes

These frequencies are averages over each candidate's sampled held-out deals,
including their card compatibility. They are not unweighted 169-cell averages
or exact full-population frequencies.

| BB's first decision | Original | Larger-data |
|---|---:|---:|
| Fold | 48.82% | 53.81% |
| Call | 21.16% | 26.04% |
| Raise to 6 bb | 16.05% | 12.87% |
| Jam to 200 bb | 13.97% | 7.28% |

The larger-data candidate's separately trained diagnostic response calls 30.69%,
raises 6.87%, jams 8.72% and folds 53.72% on its test deals. This is a restricted
response against a frozen opponent, not a new joint policy to deploy.

Calling gains for individual hands remain noisy: the held-out sample contains
only tens of deals for many suited classes. We retain all 169 rows in the
comparison artifact rather than selecting attractive examples for training.

Some patterns still warrant investigation. For example, the dense bank jams 99
about 73% and AJs about 64% when facing the initial 2 bb open at 200 bb stacks.
A lower BB root-deviation estimate cannot tell us whether such aggression is
enabled by weaknesses in BTN's responses. This is another reason not to promote
the candidate based on that one metric or on visually appealing calls.

## Next controlled question

The direct-preflop hybrid experiment keeps the dense trial's game, starting
ranges, deal schedule, sample-store cap, network fitting and 78 updates. It uses
retained sampled advantages directly at observed preflop states, while preserving
neural postflop behavior and the fallback for unobserved preflop states. Its
evaluation uses reserved new streams and the same fixed protocol. This tests
preflop regression error; it does not remove historical sampling noise.

In parallel with that training, a useful diagnostic is BTN's response to BB's
jam. Existing held-out deals can locate a weakness, but reusing them is a
post-hoc diagnosis, not fresh confirmation. It must not tune the frozen hybrid
trial or justify hand edits. Later confirmation still needs new evidence and
broader decision coverage.

The production model and the UTG-versus-LJ range preview are unchanged. This
study remains one separate heads-up blind-defense context, with fixed incoming
ranges, a restricted postflop tree and no earlier folded-card information.

Evidence: `sampled-physical-dense-evaluation-v1-result.json`, its
`independent-review.json`, `sampled-physical-dense-comparison-v1-result.json`,
and `SAMPLED-PHYSICAL-HYBRID-PLAN.md`.
