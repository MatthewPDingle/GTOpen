# Pair correction at actual conditional decisions

Registered before running. Reuse the existing bounded-memory pair-outcome
control variate, with coefficient unchanged, in the fixed-current-policy
diagnostic. This does not enable a combined normalized learning mode.

Run the same three immutable saves, same six paths, all 169 hands, 64 samples
and all 1,024 cyclic offsets as the preceding conditional sampling diagnostic.
Order: sampled seed 42, sampled seed 314159, full-particle seed 42. Cap each
process at 900 seconds and extra pair storage at 1,024 MiB. Run serially with
run07's live busy guard. Keep port 56708 unchanged.

Compare against the archived uncorrected diagnostic from the exact same save.
Require source snapshot, current prefix masses, frozen probabilities and full
action values to match exactly. Recompute all corrected means, covariance,
variance and ordering errors from raw offsets; retain the full evidence.
The existing source/device preservation and canonical CPU agreement gates
must pass. Tests must also show nonzero correction on a multiway fixture,
zero-reach handling and restored full values, without history mutation.

Screen for further learning work only if all three cases meet all of:

- Sum of per-action regret variances, weighted by current conditional hand
  mass and summed over the six diagnostic nodes, is at most 75% of baseline.
  This score is a screening statistic, not whole-game exploitability.
- Each open-plus-call blind node has no variance increase and at least 20%
  reduction in hand-mass-weighted inferior-action promotion probability.
- Worst relevant-hand promotion at each of those blind nodes increases by
  no more than 0.02 absolute probability.

Use hand mass at least 0.0025 for the gate, preserving unfiltered results.
Do not tune coefficients, select favorable nodes, widen gates or claim speed
qualification from this fixed-state screen. A later timed learning experiment
requires its own registration and unchanged combined quality gates.
