# Candidates to consider after the registered trials

These are proposals, not implemented improvements or measured speedups.

## Sampling variance reduction

The six-player screen favors cheaper terminal evaluation over a discount-schedule
change. If the large tests confirm this, consider a control-variate estimator:

`full_mean(reference_ranges) + sample_mean(current_ranges - reference_ranges)`

Both sampled terms must use the same latent particles. Reference ranges and their
full mean must be frozen consistently; multiply by the current counterfactual
reach probability, not the historical one. This is unbiased for the current
finite terminal mean at fixed inputs. Unbiased terminal estimates alone are not
a multiplayer convergence theorem. Measure actual iteration count, wall time,
memory, reference refresh cost and full-model quality before retaining it.

Potentially this permits fewer samples without as much added noise. It does not
require a neural range predictor or more hand histories. Generic baseline-based
variance reduction has primary research support in
[Schmid et al.](https://arxiv.org/abs/1809.03057) and
[Davis et al.](https://proceedings.mlr.press/v119/davis20a.html).
Those papers do not establish a speedup for GTOpen's current multiway evaluator.

## Interactive-line convergence

The selected local audits show that global convergence and usable conditional
answers are separate requirements. Keep the global accuracy check and add explicit
conditional checks on user-selected lines. A corrective local solve would need
the actual arriving ranges, unchanged legal actions/pot/locks and a new global
check after merging changes. This would be additional convergence work, not an
early preview milestone. Prior conditional-preview research cannot be relabeled
as a validated solution to this issue: its arriving-prefix correctness was unresolved.

## Lower-priority work

Assess GPU regret-pruning opportunity before implementation. The CPU already has
periodic regret refresh logic; GPU currently uses reach-based active gating for
terminal CDF work. Skipping zero-own-reach updates indiscriminately is invalid.
Further work must specify the regret bound, revisit rule and work actually avoided.
Neural value approximation remains a larger fallback if measured sampling and
convergence improvements are insufficient; it is not the first next experiment.
