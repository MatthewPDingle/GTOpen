# Both stratified training histories passed readback

Both registered 78-update stratified arms have completed and passed their full
four-worker independent readback. The automatic queue has advanced to the
complete-policy evaluation control. This is a correctness gate, not evidence
of better ranges or stronger play.

| Arm | Updates | Reconstructed BB roots | Reconstructed postflop targets | Maximum root-state error | Maximum policy error |
| --- | ---: | ---: | ---: | ---: | ---: |
| 9266201-stratified | 78 | 39,936 | 917,503 | 4.55e-12 | 9.63e-13 |
| 9266301-stratified | 78 | 39,936 | 863,717 | 2.28e-12 | 6.42e-12 |

Maximum target error was 5.69e-14 in both arms. Readback wall times were 2,473.28
and 2,245.67 seconds respectively. Different concurrent workloads and data sizes
mean these timings are not a controlled speed comparison.

The readbacks reconstructed scalar target values, policies, source-deal
weighting, ordered insertions and full checkpoint state. They share the
registered sampler/reservoir replay and native evaluator; they are not an
independent poker engine. They did not refit the networks and are not a
best-response or playing-strength certificate.

The queue result binds both readback outputs. Each output binds its own audit
registration and the original training registration. The final second-arm
checkpoint is `weightedcheckpoint-b2d9ebd56eb442574f8335dfed430fa0460958af76d638fc8bd955a330205152.json`.

Evaluation must use the complete played policy histories, generations 0–77,
with registered own-action-reach weighting. Unplayed generation 78 is excluded.
The next gates remain: complete-bank control, independent control review,
65,536 fresh common deals with all eight registered payoff comparisons, full
evaluation readback, and the queued root-trajectory analysis. No automatic
promotion or production change follows completion of an audit.

Evidence: `weighted-stratified-study-v1-training-result.json`,
`weighted-study-audit-queue-v1-result.json`, and both
`weighted-training-readback-parallel-v1-w4-*-0078-{registration,result}.json`
artifacts. Production was not modified.
