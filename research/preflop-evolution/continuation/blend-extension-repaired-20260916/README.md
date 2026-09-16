# N38: bounded settling extension of the unchanged 25% blend

Adaptive follow-up, declared after observing N35's 750 and 1000 blend snapshots
but before generating either new checkpoint. The gap fell from 0.03254 to
0.01514 bb, still above the unchanged 0.005 bb target. This is not a pass of
N35's fixed budget and does not replace that failed screen.

Resume the exact N35 blend save at iteration 1000. Preserve all coefficients,
the 25% blend share, original zero-range guard, frozen kernel, engine binary and
game configuration. Run exactly two further 250-iteration blocks, recording
1250 and 1500, with zero warmup. Both checkpoints are required; do not change
parameters, thresholds or cases in response to their results. Report the same
gap, selected-node frequency changes and hand-strategy variation. The purpose
is to distinguish continued improvement from a plateau within a bounded budget.

Run only after N35 and the read-only N37 queue have finished successfully, with
at least twelve minutes remaining before 20:49:02 UTC. Verify live process
identities. Do not compete with their GPU timing or CPU scan. If insufficient
time remains, retain the frozen plan as deferred. N35 must have failed its
settling screen; otherwise this specific follow-up is not indicated.

Charge all additional learning time to the blend. Report total observed work
since the shared iteration-500 source against N35's control cost, while stating
that the two final iteration counts differ. Checkpoint sampling does not locate
the exact first time the target was crossed. This extension alone cannot claim
maintained performance, fresh-range accuracy or full-game convergence, and
cannot qualify a production deployment. Keep its raw research saves local.
