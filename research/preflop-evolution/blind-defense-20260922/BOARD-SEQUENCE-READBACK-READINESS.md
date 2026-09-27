# Independent verification for the matched training prefix

`board_sequence_readback_v1.py` extracts the complete numerical readback from
the existing bounded GPU-control auditor into a generation-sequence function.
It accepts one through 78 consecutive generations, checks exact metric bindings
and batch coverage, and reconstructs physical targets, weighted reservoirs,
board chance draws, dense native board cashflows, scalar root/BTN regret updates,
saved random states and the complete played-model sequence. It never refits the
networks or calls the training update to produce the expected targets.

The calculation still shares the native poker engine, feature encoder, sampler
and reservoir implementation. This is independent accounting and cashflow
readback, not a second poker engine or a playing-strength certificate.

The driver `board_matched_readback_v1.py` has two modes:

- `--mode control`: read the genuine complete GPU control and compare counts,
  final checkpoint and numerical errors with the original bounded readback.
- `--mode prefix`: require that general-reader control, then audit both actual
  matched-prefix arms using their published progress and generation identities.

Both support `--check-ready`, which starts no workers and writes no artifacts.
The current readiness checks correctly report missing upstream trained results.
Syntax and read-only readiness checks have passed; the sequence reader's actual
trained-state qualification has **not** run. Do not claim it has passed until
`board-sequence-readback-control-v1-result.json` exists and its bindings verify.

At most eight physical-target workers and four native-board workers overlap.
Each numerical worker uses one BLAS thread. Admission checks CPU load, production
activity and available RAM; ongoing checks retain a 24 GB coordinator floor.
Production/RAM probes are throttled to three seconds so per-file source binding
checks do not repeatedly query the application. No GPU is used by the auditor.
The control has a 30-minute bound and the two-arm prefix a 60-minute bound.

Even a successful prefix audit does not admit all 78 generations: full-study
storage projection and continuation remain separate unfinished work.
