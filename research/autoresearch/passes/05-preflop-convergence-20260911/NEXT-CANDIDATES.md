# Candidates to consider after the registered trials

These are proposals, not implemented improvements or measured speedups.

## Reassess the remaining cost after the large 64-sample result

The completed eight-player 64-sample run spends 491.48s learning and 166.73s
checking the full model, out of 660.54s to the second passing check. Checks are
now 25.2% of that time. Native learning takes 4920.68s, so learning-only work is
about 10x faster while actual time to the target is 7.69x faster.

Before investing in a larger estimator change, screen check scheduling and
the cheap combination of the existing gamma15 schedule with sampling. Keep
the same full-model threshold and two passing full checks; compare any changed
check schedule against an equally scheduled native baseline. Do not claim a
10x convergence result by omitting validation time, projecting multiplied gains,
or giving only the candidate fewer checks. A schedule change still needs fresh
timing and quality results. These follow-ups are not part of the currently
running registered queue and have not been measured.

## Sampling variance reduction

The six-player screen favors cheaper terminal evaluation over a discount-schedule
change. If the large tests confirm this, consider a control-variate estimator:

`mu(R_ref) + mean_s_in_S[f_s(R_current) - f_s(R_ref)]`

Here `f_s` is the existing particle's conditional multiway pot-share evaluation,
and `mu` averages it over all 1,024 particles. Evaluate the two sets of normalized
opponent ranges separately. Do not feed their elementwise difference to the
equity evaluator: its products of opponent CDFs are nonlinear in those ranges.

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

### Memory and cost screen before implementation

The completed `eight-s128-a.log` records 388,082 compact CDF slots, 32-particle
batches, about 8,445 MB of CDF scratch and 13,075 MB planned total device storage.
Its 805,640 terminals provide a conservative bound; only live multiway terminals
need the proposed reference equity means. Use decimal MB consistently below.

A dense upper estimate for persistent means is
`805640 * 169 * 8 * 4` bytes, or 4356.90112 MB; normalized reference ranges for all eight
traversers cost at most `388082 * 169 * 8 * 4` bytes, or 2098.747456 MB, with the existing
compact mapping. A single traverser's temporary sampled means cost at most
`805640 * 169 * 4` bytes, or 544.61264 MB. Together these add about 7,000 MB, placing
the planned total near 20,075 MB before new maps, flags, allocator/runtime
overhead and other applications. This is an arithmetic feasibility estimate,
not an allocation test or a promise that larger/modeled trees fit.

Prefer two sequential sampled evaluations through the existing CDF scratch:
store the current sampled means, rebuild that scratch from frozen reference
ranges for the same particles, then combine with the full reference means.
Duplicating the 8,445 MB scratch as well would exceed a 24 GB device on this
conservative layout. Keep full-accuracy checks on their unchanged evaluator.
The extra sampled pass and periodic full reference refresh are real costs;
benchmark them, including any smaller particle batches required by memory.

Cache validity must be explicit per traverser. A zero-mass reference range must
either use a defined reference distribution with a consistently computed full
mean, or fall back to the original estimator. Current zero counterfactual mass
still returns zero. Do not clamp the control-variate estimate into [0,1] merely
to make it look like equity: that would introduce bias. Treat reference snapshot
consistency, current reach weighting, finite arithmetic and full-model quality
as prerequisites, not follow-up polish.

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
