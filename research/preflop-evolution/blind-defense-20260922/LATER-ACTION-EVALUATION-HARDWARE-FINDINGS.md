# Hardware use during complete-policy evaluation

A read-only five-minute observation on September 25 confirmed unused capacity
during the fresh complete-policy comparison. The live evaluation, its seeds,
batch size, source files and scheduling were unchanged. No partial poker
outcomes were inspected.

| Measurement | Observed value |
| --- | ---: |
| Sample interval / observations | 5 seconds / 61 |
| First-to-last observation | 300 seconds |
| Whole-computer CPU, interval mean | 7.80% |
| Main evaluation worker CPU | 1.041 logical cores on average |
| Whole-device GPU, snapshot mean | 19.51% |
| Highest observed GPU utilization | 88% |
| Highest observed GPU memory use | 2,706 MiB |
| Minimum available host RAM | 99.39 GiB |
| Highest main-worker resident memory | 1.45 GiB |
| Latest reported deals at sample start / end | 11,296 / 13,344 |

The main-worker CPU figure excludes native children. The sampler also recorded
the process tree and observed one child, but a five-second cadence misses short
lived children; those observations are not a complete subprocess CPU total.
Whole-computer and whole-GPU counters include other applications. GPU readings
can miss bursts. The progress log reports only every 1,024 deals, so its
bookends are not an exact five-minute throughput measurement. No before/after
speed claim follows from this observation.

## What to optimize next

The authenticated, completed 64-deal control recorded these stage times for its
two 32-deal batches:

| Stage | First batch | Second batch |
| --- | ---: | ---: |
| Native query generation | 0.187 s | 0.187 s |
| Four complete model-bank predictions, combined | 2.454 s | 2.485 s |
| Native crossed-profile evaluation | 0.203 s | 0.218 s |

These times omit serialization, archive publication, some validation and other
worker overhead. The control additionally performed CPU equivalence checks
that the fresh study does not perform. They must not be treated as a complete
breakdown of current study runtime. In particular, the separate 2.79x native
parallelism benchmark is not a 2.79x prediction for this whole evaluation.

Source inspection finds a useful next candidate: each of the four banks
reconstructs the same observation features, actor/legal-action arrays and own
history indices and transfers them to CUDA. Preparing these query-dependent
inputs once could remove repeated work. Model-dependent preflop tables and
their overrides must remain separate. A bounded pipeline could then prepare
the next batch while the current batch predicts or publishes its archive.

First instrument complete batch time on previously inspected deals; then test
shared input preparation, larger batches and stage overlap separately. Preserve
model order, float64 inference, legal actions, overridden ancestor reaches,
the complete played bank, paired deal identity and ordered result reduction.
Compare policies, reach weights, native values and archive readback with the
existing implementation, and retain resource and failure guards. An apparent
utilization gain without lower time to a verified result is not a success.

These are candidates, not implemented speedups. Nothing was adopted into the
running study or production application.

### Growing archive guard cost

A later read-only metadata probe during the same evaluation repeated the
guard's directory-enumeration and file-size calculation three times. At 9,209
paths / 8,371 files / 2,655,865,329 logical bytes, the scans took 0.468, 0.485 and
0.500 seconds. No file disappeared during these observations. File contents and
poker outcomes were not read. The probe used the same output-prefix glob and
store `rglob`, followed by `is_file` and `stat().st_size`; it tolerated a missing
transient file for measurement purposes without changing the real guard.

`recovered_evaluation_runtime_v1.guard_for` performs this scan at intervals of
at least ten seconds, in both the controller and the worker. A roughly half-
second worker scan is noticeable overhead, and directory growth can increase
it. These three cached scans are not an end-to-end benchmark or proof of the
cause of any throughput change. They do not justify removing storage checks.

A future optimization could avoid repeatedly recounting already authenticated,
immutable archives while preserving conservative accounting for in-progress
files, quota enforcement, independent supervision and final full verification.
That requires its own correctness and failure checks. The current guard was
left unchanged.

## Evidence

- Sampler: `tools/research/later_action_evaluation_hardware_sample_20260925.py`.
- Registration: `later-action-evaluation-hardware-sample-v1-registration.json`,
  SHA-256 `8e4026854288eee43f96335c570b1c8861632d449948b11731e9dc0bbb25de53`.
- Complete raw sample: `later-action-evaluation-hardware-sample-v1-result.json`,
  SHA-256 `c70ec647bf024f8caed545fd6cb78783e1c5041c8e99e76a664d26fbe2f07042`.
- Control timing source: the authenticated `summary.json` members of
  `later-action-recovered-evaluation-control-v1` batches `test-000000` and
  `test-000032`; compressed manifests and decoded member hashes checked against
  the completed control result.
- Preparation source: `sampled_visible_hybrid_gpu_bank_bulk_v1.py::average`,
  called for each bank by `crossed_complete_policy_batch_v1.py::evaluate_batch`.
