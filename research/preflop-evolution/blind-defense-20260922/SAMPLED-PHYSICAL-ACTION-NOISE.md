# Opponent-action sampling is a measurable part of root-target noise

This diagnostic fixes the old 16-deal numerical-control fixture and its frozen
78-generation averaged policy. It changes only the action-sampling seed across
64 repeats. No new cards, learned policies or held-out outcomes are used.

The existing exact fixed-deal evaluator supplies each root action's conditional
expected payoff by averaging all later actions. Its root-only forced-action
profiles were checked against the original profile row by row. The existing
sampled walker supplies the comparison targets; all 2,048 updater traversals
passed its cached-versus-direct reference check.

| Root action | Within-deal action-sampling variance (bb squared) | Between-deal variance of exact expectations (bb squared) | Estimated removable fraction on this fixture |
|---|---:|---:|---:|
| Call | 99.19 | 117.81 | 45.7% |
| Raise | 1,062.42 | 1,285.15 | 45.3% |
| Jam | 3,684.03 | 15,352.63 | 19.4% |

Fold is exactly -1 bb; its numerical reconstruction error was below 9e-16 bb.
The fraction is the estimated within-deal component divided by the sum of that
component and the fixture's between-deal component. Sixteen fixed deals are not
a population study. These percentages are neither a convergence improvement
nor a speedup, and they say nothing about neural fitting error.

## A specific follow-up if the larger-data trial remains weak

For BB's first decision, replace the sampled root advantage with the same-deal
conditional expectation under the unchanged frozen policy. Preserve the sampled
visits and all other target records. There is no earlier path to reweight at this
root. Averaging later opponent actions would remove that source of sampling noise
while retaining uncertainty from dealt cards and changing training policies.

This is a proposed estimator change, not yet a training implementation. It needs
separate transport labeling, independent payoff checks, a measured runtime cost,
and a newly registered strength comparison. It must not silently modify the dense
or hybrid trial. Extending the idea to later decisions needs additional care with
visitation and counterfactual reach.

Related primary research studies unbiased baseline estimators for variance
reduction in MCCFR. It supports investigating estimator variance, but does not
validate this specific proposed implementation or imply the same gains here.
[Schmid et al., AAAI 2019](https://ojs.aaai.org/index.php/AAAI/article/view/4048).

## Readback

`sampled-physical-action-noise-control-v1-independent-review.json` verified all
fixed deals and policies, all repeated native artifacts, exact reconstructed
sample arrays, and root-only control changes. Independent `fsum` calculations
agreed with the reported statistics within 1.9e-12. It did not rerun native
execution. The source, registration and all evidence hashes are preserved.

Production, the preview, and the ongoing dense trial are unchanged.
