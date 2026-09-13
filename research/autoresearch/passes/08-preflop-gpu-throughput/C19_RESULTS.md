# C19 rejected: exact interleaved scans are effectively tied

The first complete large-game pair improved by only 0.27%, below the registered
1% screen. Do not extend or retain this variant. The research constructor
integration is removed; the standalone manual diagnostic remains available.

| Complete fixed work | Retained C14 | C19 |
| --- | ---: | ---: |
| Six sweeps with checks, startup and synchronization | 53.1933 s | 53.0492 s |
| Candidate/control | | 0.997291 |

Warm learning time is 0.38% lower and warm check time 0.26% lower in this pair.
These near-tied observations are not evidence of a repeatable improvement.
No extended campaign or retention-only default/native regressions were run.

## Exactness and integration

All nine solver tests pass, including comparison with retained implementations
across 3-9 players, fixed and learning seats, batches 5/32, complete learning
arenas and roots, all multiway terminals, prefix output, zero reach/recovery,
CUDA graph capture/replay, eager tracing and stopping. The prior standalone
screen passes all 672 prefix cases; only writer PTX changes, with 26 registers
and no local/shared storage in either variant.

Both saved-game allocation inventories match every original buffer and plan:
313,945,632 bytes for small and 20,178,315,124 for large, preserving batch 32 and
HU-cache selection. Module/driver overhead is not included in these declared
buffer totals. All six timed gap/EV checkpoints and the full 529,900,514-entry
arena fingerprint match C14 (`27b4d2870b404cae`).

A test-only constructor uses a thread-local scoped selection, so it compiles
the candidate CDF module directly rather than compiling the old one first.
The flag resets on success/error; ordinary construction retains the old module
and separate PTX cache. The shared exact-reuse CDF writer serves both learning
and cohort checks. Global arrays, CDF layout, terminal code and arithmetic
dependencies remain unchanged. All tested integration source is archived as v3.

## Preserved harness correction

The first full run passed eight tests and failed the new constructor guard.
It incorrectly expected the first accuracy check to leave initially empty
evaluation buffers empty. Independent parsing of the saved assertion verifies
that the two learning arrays were unchanged; only result buffers were populated.
The corrected test checks unchanged learning on first evaluation, unchanged
full state on repeated evaluation, and ordinary fresh construction afterward.
Only this test changed between archived v2 and v3; kernel/integration code did not.
The corrected complete suite passes 9/9 with the saved-layout test intentionally
ignored there and run separately on both fixtures.

Frozen benchmark executable SHA256:
`1676178edc1095a08be7d61abd5c7e38370c922507fe2d7ce1ff3ae529e6c5a9`.
Both failed and corrected runs, source maps, compiler output and timing records
are preserved. Port 56708 and the qualified R03 executable are unchanged.

The next proposal needs a stronger mechanism than exposing these existing
scan chains: this source reorder did not meaningfully improve complete work.
Do not infer that another minor scan-order variation warrants the same campaign.

[Protocol](C19_PROTOCOL.md), [screen](C19_SCREEN_RESULTS.md),
[independent audit](check_c19.py), [timing result](raw/c19-timing-verified.json),
[restoration receipt](raw/c19-restoration.json).
