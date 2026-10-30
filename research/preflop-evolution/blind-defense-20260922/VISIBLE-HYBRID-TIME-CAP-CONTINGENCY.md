# Prospective handling of a training time-limit stop

Recorded 23 September 2026 at 11:39 Adelaide time, while the registered resumed
trial was still running. It had completed update 66 of 78 after approximately
3,033 seconds of its 4,818.625-second resumed allowance. Recent updates took
157-173 seconds. Finishing twelve more updates may exceed the remaining
allowance. No intermediate candidate policies, evaluation values or hand-choice
results were inspected to make this decision.

The present controller, worker, registrations, caps and audits stay unchanged.
If it finishes normally, this contingency is unused and the existing queued
audits and evaluations proceed.

## If the registered cap stops training

1. Verify that the controller and worker are actually terminal. Preserve their
   stopped statuses, logs, resource history and partial final update. Record the
   original capped experiment as incomplete; never report it as having passed.
2. Admit a separate completion only for a verified execution-deadline stop with
   at least 72 and fewer than 78 fully saved updates. A crash, data mismatch,
   resource-reserve failure or production activity is not covered by this
   contingency and needs its own diagnosis.
3. Independently replay the complete saved prefix using the unchanged original
   chance stream, action seeds, reservoir streams, integer all-in labels and
   retained-table reconstruction. Only a passing prefix audit may be resumed.
4. Freeze a new completion registration and use a separate store. Retain all
   complete immutable prefix files and checkpoint objects; exclude the partial
   next update. Restore both reservoirs and their RNGs, chance/action RNGs, the
   complete played bank and the next model. Preserve the original batch IDs.
5. Allow at most **1,200 additional training-controller seconds**, including
   restore/import overhead, solely to reach the originally fixed update 78.
   Keep the same 512 deals/update, fit steps, seeds, architecture, cache,
   optimizer, numerical settings and resource reserves. No extra updates,
   intermediate selection, alternative model or automatic repeated extension.
6. Before launching, check that the training loop is unchanged and that the
   restored next chance/action draws reproduce any already saved partial batch.
   Audit the final prefix, completed update count and complete played bank.
7. Run the originally specified evaluation families, seeds, sample counts and
   numerical controls on the completed 78-update candidate, under a separate
   completion provenance. Do not substitute the new exhaustive BTN endpoint
   for those registered sampled evaluations.

## Interpretation

This continuation would answer the intended **matched-update** representation
comparison. It would no longer be a successful trial within the original
three-hour cumulative training cap. Report both stopped attempts, cumulative
training-controller time, audit/restore costs and the extra allowance. Do not
claim matched wall-clock efficiency or hide the runtime overrun.

The prepared candidate-independent complete equity cache can still be used
afterward. Accuracy remains unqualified until the relevant independent value
tests; completing the updates and passing replay checks are not evidence of
better poker decisions by themselves.
