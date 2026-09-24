# Root-retention trial: complete independent evaluation

The complete test and independent readback passed on 24 September 2026.
Preserving every sampled BB first-decision advantage is promising, but this
run does not establish accurate preflop ranges or justify production deployment.

The previous model's frozen challenger is now unprofitable against the new
profile: -0.291 bb per entry, with a simultaneous interval entirely below zero.
A newly trained challenger has estimated gain +0.089 bb, but its interval
crosses zero and remains wide. The test therefore neither demonstrates a
profitable new deviation nor rules out a meaningful remaining weakness.

## Complete results

All 78 played generations (0 through 77) use the prospectively selected linear
weights. Generation 78 is excluded. The challenger was selected using 43,264
separate training deals, 256 per class, and frozen before 131,072 population
test deals. Later play remains frozen for both players.

| BB first-action alternative | Gain, bb per entry | Simultaneous interval |
| --- | ---: | ---: |
| Newly trained class-dependent response | +0.089304 | [-0.104912, +0.283521] |
| Always fold | -0.564200 | [-0.758222, -0.370177] |
| Always call | -0.875216 | [-1.098500, -0.651931] |
| Always raise to 6 bb | -4.038206 | [-4.331102, -3.745310] |
| Always jam | -11.537859 | [-11.731882, -11.343837] |
| Previous frozen class-dependent response | -0.290973 | [-0.498804, -0.083143] |

All six intervals use the registered bounded empirical Bernstein rule with
family error probability 0.025 and one final look. There was no sample
extension, quality-based stopping, checkpoint selection, or change of weights.

In the preceding experiment, its then-new challenger gained +0.230383 bb
with interval [+0.030301, +0.430464]. That exact policy is the previous frozen
response above (SHA-256 `85ad2773164f1cf71d683aeba3babd67789cd2fbb224e4632000fdbcf937666d`).
The new profile resists that particular policy. However, opponent continuation
play also changed, and the two newly trained challengers differ. The reduction
in their point estimates is not a measured reduction in full exploitability
or proof of a statistically reliable overall accuracy improvement.

## Hand allocation and uncertainty

These mixes use exact incoming population mass, not equal weighting of the
169 hand classes.

| Action | New candidate | New challenger |
| --- | ---: | ---: |
| Fold | 43.10% | 43.90% |
| Call | 41.12% | 37.12% |
| Raise to 6 bb | 15.33% | 18.54% |
| Jam | 0.45% | 0.44% |

The challenger selects fold/call/raise/jam for 65/71/32/1 classes. The two
training halves disagree on 62 of 169 classes, covering 35.82% of incoming
mass. Previously, they disagreed on 74 classes and 43.56% of mass. This is
descriptive evidence, not a significance test or a basis for choosing a half.
Individual challenger choices remain too unstable to serve as replacement
charts. For example, its choice to fold 77 while the candidate mostly raises
is a diagnostic discrepancy, not a recommendation to fold that hand.

The separate post-hoc attribution reconciled all 2,048 test batches and all
169 classes to the published aggregate. The new response's estimated gains
by selected action are call +0.052852, fold +0.079471, raise -0.027439, and jam
-0.015580 bb per entry. Thus the estimate includes offsetting gains and
losses. No new group-level confidence claim is made; those descriptions reuse
the completed test and must not become a tuned policy evaluated on that same
test. The all-class record is in `root-retained-wider-attribution-v1-result.json`.

## Verification and resources

Independent scalar readback reconstructed all 43,264 training deals, 131,072
test deals, 2,724 batches, 169 response choices, both training halves, and six
intervals. Maximum discrepancy was 5.34e-12 bb. This reconciles saved native
payoffs; it does not independently reimplement poker traversal or neural
inference. The preceding complete-bank CPU/CUDA control covers the numerical
inference path on its separate registered fixture.

Evaluation took 21,431 seconds, readback 848 seconds, and the controller
completed in 22,377 seconds (about 6 hours 13 minutes). All 18,399 output files
are compressed: 74.98 GB logical data occupies 28.71 GB, below the 46.09 GB
allocation cap. The global storage admission, production-idle protections,
and resource limits passed. Production on port 56708 was not changed.

## Next research decision

Retain this mechanism as a research candidate and run one independently
seeded replication before adding another training change. Keep the same
context, 78 updates, sample budget, architecture, exact all-in targets, and
linear averaging. Change only the random streams. Register the new seeds and
fixed stopping rules before launch; use fresh training and fresh evaluation
data. Audit the full training record and report all exact endpoint results.
Any wider evaluation needs its own prospective sample plan and storage gate.
Do not pick whichever seed or checkpoint produces the prettier chart.

The purpose is to find whether this improvement persists across training
randomness. If the allocation remains unstable, study call/raise target noise
and downstream continuation learning using training diagnostics rather than
introducing hand-strength rules to make charts look plausible. The positive
endpoint results alone are not sufficient to resolve that question.

This remains BB versus a BTN 2 bb open at 200 bb, 5% rake capped at 2 bb,
fixed incoming ranges, and a limited action menu. Other depths, positions,
sizes, folded-card effects, and multiway play remain unvalidated. This trial
is one step toward flexible preflop modeling, not completion of that goal.

## Evidence identities

- Registration: `f5a9e0c1b1dd5bba73dca7786ebb110e809d12e4b79dab9e3e2c2a9f3c2b2004`.
- Evaluation summary: `7cebb3a69f7a172ebd5c1e5fe104f47bc231cc9aa6db8a68ae7cb8f08d269b1d`.
- Detailed result: `dc046cbc44b9c85372d708b1866cb71f10f48993cb0f37479c66b390a48c9685`.
- Independent review: `86047a27dbee24d5d69711a17e319344e5ca20f7f5ab022d32e652171a036618`.
- Controller result: `a16ab35d0848490dacef26459273abb75c38e0acc562e2f3c140657a2cc285cc`.
- New frozen response: `7a3d234c03db0ec88ba5c3cfe9304cfa5c74d8dc7accfb0385dfcaa379a9d57e`.
- Raw evidence: `T:/GTOpen-research/root-retained-wider-study-v1/evaluation`.
