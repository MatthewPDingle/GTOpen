# Deferred candidate GPU qualification

Prepared 20 September 2026. Run only after the primary accuracy queue and
any started full-population supplement have released the GPU. Do not extend
the 09:00 Adelaide deadline, interrupt production, or change the source
reference. Compiled binaries were copied without modification into this
checkout's ignored `target/qualified-paging` folder; their SHA-256 hashes
match `paging-candidate-build-status.json` exactly. No GPU execution yet.

Before starting, verify every build-status input hash, both input game files
against the original `paged-two-freeze.json`, production idle on all three
status routes, no live main-research worker, and the existing 20 GB host /
3 GB GPU memory reserves. Hold the primary checkout's shared research lock
while running this separate checkout's guard, so another main-checkout worker
cannot overlap. Use an exclusive lock with an identifiable owner process;
release only that owned lock on completion. Do not stop or remove another
process's lock. The candidate guard retains its own local per-child lock.

Prepend the primary checkout's existing NVRTC directory to PATH. Use this
checkout's `loopback_research_validation.py` so the guard records the actual
candidate source files, not the baseline implementation. Freeze this runtime
document via GTO_RESEARCH_PROTOCOL. Bound the switching test to 600 seconds
and the connected run to 2,400 seconds, each capped by the remaining time to
09:00. Require at least 45 minutes remaining before starting qualification.

First run `target/qualified-paging/continuation_paging-test.exe` with
`--nocapture --test-threads=1`. Require the intended test to execute and pass
(not zero tests or an ignored test): 160 switches must preserve every returned
CFV and host arena bitwise, leave the non-updated opponent arrays unchanged,
and report exactly the predicted reduced transfer count. A failure stops
qualification and is retained.

Then run `target/qualified-paging/integrated_continuation_paged.exe` with the
original subtree and `old-two-orbits.json`, through all 2,000 iterations.
Preserve checkpoints 1, 20, 100, 500 and 2,000. Run the primary checkout's
strict `paging_candidate_review.py` against frozen `paged-two-result.json`:
every saved scientific field must agree exactly, accounting must pass,
final full gap must remain below 0.01 bb, and arena traffic must be precisely
five sixths of baseline. No numerical tolerance relaxation or checkpoint
selection. Any failure is a failed candidate, not a basis for deployment.

For timing, a separate uncontended baseline rerun under the unchanged primary
checkout may follow if enough time remains; its own normal shared guard owns
the lock. Record ordering and resource evidence. Compare complete runs and
also the 500-to-2,000 interval. One pair is an observation, not a robust speed
guarantee. Comparison with the historical baseline alone remains descriptive.
Do not merge, deploy, or claim production Preflop Lab acceleration from these
research-only paging tests.
