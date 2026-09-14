# R04 integration progress

R04 puts retained C23's static rank-boundary tables in the normal GPU selector.
The application on 56708 still runs R03. This is not a deployment receipt.

## Implementation and initial qualification

The selector promotes its fresh retained engine, preserving its context,
cohort plan, batches, policies and arithmetic. On promotion failure the private
engine is dropped, then the retained layout is rebuilt; the prior normal-GPU
fallback still applies. Selection metadata identifies static storage and any
promotion fallback. Fault injection and evidence-file output are test-only.

The initial source-rewrite helper refused an unmatched guard expression before
any build. Its partial gpu.rs edit was verified and restored from the archived
original, the expression corrected, and preparation completed. No failed build
or GPU run was hidden or overwritten.

Three selector tests (including real allocation failures at all three stages),
10 integrated numerical/save/stop/recovery tests, and 20 normal GPU tests passed.
CUDA source, PTX, resource reports, saved games and interrupted continuation
artifacts match the qualified C23 outputs byte-for-byte. The normal GPU test
asserts that supported cases actually select static tables.

Frozen benchmark SHA256:
`3e102a6478b4952d2d56dcf08a553569949d37600506276292c66bee674c6546`.
Source snapshots and the complete source hash map are preserved in
`artifacts/r04-v1` and `raw/r04-initial-verified.json`.

## Normal selection overhead

Both paths run in the same frozen executable: the private C23 constructor is
the control; normal application selection is the candidate. Three alternating
pairs per fixture use the full six-sweep/check workload and original saved
states. All checkpoints, complete arena fingerprints, table layouts and cohort
plans match C23. Selection reports confirm static tables with no fallback.

| Fixture | Candidate/control ratios | Median overhead |
| --- | --- | --- |
| Small | 0.95844, 1.02437, 1.00940 | +0.94% |
| Large | 0.99665, 0.97315, 1.02077 | -0.34% |

Both pass the registered maximum 3% median integration-overhead gate. Negative
overhead here is not credited as another optimization. The timings support
preserving C23's benefit when selected by the normal app constructor.

## Remaining qualification

Run immutable small/large saved-fixture continuation through normal selection,
including reload and the next iteration; compare to qualified saved witnesses.
Complete default solver/server regressions and a normal server build. Validate
save/load and actual stop/resume on an isolated server before recommending a
production switch. Preserve the user's stopped iteration-53 session on 56708.
The broader convergence-quality and 10x goals remain open.

Verification: `check_r04_initial.py`, `check_r04_overhead.py`, their raw receipts
and guarded logs. One research workload at a time; no live app state was changed.
