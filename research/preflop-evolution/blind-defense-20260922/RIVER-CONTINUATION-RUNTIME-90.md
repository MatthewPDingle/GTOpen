# Continuation runtime at candidate boundary 90

Runtime observations from the saved first ten additional rounds of A-baseline and A-river (81 through 90). Each source metric was checked against its saved progress hash. This is profiling evidence, not an accuracy result or an isolated throughput benchmark. The registered scientific run was not changed.

| Mean seconds per update | Baseline | Candidate |
|---|---:|---:|
| Whole update | 57.30 | 177.58 |
| Physical-target pipeline | 18.10 | 138.10 |
| Fitting, including preparation | 24.83 | 24.78 |
| Fit preparation only | 13.88 | 13.34 |
| GPU optimizer only | 10.26 | 10.76 |
| Checkpoint publication | 6.60 | 6.72 |

Preparation and optimizer times are parts of fitting. Other reported worker categories overlap; do not add them as independent wall times. Per-update time also excludes some outer verification and orchestration. Desktop contention and the different evolving policies can affect these observations.

## Implications for the next performance work

- All ten candidate updates used eight distinct physical workers and eight subbatches. The baseline used fewer distinct workers because its tasks finish sooner.
- The candidate spends most update time in its CPU physical-target pipeline, especially conditional river target generation. GPU fitting is a smaller portion of its cost.
- Increasing the pool limit above eight alone cannot split the eight existing tasks. Exploiting additional cores requires finer independent work units inside target generation or an equivalent scheduling change.
- Preserve the existing 64-deal subbatch identities, per-key posterior draw seeds, 32-target native chunk boundaries, insertion order, and arithmetic when qualifying any such change. Changing the training sampling configuration is a different experiment.
- The prepared vector feature optimization addresses fit setup. Full fit and complete-update parity remain prerequisites to future adoption; its feature-stage speed ratio is not a whole-update speed claim.
- Finish the current accuracy comparison before deciding whether this candidate warrants further target-generation optimization. No new CPU or GPU benchmark was run alongside it.

Evidence: `river-continuation-runtime-90-v1.json` records every source metric path/hash and the inspected implementation hashes. The final scientific report must still use all arms, both seeds, and the independent evaluation review.
