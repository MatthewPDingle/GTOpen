# Controlled evaluation-throughput test

The current evaluation spends most of its instrumented time averaging four
complete model banks. A CPU-only change reduced input-copy/preparation time by
about 12% on retained inputs, but that is not a whole-evaluation speedup. This
test measures whether that change or larger batches improve useful throughput.

## Fixed comparison

`tools/research/weighted_gpu_throughput_control_v1.py` compares four cases:

| Case | Deals per batch | Isolated query copy |
| --- | ---: | --- |
| deepcopy32 | 32 | Existing recursive copy |
| deepcopy64 | 64 | Existing recursive copy |
| snapshot32 | 32 | CPU-qualified JSON snapshot |
| snapshot64 | 64 | CPU-qualified JSON snapshot |

Every case processes the same first 64 already used evaluation deals, in their
original order, with the same four audited 78-model banks and the same native
cashflow evaluator. No fresh deals, model fitting, root-action changes, model
selection or statistical interpretation of playing strength are involved.
The model chunk size remains eight; it is not another simultaneous change.

Each case gets one warmup, then four measured repeats. The order rotates so
each case occupies each timing position once. Report all raw measurements and
medians relative to deepcopy32, without automatically choosing or deploying a
winner.

Timing covers the complete raw-batch call: native query generation, input
preparation, bank averaging/transfers, JSON transport, native cashflows and
small copies used to capture numerical evidence. It excludes one-time bank
loading, archive compression, evidence packing and equivalence checks after
each call. Bank-loading time and peak CUDA allocated/reserved memory are
reported separately. Four warmed repeats on one small retained problem are
not evidence of a universal speedup or full-study wall-time improvement.

## Correctness and resource gates

The comparison matches every observation by native information-set key,
including features, legal options, actor and prior-action history expressed in
keys rather than batch-local array indices. All four banks' action probabilities
and own-action reaches must agree within 1e-10, including repeated observations
shared between the two smaller batches. All per-deal cashflows must agree
within 1e-9. Raw evaluator artifacts and separate probability/reach captures
remain available for an independent readback before adoption.

The default command only reports readiness. `--run` requires the completed
evaluation/review queue and the following report/GPU-control queue, passing
preparation evidence, idle production, free research locks, CPU below 20%,
GPU below 10%, at least 28 GB available RAM and 8 GB free VRAM. It has an
1800-second invocation bound. Actual output is capped at 2 GB logical and
allocated at checked boundaries; a fresh global inventory reserves that output
plus 2 GB headroom under the 800 GB ceiling. Final size and global allocation
are checked again before publishing success. Transient writes are guarded but
these boundary checks are not an operating-system disk quota. Failed evidence
is preserved and there is no automatic retry.

No running experiment or port-56708 configuration is modified. No GPU benchmark
has been launched yet.

## Preparation evidence

`weighted-gpu-throughput-preparation-v1-result.json` passed in 8.469 seconds,
using the existing native query generator on the retained deals and no CUDA.
The two 32-deal batches have 14,531 and 14,540 rows; the 64-deal batch has exactly
their 29,040-row distinct union. Thus 31 observations are shared across the
smaller batches. Features and complete prior-action histories agree exactly.

Reversing the native row order while correctly remapping history indices also
passed. Deliberate changes to a probability, own reach, history link and feature
identity were rejected. The probabilities in this preparation check are
synthetic fixtures: trained-policy GPU equivalence and speed remain unmeasured.

## Independent readback

After the benchmark completes, run
`tools/research/weighted_gpu_throughput_readback_v1.py --run`. Its default mode
only reports whether the benchmark result exists. The readback uses four CPU
workers, single-threaded numeric libraries, a 900-second limit and available
RAM/production-activity checks. It never performs CUDA inference or native
poker evaluation.

The existing scalar verifier checks all 30 saved batch transports, legal
probabilities, crossed-profile construction, conditional all-in labels, native
cashflow conservation and summary identities. The added reader binds captured
probabilities and own reaches to their recorded hashes, checks row identities
without using the benchmark packer/comparator, and compares all 20 runs with
the original warmup's 64 deals. It independently recomputes the timing medians
and ratios. It cannot independently establish engine correctness or the
accuracy of the timing clock, and it does not establish playing strength.

`weighted-gpu-throughput-reader-control-v1-result.json` passed in 17.781 seconds.
Varied synthetic probabilities and reaches were placed on the existing native
query geometry. All 29,040 states agreed across batching and a correctly
remapped reversed row order. Perturbed probabilities, reaches, a missing state,
and a different but legal prior-history action were rejected. Actual saved-GPU
capture readback remains pending; this preparation is not that result.
