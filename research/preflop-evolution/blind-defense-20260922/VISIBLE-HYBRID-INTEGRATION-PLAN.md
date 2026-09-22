# Visible-feature integration admission

This is a four-update correctness run, not a preflop strength experiment. It
cannot launch until the existing research workload releases its GPU lock and
production is idle. No full candidate is admitted by this plan.

## Fixed control

Use the independently reviewed combined direct-preflop/exact-all-in control's
configuration, sampler, action seeds, reservoir seeds, fitting seeds, optimizer,
512 steps per fit, and native traversal. Run exactly four updates of 512 deals
(2,048 deals total). Retain its all-in cache, payoff estimator and action menus.
The only representation change is the explicit 302-input visible feature model
with matched original weights and zero-initialized appended columns. New-format
checkpoints include the feature specification and original 269-input records.

The run has its own storage and output prefix:
`sampled-visible-hybrid-allin-control-v1`. It has a 15-minute wall limit, 5 GB
output limit, and retains 20 GB host RAM, 3 GB VRAM and 40 GB SSD free. Production
activity, integrity failure or resource limits stop it; there is no automatic
retry, extension, deployment or result-driven candidate selection.

## Admission sequence

1. Existing visible checkpoint, CPU bank and CPU noisy-repeat fitting controls
   must pass, with all registered source/artifact hashes unchanged.
2. Run the frozen synthetic-bank CUDA check:
   `hu_visible_hybrid_gpu_bank_control_v2_20260923.py --run`.
   The original v1 attempt stopped because the required deterministic cuBLAS
   workspace environment setting was absent. Its registration and failure are
   preserved. Version 2 sets that launch requirement before importing Torch;
   the GPU bank implementation, test models and tolerances are unchanged.
3. Run the noisy-repeat fitting check on CUDA:
   `hu_visible_hybrid_fit_backend_control_20260923.py --device cuda`.
   Its independent raw CPU objective/gradient and full-tensor optimizer reference
   use the same fixed synthetic records as CPU mode. Nonzero within-observation
   target variance is deliberate; these targets are not poker outcomes.
4. Only after those gates pass, run
   `hu_visible_hybrid_allin_control_20260923.py --run --control`.
5. After the controller and worker are terminal, run
   `hu_visible_hybrid_allin_review_20260923.py --control`.
   It reconstructs every deal, action seed, reservoir insertion and preflop
   table, verifies the native cashflow/reference evidence, checks complete-bank
   membership, and restores the exact final reservoir/RNG state. The initial
   uniform update must reproduce the 269-input control's observations, policies
   and numerical targets, apart from transport identifiers. This review does
   not independently rerun neural fitting or inference.
6. Run `hu_visible_hybrid_saved_policy_control_20260923.py --run` to reproduce
   every saved CUDA float32 policy row exactly. It additionally compares the
   complete four-model played bank under CPU/CUDA float64 inference on every
   first-update query batch. Use only the control's existing observations.

All CUDA steps require the exclusive research lock and retain production-idle
and resource checks. They run sequentially, never beside the active combined
experiment. A failed gate stops admission and remains preserved for diagnosis.

## What passing would mean

Passing would establish that the new representation can travel through this
short training/checkpoint/evaluation pipeline consistently. It would not prove
that the learned ranges improve, that sampled continuation values are accurate,
or that the approach works across arbitrary preflop configurations. A separate
full-budget trial protocol, fresh evaluation streams, and strategic analysis
remain necessary before any deployment recommendation.
