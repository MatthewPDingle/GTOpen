# GPU strategic check for exact-mean advantage fitting

Status: first GPU case finished and failed the strategic target; remaining cases
continue under the unchanged registration. No deployment or preview change.

No-rake/seed-17 ended at **0.01040170152** at 2,048 updates, after
**0.01018870600** at 1,536. Neither is at or below 0.01, so it has zero qualifying
consecutive checkpoints. It must not be relabeled a pass or extended after seeing
the outcome. All eleven stored gaps were independently reconstructed exactly,
the frozen inputs and final bank hash were verified, and replay/averaging errors
remain zero. Implementation checks pass; the strategic gate does not.

The matched CPU case ended at 0.00735994681 and passed. The earlier GPU
small-reservoir/minibatch case ended at 0.02791287597; the revised GPU candidate
improves on that result but still misses its fixed target. These single-case
comparisons do not establish a systematic device penalty or isolate the cause.
The remaining runs are needed to assess consistency. The overall all-cases-pass
acceptance condition cannot be met by this candidate even if later cases pass.

This is the GPU counterpart of the
[revised CPU comparison](SAMPLED-NEURAL-MEAN-CONTROL.md), whose first completed
run passed the target. The [physical GPU fit control](SAMPLED-PHYSICAL-GPU-CONTROL.md)
established inference, gradient and weight-transport consistency, but it cannot
establish the behavior of a long self-play trajectory. Float32 arithmetic and
optimizer execution can change that trajectory, especially near action ties.

## Fixed comparison

Keep the existing finite imperfect-information game, both payoff settings,
seeds 17 and 31, 256 traversals per player per iteration, 262,144 retained
advantage records per player and 512 exact empirical-mean gradient steps per fit.
The architecture remains 28-64-64-3 with Adam learning rate 0.003. Networks start
fresh at the same per-iteration seeds. This is the full four-run comparison,
not a selection of the CPU run that passed.

Feature tensors, network evaluation, loss gradients and optimizer updates move
to CUDA float32, with TF32 disabled and deterministic algorithms enabled. Raw
target normalization and count-preserving grouping remain on CPU, as in the
paired reference, to avoid changing those reductions at the same time.
GPU/CPU strategy identity is not an acceptance condition; the same independent
exact strategic target is. This is a learning-method check, not a production
CPU/GPU speed benchmark.

Both updater passes see frozen policies. Ordinary signed regret matching uses
the highest legal action when no predicted advantage is positive. Retain every
actually played network, including the initial uniform policy; exclude the
unused final fit. Reloaded GPU weights must reproduce all played probabilities
within 1e-12, and own-reach model averaging must match the separately accumulated
average within 1e-12. All-information arrays are finite-game verification oracles,
not a scalable representation for physical poker.

## Stopping and safeguards

Checkpoints remain 1, 16, 32, 64, 128, 256, 512, 768, 1,024, 1,536 and 2,048.
Stop each run at two consecutive exact summed best-response gaps <=0.01, or
2,048 iterations. The controller has a four-hour total execution cap: if that
cap is reached before all cases finish, preserve completed/partial evidence and
report the experiment as incomplete, without changing its registered budget.
There is no automatic retry or outcome-based extension.

The common research GPU lock is exclusive. Production activity is checked every
two seconds; starting a user solve stops only this research child. Reserve at
least 20 GB of host RAM and 3 GB of VRAM. The ongoing CPU comparison uses its own
lock and can continue independently. No production server is restarted.

The final review must recompute all saved checkpoint gaps, audit the consecutive
stopping rule, check bank hashes and verify all frozen inputs. Passing the small
game still leaves full physical-poker learning and fresh independent evaluation
unproven. Evidence prefix: `sampled-neural-mean-gpu-v1`.
