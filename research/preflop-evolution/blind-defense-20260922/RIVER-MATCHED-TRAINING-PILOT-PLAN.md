# Next matched river-target training pilot

Prepared 2026-09-28; not yet admitted or started. This plan is not a result.

## Purpose

Measure complete training cost and check whether conditional river targets alter
the fitted policies usefully. The existing baseline integrates future actions
at one sampled opponent hand. The candidate adds the qualified posterior64
river-only overlay. Keep that single treatment fixed.

## Initial states and learning budgets

The read-only preflight validated both complete 78-update board-root checkpoints:
9266201-board-root and 9266301-board-root. Each includes played generations 0..77,
next model 78, reservoirs, sampler/action RNG state, board-root accumulator and
exact BTN accumulator. Both states restore successfully under their original
configuration. Candidate configuration adds only explicit river-target method
and K=64; create a new fork checkpoint rather than relabel the source.

For each seed, create baseline and candidate copies at that identical boundary.
Required source objects total 615,647,430 bytes across all four copies. Preserve
all originals. Run two complete joint updates per arm (iterations 79 and 80),
using the existing 512-deal generations, 64-deal subbatches, 512 optimizer steps,
262,144-row reservoir capacity, four board draws and all original seeds/rates.
Counterbalance arm order across the two seeds. Four physical CPU workers and
four board workers are a prospective choice, subject to resource admission.

First-update physical source draws, action draws, visit order and root policies
should be identical across each pair before the river substitution. In the
second update, policies legitimately differ, so later visit counts may differ;
the common source/action random streams and declared budgets remain matched.

Use the versioned candidate pipeline. Preserve complete joint publication and
exclude the next unplayed model from played-policy averages. Test checkpoint
reload and a deterministic replay of one candidate update, using a fresh replay
folder. Deliberate stop before publication must leave the caller's full state
unchanged. Account for these qualification runs separately from training cost.

## Why two updates, and limits

After just one new update, both played-policy banks are still identical: the
changed fitted model has not yet played. Two updates include changed model 79
in the 80-model average. Model 80 is still unplayed. Any current-model diagnostic
must be labelled separately and never passed off as the played-policy average.

This short warm-start pilot retains many historical reservoir targets and old
played models. It can show mechanics and costs, and preliminary policy effects;
it cannot establish long-run convergence or broad preflop range accuracy.

## Prospective evaluation

Before generating any test deals, freeze and register the full runner, policy
identities, budgets and inputs. Proposed fresh evaluation: 1,024 common physical
deals, seed 9293101, eight crossed full-policy player-replacement contrasts with
one final look. No matching existing registration/plan used that seed at the
preparation check. Recheck when registering. Use the established native full-
action evaluator and conditional all-in cache; preserve paired cashflow checks.

Compare the complete played-policy averages, with own-history reach weighting.
An optional current-model diagnostic is separate exploratory evidence and needs
its own declared policy identity. Do not tune on this final pilot set. Report
intervals, source coverage and elapsed costs including board targets, fitting,
publication and evidence IO. Positive point estimates alone do not qualify a
production model. An equal-time learning comparison remains a later requirement.

## Admission

No GPU training has started. Last probes show 100% external GPU utilization;
do not compete with the user's heavy workload. Light desktop/video sharing is
authorized under the qualified <65% admission check, 4 GB own CUDA budget and
2 GB external headroom. Probe after suspending own GPU work, so own utilization
is not mistaken for competition. Active production solves take priority.

Refresh the global allocated-storage inventory before launch. Prospective new
study cap: 8 GB, with 2 GB follow-up reserve, within the global 800 GB ceiling.
Use compact conditional transport. Preserve raw source evidence and failures;
resume only from complete published boundaries. No production deployment or push.

The full-update runner and GPU/restart checks are still to be completed. The
spawned-worker check and source preflight are finished and recorded separately.
