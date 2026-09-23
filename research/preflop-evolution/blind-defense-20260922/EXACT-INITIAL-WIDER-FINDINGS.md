# Exact-initial candidate: completed wider evaluation

24 September 2026. The fixed evaluation and independent readback both completed
successfully. The candidate still has a profitable BB first-action deviation
and is not ready for production.

## Main finding

A newly trained class-dependent BB response gains **0.23038 bb per original
entry into this spot**, with simultaneous interval **[0.03030, 0.43046]**.
Its positive lower bound identifies a remaining weakness even with all later
decisions held fixed. It is not a full best response or an upper bound on
exploitability.

The previous frozen response now has estimated gain **-0.00544 bb**, with
interval **[-0.20929, 0.19841]**. Its estimated advantage is near zero, but the
interval includes substantial positive gains. We cannot claim that weakness
is eliminated. The old and new broader tests used different samples and
different newly trained responses; the reduction from the old 0.29253 estimate
to 0.23038 does not establish a statistically reliable overall improvement.

The separate exact all-in screen did improve by about 75% for both players;
see [the endpoint findings](EXACT-INITIAL-ENDPOINT-FINDINGS.md). This broader
result confirms that improving those endpoints does not finish the ordinary
calling/raising problem.

## All registered alternatives

| BB first-action alternative | Gain, bb per entry | Simultaneous interval |
|---|---:|---:|
| Newly trained class-dependent response | +0.230383 | [+0.030301, +0.430464] |
| Always fold | -0.438195 | [-0.633221, -0.243169] |
| Always call | -0.330141 | [-0.546605, -0.113676] |
| Always raise to 6 bb | -3.401183 | [-3.691347, -3.111019] |
| Always jam | -10.680674 | [-10.875700, -10.485649] |
| Previous frozen class-dependent response | -0.005440 | [-0.209287, +0.198407] |

All six intervals follow the prospective bounded empirical Bernstein rule,
family error 0.025, one final look after 131,072 independent population deals.
The new response was frozen after 43,264 separate training deals, 256 per
class. No checkpoint search, strategic early stopping or sample extension was
used. Both players' later play remains that of the complete new linear bank.

## What the profitable response changes

| Action | Candidate | Newly trained response |
|---|---:|---:|
| Fold | 41.55% | 43.02% |
| Call | 38.51% | 47.54% |
| Raise to 6 bb | 19.23% | 8.62% |
| Jam | 0.71% | 0.83% |

These frequencies use exact incoming population mass. The response selects
fold/call/raise/jam for 63/86/19/1 hand classes. Its estimated gain comprises
0.01454 bb of exact fold/jam offset plus 0.21584 bb of sampled call/raise
residual. This points toward studying call/raise learning and continuation
values, but does not isolate which training mechanism causes the error.

Training halves disagree on 74 of 169 classes, covering 43.56% of incoming
population mass. This diagnostic was not used for selection. The aggregate
positive result is evidence of a weakness; the individual choices are not a
stable replacement chart and have not been tested after changing later play.

## Verification and scope

The independent scalar reader reconstructed all 43,264 training and 131,072
test deals, 2,724 batches, 169 response choices, both training halves and six
intervals. Maximum scalar discrepancy: 4.24e-12 bb. It reconciles stored native
payoffs rather than independently rerunning native traversal or neural
inference. The separate 78-model CPU/CUDA admission covers that numerical
path on its registered 64-deal fixture.

Evaluation took 16,993 seconds including worker overhead; independent readback
took 798 seconds including overhead. The controller completed in 17,861
seconds, about 4 hours 58 minutes. Raw evidence is preserved at
`T:\GTOpen-research\exact-initial-wider-study-v1`.

This is the fixed heads-up BB-versus-BTN 2 bb open context, 200 bb stacks,
5% rake capped at 2 bb, and a limited action menu. It does not validate other
stack sizes, positions, trees, folded-card effects or multiway play. Production
on 56708 is unchanged.

## Next research action

Before another expensive training run, diagnose how much BB root information
is discarded by the shared finite advantage reservoir. The current preflop
table uses means of retained samples, while root call/raise targets are still
sampled. Reconstruct all root samples from the completed training record and
compare their coverage and regret-matched policies with the retained tables
at the same boundaries. This is a post-hoc training diagnostic, not a new
candidate or another look at the population test. It can distinguish a
cheap data-retention opportunity from the need for more expensive variance
reduction. Any changed trainer requires fresh controls and fresh evaluation.

## Evidence identities

- Registration: `67da210b25391365e130e69beb898fee7266162baee99df0ec1acde8d8463e0b`.
- Evaluation summary: `c72c7242de65ad24c497b89a97ca77b17ae3ecbf030804fecb5762829c3c6862`.
- Detailed result: `3b7ac91c4b71d9404f6a0d40ef4f8616f69316d97d6f7133bbbed17e36411f1f`.
- Independent review: `e2050dad081bd0c18780eed2370ac3168c8333506758b3254b4b662b64f90ed1`.
- Frozen new response: `85ad2773164f1cf71d683aeba3babd67789cd2fbb224e4632000fdbcf937666d`.
- Frozen prior response: `73ea827f70d5c6cb055c98e01775ea51d0b95aa23c92e29c3282aa4fec307c2b`.
