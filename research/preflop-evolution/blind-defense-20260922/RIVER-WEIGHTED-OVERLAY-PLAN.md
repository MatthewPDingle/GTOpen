# Actual weighted-ingestion posterior64 control

Prepared before execution, 2026-09-28. The native K=64 candidate passed its
eight-case comparison, with 2.528x throughput relative to exhaustive opponent
averaging. This step qualifies its connection to real training storage. It
does not fit a model, modify a played checkpoint or claim improved ranges.

Generate one complete 384-deal class-stratified TRAIN source with seed 92828201.
Validate it through DealWeightGeneration. Use exactly its first four deals as
one-deal slices at original offsets 0..3, for each last-played generation-77
model from the earlier registration. Native action seeds are 92828301+offset,
shared across the two policy cases. Do not fabricate weights for old fixtures
or choose replacement deals if a case is empty or unfavorable. Preserve all
eight cases, any empty river sets and any unsupported-posterior rejection.

For each model construct InitialTargets from the complete current preflop
catalog policy and admitted exact matrix. Use the complete v2 private all-in
cache and original native bridge/trace. Use the existing board_training_policy_v1
path for ordinary query inference, and compare every conditional river target's
current policy with that original row. first_action_view annotates only
structurally initial nodes. Complete native river histories supply their own
history dependencies for the two-stage conditional inference. Use K=64 and
the qualified identity-derived sampling stream unchanged.

Build the full river overlay first, binding it to context, raw queries,
policies, native updates, trace, generation/source slice, iteration, current
policy and independent generator evidence. Its rows cover positive river
records once in original order. Require finite legal zero-padded values,
current-policy centering and strictly positive opponent support. An unsupported
batch rejects before reservoir mutation. No source weight multiplies a target.

Then run the original weighted ingester into a staging collector, preserving
its native cashflow verification, exact initial correction, full-action
flop/turn derivation and source weights. Replace only validated river values,
then perform real WeightedPhysicalReservoir insertion in original order.
Use capacity 7 and deterministic per-actor seeds 92828401+actor. Compare with
an independent oracle that replays baseline collected visits with only the
approved values substituted. Compare keys, active features, arities, iteration
labels, source weights, values, counters and RNG state. Compare all non-value
state with the original baseline reservoirs. Retain counts of overflow to show
Algorithm R was actually exercised. Save/load each candidate reservoir and
check round-trip identity. All preflop/flop/turn collected values must be exact
matches, and the original three audits must be unchanged.

Before any real mutation, reject wrong policy/query/trace/source/evidence
bindings, duplicate/missing/reordered or misidentified visits, nonfinite values,
illegal padding, miscentering, zero support and wrong sample count. For the
chosen negative-control fixture use the first encountered case with a river
row, and a row with fewer than four actions for illegal-padding checks; this
is only test-input selection, not omission from positive results. Snapshot
complete reservoir state before and after each rejection. Also corrupt the
underlying native trace to prove the original validator still executes.

CPU only; no GPU use or production writes. Maximum 300 seconds and 512 MB
new evidence, with 64 MB output headroom before native calls, 24 GB free RAM
and idle production. This stays under the last inventory plus subsequent
bounded allocations (<722 GB against the 800 GB research cap). Register and
recheck inputs and retain output hashes. Preserve failed attempts and version
corrections. Full training still needs an in-memory transport/storage budget,
matched compute accounting and fresh full-policy evaluation.
