# Wider evaluation readback and remaining admission

23 September 2026. Preparation while the fresh averaging run is still training;
no active-candidate probabilities or results were used.

The reusable `wider_root_readback_v1.py` now reconstructs the evaluation for its
registered counts and batch size, instead of relying on the small control's
hard-coded 338 training / 128 test deals. It independently computes class action
means, fallback/choice rules, both training-half choices and their disagreement,
exact offsets, physical residual bounds, residuals and five final intervals.
It replays the class-conditioned training and population test streams separately,
verifies sample identities and frozen responder hashes, and reconciles summary
payoffs with the stored native output. Each native artifact's bytes are checked.

The registered readback control passed on all 30 existing batches, all 169 class
choices, both training halves and five intervals. Maximum scalar discrepancy was
2.274e-13 bb. Seven deliberate in-memory corruptions were rejected: interval mean,
stability count, selected action, native payoff, saved residual, test RNG state,
and training class count. Original evidence files were unchanged. This used no
GPU and took 39.8 seconds including all corruption checks.

This is an arithmetic/provenance control, not a strategic result. It does not
independently rerun native poker traversal or neural inference, and has not yet
been exercised at the planned full sample count. A production-sized controller
must still verify frozen model/source identities, resource limits and weighted
CPU/CUDA agreement for the candidate before admitting an evaluation.

## Storage is a real admission constraint

The completed small evaluation holds 196,812,980 logical bytes for 466 deals.
About 196 MB is the query and five-profile transport, rather than summaries.
Simple proportional scaling to the planning 174,336 deals is about 73.6 GB.
This is an estimate, not a storage guarantee: query deduplication and batch size
change the cost. The live S drive had about 85.2 GB free at inspection, while the
research reserve is 40 GB and training still writes there. An uncompressed full
evaluation at that planning count is therefore not admitted.

Before launch, measure lossless output compression with unchanged decoded bytes,
choose a bounded storage plan, and retain resource guards during every batch.
Do not reduce the test count after seeing results to fit the disk. The current
training run and its registered sources remain unchanged.

Evidence: `wider-root-readback-control-v1-registration.json` and
`wider-root-readback-control-v1-result.json`.
