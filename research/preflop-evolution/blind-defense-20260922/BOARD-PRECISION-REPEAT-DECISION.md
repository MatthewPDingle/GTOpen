# Decision after the independent precision repeat

The completed 128-board repeat supports building a bounded mechanical training
control. It does not authorize a production change or establish better ranges.
The current complete-bank evaluation continues independently.

Both registered precision runs are complete. The repeat reviewed all 466 jobs,
1,352 private-pair artifacts, the chance streams, all 169 hand classes and
independently reduced numerical moments (maximum discrepancy 9.095e-13).
The comparison figure has been visually checked.

## What improved

Relative to the private-first CPU reference, the repeat's variance multiplied
by summed worker wall time was 0.0858 for raise versus call, 0.1825 for call
versus fold, and 0.1487 for raise versus fold. Their reciprocals are approximately
11.7, 5.5 and 6.7. These describe estimator precision per measured computation,
not training convergence, production GPU throughput or playing strength.

The earlier 32-board pilot gave corresponding ratios 0.0942, 0.2521 and 0.1419.
The two runs were not pooled. Both use one fixed played generation-77 policy;
changing policies during learning is an additional test, not a proven result.

The repeat's RMS standard errors were 0.461, 0.469 and 0.643 bb, compared with
2.036, 1.421 and 2.156 bb for private-first estimates. Its class-weighted mean
differences were +0.107, -0.033 and +0.073 bb. Agreement of sampled means does
not prove unbiasedness; the separate arithmetic and chance-law controls remain
essential. Class errors share boards and are correlated.

## Exceptions remain visible

Board variance was higher for 64s in raise versus call; T2o, 62s, 64s and 98o
in call versus fold; and 86o in raise versus fold. No hands were dropped.
The largest absolute descriptive standardized mean discrepancy was 2.72
combined standard errors (QJo, raise versus call). This is selected from many
comparisons and is not a significance test. The pilot's AA raise-versus-call
and 93o raise-versus-fold discrepancies were smaller in this independent run
(1.39 and 0.19 combined standard errors respectively), but rare large payoffs
still need attention.

## Next bounded work

Implement a separate board-root accumulator and round-trip control, preserving
the expected per-generation scaling of the current weighted root estimator.
Verify all root increments independently, retain exact preflop terms, reject
incomplete or detached generation evidence without mutating state, and verify
identical continuation after recovery. Count public board draws honestly;
never relabel them as physical-deal visits. Do not edit registered dependencies
or the running trainer. See BOARD-ROOT-TRAINING-INTEGRATION-NOTES.md.

Only after those controls and interpretation of the existing main study should
a prospective matched training trial be registered. Board count and worker
count must be chosen before inspecting that trial's ranges.

## Use of the available machine

The repeat used four independent CPU workers with one math thread each while
the main evaluation control used the GPU and its CPU reference path. It took
719.4 seconds for 128 boards and 21,632 private deals. A contemporaneous resource
sample showed 27.2% system CPU, 102.1 GiB available RAM, 2,374 MiB occupied GPU
memory, 257.9 GiB free on S: and 59.5 GiB free on T:.

This confirms headroom, not that every stage can profitably use it. Preserve
the running experiment. For subsequent work, benchmark larger worker pools on
identical inputs, overlap independent preparation and GPU work, and compare
end-to-end elapsed time. Avoid competing GPU jobs and respect production use,
available-memory guards and the 40 GiB S: reserve. Keep large disposable data
on S:; do not treat the earlier 800 GB free-space estimate as still available.

Evidence: BOARD-PRECISION-COMPARISON.md, board-precision-repeat-v1-review.json,
board-precision-repeat-v1-all-classes.json and the registered input artifacts.
