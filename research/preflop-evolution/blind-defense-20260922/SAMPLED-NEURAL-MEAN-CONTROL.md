# Self-play with larger retention and exact retained-data gradients

Status: completed; all four CPU cases pass the registered stopping target.
This is a finite learning-method qualification,
not a new BB policy, production deployment or CPU preflop performance project.
The original GPU bank comparison finished with four strategic-target failures.
A separately registered matched exact-mean CUDA comparison is now running.

The [capacity control](SAMPLED-RESERVOIR-CAPACITY.md) showed lower error with
262,144 retained examples per player. The [fixed-data controls](SAMPLED-LARGE-FIT-CONTROLS.md)
then verified that grouping repeated observations with their counts gives the
same squared-error gradient as visiting every retained training example. It
removes training-minibatch noise; it does not remove retained-sample noise or
guarantee a sufficiently accurate network fit.

This candidate uses the same observable 28–64–64–3 network, highest-regret
fallback, sampler, 256 traversals per player per update, frozen policy for both
passes, ordinary iteration weights and retained-model averaging. Changes are:

- 262,144 retained advantage examples per player rather than 32,768.
- 512 full retained-data gradient steps per fit rather than 128 random minibatch
  steps; Adam remains at 0.003 and each fit starts from a newly seeded network.
- CPU float32 fitting with two threads. This isolates it from the live GPU job;
  it is not a hardware speed comparison or proof of CUDA-equivalent trajectories.

The 512-step budget is a registered candidate, not a claim that every fit is
accurate enough. Fixed-data diagnostics still showed substantial action-mix
error for one such fit. The self-play test must determine whether the resulting
averaged strategies meet the target. Capacity, fitting method and budget change
together, so the strategic result cannot attribute gains to one factor alone.

## Frozen evaluation and stopping

Run both payoff settings (no rake and capped 5%) with seeds 17 and 31, at the
same checkpoint schedule through 2,048 updates. Stop each run only after exact
summed best-response gain <=0.01 at two consecutive checkpoints, or its cap.
No outcome-based extension or automatic retry is permitted.

Every checkpoint saves all played advantage networks, excluding the newly
trained unused model. Reloaded parameters must reproduce every played policy
within 1e-12. Their own-reach-weighted bank average must match the independently
accumulated finite average within 1e-12. The complete run is reviewed by
re-evaluating stored policies, checking stopping rules and checking source and
final-model hashes. No passing result is assumed from a low fitting loss.

The controller reserves 20 GB of free RAM, has a 10,800-second total deadline,
and checks production activity every two seconds. It uses no GPU and its own
research lock, so it can run alongside the existing GPU control. If a production
solve starts, only this research child is stopped and available evidence is
preserved. Full interrupted-training resume is not yet implemented.

## Completed results

Evidence prefix: `sampled-neural-mean-cpu-v1`. Every case crossed 0.01 at two
consecutive registered checkpoints and stopped at the first eligible checkpoint.

| Payoffs | Seed | Final update | Previous checkpoint gap | Final gap |
|---|---:|---:|---:|---:|
| No rake | 17 | 2,048 | 0.00877510285 | 0.00735994681 |
| No rake | 31 | 1,536 | 0.00906805970 | 0.00972530205 |
| Capped 5% rake | 17 | 2,048 | 0.00973602234 | 0.00660413599 |
| Capped 5% rake | 31 | 2,048 | 0.00796620370 | 0.00736837890 |

These are exact summed best-response gains in the finite control's payoff units.
The second run's final gap increased while remaining below target; learning is
not assumed monotonic. The controller completed normally in 9,720.08 seconds
(about 2 hours 42 minutes), within its original three-hour cap.

The full controller review and a separate terminal-result audit verify all 13
frozen inputs, all four final bank hashes, and every stopping decision. All
**43 checkpoint gaps** reconstruct exactly from the stored average policies;
the two player EVs and best-response values also reconstruct within 1e-12.
Stored checkpoint model replay errors are zero and own-reach averaging errors
are below 1e-12. The terminal audit rechecks those recorded errors and model
hashes; it does not rerun every network forward pass a second time.

The earlier small-reservoir/minibatch GPU run ended at 0.02791287597 for
no-rake/seed 17 at the same update cap. The revised CPU run's final gap is 73.6%
lower. Capacity, fitting method, fitting budget and device changed together;
the comparison does not isolate one cause or measure physical-poker improvement.

## What this qualifies

This establishes that the revised CPU implementation can meet the registered
target across these four finite controls. It does **not** qualify its CUDA
counterpart: the first completed matched GPU case misses the target, and the
remaining cases continue unchanged. The four CPU passes cannot override that
failure or justify relaxing the GPU stopping rule.

The second CUDA case (no rake, seed 31) is now terminal too. It passed at
2,048 updates: the last two gaps were **0.00597943024** and **0.00653332093**.
An independent review reconstructed all 11 stored checkpoint gaps exactly,
verified the stopping rule, all 16 registered inputs and the final model-bank
hash. Stored replay checks passed; this review did not rerun every saved
network. Evidence is `sampled-neural-mean-gpu-v1-case0-seed31-independent-review.json`.
The two no-rake seeds therefore give one failure and one pass under the same
budget, rather than a uniform CUDA failure.

The capped-rake seed-17 CUDA case has also completed and passed at 2,048
updates. Its last two gaps were **0.00960521569** and **0.00776814065**.
Its separate review again reconstructed all 11 checkpoint gaps exactly and
verified all 16 registered inputs, stopping, stored replay checks and the final
bank hash. Evidence is `sampled-neural-mean-gpu-v1-case1-seed17-independent-review.json`.

| CUDA payoffs | Seed | Terminal result | Final gap |
|---|---:|---|---:|
| No rake | 17 | Missed target at 2,048 | 0.01040170152 |
| No rake | 31 | Passed at 2,048 | 0.00653332093 |
| Capped 5% rake | 17 | Passed at 2,048 | 0.00776814065 |
| Capped 5% rake | 31 | Running | Pending |

Two of the three terminal CUDA cases passed. The last case is running within
the original **four-hour total cap**, not a fresh four-hour budget. A budget
stop before its own stopping condition would leave it incomplete, not failed
at 2,048 or passed. The first failure already prevents an all-four pass.
No target, case order or budget changed, and these finite results do not
qualify actual-poker strength.

Finite arrays and repeated-observation grouping do not establish generalization
to physical poker's much larger information space. The separate
[physical fit/reload](SAMPLED-PHYSICAL-FIT-CONTROL.md),
[checkpoint](SAMPLED-PHYSICAL-CHECKPOINT-CONTROL.md), and
[fixed-profile evaluation](SAMPLED-PROFILE-EVALUATION-CONTROL.md) checks qualify
parts of that integration only. Physical self-play and independently reserved
poker evaluation are still needed. Production and the preview remain unchanged.
