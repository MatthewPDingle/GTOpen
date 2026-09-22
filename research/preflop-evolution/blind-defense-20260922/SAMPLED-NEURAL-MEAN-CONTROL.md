# Self-play with larger retention and exact retained-data gradients

Status: registered and running. This is a finite learning-method qualification,
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

Evidence prefix: `sampled-neural-mean-cpu-v1`. The first checkpoint passed its
replay checks; strategic results remain pending. Finite arrays and duplicate
grouping are method controls, not a claim that the full physical poker problem
has only a few observations or now fits in memory. A successful candidate still
requires physical-observation integration and independent poker evaluation.

The first no-rake/seed-17 run passed its registered stopping rule. Exact gaps
were **0.00877510285** at 1,536 updates and **0.00735994681** at 2,048: two
consecutive checkpoints below 0.01. The saved-bank hash and all 13 frozen inputs
were reverified, all 11 checkpoint gaps were independently reconstructed exactly,
and model replay errors remain zero.

The second no-rake/seed-31 run also passed: **0.00906805970** at 1,024 updates
and **0.00972530205** at 1,536, then stopped as registered. Its final gap rose
slightly while remaining below target; improvement is not assumed monotonic.
All ten checkpoint gaps were independently reconstructed exactly, the 13 inputs
and final model-bank hash were verified, and replay errors remain zero. Both
raked runs are still pending. These two passes do not qualify the overall four-run
candidate or physical poker. Per-case evidence includes the terminal seed-31
result and its separate review JSON.

The earlier small-reservoir/minibatch neural run ended at 0.02791287597 on this
same case/seed and update cap. The revised run's final gap is 73.6% lower. This
combined change includes reservoir capacity, fitting method, fitting budget and
device; it does not isolate one cause and is not a physical-poker accuracy claim.
The separate [physical fit/reload control](SAMPLED-PHYSICAL-FIT-CONTROL.md)
qualifies that integration step only, without changing this experiment.
