# A removable source of noise in root learning

The seed replication exposed unstable hand assignments. Two subsequent
diagnostics distinguish noise that remains even under a fixed policy from
additional noise caused by sampling opponent actions. The latter can be removed
without adding neural inference for the same physical deals. Whether that yields
better learned ranges still requires a matched training experiment.

## Fixed-continuation evidence, reusing existing data

The completed first root-retention wider evaluation already contains 256
class-conditional deals for every one of the 169 BB hand classes, evaluated
against one frozen average policy. Reanalyzing these 43,264 deals required no
new solves or large dataset. An independent standard-library reader reconstructed
the means, paired variances, covariance and half-sample choices; its maximum
scalar discrepancy was 1.36e-12.

The two 128-deal halves select different root actions in 62 classes, representing
35.82% of the exact incoming hand mass. Because the continuation is fixed here,
this disagreement is not caused by opponents changing between training updates.
The sampled action values are not yet precise enough to treat every maximizing
hand choice as a reliable prescription.

| Contrast | Incoming-mass-weighted RMS per-class standard error, bb |
| --- | ---: |
| Call minus fold | 0.917 |
| Raise minus fold | 1.533 |
| Call minus raise | 1.269 |

These are descriptive standard errors at 256 samples per class. They are not
simultaneous confidence bounds, errors on the whole-range mean, or evidence of
how many decisions are wrong. This sample was previously used to fit a responder.
The previous registered population holdout and its reported interval are unchanged.

Using the same physical deal for call and raise already helps: the weighted
paired call-minus-raise variance is 50.5% of the sum of separate call/raise
variances. This does not remove the remaining card/runout noise. Smoothing the
display would conceal the problem rather than establish accurate ranges.

## Opponent-action noise control

The training traversal samples opponent actions. The full-policy evaluator
instead averages all action paths on the same supplied cards. We used the
predeclared batch-00 fixtures at updates 1, 26, 52 and 78 from both audited
training runs: 512 saved physical deals. For every fixed policy/card fixture,
16 fresh action seeds were evaluated without drawing any new physical cards.

The independent reader passed all eight fixtures and 8,192 action-seed/deal
instances, including policy/card transport preservation, raw root payoffs,
root mixtures and conditional variances. Maximum scalar discrepancy was
1.14e-13. Native reverse evaluation and separate forward investment/cashflow
accounting agreed to their existing 1e-10 tolerances.

Across the fixtures, the RMS conditional noise from opponent-action sampling was:

| Quantity | Conditional standard deviation, bb per deal |
| --- | ---: |
| Call payoff | 9.32 |
| Raise payoff | 19.96 |
| Call-minus-raise payoff | 22.03 |

All fixture-specific variances and sample errors remain in the result artifact.
This is a small, intentionally selected diagnostic grid, not a population-wide
variance estimate. These figures must not be compared directly with the fixed
average-policy statistics above as a measured percentage improvement: the
policies, samples and conditioning differ.

The full action expectation is deterministic for fixed cards and policies, so
it eliminates this particular conditional randomness. It still samples private
cards and boards, uses the learned continuation and limited tree, and does not
make the root values exact preflop values. The native computation for all five
profiles took 0.266-0.313 seconds per 64-deal fixture. Serialization, storage,
fitting and inference are additional costs; this is not an end-to-end training
speed measurement. Crucially, the required complete current-policy query table
is already calculated by the present training runner.

## Implemented adapter and next experiment

`action_integrated_root_targets_v1.py` now derives separately typed BB-root
targets from the admitted full-action output. It:

- Keeps every later policy and original physical deal unchanged.
- Uses the full-action call/raise values on the supplied board.
- Preserves the existing exact initial-jam expectation over compatible private
  cards, rather than replacing it with one sampled private pair's value.
- Recenters advantages under the original current root policy.
- Leaves the old native updates and sampled reservoir rows untouched.

The adapter control passed all 512 roots, rejected 11 incompatible or malformed
inputs, preserved input documents, and had maximum centering error 6.22e-15.
It has not yet been connected to a trained model. The next step is a separately
typed checkpoint/training variant and a two-update CPU/CUDA/restart control,
followed only if admitted by the matched two-seed training protocol.

Do not claim the change improves ranges until complete audits, endpoint checks,
and cross-seed hand-allocation comparisons support that conclusion. A broader
fresh response evaluation would still be needed; full preflop accuracy and
generalization remain unresolved.

## Resource use and evidence

The action-noise control completed in 116.8 seconds. Its separate compressed
store occupies 354.4 MB allocated (572.0 MB logical), well below the admitted
2 GB allocation / 4 GB logical caps. It performed no GPU inference, no training,
no production changes and no deployment. All original files were preserved.

- Fixed-policy diagnostic: `root-fixed-variance-v1-result.json`.
- Independent fixed-policy reader: `root-fixed-variance-v1-independent-review.json`.
- Action control registration: `root-action-integration-v1-registration.json`
  (`d747e5ad9c7569777da65abe9df47ea6406a66b7bf2d47855465d9dfe81b9563`).
- Action control result: `root-action-integration-v1-result.json`
  (`d706945e689791aa4d13923e7011099c03877ed1e635c354d5b119c9d7f38bbd`).
- Independent action control reader: `root-action-integration-v1-independent-review.json`
  (`99f30af4d7c3f7573cd93b0322d68d70fb22116b2cd1977506e2006b4b8dd764`).
- Target adapter: `root-action-target-control-v1-result.json` and eight fixture artifacts.
