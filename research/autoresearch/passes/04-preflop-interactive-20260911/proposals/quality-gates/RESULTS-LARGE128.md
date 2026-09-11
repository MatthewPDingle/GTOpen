# Large128 native trajectory results

Registered protocol: `HERDING128-NATIVE-PROTOCOL.md`. This is the reused1,567,754-node eight-seat development/workflow fixture, not new held-out policy evidence. Native model is `coupled_preview128_v1`; full-reference quality evaluations use the registered full1024 iteration1024 checkpoint. Physical128 confirmation and small native policy failures are separate evidence and remain unchanged.

## Fixed50: faster fixed work, failed global quality

Both `raw/preview128-eight-050-a-result.json` and `raw/quality-large128-050-a-result.json` record returncode0 and no cancellation reason. Source is `6a7b4842798f84e97dcdc956333123d429be6731`, cacheSHA `78b4656ddace5efdb84c77811e9e7891982fb9180d9909a770e7ca4a28fd27ad` (20000 samples). No active1000 log was used to infer a completed result.

Timing from `raw/preview128-eight-050-a.log`:

| Measurement | Seconds |
|---|---:|
| Tree build |0.68881|
| Initialized, cumulative |2.38213|
| First published snapshot, iteration2 |4.62325|
| Published snapshot, iteration10 |10.77540|
| Published snapshot, iteration20 |19.46043|
| Published snapshot, iteration30 |28.49190|
| Published snapshot, iteration40 |37.19081|
| Published snapshot, iteration50 |45.66157|
| Final own-model check |0.99316|
| Solver stage |47.35589|
| Total through native save/reload audit |55.18025|

Native roundtrip is exact. The run completed the fixed50 budget; its own-model summed gap1.36367970 is not converged. Publication means a snapshot is available, not that it passed decision-quality gates. These standalone snapshot measurements do not substitute for the separate server/API workflow tests.

The historical full1024 fixed50 run in `raw/reference-eight-timing-a.log` took302.4537862s solver stage and309.5496134s total, with exact roundtrip. Its result file identifies source`43200db7fe8b186bc3da1915a25bb95b406ed97d`; retain that literal provenance rather than relabel it as the current binary. The same frozen-input historical fixed-work comparison is approximately6.39x faster in solver-stage time for128. It is neither a matched fresh time-to-quality comparison nor the requested10x usable-quality result. The resumed full1024 quality reference also supplies no fresh1000 timing denominator.

Full-reference quality from `raw/quality-large128-050-a.log`:

| Metric | Result bb/hand | Registered limit | Outcome |
|---|---:|---:|---|
| Reference learning gap |0.00478375|<=0.005|Pass|
| Candidate learning gap under full payoffs |1.36419668|reported separately|Not converged|
| Excess learning gap |1.35941292|<=0.02|Fail|
| Mean positive unilateral loss |0.07974273|<=0.01|Fail|
| Maximum positive unilateral loss |0.12342955|<=0.03|Fail|

Global policy flag is false. Evaluation took92.10342s internally (guarded process96.11s). This read-only research evaluation is additional to the55.18s trajectory/save audit and is not user-facing latency. Local strong-action tails, physical equity, speedup qualification and preview workflow are explicitly not evaluated by this global quality call. Earlier physical passes cannot rescue this failing50-iteration policy.

## Fixed1000: global policy gates pass; overall quality remains unqualified

Both `raw/preview128-eight-1000-a-result.json` and `raw/quality-large128-1000-a-result.json` now record returncode0 with no cancellation reason, the same source commit and cache hash as fixed50. The trajectory completed its registered1000 iterations and exact native save/reload audit. Completed nativeSHA256 is `48ea4613b22af7c39f557f69eba64ffdb402bcb2d66d1f07ebf2b16ce1002012` for lab `target/research-preview/preview128-eight-1000-a.gtop`.

| Measurement | Result |
|---|---:|
| Solver stage |728.12564s|
| Total through native save/reload audit |734.91873s|
| Final own-model check |0.99654s|
| Own-model learning gap |0.00614523bb/hand|
| Candidate learning gap under full payoffs |0.00742875bb/hand|
| Reference learning gap |0.00478375bb/hand|
| Excess learning gap |0.00264499bb/hand|
| Mean positive unilateral loss |0.00026127bb/hand|
| Maximum positive unilateral loss |0.00117942bb/hand|
| Full-reference quality audit |91.71271s internally;95.046s guarded process|

All registered **global relative policy gates** pass: the reference is converged, excess<=0.02, mean positive loss<=0.01 and max<=0.03. The candidate's own and full-evaluated absolute gaps both remain above0.005, so this fixed iteration run is not reported as converged to that absolute target. No gate has been loosened.

The full-reference GPU call does not evaluate large-game local strong-action tails, physical equity or workflow. In particular, the previously recorded native128 small local failures and fixed/frozen100 global failure persist; no result here supersedes them. The separate frozen128 physical confirmation passed its registered terminal gates, but that is not a complete decision-quality guarantee.

This supports a **globally evaluated initializer candidate on this reused large fixture**. It does not establish a generally qualified preview/default, a validated prefix for conditional refinement, or10x time to usable quality. The historical64 fixed1000 result is a separate cross-model comparison; the resumed full1024 reference has no matching fresh1000 timing history. Preserve raw fixed50 failure alongside this later success.

Machine-readable measured values and explicit unverified scopes are recorded in `RESULTS-LARGE128.json`.
