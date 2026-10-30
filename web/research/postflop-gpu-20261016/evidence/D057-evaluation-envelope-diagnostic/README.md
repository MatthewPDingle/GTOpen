# D057 evaluation envelope diagnostic — preparation only

This package adapts the D045 build/run/assessment lifecycle for the fixed D057 scope plan. Source under `source/` is owned and sealed separately. The initial draft is preserved in `draft-r1`; no script, compiler, native test or GPU execution occurred during preparation.

A root authorization, sealed independent source/script reviews, exact source activation and an unused isolated GPU-only Cargo target are required before a build. Root must observe terminal successful compilation before the single ignored diagnostic invocation. The registered test uses two independent solver states on the two-tone compressed fixture, ordinary warm checks through140 and exactly three fixed20-iteration/evaluation batches ending160/180/200. Only two timing event handles bracket the instrumented arm's already-captured evaluation graph. There are no outer events, training graph edits or extra evaluations.

Both arms must match all immutable exploitability anchors and every defined post-evaluation raw state, evaluation root vector and compressed store at140/160/180/200. The full final fingerprint object must equal immutable original/E015/E020 evidence. CUDA or exactness failures are invalid; every failure and partial output is retained.

All three samples are retained before assessing `abs(instrumented_host_batch_ms / ordinary_host_batch_ms - 1) * 100 <= 10` separately for each batch. An exceedance is inconclusive for low-perturbation interpretation; it never triggers exclusions, another sample, a changed bracket or an extension. The event interval is an event-perturbed evaluation-device envelope, not evaluation wall time or a pure-work estimate. It establishes no family/individual-kernel fraction, native solve fraction, removable headroom, speedup, candidate acceptance or deployment change.

Root-only commands after the final freeze and a separately reviewed authorization:

```powershell
& 'C:\Program Files\Python312\python.exe' -B build.py <AUTHORIZATION_SHA256>
# Observe terminal compiler success before the following command.
& 'C:\Program Files\Python312\python.exe' -B run.py <AUTHORIZATION_SHA256>
# Observe terminal native success before assessment.
& 'C:\Program Files\Python312\python.exe' -B assess.py <AUTHORIZATION_SHA256>
```

The build writes `runs/D057-build` and immutable `binaries/D057-solver.exe` plus manifest. The one actual native run is `D057R1`, with orchestration evidence in `runs/D057-execution`. Assessment writes a new `comparisons/D057-evaluation-envelope-diagnostic` directory. Existing outputs are never reused. After independent custody review, root restores only the appended module declaration and removes the new helper, checking all162 accepted source identities and the exact live desktop-runtime binary.
