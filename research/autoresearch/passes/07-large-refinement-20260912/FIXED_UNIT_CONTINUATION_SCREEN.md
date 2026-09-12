# Fixed-unit continuation small screen v1: registered before learning

Inputs: target/convergence/six-native-a/final.gtop and six-s64-a/final.gtop.
Both are 23,038-node, six-learning-seat canonical coupled-deck saved policies
at global iteration 350. Runner records SHA-256 before/after for both inputs,
paths and executable; no production server mutation. Execute serially.

For each input compare:
- control: retain saved histories and continue native full-particle GPU DCFR;
- candidate: compact-refine disjoint roots [2,0,0] and [1,0,0] for 1,000 local
  iterations each, then continue full GPU DCFR using their fixed history units.

Preserve global age. No fresh reset, sampling, changed schedule or thresholds.
Audit the six historical paths in exploration-diagnostic-paths.json, including
all descendants of those two roots. Do not drop unreachable paths. Evaluate
initial state, post-refinement state, then after every 25 global iterations,
up to 250 additional iterations. Both modes reconstruct the GPU per block;
setup/check/conditional-audit time is included in total wall time. This is an
end-to-end offline screen, not a persistent-engine throughput measurement.

Two consecutive full canonical global checks must have summed gap <=0.005 bb
with finite nonnegative per-seat gaps. In addition all six conditional paths
must pass the existing 0.1-bb action-loss / 0.1 bad-action probability /
0.0025 relevant conditional hand-mass gates simultaneously. Require those
conditional passes at both consecutive checks as well. Stop early only then.

A candidate must qualify on both inputs before a larger experiment is justified.
If a control also qualifies, compare total time including compact setup; do not
claim a speedup for a candidate slower than a qualified control. If controls do
not qualify, report quality feasibility only, not a speed multiple. Rejection
of this screen does not weaken the original large all-27-path qualification.

Limit each process to 900 seconds with run07's live-work guard. Final .gtop
files are audit artifacts only. Unit metadata remains in memory for the entire
process; there is no resume mode. Verify output save/reload histories, emit
final metadata and source/input evidence, and preserve every failed check.
