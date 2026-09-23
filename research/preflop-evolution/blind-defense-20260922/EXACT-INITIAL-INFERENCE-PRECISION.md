# Exact-initial runtime: CPU/CUDA integration passed

The current validated research path is `exact_initial_training_v2.py` with
`exact_initial_single_policy64_v1.py`. It requires the explicit configuration
`current_policy_inference = float64-widened-float32-weights-v1`.
Network fitting and saved weights remain float32. Current-policy inference
widens those same weights and uses float64, matching the existing policy-bank
evaluator. This changes neither a hand-strength prior nor any action threshold.
Production and the completed wider evaluation were not modified.

## Preserved numerical failure

The first CUDA gate, `exact-initial-gpu-control-v1`, stopped because single-model
float32 CPU/CUDA probabilities exceeded its 1e-5 tolerance. The separate
`exact-initial-single-precision-diagnostic-v1` checked both complete initial
catalogs and native later-street queries for all frozen fixture models.

Three historical postflop query rows exceeded that tolerance. The largest
probability discrepancy was 2.376e-5, or about 0.0024 percentage points. Small
differences in positive network scores were amplified by normalization. Model
coverage agreed, and the exact BTN overrides were not the cause. This was a
small numerical mismatch, not an explanation for the roughly 0.293 bb poker
leak found by the independent wider study. The failed gate and its original
source/registration are preserved.

Instead of relaxing the failed tolerance, the new single-model runtime uses
the same widened-weight arithmetic as the already admitted float64 averaging
bank. Gate v2 tightens single-model probability tolerance to 1e-10.

## Passing checks

`exact-initial-gpu-control-v2` passed on the RTX 3090:

- 12 CPU/CUDA single-model comparisons; maximum probability discrepancy
  2.37e-14.
- 36 bank comparisons across two fixture banks, complete initial catalogs and
  native own-action histories, three weight schedules and three model chunk
  sizes. Maximum probability discrepancy 1.84e-14; reach discrepancy 3.48e-14.
- Non-response probabilities and their own-action reach remained identical to
  the corresponding base CUDA bank.

`exact-initial-joint-cpu-control-v2` and
`exact-initial-joint-gpu-control-v2` each completed two real native training
updates and reproduced the second update from a saved checkpoint. Each used
64 fresh deals plus 32 replayed deals and four fitting steps per player/update.
Native artifacts, learned models, exact state, reservoir contents and all
chance/action/reservoir RNG states matched the restart on the same backend.
These tiny controls took about 17 seconds each; they are not performance
benchmarks or poker-strength candidates.

Independent CPU readbacks of both controls reconstructed all 64 corrected BB
roots, all 1,066 BB / 205 BTN insertion events, the complete initial catalogs,
every saved query policy and both checkpoints. Target discrepancies were below
2.85e-14 bb. Policy discrepancy was zero for the CPU control and 8.11e-15 for
the GPU control. The readers did not call the new trainer/target adapter or
accumulator update, did not refit, and used no GPU.

The prepared version-1 CUDA joint control was never run: version 2 uses the
resolved inference arithmetic and the passed version-2 policy gate. All older
CPU controls remain valid for their explicitly declared older runtime; they
are not silently relabeled as evidence for the new one.

## Remaining work

Register and run a fresh fixed-budget trial. Its changes must explicitly name
the BB root exact conditional shove target, the separate exact BTN cumulative
counterfactual update, and the unified current-policy inference precision.
Evaluation must retain ordinary call/raise alternatives; passing these
integration gates or reducing exact all-in error cannot establish good
preflop ranges, full-game convergence or cross-context accuracy.
