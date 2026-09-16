# N24: separate card-accounting effects from learned-value effects

Diagnostic only. N20 compares the ordinary Balanced path with an interface that
both enforces compatible two-player card combinations and predicts continuation
values from ranges. Its larger convergence gap cannot be attributed uniquely
to the predictor from that comparison alone.

Use the exact N20 double-precision CUDA source and research executable. Disable
only the learned predictor through the existing `balanced` research mode. This
retains the interface's legal-pair chance/accounting and ordinary Balanced
continuation values. Its arithmetic already passed the independent N17 double
oracle, including normal/sparse two-, three- and eight-player fixtures. Verify
source identity before running; do not alter solver code or tolerances.

Build a fresh game from the identical N20 configuration. Save after150 and500
iterations, with no extra warm-up, resuming150->500. Compare summed frozen-value
gaps and all17 selected action-frequency rows with the already saved ordinary
and learned N20 policies at the same iteration counts. Record exact snapshot
hashes and learning/setup times, but a single diagnostic is not a repeated
speed benchmark. N20's original50 warm-up iterations counted toward150 and500;
all three paths therefore have the same total learning iterations.

This tests a possible explanation, not a new model or an accuracy/convergence
gate. Even if the chance-only control settles, it does not establish that a
particular model feature causes the candidate's behavior. Gaps are computed in
each path's own approximate continuation game; they are not comparable full-game
exploitability estimates. Different strategies are not evidence of correctness.

Run only after the validation queue has exited, with at least20minutes remaining
before the fixed20:49:02UTC deadline and no other GPU research/timing workload.
Keep the app unchanged. These experimental saves retain Balanced metadata and
must never be opened in the ordinary app. No automatic deployment.
