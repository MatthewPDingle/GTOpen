# Physical observation GPU fit and reload

The GPU implementation check passed after waiting for the previous research
experiment to finish naturally. The common GPU lock serialized the jobs; no
running solver or experiment was interrupted. The live application is unchanged.

This uses exactly the frozen physical-observation records and architecture from
the [CPU integration control](SAMPLED-PHYSICAL-FIT-CONTROL.md). It is a fixed-data
fit to synthetic behavior, not a physical-poker self-play study or evidence of
better ranges. The finite strategic qualification remains separate.

## Checks and results

- All 1,785 physical observations were evaluated with the same trained CPU
  weights on CUDA and compared against the Rust adapter. Maximum score error
  was 2.87e-6; maximum action-probability error was 8.37e-6.
- For the same parameters and legal-action-masked, count-weighted loss, CPU/GPU
  gradients agreed within 1.12e-7 absolute error.
- Fresh seeded networks were fitted on GPU for the same 128-step budget.
  Normalized training loss fell from 1.35103 to 0.05530 for BB and from
  1.65297 to 0.01998 for BTN. These are fitting residuals, not strategic losses.
- Exporting those GPU-trained weights and reloading them in Rust gave maximum
  score error 2.39e-6 and action-probability error 6.60e-6 across all inputs.
- All score and policy comparisons passed the predeclared 2e-5 and 1e-4 bounds.
  CUDA used float32, deterministic algorithms and disabled TF32. Maximum tensor
  allocation was 71,696,384 bytes, excluding CUDA context and other processes.

The small fit is not a GPU speed benchmark. CPU and GPU optimizer trajectories
need not be identical despite close gradient agreement; note the slightly
different BB fitting residual. Before relying on GPU learning for a poker pilot,
its finite-game strategic behavior still needs checking under the registered
stopping rule, not merely assuming bitwise identity with CPU training.

Evidence prefix: `sampled-physical-gpu-v1`. The registration freezes the inputs,
tolerances, seeds, 128 steps, a 180-second execution cap and a bounded queue wait.
The controller checks production activity and memory reserves, stops only its
own child if required, and never retries failed outcomes automatically. The
review verifies frozen input hashes and the recorded result; fitted weights and
Rust replay outputs carry hashes in that result.
