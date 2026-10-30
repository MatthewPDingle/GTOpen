# Prepared full-update qualification for execution optimizations

Run only after the current matched river continuation and independent review
finish, and after visible-features-vector-gpu-control-v1 passes all eight fits.
Default preflight reads sources and readiness only; it must not start a fit or
replace either research lock. Do not alter the current scientific run.

Four cases restore the original A-seed boundary 78 and replay update 79:
baseline reference, baseline candidate, river candidate, river reference. All
use eight physical workers and four board workers, with the original seeds,
model, deals, action streams, reservoir insertion, 512 optimizer steps and all
learning settings unchanged. These are replays, not new learning-bank members.

The baseline candidate changes only the fit-feature preparation import. The
river candidate also uses the subset-preparation worker pool. The pool retains
the original initializer and replaces only that worker instance's prepare
method. Existing pipeline, worker and fitter files remain unchanged.

Require exact saved model/checkpoint identities, complete restored-state equality,
per-batch artifacts, original non-timing fit metrics and ordered reservoir
contents. All four cases must match their original archived oracle, not merely
each other. The current full fit control supplies both-seed/model-80 coverage;
this complete-update control covers two methods at one earlier A-seed update.
Do not claim universal equivalence or broad poker accuracy from these checks.

Record full update timings and external GPU waits. This is one paired replay
per method with reversed method order, not a robust performance benchmark or an
equal-time accuracy experiment. Candidate adoption requires full parity; speed
benefit must be assessed in the measured complete updates, not inferred from
the earlier preparation-only timing ratio.

Use the existing production and heavy-work priority guards, light desktop GPU
sharing, 4 GB own CUDA cap and 2 GB external headroom. Reserve 12 GB logical
storage plus 2 GB follow-up within the 800 GB global allocated cap. A single
invocation is bounded to 90 minutes. Preserve failed attempts; no automatic
retry or deletion. A separately authorized/versioned recovery can reuse verified
completed cases. No push, deployment or changes to saved production games.
