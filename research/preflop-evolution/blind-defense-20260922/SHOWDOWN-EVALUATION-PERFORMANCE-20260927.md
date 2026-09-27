# Evaluation performance investigation

The user requested faster execution after observing intermittent GPU use.
The admitted 65,536-deal study remains running unchanged. No interim poker
outcomes were inspected for this investigation.

## Measured bottleneck

A 40-second, 50 Hz py-spy recording of worker 40612 collected 1,909 samples
with zero sampling errors. Stack attribution:

| Stage | Samples | Share |
| --- | ---: | ---: |
| Archive publication | 1,026 | 53.7% |
| Archive release verification | 364 | 19.1% |
| Other evaluation | 228 | 11.9% |
| Bank inference | 147 | 7.7% |
| Shared query preparation | 136 | 7.1% |
| Other | 8 | 0.4% |

These are Python sampling proportions, not direct CUDA kernel timings.
Recent batch timing fields separately showed 1.88–2.31 seconds across the
four bank calls, including shared CPU preparation, and roughly 0.24–0.27
seconds for the native payoff process. Typical complete batch cadence was
about 14 seconds. This points primarily to serial CPU archival overhead,
not lack of available GPU memory.

## Isolated candidate

`crossed_profile_decoder_fast_candidate_20260927.py` reconstructs each of
the four donor policies once and reuses its canonical JSON row bytes across
eight crossed profiles. It also vectorizes residual value assignment while
retaining scalar exact-sum prediction and integer overflow checks. The
existing archive format, float precision, probability values and all original
archive integrity checks are retained. The original registered files have
not been edited.

On the two reused full-bank control batches, three decoder timings each
showed median speedups of 2.55x and 2.97x. All decoded bytes matched the
original profiles exactly. A complete publication/release experiment on the
first control batch took 7.96 seconds with the original decoder versus
5.81 seconds with the candidate (1.37x). Compressed archive bytes matched
the existing control archive exactly. Wrong hash, wrong length and wrong
codec were rejected. These are small, concurrent-workload measurements;
they are not a measured end-to-end study speedup or full decoder qualification.

Benchmarks used separate process-local decoder substitution and temporary
owned archive directories. Neither the study process nor its inputs were
modified. A temporary profiler installation is outside the repository.

## Next execution work

The larger opportunity is to overlap inference with bounded CPU archive
workers, using the spare CPU cores. Keep exact deals, batch boundaries,
model order, archive bytes and final paired analysis unchanged. Bound queued
scratch by the existing output/storage limits; do not multiply model banks
or GPU jobs just to raise utilization.

For the current run, switching implementations requires a separately
documented deterministic continuation. Verify every completed archive,
reconstruct sampler position and sufficient statistics without examining
interim outcomes, then resume the exact next batch under new evidence
routing. Preserve the original attempt and its terminal status. The existing
review supervisor is bound to the old worker and must be handled explicitly.
Do not hot-patch the running process or silently relax its source hashes.

First qualify the optimized codec on broader valid and malformed fixtures
and benchmark bounded archive parallelism on reused control inputs. Only
switch this run if the measured time saving exceeds migration/validation
cost. Otherwise keep the ongoing study and apply the improvement to later
work. No improvement in poker strength follows from these execution tests.
