# Batch inference to physical-poker updates

The corrected version-2 bridge passed. It exports the bounded cache's observable
rows, evaluates frozen player networks as tensors, and transports their legal
probabilities back into the physical-poker traversal. Both updater passes use
those same frozen probabilities. This is a usable research data path, not a
trained equilibrium or a change to the live ranges.

## Pipeline and scope

`hu_sampled_batch_bridge_v2` offers `queries`, `walk` and `verify` modes. A batch
contains physical deals, a seed, an ID and an explicit query budget. The bridge
rejects invalid deals and excessive query counts rather than reducing hand
support. Query rows contain only the acting player's visible observation,
legal-action count and identity. Metadata carries exact context/batch provenance;
it is not passed as neural input.

`sampled_batch_model_v1.predict` evaluates each player's network only on that
player's rows. It preserves the caller's CPU random-generator state, uses legal
regret matching with the established highest-legal fallback, and emits no mass
on unavailable actions. The version-2 protocol binds every returned row to its
canonical key, actor and legal menu, as well as the original context and batch.
Use `sampled_batch_protocol_v2.policy_document` for this binding; the version-1
protocol is retained only as failed experimental evidence.

Walk mode emits signed update records and per-deal updater values. Verify mode
also reconstructs policy lookup on demand from canonical keys and compares every
traversal's root value, records and random-generator state. All visit records
remain separate, including duplicate observations. The consumer must preserve
their multiplicity and distinguish positive-tag advantage records from
negative-tag opponent-policy observations.

## Fixed-data results

The 16-deal fixture produced 7,280 raw queries and 7,277 canonical observations.
Batched PyTorch and independent NumPy scores differed by at most 3.10e-6.
Reversing the inference row order produced zero score difference in this test.
The caller's CPU random state was preserved.

All 32 traversals matched the independent lookup path exactly, producing 1,072
records across all four streets. Advantage records numbered 444 for BB and 32
for BTN. These small, unequal samples are implementation fixtures, not sufficient
training coverage. Six malformed transports were rejected: stale context, stale
batch, reordered rows, negative probabilities, wrong total probability and
probability assigned to an illegal action.

The registered control uses CPU tensor inference so it can run alongside the
active GPU strategic comparison. It took 1.24 seconds. CUDA inference is available
in the helper and its mathematical adapter has a separate passing control, but
the combined full-query CUDA bridge still needs its own execution check.
There is no GPU speed or new poker-strength claim here.

## Version-1 failure and correction

Version 1 compared parsed JSON context objects after a Rust/Python numeric round
trip. The unchanged input accumulated 629 tiny numerical representation differences
and was incorrectly rejected as stale before traversal. Its registered sources,
partial artifacts and failed status are preserved; it was not marked passing.

Version 2 carries the original context and batch text as opaque identity strings.
The engine still parses the original files for all game calculations. It checks
exact source identity without re-serializing context numbers or weakening the
check to a numerical tolerance. Actual changed settings are rejected. Assertions
also avoid printing the entire context on mismatch.

The version-2 review verifies 17 input hashes and all generated artifact hashes.
Malformed-input files are retained under `target/research-sampled/` and are
reproducible from the registered control; source recipes and their hashes are
saved. A separate post-hoc audit checks the serialized probabilities in visited
opponent-policy records against the Python inputs within 1e-12.

Evidence prefixes: `sampled-batch-bridge-v1` (failed identity check) and
`sampled-batch-bridge-v2` (passing corrected bridge). Neither changes the finite
accuracy experiments. Remaining steps are full-query CUDA integration, streaming
bounded training reservoirs, the physical self-play pilot, and fresh independent
evaluation. Strategic qualification must not be inferred from data-path checks.
