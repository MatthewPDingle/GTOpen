# Saved root-action replay: CPU throughput qualification

All 48 repeated-input jobs reproduced the qualified action values and native
outputs exactly. Twelve workers were fastest in this bounded timing test.

| CPU workers | Time for 12 batches | Speed relative to one worker |
| ---: | ---: | ---: |
| 1 | 52.72 s | 1.00x |
| 4 | 16.17 s | 3.26x |
| 8 | 12.16 s | 4.34x |
| 12 | 7.88 s | 6.69x |

This measures saved-data reconstruction, validation, serialization and native
evaluation, including worker startup. It is not a preflop-solver speedup or a
range-accuracy result. Each worker-count case was timed once on the same small
repeated inputs; full-sample throughput may differ.

The benchmark used only the two already-qualified 32-deal batches. Repetition
did not add independent scientific samples. All later policies stayed fixed.
The next replay should use 12 workers when other workloads permit, with the
original full sample and per-batch mixture/accounting checks.

The benchmark retains 11.62 MB. Its newly owned temporary input copies
were hash-verified and retired; original evidence remains intact. An independent
file review checked all 48 receipts, exact original-versus-replayed output bytes,
the worker selection rule, and absence of leftover temporary inputs.

The benchmark used no GPU and changed no production code. The full 65,536-deal
replay has not launched; its bounded recovery/aggregation runner is the next step.
