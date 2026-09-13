# Shared-reference variance reduction: convergence screen rejected

The implementation passes numerical correctness and memory accounting, but
does not improve time to the required combination of global and conditional
accuracy. No second-seed extension, large learning run or deployment is admitted.
Port 56708 was unchanged throughout.

## Completed comparison

Fresh six-player, 23,038-node fixture; seed 42; native counterfactual units;
DCFR gamma 15 and horizon 1000. All runs use identical source and executable
hashes. Every 25 iterations, evaluate the canonical 1,024-particle global gap
and all 169 hands at each of six fixed branches. Qualification requires global
gap <= 0.005 bb and all six conditional checks twice consecutively. The cap is
3,000 iterations. Times include preparation and checks through the final check,
but exclude compilation and the separate saved-file audit.

| Learning method | Particles | Iterations | Seconds | Final gap (bb) | Branches | Qualified |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Native control | 1,024 | 3,000 | 184.802 | 0.00028436 | 4/6 | No |
| Native sampled control | 64 | 2,700 | 33.192 | 0.00066406 | 6/6 | Yes |
| Previous CV, refresh 32 | 64 | 3,000 | 63.559 | 0.00056701 | 4/6 | No |
| Shared CV, refresh 32 | 64 | 3,000 | 60.409 | 0.00031519 | 4/6 | No |
| Shared CV, refresh 64 | 64 | 3,000 | 56.625 | 0.00031933 | 4/6 | No |

Both shared variants independently fail conditional accuracy. The registered
screen also required a qualifying full-particle control, which did not qualify
within its cap. Neither a smaller final global gap nor a shorter capped run is
a time-to-qualified-solution improvement. The successful plain sampled result
is one small-fixture seed, not a large-game claim.

Each run has an independent saved-file audit that exactly reproduces its final
per-hand checks. `check_shared_cv_screen.py` recomputes stopping, full-model
gates, reference refresh counts, capture counts, source identity and selection.
`raw/shared-cv-screen-verified.json` records the verified result and no selection.

## What worked

One shared reference snapshot, packed live-traverser terminal values and
captured learning graphs reduce extra large-tree storage from 12,196,748,616
to 3,089,822,268 bytes (74.67%). This is exact geometry accounting, not a tested
large GPU allocation. Small GPU allocation and numerical checks are documented
in [SHARED_CV_NUMERICAL_RESULTS.md](SHARED_CV_NUMERICAL_RESULTS.md). The default
release solver suite and both native GPU equivalence suites pass.

## Interpretation and next boundary

Reducing sampling noise did not repair the conditional branches in this
screen. Together with the earlier zero-current-reach diagnostic, this motivates
investigating how learning visits rare branches. It does not prove that noise
itself causes the successful sampled trajectory.

Do not extend these CV runs unchanged. A distinct next candidate is a correctly
formulated behavioral perturbation with an eventual return to unrestricted
learning. Unlike the rejected opponent-only reach mix, it must consistently
modify own continuation, regret updates and strategy accumulation. It needs an
independent numerical derivation and epsilon-zero native equivalence before a
bounded convergence test. Global and per-hand acceptance gates remain unchanged.
