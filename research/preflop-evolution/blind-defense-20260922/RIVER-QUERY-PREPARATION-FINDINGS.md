# CPU river-query preparation: isolated improvement

The ongoing scientific continuation is unchanged. A separate CPU-only replay
found a preparation improvement worth qualifying for future training runs.
It does not demonstrate better poker play or a whole-training speedup.

## What was measured

A profile of the first two history/selected chunks from archived A-river update
79, batch 00, reproduced every original probability byte. Preparation dominated
neural inference in these four exports. For example, the first history export
took 3.125 seconds in profiled preparation versus 0.218 seconds in inference.
The profile identified repeated whole-query validation/table scans, alongside
feature and own-history preparation. cProfile overhead and concurrent training
make these descriptive timings, not isolated performance benchmarks.

The isolated candidate keeps the existing visible-array and own-history
validation. It checks key/phase agreement once, then applies the same preflop
tables in their original order only to preflop observations. Postflop rows keep
their original probabilities and arrays. Exact BTN and BB-root checks still run
on the preflop subset; table precedence and missing-row behavior are preserved.

## Completed comparison

The control used all 38 exports in that fixed historical batch, in their original
order, with the original generation-78 model. It replayed native exports against
archived byte counts and hashes, checked every prepared array byte, and checked
both implementations against the original stored policy arrays.

| Check | Result |
| --- | ---: |
| Export streams | 38 |
| Query rows, including repeated rows across exports | 916,635 |
| Prepared arrays and archived policy probabilities | Exact bytes |
| Invalid-input cases rejected by both implementations | 12 |
| Original preparation, sum | 39.865 s |
| Candidate preparation, sum | 21.130 s |
| Observed preparation ratio | 1.887x |
| Observed preparation time reduction | 47.0% |

The timing is one pair per export with alternating first implementation. Because
exports alternate history and selected, reference runs first on history exports
and candidate first on selected exports. This is not a balanced repeated timing
study. The main continuation was running concurrently. There is no claim that
the entire update becomes 1.887x faster; native export, posterior calculations,
inference, fitting and publication remain separate costs.

The invalid cases cover feature types, bounds and duplicates; actor and arity;
phase/key disagreement; own-history links/actions; and context mismatch. They
use a compact remapped ancestor chain from a real saved query. This is focused
validation, not proof for all possible malformed inputs or future table types.

## Next qualification

Keep this candidate out of the registered scientific continuation. Check broader
models and complete target-generation/update equality before future adoption.
The separate feature-preparation optimization also still needs its queued GPU
fit and complete-update checks. Neither changes the measured learning objective.

The CPU profile finished successfully in 13.766 seconds (exec 83243); the full
comparison finished successfully in 111.687 seconds (exec 84986). Both helpers
are stopped. Their result files record exact overlap timestamps. RSS fields are
sampled at guard boundaries, not complete peak-memory measurements. No new deals,
GPU work, fits, production modifications, push or deployment occurred.

Evidence and implementations:

- `river-query-cpu-profile-v1-result.json` and `river_query_cpu_profile_v1.py`.
- `river-query-preflop-subset-control-v1-registration.json` and its result JSON.
- `river_query_preflop_subset_v1.py` and `river_query_preflop_subset_control_v1.py`.

The control registration SHA256 is
`eaf9f130f41e2837b307e10d0b2730b5556ac4b3b55c48662e4166158dfc971f`.
Source, fixture and model identities are recorded in the frozen evidence.

## Complete target-calculation replay

A later CPU-only control replayed the entire conditional-target calculation for
A-river update 79, batch 00 (model 78), and B-river update 80, batch 00 (model 79).
It used the isolated preparation candidate, the saved original inputs and the
unchanged opponent posterior, sampling and regret-calculation code.

Both cases passed. A covered 585 river rows in 19 chunks and B covered 944 rows
in 30 chunks. Every one of the 249 output files matched its original SHA256 and
bytes, including native requests/output receipts, posterior sampling plans,
policy arrays, evidence and the final target overlay. A separate PowerShell
readback also compared complete file lists and all 249 original/output hashes.

This expands the component evidence to 1,529 complete river targets across two
training seeds and two model generations. It still does not qualify an entire
training update, fitted model or checkpoint. That check remains queued after
the current scientific study, alongside the separate GPU feature-fit control.

The helper (exec 17104) exited 0. Candidate-only calculations took 83.107 and
132.138 seconds; they are not paired speed benchmarks. The whole invocation took
396.906 seconds including storage admission. The result's started_unix marks the
calculation phase after admission; the total seconds also includes the earlier
inventory. The control retained 16,118,489 bytes and used no GPU or fresh deals.
Its inventory plus reserved space was below the global 800 GB allocation cap.
No registered live-study implementation or settings changed.

Evidence: river-preflop-subset-targets-control-v1-registration.json and its
result, plus river_preflop_subset_targets_control_v1.py. Registration SHA256:
fe5acec47b556e2c1e0962273802551a9d30cddd2c992cf98a95d1ca3352cbe9.
