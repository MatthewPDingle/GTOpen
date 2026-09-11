# Adaptive native128 follow-up: fixed500

This follow-up is registered **after observing** large128 fixed50 global failure, fixed1000 global pass, and small fixed/frozen100 global failure. It is adaptive diagnostic/development work, not preregistered blind confirmation. Earlier results and all thresholds remain unchanged.

Two independent groups may run only if root schedules them after production validation and before the2026-09-11 03:03:27UTC deadline. Missing groups are unrun, never presumed passed. No active/live solves may be interrupted.

1. **Small constrained trajectory:** fresh `four-fixed-frozen-holdout` native128, explicit fixed500, same four CPU threads and original corpus/cache. Save/evaluate100 and500 against the existing full420 reference. SHA256 of the new100 checkpoint must equal the old primary100 native checkpoint before interpreting the extended trajectory. If it differs, stop the group and preserve a trajectory-identity failure; do not reinterpret this as a quality failure or silently change precision. The500 result distinguishes the old100 cap from a persistent constrained-policy issue. Root/limp/raise local checks use the same companion paths; forced or unreachable results remain unverified.
2. **Large earlier checkpoint:** fresh native128 fixed500 with the same frozen eight-seat config/cache, preview cadence10, no early gap stopping. Run the same full-reference GPU global evaluation against the existing full1024 iteration1024 checkpoint. This is a new fresh500 solve, not extracting a checkpoint that the1000 harness did not save. It brackets the observed50 failure and1000 success only on this reused fixture; it does not locate an exact minimum iteration or promise monotone quality.

Exact frozen executables and original argument/reference paths come from the completedH protocol records, each with source `6a7b4842798f84e97dcdc956333123d429be6731`:

| Purpose | Frozen executable SHA256 |
|---|---|
| Large trajectory |069f5c041297194e6690ed94f26180ad0b5fbbf178fbc32ab5b076770131fb67|
| GPU quality |bc9890c1b75b02abb7cacd15e05a08b33089d1ef173fbf8b8c9697c0b7c9ad0c|
| Small trajectory |421df2e04a5d307878935a5758f7ebb25766d07b1fdcd73ddf0abf6439ce93ca|
| CPU quality |bf057d98c84b832ddd1422243f86210b08a8048061108c0feef68d139bfc60c3|

CacheSHA is `78b4656ddace5efdb84c77811e9e7891982fb9180d9909a770e7ca4a28fd27ad`; realization-fitSHA is `3f3040ca917930fafa0c9ab8982c44d31513321f3e63d44f39b3d2157673bf18`. No rebuild or replacement binary is permitted in this comparison. The driver reuses immutable original protocol commands with only new output, iteration count and corresponding quality input changes; root's guarded runner provides live/deadline protection and fresh per-job records.

Source review tightened input protection before any run: record full hashes of both frozen executables, corpus/config, full-reference native, cache and fit; small additionally records the original100 native and local paths before solving. Verify these before and after every child, compare guarded executable/cache/fit provenance, and verify each new candidate native is unchanged by its quality audit. The small corpus must match its original registeredSHA and paths must remain `[[],[1],[2]]`. A new100 checkpoint matching only a later-read original is insufficient; the comparison now uses the original's pre-run hash. Completed job status still says nothing about whether500 passes the unchanged quality gates.

Source-only prepared driver, run by root if scheduled:

```powershell
$follow128 = 'T:/Dev/GTOpen/research/autoresearch/passes/04-preflop-interactive-20260911/proposals/quality-gates/run_adaptive128_followup.py'
python $follow128 --group small
python $follow128 --group large
```

Small commands are the prior trajectory command with output`small128-fixed-frozen-fixed500-followup-a` and appended`--fixed-iterations=500`, followed by the prior CPU quality command with candidate100/500 and fresh IDs. Large commands are the prior1000 trajectory command with iteration`500` and output`preview128-eight-500-followup-a.gtop`, followed by its prior GPU quality command with that new candidate. The driver pins original executable bytes and records the actual expanded commands. All files use exclusive creation; no prior evidence is overwritten. A group requires a conservative remaining window (small120s, large720s); this is a scheduling guard, not a measured time estimate. The large trajectory cap is500s and global audit cap180s.

Unchanged global gates: converged full reference<=0.005, excess full gap<=0.02, positive unilateral mean<=0.01/max<=0.03bb per hand. Candidate absolute gap remains separate. Local: conditional hand mass>=0.0025, action loss>0.1bb, inferior-action probability<=0.1. No rare-node exclusion or conditional-refinement waiver. Native/frozen/forced/adaptive semantics and exact roundtrip must hold.

Report solver, publication, save/roundtrip and separate audit time. Passing global500 could shorten this fixture's observed time to **global tolerance**, but cannot establish overall usable quality, remove known small local/physical-model limitations, validate a preview prefix, or produce a10x claim without a matched passed-quality timing baseline. A failed500 result remains a meaningful lower-budget failure, not a reason to move thresholds.
