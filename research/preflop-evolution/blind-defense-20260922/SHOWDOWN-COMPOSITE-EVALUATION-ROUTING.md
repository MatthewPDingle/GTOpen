# Evaluation after the fourth-arm continuation

This amendment changes evidence routing, not the scientific comparison in
`SHOWDOWN-COMPLETE-EVALUATION-PLAN.md`. It is prepared before completion of the
fourth arm, before its independent readback, and before fresh evaluation draws.

The original four-arm controller failed its storage guard. Preserve that failed
status and the absence of an original global success result. Three original arms
completed all 78 updates and passed their independent version-2 readbacks. The
fourth is continuing under its separately registered recovery protocol. It must
complete all 78 updates, verify its final restore, and pass the full independent
composite training readback before any evaluation bank is admitted.

For the fourth arm, updates 1–48 come from the original directory and updates
49–78 from the continuation directory. Recovery comparisons for 49–56 remain
evidence of exact replay, not additional training samples. Each played generation
0–77 occurs once with weights 1–78; generation 78 remains excluded.

The new composite bank reader validates the three original banks through their
existing read-only loader, then binds their completed arm results and all four
audits explicitly. It preserves the original loader's implementation-control
identity inside each of these banks. The fourth bank uses the validated local and
predecessor object readers and the separate composite audit. An independent
evaluation reviewer checks these bindings separately. No original global success
result is created or implied.

Use `hu_showdown_composite_evaluation_v1_20260927.py --control` first, followed by
`hu_showdown_composite_evaluation_review_v1_20260927.py control`. Only after both
pass may `--study` run, followed by its `study` review. These use distinct
`showdown-composite-evaluation-{control,study}-v1` output locations.

The full-bank CPU/GPU comparison, 64 reused control deals, 65,536 fresh study
deals, seed 9267201, eight pairings and contrasts, native payoffs, one final look,
interval formula, storage ceiling and reserves, runtime limits, and production
guards remain unchanged. The preliminary tests qualify only admission and
readback plumbing; they do not qualify full-bank inference or poker strength.

The study must still fit its storage admission using the measured full-bank
control output. Do not draw fresh deals if it does not fit. Retain original
failure records and all scientific evidence. Any further storage or continuation
procedure requires its own prospective documentation.
