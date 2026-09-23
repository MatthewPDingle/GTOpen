# Exact-initial trial — completed, broader weakness remains

## Latest verified boundary — 24 September 2026

The fixed training run completed all 78 updates and 39,936 fresh deals with
exit code zero. Training took 10,145 seconds including controller overhead
(about 2 hours 49 minutes). Its final checkpoint is
`exactcheckpoint-d07cfb5a74d30a07ee36160ec9e21a1af417014536298a5796c8e9ce45c6e7f0.json`.
The terminal result SHA-256 is
`929f5b614247b513e63babcc0716c725f11e7ee8013e4747cc42ce472f0f20c1`.

The independent CPU training audit passed all 78 updates. The primary exact
endpoint screen then passed, with restricted BB and BTN gains reduced by
74.5% and 75.0% respectively versus the old linear/linear candidate. The
independent endpoint review and the full-candidate CPU/CUDA admission check
also passed. See [the interim findings](EXACT-INITIAL-ENDPOINT-FINDINGS.md).

The six-alternative wider test and independent audit are complete. A newly
trained BB response gains 0.23038 bb per entry, interval [0.03030, 0.43046].
The previous frozen response is near zero on its point estimate but remains
inconclusive. See [the complete wider findings](EXACT-INITIAL-WIDER-FINDINGS.md).
No production code or server was modified; this candidate is not qualified
for deployment. All dependent stages completed; do not rerun the controllers.

The previous later-weighted candidate completed its wider independent test.
It still permits a profitable BB first-action deviation of approximately
0.293 bb per entry into this fixed spot. See
[the completed wider findings](LATER-WEIGHTED-WIDER-FINDINGS.md).
It is not qualified for production.

The completed fresh 78-update trial is `exact-initial-fresh-pilot-v1`, stored at
`T:\GTOpen-research\exact-initial-fresh-pilot-v1`. The prospective recipe is
in [the trial plan](EXACT-INITIAL-FRESH-TRIAL-PLAN.md). It uses the validated
v2 trainer, corrected initial all-in targets, and double-precision policy
inference. No production code or server was modified.

## Completed admission controls

- Full-size two-update CUDA control: 1,024 fresh deals, 512 fitting steps per
  player/update, complete in 105.3 seconds including controller overhead.
- Independent CPU readback: reconstructed all 1,024 BB roots and 21,924 BB /
  4,865 BTN insertion events, every saved policy, both exact updates and both
  checkpoint states. Maximum target error 4.27e-14 bb; maximum policy error
  6.93e-14. Completed in 73.9 seconds.
- Exact endpoint evaluator and scalar independent review also passed for the
  two-update bank, across all four equal/linear player pairings. Maximum scalar
  discrepancy 6.67e-16 bb; maximum cashflow discrepancy 1.43e-14 bb.

The tiny bank is an integration control, not a range-quality candidate.

## Completed sequence and next step

The terminal continuation record is
`exact-initial-study-continuation-v1-status.json`. Training, training audit,
exact endpoint evaluation, endpoint audit, wider admission, wider evaluation
and wider audit all completed successfully. No controller is still waiting
for a dependent stage. Do not rerun these controllers against their existing
stores.

The prospective endpoint screen required at least 25% improvement for both
players and passed. That justified the separately registered wider test,
which found a remaining profitable response. Preserve the registrations,
source bytes and raw artifacts unchanged.

The next action is a read-only diagnostic of root training sample retention,
described in [the wider findings](EXACT-INITIAL-WIDER-FINDINGS.md). This is
not a new candidate or a production deployment.
