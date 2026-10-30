# Faster preparation of identical visible hand features

28 September 2026. CPU-only control completed while the registered matched
river continuation kept running with its original frozen implementation.

The baseline timings showed about 14 seconds of combined setup before two
fits, versus about 10 seconds inside their optimizers. Inspection found that
the bulk feature decoder still called a Python card-summary routine for each
unique visible hand/board. A separate vector implementation computes the same
33 summaries, retaining the original 269 lossless inputs and validation.
There is no new poker information, hidden-card access or changed representation.

The original scalar evaluator remains the reference. The initial control
covered 40,011 synthetic cases across all nine made-hand categories, two through
seven visible cards in legal phases, wheel/straight flush, two trips, three
pairs, board-only hands, card-order invariance and eight malformed-input cases.
Every valid output matched the original float32 values exactly.

The completed full-feature control then used all eight immutable parent-pilot
reservoirs at boundary 80, grouping by the same observation keys as the fitter.
All **1,558,846 rows of 302 features matched byte for byte**. The full feature
stage was **2.32–4.26 times faster** in these paired observations. Each fixture
was tested once, with implementation order alternating; main-study activity,
caching and OS load affect timings. This is not an end-to-end speedup claim.

| Parent arm | Player | Rows | Original (s) | Vector (s) |
| --- | ---: | ---: | ---: | ---: |
| A baseline | 0 | 243,709 | 5.687 | 1.672 |
| A baseline | 1 | 144,661 | 4.453 | 1.078 |
| A river | 0 | 243,725 | 6.219 | 2.266 |
| A river | 1 | 144,698 | 4.640 | 1.562 |
| B baseline | 0 | 244,391 | 5.907 | 1.719 |
| B baseline | 1 | 146,597 | 4.656 | 1.094 |
| B river | 0 | 244,425 | 6.907 | 2.109 |
| B river | 1 | 146,640 | 4.860 | 2.093 |

Evidence: visible-features-vector-control-v1-registration.json and
visible-features-vector-control-v1-result.json. The control used no GPU,
performed no fitting, drew no payoff-test deals and changed no training state.

## Remaining qualification

The separate vector objective/fitter only replace the feature provider. They
are **not integrated or GPU-qualified**. After the active matched study and
its evaluation finish, compare both fitters on these same frozen reservoirs:
same original fit seeds, 512 steps, chunk size, learning rate, deterministic
CUDA settings and precision. Require each original fit to reproduce its saved
model-80 network and the candidate to match it exactly. Compare normalized
objectives and scales, peak memory and elapsed stages. Do not mix an altered
runtime into the active study. If full fitted-network parity passes, check a
complete update/checkpoint before using the optimization in a future study.

This change improves execution efficiency only; it supplies no evidence of
better ranges or playing strength. The registered matched study and its
prospective analyses remain authoritative for the current quality question.
