# Fixed-bank evaluation consumer: implementation findings

The consumer is implemented and its admission, selection and component
integration checks passed. The scientific comparison has not started: the
four 64-cycle training runs must first finish successfully and release ownership.
No improvement in poker ranges follows from these implementation checks.

## Complete played-bank selection

`stack_context_final_bank_v1.py` authenticates the final checkpoint metadata,
all four arm identities, the five fitting/two held-out depth partition, and
matched streams within each replication. It selects generations 0 through 63,
with weights 1 through 64 for each actor. It authenticates but excludes the
unplayed generation 64. The model loader uses the existing complete-model reader,
which binds each model's fitted local context state and source identity.

`stack-context-final-bank-check-v1-result.json` passed in 0.828 seconds. Synthetic
completion metadata exercised all four arms, 64 selected generations, the
excluded generation, and the 2,080 actor-weight sum. Twenty invalid cases were
refused, including the actual live arm at cycle 1. The loader-routing test used
an explicit mock reader; it is not a test of 64 trained models or their accuracy.

## Native transport and driver integration

`stack_context_evaluation_driver_v1.py` connects the existing full-action native
batch evaluator to the durable journal. On reopening and before the final look
it authenticates all completed archives. Resource pauses occur before the next
fresh batch. Partial scientific work cannot be automatically retried or skipped.

The combined check passed in 13.047 seconds, retaining 2,906,663 bytes of evidence
under `S:\GTOpen-research\stack-context-matched-evaluation-integration-check-v1`.
It used original retained two-deal fixtures at 20 and 60 BB, repeated to exercise
32-deal transport, plus two-generation synthetic routing models. The 20 BB fixture
uses fitted local overrides; the 60 BB fixture is held out. Four different
bank/weight combinations exercise the eight crossed profiles.

For both depths, the cached and existing reference complete-average paths gave
identical action probabilities, own-history support and native payoffs: maximum
observed differences were zero. Query counts were 296 and 622. Both sets of
actual native output artifacts passed the journal's input and value-identity
checks. Conditional exact all-in labels came from the already verified complete
cache. This is consistency with the existing reference and native evaluator,
not a second independent poker engine.

A separate in-memory driver check verified a pause after 64 deals, continuation
to exactly 4,096, no repeated evaluator calls after completion, refusal of partial
work, final archive verification, and exact final analysis. Its repeated fixture
payoffs are synthetic orchestration evidence, not independent scientific samples.

The check also invoked the controller's read-only default and verified refusal
to prepare scientific evaluation while training remains unfinished. It used CPU
only: no current trained-bank output, GPU inference, new fitting or scientific
test hands. Sources, artifacts and controller identity are recorded in
`stack-context-evaluation-integration-check-v1-result.json`.

## Consumer and remaining requirements

`stack_context_matched_evaluation_v1.py` is the prepared consumer. Its default
command reports readiness without starting work. `--run` additionally requires
successful unchanged training, all implementation gates, free study ownership,
and resource admission. `--run --resume` is restricted to the same admitted
comparison after normal exit at a complete boundary. Terminal failures remain
evidence and forbid automatic retries.

The controller pins all actual model/context/cache/program inputs before fresh
draws, evaluates the original seven-depth 4,096-deal protocol, and exports all
four complete averaged preflop policies with arriving ranges at each depth.
See `STACK-CONTEXT-MATCHED-EVALUATION-PLAN.md` for storage and execution bounds.
No frozen training input was modified; all 142 registered Python sources were
rechecked. No push, deployment or production-56708 change occurred.

Still outstanding: actual training completion; long 64-model bank performance
and resource behavior; the scientific evaluation and range exports; independent
result readback; plain-English outcome analysis; and the separately designed
continuation-prediction diagnostic. The main end-to-end admission and full run
cannot be exercised against finished scientific inputs before those inputs exist.
Fixed-entry heads-up BB/BTN gains would still not establish all-position or
multiway preflop accuracy or a full-game equilibrium.

Environment note: the restricted shell did not expose the installed `psutil`
module. The same read-only readiness command passed in the full Python environment
used by the study and controls. That shell limitation was not a scientific-run
failure and required no package installation or research restart.
