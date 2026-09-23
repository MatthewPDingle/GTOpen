# Next training integration: preserve raw traversal evidence

The version-4 model, checkpoint and CPU runtime controls are ready. CUDA parity
and actual training integration remain untested. Do not change the current
wider evaluation or start competing GPU work.

At each new training iteration, freeze the current version-4 policy for both
players and every subbatch. Evaluate its entire admitted initial-node catalog
once. The exact matrix must use those current played policies, not the final
average or the historical fixtures used in serialization controls.

For each BB updater's initial root record, preserve the native batch, policies,
updates and cashflow-verification results unchanged. The known fold payoff and
reported root value identify its sampled action values. Replace only the root
shove action value with the exact conditional value for BB's hand class, then
recenter all four advantages under the same frozen root policy. Cross-check
the reconstructed baseline against the native root-value record and require
both old and corrected own-policy-weighted advantages to sum to zero.

Produce separately typed derived training targets; never rewrite a native
format-3 update while retaining claims that its new values passed the native
cashflow verifier. A validation-only receiver can collect the existing ingest
function's checked insertion events without consuming a reservoir RNG. Derive
and validate every correction before inserting events into the real reservoirs
in their original per-player order. Keys, visible features, action counts,
iteration tags, insertion counts and reservoir-selection draws must match the
unmodified ingest. Only affected BB root target values may differ.

Keep ordinary call/raise and postflop records unchanged. Keep the original BTN
sampled records in the network reservoir for this declared comparison, while
the exact runtime table overrides its initial response. Update the separate
exact BTN accumulator exactly once per completed played generation using the
full matrix and opponent reach already included once. Do not add its sampled
records to that accumulator. Both next networks and the next exact state must
be complete before publishing the next model/checkpoint.

Before a fresh trial: test the ingestion transformation against independent
action-value reconstruction on old immutable native traces; verify all other
records and RNG streams; reject malformed batches without partial insertion;
then check CUDA policy parity, native execution, complete small training replay
and restart restoration. A fresh comparison must declare seeds, budget,
unchanged components, evaluation and stopping before running. These integration
steps do not address other positions/stacks or certify ordinary calling play.
