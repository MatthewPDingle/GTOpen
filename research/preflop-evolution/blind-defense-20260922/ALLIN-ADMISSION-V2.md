# Admit the unchanged all-in trial after the repaired hybrid evaluation

The prepared v1 study launcher requires the original hybrid evaluation v1,
which failed its numerical gate before any held-out deals were generated.
That prerequisite cannot complete. Preserve the launcher and all sources
frozen by the existing pipeline control. The new v2 launcher instead requires
the complete hybrid repair workflow, evaluation v2 independent review,
range comparison and supplementary BTN diagnosis/readback.

This changes scheduling prerequisites only. The seven child stages, dense
training baseline, exact all-in cache, model architecture, fit, chance streams,
sample counts, statistical families, deadlines and resource guards remain
those in SAMPLED-PHYSICAL-ALLIN-PLAN.md. No hybrid result is used to select
hands, seeds, hyperparameters or a checkpoint. The wrapper prefix becomes
sampled-physical-allin-study-v2; all child prefixes remain v1.

## Numerical precision decision

Keep the prepared all-in trial's original float32 evaluator to isolate its
training-estimator change against the float32 dense baseline. The observed
hybrid near-tie failure is a known risk, not grounds to relax numerical gates.
The first 256 response-training deals still require independent CPU/CUDA
policy and payoff agreement before held-out evaluation. Any failure stops the
trial without automatic retry. A further precision change would require a
separately recorded diagnosis and version, preserving failed evidence and
disclosing whether any held-out data had already been generated. A passing
256-deal control does not certify every possible near-tie observation.

## Entry point

`tools/research/hu_sampled_physical_allin_study_v2_20260923.py --run`

The admission helper verifies completed stages and log hashes, repaired
evaluation result/status/registration hashes and counts, and the supplementary
BTN audit. Existing cache and prepared-pipeline hash checks are retained. This
preparation does not launch training or modify production or the range preview.
