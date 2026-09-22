# Fitting the larger retained sample without changing self-play

Two CPU-only diagnostics use the frozen seed-17/no-rake, 2,048-update table
reservoir from [the capacity comparison](SAMPLED-RESERVOIR-CAPACITY.md). Each
player has 262,144 examples and 28 occupied observations. Neither experiment
changes the sampled learning trajectory or demonstrates strategic improvement.

Both use the existing 28–64–64–3 ReLU network, Adam at 0.003, float32 fitting,
raw-target RMS scaling, and two starting-model seeds. The CPU random-number
stream differs from earlier CUDA fits; no claim of identical CUDA trajectories
or GPU throughput is made. The live GPU comparison was left running separately.

## Larger random batches

Registered fits used 128 steps of 512 examples, 128 steps of 8,192 examples,
and 512 steps of 8,192 examples. Larger batches reduced excess mean-fitting
error in all four player/initialization combinations at the same 128 steps.
However, action-probability agreement was not uniformly improved by longer
fitting. One player-1 fit reduced excess MSE from 0.00240 to 0.00106 while its
visitation-weighted probability L1 error increased from 0.209 to 0.701.

For a frequently observed decision, empirical action advantages were only
[-0.0002452, +0.0002452], while that fit predicted [0.02457, -0.00668]. This
reversed the regret-matched action. Action-probability error is sensitive to
small advantages and is not itself a measured best-response loss. The result
supports checking fitting precision rather than judging ordinary training MSE
or strategy-chart appearance alone.

All 12 fits completed in 31.61 seconds. Nine frozen inputs verified. Per-visit
loss equaled irreducible retained-target variance plus excess mean-fit error
within 1e-10. Evidence: `sampled-large-fit-cpu-v1`.

## Exact retained-data gradients

For repeated observations, squared-error gradients depend on the target mean
and observation count. Grouping identical observable inputs and preserving
their multiplicities yields the full retained-data gradient; the omitted
within-observation variance is constant with respect to the network parameters.
This is not a change to the regression target, a hand-strength bucket, or a
lookup embedding. It removes random training-minibatch noise while preserving
the retained dataset's sampling noise.

Before fitting, the test compared full 262,144-record losses and all parameter
gradients against the grouped calculation in double precision. Maximum gradient
errors were 1.20e-13 and 3.25e-13; loss-decomposition error was 2.23e-16.

The fixed gradient comparison then used 128, 512, or 2,048 float32 optimizer
steps from the same starting models. At 2,048 steps:

| Player | Initial seed | Excess mean-fit MSE | Weighted probability L1 |
|---|---:|---:|---:|
| 0 | 991 | 2.83e-8 | 0.000049 |
| 0 | 20260922 | 5.15e-6 | 0.000151 |
| 1 | 991 | 2.11e-8 | 0.014028 |
| 1 | 20260922 | 7.65e-6 | 0.045410 |

The 512-step fits were less consistent: player 1/seed 991 retained probability
L1 error 0.436 despite excess MSE 1.81e-5. Better numerical fits do not establish
an acceptable self-play convergence rate or justify a fixed probability floor.

All 12 fits and gradient controls completed in 17.75 seconds. Ten frozen inputs
verified. Evidence: `sampled-mean-fit-cpu-v1`. Timing is diagnostic only; the
first fits include framework initialization and the tiny game has just 28
occupied observations per player. Physical poker will have many more distinct
observations. Its training cost and convergence remain unqualified.

The next self-play candidate can test larger retention with exact retained-data
gradients under a separately registered fitting budget. Passing this frozen-data
diagnostic is insufficient; independently evaluated learned strategy averages
must also improve before moving to physical-poker training.
