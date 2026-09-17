# Paired continuation research

This study investigates whether correcting connected postflop values improves
the earlier BB call-versus-3-bet decision. It is entirely offline. Port 56708
and production code are unchanged.

## Initial development screen

The 18-feature candidate is frozen in `candidate.json`. It passed the leaf-error
guard, but did not improve action prediction when an entire policy family was
left out. The best screened choice increased mean adjusted action error from
about 0.206bb to 0.220bb. Its action-loss weight was zero; direct action fitting
did worse on the other family. **It was not advanced to the planned prospective
test, and no test references were generated for it.**

`PROTOCOL.md` preserves the original plan, including the unused test design.
`training-screen.json` contains all 12 choices. `transfer-diagnostic.json`
records a subsequent exploratory capacity check: aggressive fitting substantially
reduces same-family error, but can worsen predictions for the other family.
Adding range-composition features helped one transfer direction, not both.
These results suggest a transfer problem; two related families cannot determine
whether data coverage, model structure, or label noise is the dominant cause.

## Broader development data

`development-expansion/` is a separate, preregistered acquisition of 60 reference
solves. It adds two synthetic policy families with coherent reaching ranges,
covering called opens, called 3-bets and called 4-bets on ten shared stratified
boards. These fixtures are not claimed GTO strategies or observed player models.

The expanded screen considers both 18- and 54-feature corrections and validates
by leaving each of four policy families out. Its protocol fixes the choices,
quality gates and selection rule before fitting. The unchanged model is the
baseline; an improved same-family fit is insufficient to select a replacement.
Any resulting candidate still requires an independent prospective test.

## Reproduce or resume

Set `OPENBLAS_NUM_THREADS=1` and use Python with NumPy/Torch installed. The recorded
offline GPU reference executable and input hashes are in the manifests. Every
new GPU job checks that the live app is idle; there are no live-server mutations.

```powershell
python tools/research/run_paired_expansion.py run
python tools/research/run_paired_expansion.py screen
```

The first command resumes missing development references. The second refuses
to overwrite a completed screen. Do not rerun preparation or training over
frozen manifests/candidates. No background scheduler is installed by this study.

The original strict runner stopped after three successful solves because Rust
serialized one inclusion probability one floating-point step differently from
Python. `runner-freeze.json` records the repair. The adapter allows only that
metadata field to differ by at most two ULP; every other field and all solver
quality gates remain exact. It does not rewrite the original reference files.

Tests: `test_paired_continuation.py`, `test_paired_expansion.py` and
`test_paired_metadata.py` cover null corrections, known-residual recovery,
conservation, bounds, legal coherent reaches and strict metadata rejection.
