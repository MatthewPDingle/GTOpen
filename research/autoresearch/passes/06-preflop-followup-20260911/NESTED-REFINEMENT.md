# Follow-up to the registered conditional screen

The first 100-iteration two-subtree solve completed in 8.04 seconds including
load/global revalidation/save (4.40 seconds learning). Total global gap remains
0.004135 bb, but only two of six local gates pass. The remaining nested cold-call
branches can still lose current incoming mass inside the larger local solve.

Test six selected branch roots in upstream-to-downstream order, 100 iterations
each, recomputing incoming average distributions before each root. Each call
is individually disjoint and bounded; later calls may refine descendants of an
earlier call. Recheck every selected path and the global result afterward.
No assertion that an earlier local solve remains qualified after child changes.

Run from `six-native-b` and `followup-six-gamma15-s64-42`, retaining both
outcomes, with a 600-second cap per run. These are additional solve seconds,
not part of the earlier GPU speed ratios. This does not establish a general
convergence guarantee or qualify a large game for production.

The 100-iteration nested screen finished normally. Sampled local gates improved
from 2/6 to 4/6, native remained 2/6 despite lower weighted losses. Both full
global gaps remain below 0.005. Register a 1,000-iteration-per-root follow-up
from the same original native and sampled snapshots, not the already-refined
copies. Same paths, constraints, 600-second cap, global and local revalidation.
