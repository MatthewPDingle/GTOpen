# Overnight reports from saved scenarios

The runner reads the latest **saved Preflop Lab scenario settings** at startup.
It uses those tree settings to generate fish/TAG opponent profiles and solve
responses jointly above a 25%-of-stack raise-to cutoff; it does not use the profiles or strategy from a saved game.
No old stack, opening-size, re-raise, all-in or rake defaults are substituted.

On Windows, `tools\phh\run_overnight.cmd` opens/reuses the normal server and
starts the queue. Each run gets a unique directory under `saves/overnight/`,
containing its log, exact scenario inputs, exported report queue and completion
marker. Completed reports appear in the app's report library with the run ID.
This command starts immediately; scheduling is separate.

```sh
python tools/phh/overnight_reports.py --dry-run
python tools/phh/overnight_reports.py --games 2-2,2-5 --flops 184
```

A dry run reads and validates the saved settings without starting a solve.
Windows recovery may copy older hidden-stream scenario saves into normal files.
If each game has one matching scenario, selection is automatic. To disambiguate,
`saves/overnight/settings.json` maps game labels to exact saved scenario names:

```json
{
  "2-2": "My saved 2/2 scenario",
  "2-5": "My saved 2/5 scenario"
}
```

The configured desktop already has this selection; no edits are needed there.
Later edits saved under the selected names are picked up on the next run.
Missing or ambiguous names abort before a solve. The current spot recipes
require eight seats and appropriate limp/open/re-raise branches.

The queue backs up the current lab with a unique name before replacing it.
A backup failure aborts the queue. It restores the lab after preflop preparation,
including on preparation failure, then runs the postflop reports. The existing
postflop browse session is left intact. Avoid interactive solving while the
queue is active. A file lock prevents two overnight queues from running together.

Defaults retain the original study scope: eight 2/2 spots and four 2/5 spots,
each with GTO, station and folder postflop opponents (36 reports, 184 flops
each). Preflop solves use up to 3,000 iterations and require a summed learning-seat
gap of at most 0.05 bb before exporting any ranges. Failure to reach that target
aborts preparation and restores the original lab. Adaptive opponents retain
their ordinary-action rules during convergence checks. Reports use up to 600 iterations with
a 0.35% target. These are finite-budget model studies, not proofs of exact
equilibrium. Incomplete reports and errors are recorded as failures.

The Windows runner temporarily prevents automatic sleep while it is active,
then releases that request when it exits. It does not change the power plan.
For a scheduled start, the computer and scheduling app must be awake/available
at the appointed time.

See [modeling assumptions and corrections](preflop_modeling_fix.md).
