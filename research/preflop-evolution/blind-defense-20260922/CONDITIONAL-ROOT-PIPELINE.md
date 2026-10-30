# Direct conditional evaluation path

The full-sample diagnostic showed useful variance reduction, but reused saved
profiles and evaluated them as a second pass. A future fresh study needs a
direct path from model inference to conditional payoffs.

`sampled_conditional_root_evaluation_v1.py` provides that separate path. It
accepts an explicit policy bank and an exact equity cache, queries the original
visible observations, computes the complete averaged strategy, constructs the
four root-action deviations, and evaluates them with the conditional all-in
native evaluator. It does not run the old sampled-payoff evaluator first.

The policy bank uses the existing unlabelled query document and visible feature
rows. Exact equity labels go into a separate terminal-evaluation batch. The
function preserves both documents, their identities and the connecting policy
rows. Its format-2 summary explicitly identifies conditional preflop all-ins,
the cache hash, sampled postflop outcomes and all five supporting artifacts.
It cannot be treated as an unchanged old-format evaluation summary.

The integration control uses the complete 78-model hybrid played bank with
float64 CPU inference on the same 256 diagnostic deals as the earlier reviewed
learned-bank control. It compares complete query, policy and native payoff
documents, and verifies that reconstructed root values match the summary. No
new chance stream, responder, GPU job or strength evaluation is launched.

The control **passed** in 210.7 seconds. All 256 deals, 78 played models and
16 unlabelled policy-bank calls were retained. Complete policy and native-output
documents matched the separately reviewed reference exactly; summary payoff
error was zero. This establishes integration equivalence on those fixtures,
not fresh strategic accuracy or CUDA equivalence for a future candidate.

This prepares a reusable component, not a new experiment. A future controller
still needs a frozen candidate and precision choice, checked CUDA inference,
separate responder-training and test streams, exact labels for those streams,
fixed counts/error budgets, both-player checks, resource admission and a final
readback. The active all-in study keeps its original evaluation protocol.

Evidence uses the prefix `sampled-conditional-root-pipeline-control-v1`; local
query/profile/native artifacts use that prefix under `S:/GTOpen-research`.
