# Independent readback of the root-action replay

The 64-deal qualification passed on 2026-09-28. The full 65,536-deal replay
was still running at qualification; these small-control results do not
establish any improvement in poker play.

The reader reconstructs all 32 forced-root transports from the authenticated
original archive through its separate routed archive reader. It compares their
digests with the inputs retained in each replay receipt, then checks physical
hand identities, all saved native outcomes, both player values and rake. It
independently recomputes class and overall means and standard errors using
40-digit Decimal sums and squared sums, rather than the replay's Welford updates.

The control checked 930,336 transported policy rows over two batches. The maximum
mixture difference was 2.189e-14 bb; the largest summary difference was 2.843e-14.
All eight profiles and all 169 class slots were checked, including explicit
empty slots. This does not mean that 64 deals cover all 169 hand classes.
Elapsed control time was 9.625 seconds with two CPU workers; no GPU was used.

Full readback uses 12 CPU workers and the same code, with a one-hour deadline.
It requires a finished replay, unchanged registered inputs, matching completed
checkpoint, passing readback control, available memory, no competing research
owner and no active production work. It does not create new evaluation deals or
change the existing comparison's stopping rule. Final source hashes are checked
again before publication. A failed audit cannot publish a passing result.

This is independent reconstruction and arithmetic, not an independent poker
engine or a new neural-policy evaluation. A passing readback validates the
retained calculation. Scientific interpretation and any fresh validation of
proposed changes remain separate work.

Evidence: `board-root-action-replay-readback-control-v1-registration.json` and
`board-root-action-replay-readback-control-v1-result.json`.

Reviewer SHA-256:
`602bb5fe13a35bc796d270922adf73e0269f599bb5def4ab9a7a8ba15b969136`.
Control registration SHA-256:
`294a420e451794f099b5d4b81d9bb8309d64da7ae37db61785ad0b165adcbb12`.
