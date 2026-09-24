# Root-retained fresh trial status

## Training completed — independent audit passed

All 78 registered updates completed successfully on 24 September: 39,936 fresh
deals, with no early quality-based stopping or checkpoint selection. Training
execution took 13,304.687 seconds (about 3 hours 42 minutes). The final checkpoint
hash is `306a9ebba3cf1bb13a557bd4cefd19aa3ad067985a9db9993ce4617d1adb9ec2`.
The result hash is
`2f8c8c319353e2b686dd369269f579d43e754e28bc3219f1cfa445482880ad3b`.

The independent audit completed successfully in 5,042.406 seconds. It
reconstructed all 78 updates and 39,936 sampled BB first decisions, including
the retained root state after the shared reservoir filled. It replayed 861,131
BB and 130,151 BTN training-record insertions and checked policies, checkpoint
state, reservoir contents and random streams. Maximum root-state discrepancy
was 9.10e-12 bb, target discrepancy 5.69e-14, and policy discrepancy 1.01e-12.
The audit result hash is
`78e54e6c7d64e03ee66a1080619ea91c0e3a3335dabf6e8db774ebf52c152d37`.
These are correctness checks, not evidence of stronger poker ranges.

The continuation controller exited successfully. The full 78-model exact
restricted endpoint evaluation has been launched separately. It will report
all four registered averaging pairings without selecting a favorable result;
the broader test still uses its preselected linear/linear policy.

Lossless storage recovery is complete. The three-root inventory was about
722.1 GB, with the next full evaluation allowance projecting 770.2 GB against
an 800 GB cap. Remeasure after the audit before launch. The next actions remain
the complete exact restricted endpoint check and its independent review,
followed by candidate-specific numerical/storage admission and the separately
registered wider call/raise evaluation.


## Verified launch — 24 September 2026

The full-size two-update control completed 1,024 fresh deals. Its independent
CPU readback passed all raw target, policy, accumulator, reservoir and random
stream checks. Maximum root-state discrepancy was 2.28e-13 bb; maximum policy
discrepancy was 6.79e-14. This is correctness evidence, not stronger ranges.

The 78-update pilot was launched at
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
