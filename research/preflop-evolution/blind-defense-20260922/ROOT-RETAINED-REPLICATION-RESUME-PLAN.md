# Resume the interrupted independent-seed replication

Windows reported an unexpected reboot at 21:03 on 24 September 2026. Both
research processes and their watcher are gone. The original running status
files are stale and remain preserved as evidence. The same production binary
was restarted on port 56708; no new game or solve was started.

The newest checkpoint pointer (6), update-6 metrics and latest pointer contain
invalid zero-filled JSON. Checkpoint 5 restores successfully, including all
reservoirs, root accumulators, played models and random states. Every registered
input hash still matches. All five complete iterations' raw artifact hashes
match their metrics. Selection of update 5 is solely the highest contiguous
verifiable completion boundary; no strategy results were inspected to choose it.

Before resuming, independently reconstruct those five updates with the same
scalar reader, stopping at five while retaining the original 78-update config.
This prefix audit is explicitly nonterminal. Check the next saved random draws
where readable partial evidence exists, and verify the update loop is unchanged
apart from starting at six and flushing completed evidence to durable storage.

Copy only the 264 verified prefix files into a separate compressed resume store;
do not overwrite or delete the interrupted run or its incomplete sixth update.
Retain the original batch identifiers, seeds, model configuration, fit settings,
and played generations. Resume from the complete fifth checkpoint and finish
the original 78 updates. This is the same candidate, not a new random trial.

Charge 2,280 seconds to the interrupted attempt (20:25:15 admission to the
21:03:14 boot time, rounded conservatively). The remaining execution allowance
is 19,320 seconds, preserving the original six-hour cumulative training cap.
Downtime and independent audits are excluded as before. If that allowance is
insufficient, report an incomplete experiment without extending it based on
results. No automatic retry is configured.

Measure all three research roots again. The full new-store allowance of 40 GB,
including its copied prefix, plus the existing 2 GB reserve must fit within
800 GB. Preserve all original free-space, host-memory and GPU-memory checks.
The controller and audit watcher keep the production-idle and exclusive GPU
guards. Record the new registration and provenance before training.

After completion, independently read back all 78 updates, including the copied
prefix. The previously prepared endpoint test must be explicitly adapted to
the resumed candidate's provenance; do not make the interrupted original appear
complete. No production deployment or wider evaluation is authorized by a
successful restart alone.
