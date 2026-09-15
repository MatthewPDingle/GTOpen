# Result-extraction failure reproduction

All jobs here are diagnostic and have distinct diagnostic manifest identifiers.
They must not be copied into a training batch.

The retained night1 worker failed the original zero-rake accounting gate on
`train-seven-open-04-QcJd9c`. `range_value_diagnostic.rs` reproduces the same solve
but prints the discrepancy so its values can be inspected. Each comparison uses
the same ranges, tree, 0.1%-pot GPU target and 275 iterations:

| Extraction | Pot-sum error (bb) | CPU BR gap (% pot) |
|---|---:|---:|
| Compressed host, symmetry query | 0.002047516 | 0.0984878 |
| F32 host, symmetry query | 0.002047705 | 0.0988402 |
| Compressed host, explicit materialized branches | 0.000000048 | 0.1038768 |

The GPU gap at that iteration was 0.0988383% of pot. Storage precision alone
does not fix the failure. The query shortcut relies on suit invariance, while
the explicitly transported policy can retain small suit asymmetries.

`corrected-query` uses the retained night2 runner, which requires the GPU and
explicit CPU BR gaps to meet the original target. It converges at 300 iterations
and satisfies the unchanged pot-accounting check. See the corrected run's
README and preflight-validation.json for the regenerated experiment.

The diagnostic modes are selected by `DIAGNOSTIC_F32=1` or
`DIAGNOSTIC_FULL_QUERY=1`; default mode reproduces the original compressed query.
`pot-accounting-full-query` uses the latter option. The corrected reference
runner always performs explicit queries and enforces both accuracy gates.

This investigation did not modify or deploy the live application on 56708.
