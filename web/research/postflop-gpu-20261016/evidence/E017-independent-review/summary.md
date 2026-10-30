# E017 independent terminal evidence review

**Audit PASS; rejection confirmed.** The unchanged score is 9752.1872 -> 9718.1350 ms, a 0.349175% reduction against accepted E015, below the registered 2% aggregate gate. There is no repeated material fixture-regression guard failure. This result does not qualify E017 and warrants no additional performance runs to rescue it.

| Fixture | E015 median complete cycle, ms | E017 median complete cycle, ms | Observed reduction | Paired regressions above 3% |
|---|---:|---:|---:|---:|
| Rainbow | 5752.6926 | 5696.9274 | 0.969376% | 0/3 |
| Two-tone | 3897.3697 | 3920.4521 | -0.592256% | 0/3 |
| River | 102.1249 | 100.7555 | 1.340907% | 1/3 |

The river's third pair regresses by 14.841223%; it remains in the ledger. The fixture guard nevertheless passes because neither its median nor a strict majority of its paired repetitions establishes the registered greater-than-3% repeatable regression condition. The aggregate failure independently determines rejection. No significance or general absence-of-regression claim follows.

## Correctness and provenance checks

- `V017-unit`: 86 passed, zero failed, four ignored. The seven focused plan, mixed/uniform lifecycle, standalone reach, evaluation and tight-budget tests were individually located and confirmed successful in raw stdout.
- `V017-capacity`: the intended feature-gated mixed/uniform planned-versus-observed metadata test passed; zero failed, 202 filtered. Its manifest records the `preflop-research` library build, and build logs/stderr hashes verify.
- All 18 primary `AUTORESEARCH_RESULT` objects were independently parsed from raw stdout and match the report copies. Every corresponding complete non-timing object is identical across all six runs, including full state fingerprints, aggregate fingerprints, exploitability bits/values, stopping iterations, config, target and workload settings. Only the six explicit timing fields, including excluded fingerprint timing, were removed for that comparison.
- Native binaries, build manifests and raw logs verify against their recorded hashes. Each arm uses one unchanged binary and source identity. Candidate and validation manifests match the three frozen E017 source files; archived accepted E015 sources match the baseline manifests. The only solver-source differences are the three reviewed files. All 162 build-time source entries match runtime provenance for each of the three candidate and two validation runs.
- The primary environment is unchanged: 16 Rayon threads, compressed storage, all three fixtures in fixed order, profiling disabled, identical recorded GPU identity/driver/capacity. The observed run chronology is serialized and matches the recovered fixed order.
- Medians, aggregate score, paired fixture regressions and the strict-majority guard were recomputed independently without importing the comparison implementation. They agree with the published rejection report.

## Operational recovery retained in the audit

The original script completed both validation runs and B053, then encountered a dashboard-ID collision for logical candidate E017. The recovery protocol renames only the first measured candidate to E017R1. There is no `runs/E017` directory. Inspection of the unchanged runner confirms that its dashboard collision check raises before run-directory creation and before entering the native launch routine. The recorded original script hash verifies.

The resulting order is B053, E017R1, E017R2, B054, B055, E017R3, paired as B053/R1, B054/R2, B055/R3. The first baseline-to-candidate gap is **86 seconds**; other adjacent run gaps are zero or one second at report timestamp precision. This operational pause is disclosed, not removed or treated as a reason to rerun a pair. The B053 report/log and both validation report/log pairs still match the hashes sealed before recovery.

The comparison CLI subsequently required an actual run ID and matching patch alias. `runs/E017R1.patch` is byte-identical to the frozen build/design patch (SHA-256 `32e0e331919261cb24b79372f02610a7cd6baa55558ac5e1768a1b40ae04a861`). The comparison-adapter record preserves those bookkeeping failures. Refusal/error descriptions are operator records; separate stderr transcripts for these pre-measurement/dry-run failures were not supplied. No measured run was excluded, replaced or reclassified.

## Scope

This reviewer performed only source, file-hash and raw-evidence analysis. No GPU work, build, source change or live-server action occurred. Checkout cleanup does not invalidate the audit because frozen source copies and preserved binary manifests identify the tested implementation.

The completed checks establish the specified library tests and primary compressed-fixture exactness. Additional frozen saved-state/action-menu/resume controls were not rerun for this candidate after its performance rejection; this review makes no broader E017 compatibility or deployment claim. The earlier source PASS remains a source assessment, while the terminal performance disposition is rejected.
