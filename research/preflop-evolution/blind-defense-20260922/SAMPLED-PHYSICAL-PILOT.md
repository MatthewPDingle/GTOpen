# Bounded full-deck BB/BTN training trial

Status: stopped at the registered one-hour execution budget with **78 complete
iterations**, all independently audited. The separate fresh-deal evaluation is
complete and audited; its [findings](SAMPLED-PHYSICAL-PILOT-FINDINGS.md) expose a
remaining profitable root deviation, so the candidate is not ready for use.
Production and the range preview remain unchanged.

## Terminal outcome and independent review

The final published checkpoint covers **4,992 fresh physical deals** and
**9,984 reference-matched traversals**. It retains 109,558 BB and 13,434 BTN
advantage records. Played generations 0 through 77 are eligible for the average;
newly fitted generation 78 has not played and is excluded. Iteration 79 was
interrupted and is excluded completely. The 128-iteration target was not reached.

The controller stopped 3,601.25 seconds after admission publication. Its last
execution-relative resource record was at 3,596.875 seconds, corroborating the
deadline assertion. The controller's `total_seconds` includes the earlier queue
wait and must not be described as training time. No observed resource limit was
breached: minima were 99.12 GB free host RAM, 21.86 GB free VRAM and 202.00 GB
free SSD; maximum recorded study storage was 1.72 GB (decimal units).

The independent review replayed every completed deal, traversal seed and reservoir
insertion, checked every iteration's recorded artifact hashes and model-bank
progression, and restored the final reservoir arrays and RNGs exactly. All 27
registered inputs verified. The review took 29.92 seconds. It did not rerun
neural optimization or GPU forward inference and does not establish strength.

Evidence: `sampled-physical-pilot-gpu-v1-independent-review.json`, terminal
`-status.json` and `-resources.json`. Reviewer:
`tools/research/hu_sampled_physical_pilot_review_20260922.py`.
The [fresh-deal study](SAMPLED-PHYSICAL-ROOT-STUDY.md) binds this budget-limited
checkpoint and its full played bank before drawing any evaluation data.

## Earlier admission and checkpoint checks

The admission records the finite GPU comparison's four-hour budget stop and
the combined CUDA pipeline's passing result. It explicitly retains the lack
of GPU strategic qualification. The first iteration sampled 64 fresh deals,
completed 128 reference-matched traversals, retained 1,098 BB and 320 BTN
advantage records, and published a restorable checkpoint. All 27 registered
inputs verified. Its played bank contains generation 0, excluding unused
generation 1. See `sampled-physical-pilot-gpu-v1-first-checkpoint-review.json`.
This first-checkpoint check proves data flow and restoration, not poker strength.

The terminal-review helper `sampled_physical_pilot_audit_v1.py` has also been
exercised on that first immutable iteration. It reproduced all 64 sampled deals,
the traversal seed, both players' retained records and reservoir RNG states
exactly from the registered seeds and saved update transcript. It checks each
iteration's artifact hashes, native verification evidence, fitting settings,
checkpoint progression and exclusion of the unused model. The one-iteration
read-only replay took 0.344 seconds. It does not rerun neural fitting or establish
strength. The whole completed prefix subsequently passed the terminal review
above. Evidence: `sampled-physical-pilot-gpu-v1-replay-prefix1-review.json`.

The revised finite CPU method passed all four registered accuracy tests. Its
CUDA counterpart has a completed failure, so it is not strategically qualified.
This trial does not override that result or relax its target. It investigates
the complete physical learning path, resource growth and fitted behavior in the
actual BB-versus-BTN context; a finite-model failure does not prevent collecting
clearly labeled diagnostic evidence on that different problem. No poker-strength
or deployment decision follows merely from completing the trial.

## Fixed scope and budget

- Preserve the saved BB/BTN incoming supports (169 and 96 hand classes under
  the existing per-combination cutoff), all three postflop branches, and the
  existing research betting menu. Earlier players' folded cards remain omitted.
- Sample 64 fresh compatible full-deck deals per iteration. Each deal supplies
  one frozen-policy updater traversal for each player. Opponent actions are
  sampled; every legal action of the updater is traversed. All runouts are
  available through full-deck sampling; this is not a reduced selected-flop panel.
- Use the existing observable 269-64-64-4 networks, 262,144 retained advantage
  visits per player, and 512 full retained-data Adam steps at learning rate 0.003.
  Chunks of 4,096 observations accumulate gradients before each optimizer step.
  Models start afresh from their registered seeds each iteration.
- Keep ordinary equal iteration weights and the played model bank. The newly
  fitted, unused next-generation model is excluded from the average.
- Stop at **128 completed iterations or one hour**, whichever comes first.
  The maximum completed training sample is 8,192 deals / 16,384 updater passes.
  The time limit may leave fewer completed iterations; that is an incomplete
  pilot, not a pass or an invitation to extend the budget automatically.

There is no convergence-gap stop in this pilot because no valid physical
best-response certificate is available. Training loss is recorded as a fitting
diagnostic, not substituted for exploitability. Stopping criteria and seeds are
registered before any new physical training draw.

## Admission and isolation

The controller waits for the existing finite CUDA comparison to become terminal
and the combined physical CUDA pipeline check to pass. It verifies frozen source
and prerequisite hashes and records the completed upstream outcomes before
launching the worker. A terminal finite failure or budget stop remains a failure
or incomplete comparison; it is not relabeled as a strategic pass.

The queue has a four-hour deadline. It will not clear a stale research lock,
compete with a live GPU-lock owner, or start after the combined CUDA check fails.
Once admitted, it takes the shared GPU research lock. Both waiting and training
stop on production activity. Only this controller's worker and descendants can
be stopped; the production server is never restarted or modified.

Reserves are 20 GB free host RAM, 3 GB free VRAM and 40 GB free SSD space.
The run's own storage limit is 40 GB. The S drive had about 204 GB free at
preparation, so admission checks the current free space rather than relying on
the earlier 800 GB estimate. Training stays on CUDA with deterministic float32
operations and TF32 disabled.

## Durable state

Artifacts are stored under
`S:/GTOpen-research/sampled-physical-pilot-gpu-v1/`, outside the build directory.
Every completed iteration retains its batch, query, policy and update hashes,
fitting metrics, model generation, and immutable checkpoint objects. Checkpoints
include the deal/action/reservoir random states and retained records.

`latest.json` advances only after a full iteration and its checkpoint have been
published. An initial `checkpoint-0000.json` also exists before the first deal.
An interrupted iteration is not valid training progress and must be discarded
when restoring the last completed boundary. Nothing resumes or extends itself
automatically: a continuation would need a separately reviewed invocation and
budget using the preserved checkpoint. This version has no resume command.

## Controller check and remaining evaluation

Before queueing, the actual pilot worker completed two tiny CPU iterations with
two deals per iteration, eight fit steps and 32-visit reservoirs. All eight
traversals matched the reference; published batch/update hashes verified; the
latest checkpoint restored; generations 0 and 1 formed the played bank and
unused generation 2 was excluded. Nineteen source/input hashes verified. This
6.76-second check covers worker orchestration and durable publication only,
not CUDA, long-run resources, the queue lifecycle or strategic accuracy.

A separate evaluation still needs frozen candidate policies and independently
trained responders, a declared compatible-deal distribution and fresh evaluation
draws. The completed fixed-profile payoff checks supply part of that path, but
no held-out test outcomes are examined or optimized during this training pilot.
Neither attractive root ranges nor lower regression loss can qualify deployment.

Controller: `tools/research/hu_sampled_physical_pilot_20260922.py --queue`.
Frozen registration: `sampled-physical-pilot-gpu-v1-registration.json`.
Worker check: `sampled-physical-pilot-controller-v1-registration.json`,
`-result.json` and `-review.json`.
