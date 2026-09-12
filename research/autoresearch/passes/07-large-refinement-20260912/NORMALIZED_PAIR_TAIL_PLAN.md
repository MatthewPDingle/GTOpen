# Fresh four-seed convergence-tail check at equal qualified wall time

Registered after the original two-seed/1,000-iteration screen failed. That
failure remains unchanged. Seed 314159 qualified 4.36x faster than the full
control; seed 42 passed all local paths but missed the global target at 1,000.
This follow-up tests the same 64-particle algorithm with more steps, without
loosening accuracy or the minimum speed gain.

All games start fresh; no old save resumes or cap extensions. Same 23,038-node
six-seat fixture, 64 samples with the tested normalized pair correction,
gamma15 with horizon 1,000 (its factors are constant exponents and do not
depend on horizon), and the same full-reference global and six-path check
every 25 steps. Stop at two consecutive combined passes or 3,000 iterations.
No exploration, coefficient adjustment, pruning or other algorithm change.

Run order: full 1,024 normalized control seed 42; corrected 64 seeds 42,
271828, 314159, 1618033; repeat full control seed 42. The two added seeds
have not been used in this candidate's learning screen. The control repeats
measure timing variability; they are not independent learning trajectories.
Each process has a 300-second safety cap, base 4,096 MiB and pair extra cap
1,024 MiB; run serially with run07 and leave the live app unchanged.

Both controls must reproduce the previous full-control save exactly. All
four candidates must pass combined quality and each complete runtime must
be <= the faster control's runtime / 1.25. More iterations do not permit a
slower qualified result. The iteration cap is a safety ceiling, not a relaxed
accuracy criterion. If any case fails, do not claim this candidate qualified
across seeds, extend the cap, or select only successful seeds.

Preserve every per-hand check, saved exact arena round trip, separate saved
audit, hashes and archive envelopes. Independently verify all gates and
control replay. This still cannot establish large-game qualification.
