# Exact-initial trial resumed — 23 September 2026

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

The registered continuation controller is now watching the already running
trial: `exact-initial-study-continuation-v1-status.json`. Its process identity
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
