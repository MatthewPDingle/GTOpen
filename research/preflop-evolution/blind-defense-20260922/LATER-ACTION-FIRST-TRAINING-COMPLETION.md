# First matched training run completed

The first later-action matched trial completed all 78 registered updates on
September 25. Its controller exited successfully after 8,858.921 seconds
(about 2 hours 28 minutes). It processed 39,936 fresh training deals. No result
was selected by intermediate performance or by inspecting its ranges.

The final store contains 7,266 compressed files: 25.075 GB logical and 8.053 GB
allocated, within the 40 GB logical and 9 GB allocated limits. The final
checkpoint SHA-256 is
`b63320661a9485b3adf150d11cfc8ed9ca51854abd6c038dd98daadb2c126690`.

This is a completed training run, not an independently verified strength or
convergence result. The registered supervisor has launched the first CPU
readback and the replication controller concurrently. The replication performs
its own admission checks before GPU training. Both full readbacks must pass
before the fixed complete-policy evaluation can begin.

No production settings, ranges, or source files were changed. The recent bulk
single-policy and parallel native-evaluation candidates were qualified
separately and are not substituted into either matched trial.

Evidence: the `later-action-matched-first-v1` registration, successful status,
result, environment, resource history, storage accounting, and completed log.
Independent readback and the final scientific comparison remain pending at
this milestone; this document does not anticipate their outcomes.
