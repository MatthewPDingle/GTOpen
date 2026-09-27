# Parallel independent readback

The user requested better CPU utilization during independent verification.
The original single-process checker remains running and unchanged. A separately
named reviewer will distribute whole archive batches across eight CPU processes.
This is an execution change after sampling, not a new scientific experiment.

Every worker calls the frozen original `verify_batch` and original archive
decoder. The parent keeps the original chance stream, initial/final RNG checks,
input hashes, bank identity checks, root-stability checks, all eight statistical
comparisons, and ordered scalar reductions. No inference, retraining, additional
evaluation hands, changed intervals, omitted checks, or outcome selection.

Qualification: compare serial and parallel results exactly on 16 completed
batches (512 hands), equally covering original and continued archives. Require
the same results, observation counts and summary hashes; require malformed
chance/batch metadata to fail through the process boundary. Require a measured
speedup above 1.5x before starting the full parallel reviewer. Startup is included.

Bound eight workers, sixteen queued batches, 300 seconds per queued batch,
six hours total, and at least 20GB available host RAM. Workers read existing
archives only. Failures propagate without automatic retries. Keep output names
separate from the existing review. The full parallel run rechecks all 65,536
hands, including those already checked serially; partial serial progress is not
accepted as a substitute. Keep the serial reviewer until the parallel proof and
its source-immutability checks pass, then stop only the verified redundant
reviewer/controller if they remain live. Retain its logs and record interruption.

This checks archived transport, chance, payoff identities and statistics. As
before, it does not independently reimplement neural inference or native poker
evaluation, and does not establish general preflop accuracy.
