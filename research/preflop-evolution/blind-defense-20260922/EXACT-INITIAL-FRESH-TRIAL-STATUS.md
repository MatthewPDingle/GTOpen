# Exact-initial trial — training complete, audit running

## Latest verified boundary — 24 September 2026

The fixed training run completed all 78 updates and 39,936 fresh deals with
exit code zero. Training took 10,145 seconds including controller overhead
(about 2 hours 49 minutes). Its final checkpoint is
`exactcheckpoint-d07cfb5a74d30a07ee36160ec9e21a1af417014536298a5796c8e9ce45c6e7f0.json`.
The terminal result SHA-256 is
`929f5b614247b513e63babcc0716c725f11e7ee8013e4747cc42ce472f0f20c1`.

The existing continuation controller started the independent CPU training
audit automatically. Accuracy results and the wider-test admission decision
are still pending. A completed training run alone does not establish range
quality. No production code or server was modified.

The previous later-weighted candidate completed its wider independent test.
It still permits a profitable BB first-action deviation of approximately
0.293 bb per entry into this fixed spot. See
[the completed wider findings](LATER-WEIGHTED-WIDER-FINDINGS.md).
It is not qualified for production.

The next fresh 78-update trial is `exact-initial-fresh-pilot-v1`, stored at
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

## Continue from here

The registered continuation controller tracks the training and dependent
checks: `exact-initial-study-continuation-v1-status.json`. Its process identity
and the watched training process identities are recorded in the matching
registration. It does not restart training or own the GPU while waiting.
It will perform the stages below automatically, then (only after a passing
primary screen) the admission and six-alternative wider test described in
[the prospective wider plan](EXACT-INITIAL-WIDER-TEST-PLAN.md). Do not launch
duplicate stages while this controller is live. Check its live process as
well as its status file before considering manual recovery.

Read `exact-initial-fresh-pilot-v1-status.json` and the matching `.log` in this
directory. The complete training boundary is the store's `latest.json`.
Do not rerun the controller against its existing store. It owns the shared
research lock while running and stops if production becomes active.

The first dependent stage after a successful terminal result is the frozen
independent readback:

```text
tools/research/hu_exact_initial_fresh_review_20260923.py
```

If that passes, these run sequentially with no competing GPU work:

```text
tools/research/hu_exact_initial_fresh_exact_20260923.py
tools/research/hu_exact_initial_fresh_exact_review_20260923.py
```

The primary screen compares new linear/linear exact endpoint gains with the
old linear/linear candidate, requiring at least 25% improvement for both
players. A pass only justifies a separately registered wider call/raise test.
Do not deploy, select a different checkpoint, or call this full convergence.
Preserve all registrations, code bytes and failed artifacts unchanged.
