# Root-retained fresh trial status

## Verified launch — 24 September 2026

The full-size two-update control completed 1,024 fresh deals. Its independent
CPU readback passed all raw target, policy, accumulator, reservoir and random
stream checks. Maximum root-state discrepancy was 2.28e-13 bb; maximum policy
discrepancy was 6.79e-14. This is correctness evidence, not stronger ranges.

The 78-update pilot is now launched at
`T:\GTOpen-research\root-retained-fresh-pilot-v1` under the unchanged
[prospective plan](ROOT-RETAINED-FRESH-TRIAL-PLAN.md). Its live identities at
launch were controller 47576 and worker 38260. The shared GPU lock was owned
by controller 47576. Verify current processes and their creation/command
identity before treating this launch snapshot as current status.

`root-retained-study-continuation-v1` (controller 40860 at launch) watches
that exact training process. It will run the independent complete-training
readback once after successful training. It does not restart training or
schedule quality evaluation. It owns no GPU while waiting.

## Where to continue

- `root-retained-fresh-pilot-v1-status.json` and `.log` in this directory:
  training controller status and completed-update output.
- The store's `latest.json`: last fully published checkpoint.
- `root-retained-study-continuation-v1-status.json`: dependent readback status.
- `root-retained-study-continuation-v1-training-audit.log`: appears when the
  independent audit starts.

Do not restart either controller solely because a tool observation times out.
Do not overwrite their existing registrations or stores. Preserve raw files
and source bytes referenced by the registrations. The live application on
56708 is unchanged; production activity stops research.

After the complete pilot and audit, report exact restricted endpoint results
and prepare a separately registered fresh wider call/raise evaluation. Check
storage before admitting that larger evaluation; do not delete old evidence
to make room without a considered preservation plan.

## Evidence

- Full-size control registration:
  `82c82043c5523ffa7272307aed7cf5b7a004f78af2b7165bd09aedf9c69e31a4`.
- Full-size control result:
  `e4515810a9071d0c67af9ea128cee8758cfa16e3828c5cc23362d1e93c99711c`.
- Independent control readback registration:
  `9bbdf14acc8951e934d64be838ffcebc6f7899d745af59218269704725399ee2`.

The motivating diagnostic and completed small controls are summarized in
[the retention findings](ROOT-RETENTION-FINDINGS.md).
