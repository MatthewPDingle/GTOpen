# Automatic follow-up to the current evaluation

This queue advances the already specified board-root study after the existing
evaluation, report and genuine GPU training/restart control finish. It does not
replace, stop or restart any of those processes. It binds the upstream queue's
PID and creation time and requires its successful, source-bound results.

The fixed sequence is:

1. Independently read back the genuine two-generation training control with
   eight physical CPU workers and four board workers.
2. Compare the general sequence reader with that bounded control's readback.
3. Compare the typed CUDA policy bank with the CPU reference on the control's
   played models 0 and 1. Check all 169 root hand classes and 29,031 retained
   native observations with action histories. Use chunks 1, 2 and 8 and check
   probabilities and own-action reach to 1e-10. Test the actual learning weights
   and an explicitly artificial actor-specific weighting case. Save no new raw
   batch data and do no fitting. This does not qualify a future 78-model bank.
4. Run the existing version-2 matched prefix: the first two actual-budget
   generations of each prospectively specified arm, including exact restart
   replay. These generations count toward the fixed 78-generation endpoint.
5. Independently audit both completed prefixes with the qualified general reader.

Each stage keeps its existing source, resource, time and storage checks. GPU
stages wait for measured utilization below 10%, more than 6,000 MiB free VRAM,
low CPU use, adequate RAM and disk space, an idle production server and both
research locks to be free. The CPU audits also wait for low CPU use, spare RAM,
an idle server and free research locks. These are admission checks; they cannot
reserve resources against a user starting another application later.

The prefix still requires a fresh global inventory and reserves its full 4 GB
allocation allowance plus 2 GB headroom under the 800 GB research ceiling.
There is no assumed compression credit. The CUDA bank control writes at most
4 MB of metadata within the existing metadata reserve and uses existing models
and queries. No throughput experiment or other GPU training is launched in
parallel by this queue.

The queue has a 24-hour bound and explicit per-stage bounds. It does not retry
failures, overwrite an existing stage registration, resume an interrupted stage
automatically, change samples after looking at evaluation results, or deploy a
model. Only its own unfinished child process and descendants may be stopped on
failure; the upstream jobs and user applications are never terminated.

After the two prefixes and their audits pass, work stops at the full-study
storage decision. Full 78-generation training needs a measured storage
projection, sufficient fresh global headroom and the separate continuation
admission. It is not queued here. The completed current evaluation still needs
human-readable interpretation and visual review of its generated graph.

The new CUDA comparison is pending genuine input data and an idle GPU. A
readiness response is not a passing numerical comparison or training result.
