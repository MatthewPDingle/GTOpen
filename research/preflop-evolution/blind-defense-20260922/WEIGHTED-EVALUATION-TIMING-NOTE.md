# Where the current evaluation spends its instrumented time

Read-only inspection of the first 16 committed batches (512 deals) found these
mean recorded wall times per 32-deal batch:

| Stage | Seconds | Share of instrumented time |
| --- | ---: | ---: |
| Generate native queries | 0.2042 | 7.9% |
| Average the four complete saved-model banks | 2.1466 | 83.1% |
| Evaluate native crossed-policy cashflows | 0.2326 | 9.0% |

Evidence: `weighted-evaluation-stage-timing-v1-result.json`, bound to the
committed checkpoint, archive manifests, compressed bytes and original summary
hashes. Inspection took 0.22 seconds using four decompression threads. No GPU
work, additional poker deals, payoff interpretation or running-study changes
were performed.

The bank interval includes CPU query/table preparation, transfers, CUDA
execution and ordered averaging. It does not identify GPU arithmetic as the
bottleneck. Serialization, archiving and coordinator overhead are not fully
instrumented, so these percentages are not fractions of total job time.

This makes bank averaging the first target for the next evaluation throughput
experiment. Compare the already supported 64-deal transport with 32-deal batches
on the same previously used deals and frozen model banks; measure complete wall
time and GPU memory, and verify per-deal policies/reaches and cashflows before
using it in a future evaluation. Instrument preparation versus CUDA separately
if larger batches do not help. Do not change the running fixed study or claim
a speedup from these timing observations alone.
