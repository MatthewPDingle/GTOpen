# Full board-root continuation: prepared, not admitted

`board_matched_continuation_v1.py` prepares generations 3 through 78 of each
prospectively specified board-root arm. The first two genuine generations count
toward that endpoint. It uses the original pipeline, scientific configurations,
samples, model fitting and two-physical/four-board-worker layout. It makes no
new range-quality or playing-strength claim.

The runner preserves each prefix `progress.json`, restart replay and checkpoint.
It writes a separate `continuation-progress.json` and new generation directories
inside the same study store, retaining the original prefix metrics as the first
two entries. Every complete update is restored and compared before its progress
is published atomically. Explicit `--run --resume` restores the last published
checkpoint; unpublished failed attempts stay on disk and count toward the budget.
There is no generation 79, automatic retry, new stopping criterion or deployment.

Execution requires the genuine GPU/restart control, trained-state readback,
successful version-2 prefix, successful independent prefix audit, unchanged
source bindings and completed upstream queues. Missing evidence rejects before
CUDA or resource admission. The default command only reports readiness.

## Storage admission still to prepare from actual measurements

The fixed admission artifact is
`board-matched-full-storage-admission-v1.json`. It does not exist yet. Do not
create a passing artifact merely to satisfy this interface. After the genuine
full-budget prefix and its readback pass, project all 78 generations using its
measured raw generation and checkpoint components, including growth of the
reservoirs to their configured capacity. Include readback/evaluation space and
failed-attempt headroom. Both proposed logical and allocated caps must cover
their projections; NTFS flags alone do not justify assumed compression savings.

The artifact must identify format 1, the exact existing store, two arms and 78
generations per arm; bind the prefix result/audit hashes and all source and
measurement evidence; include every prefix generation metric; and record
positive `projected_full_allocated_bytes`, `projected_full_logical_bytes`,
`maximum_allocated_bytes`, `maximum_logical_bytes` and `reserved_followup_bytes`.
The follow-up reserve is at least 4 GB. Its scope is
`Measured full-budget prefix projection; fixed 78-generation study`.
`passed` and `full_study_storage_admitted` may become true only after the
projection and fresh global inventory genuinely fit.

At actual launch the runner repeats the inventory across all three research
roots, adds the remaining full-store allocation allowance and follow-up reserve,
and retains a separate 2 GB buffer under the 800 GB ceiling. It checks actual
logical/allocation sizes before and after updates and before final publication.
These are admission/publication checks, not an operating-system disk quota;
an interrupted update can transiently exceed a limit before being rejected.

Full trained-state readback and the fixed fresh 65,536-deal, eight-contrast
evaluation still follow complete training. Those are required before claiming
that the new estimator produces stronger play. No full-study launch is queued.

## Verification and prepared full reader

`board-continuation-sequence-control-v1-result.json` passed in 2.109 seconds.
It used real Windows files and atomic publication with synthetic training
states, covering the complete 2-to-78 sequence, refusal to advance to 79,
preservation of the original prefix, failed progress publication, a storage
failure before publication and a guard failure after publication. Resume
repeated only the unpublished update. Wrong prefix and registration identities
were rejected. Missing genuine evidence stopped the runtime before resource
or CUDA admission. This is orchestration evidence only.

`board-continuation-preparation-v1-result.json` binds all four source files and
records both runners correctly reporting their still-missing qualifications.
The actual full training and full readback have not run.

`board_matched_complete_readback_v1.py` is the prepared full reader. It requires
completed training for both arms, the qualified general sequence reader, and
the genuine prefix audit. It verifies preservation of both prefix histories
and checks all 78 generations with the existing scalar/physical readback:
312 sampled boards and 39,936 physical roots per arm, plus saved targets,
reservoirs, policies, RNG state and checkpoint identities. It permits eight
physical CPU workers alongside four board workers, uses no GPU or refitting,
and has a twelve-hour invocation bound. Its shared native engine, feature
encoder, sampler and reservoir remain explicit limitations. Successful
mechanical readback alone cannot establish stronger poker play.
