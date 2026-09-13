# Prepared switch to port 56708

Executed after explicit user authorization on 14 September 2026. See
[R03 deployment record](R03_DEPLOYMENT.md). The procedure below is retained as
the original plan, including its pre-deployment observations.

This document is a plan, not a deployment record. Qualification never restarts
56708. The user asked whether promotion would be a good idea; the live switch
is a separate step after reporting readiness.

Observed before qualification: PID 99900 serves 56708 from
`T:/Dev/GTOpen/target/autoresearch/preflop-interactive-production-20260911/target/qualification/gto-server.exe`.
Its source checkout is clean at `53ce9dec08de9fa2f93f246d7f5efcccc8c22c68`.
Preflop is stopped at iteration 16; postflop is done at iteration 210; reports
are idle. These are observations, not conditions to assume later.

The qualified candidate is frozen separately at
`target/r03-v3-server-frozen.exe` in the research checkout. Record its SHA256
from the isolated-server evidence and verify that hash again before promotion.
Normal `gpu` features only. Web files are identical to the current production
source; the server source change selects the retained preflop GPU evaluator.

## Switch procedure

1. Re-read all three live status endpoints. Wait for any solve, report or model
   operation to finish. Re-identify the listening PID, executable, launch working
   directory, environment and current session metadata; never act on stale PID.
2. Save both live sessions through their existing APIs with unique timestamped
   backup names. Record configuration, iterations, profiles, locks, hero,
   publication state and root strategy/EV data. Hash the resulting files and copy
   them to a separate timestamped backup directory, together with current binary
   and launch configuration. Preserve all report libraries and player models.
3. Keep the candidate binary and old binary at separate immutable paths. Start
   the candidate with the existing application data working directory and CUDA
   environment on 56708 only after stopping the verified old process. Do not
   replace or rebuild the old executable in place.
4. Restore both snapshots. Verify model/configuration/iteration/strategy data,
   preflop seat models/locks/hero and report library inventory against the backup.
   Do not start a large new solve as a smoke test in the user's sessions.
5. Check health, current-session endpoints and UI access. Record new PID, binary
   hash, restored snapshots and final status. Keep both snapshot copies and the
   old executable for rollback.

## Rollback

If startup or restoration fails, stop only the verified candidate process,
restart the old immutable executable with its recorded working directory and
environment on 56708, restore both original snapshots and repeat the comparison.
Do not overwrite the original snapshots with candidate saves. Report any
restoration discrepancy rather than silently rebuilding or discarding a session.

The throughput gain is workload-specific: retained paired large fixed-work
measurements imply about 20.6% less time than the original baseline, not 10x and
not a measured reduction in iterations to convergence. Unsupported memory/layout
cases keep ordinary GPU evaluation, with an explanation in status.
