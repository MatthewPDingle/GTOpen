# Adaptive128 follow-up results

This is the explicitly adaptive follow-up in [HERDING128-ADAPTIVE-FOLLOWUP.md](HERDING128-ADAPTIVE-FOLLOWUP.md), selected after observing the primary100 constrained failure and large1000 global pass. It is not new held-out confirmation. All earlier results and thresholds remain unchanged.

## Small fixed/frozen500: global cap effect improves, local failure remains

`raw/adaptive128-small-followup-a-summary.json` reports all three jobs returncode0 and immutable input checks exact. Original and new100 nativeSHA256 both equal `5c19b5c4e737ac44d0a069ead987cb6151316166763b3a8133ef811bb20a1e97`. Thus the new trajectory matches the prior primary through100; the500 outcome is not explained by an altered first100 iterations. Frozen executables, corpus, cache, fit, full reference and local paths are unchanged, and candidate natives remain unchanged by their audits.

Both quality checks use the same full420 reference, whose learning gap is0.004980812076086886.

| Metric bb/hand | Candidate100 | Candidate500 | Registered limit |
|---|---:|---:|---:|
| Candidate full-reference gap |0.02855315|0.00685020|absolute0.005 reported separately|
| Excess gap |0.02357233|0.00186939|<=0.02|
| Mean positive unilateral loss |0.01024952|0.00027522|<=0.01|
| Maximum positive unilateral loss |0.01164134|0.00032505|<=0.03|
| Global relative gates |Fail|Pass|all required|

The old100 cap explains part of this scenario's global error: the identical trajectory passes the relative global gates by the measured500 checkpoint. This does not locate the first passing iteration. Both the500 own-model gap0.00603236 and full-evaluated gap0.00685020 still miss absolute0.005. The explicit fixed500 run finishes in1.74742s including initialization and registered checks/saves; cumulative iteration compute is1.38226s and checks0.32262s. These are tiny-tree development timings, not a large-game or10x usable-accuracy result.

The local gate is unchanged: for conditional hand mass>=0.0025, probability on actions losing>0.1bb under the original reference continuation must be<=0.1.

| Path / seat |100 bad-action probability|500 bad-action probability|500 outcome|
|---|---:|---:|---|
|root CO|not applicable|not applicable|Forced; not counted as pass|
|[1] BTN|0.99702317|0.99997573|Fail|
|[2] BTN|0.02935555|0.00024598|Pass|

At[1], candidate500 weighted action loss0.00777521bb remains above reference0.00011671bb. More training does not remove this particular original-continuation tail failure. At[2], candidate500 weighted loss0.00014262bb is slightly below reference0.00016504bb, but that passing path cannot cancel[1]. The previously recorded constrained100 failure stays visible, while the adaptive500 improvement is reported separately. **Overall policy qualification remains false.**

Raw evidence: `raw/small128-fixed-frozen-fixed500-followup-a.log`, `raw/quality-small128-fixed-frozen-followup-100-a.log`, `raw/quality-small128-fixed-frozen-followup-500-a.log`, and each completed companion result record.

## Large fixed500: completed, relative global gates pass

The trajectory and full-reference audit both completed with returncode0, as recorded in `raw/adaptive128-large-followup-a-summary.json`. All immutable input checks pass. Native roundtrip is exact and outputSHA256 is `4da7176410d5dc7415d7c5925fa45514d22af01a26530d08b14673a8377a29b1`.

| Metric | Result | Registered limit |
|---|---:|---:|
| Own-model gap |0.02307098bb/hand|absolute0.005: missed|
| Full-reference candidate gap |0.02411742bb/hand|absolute0.005: missed|
| Reference gap |0.00478375bb/hand|<=0.005: pass|
| Excess gap |0.01933366bb/hand|<=0.02: pass|
| Mean positive unilateral loss |0.00160932bb/hand|<=0.01: pass|
| Maximum positive unilateral loss |0.00498482bb/hand|<=0.03: pass|

The frozen global relative gate passes. Excess is only0.00066634bb below its limit; report that measured margin without changing the threshold or implying stronger accuracy. This adaptively selected checkpoint provides an earlier observed global pass than1000, with50 still a failure. It does not establish monotonic quality or the first passing iteration.

Trajectory solver stage is389.27333s; total through native save/reload audit396.52631s (guarded process397.531s). Final own-model check is0.99159s. The separate full-reference global audit is92.13732s internally,96.156s guarded. Audit time must not be silently omitted from a validation-workflow total or mistaken for solver time.

This is a reused development fixture and explicitly adaptive follow-up. Both absolute gaps remain far above0.005; large local tails are unmeasured, small original-continuation failures remain, and no generally validated preview prefix is established. The same passed-quality fresh full baseline was not timed, so **no10x qualified time-to-accuracy claim follows**. Raw fixed50 failure, fixed1000 pass and all previously recorded limitations remain unchanged.
