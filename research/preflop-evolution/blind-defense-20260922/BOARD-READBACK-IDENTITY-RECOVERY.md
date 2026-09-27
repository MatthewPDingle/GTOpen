# Separate stored-byte integrity from numerical agreement

The original trained-state audit stopped on a hash comparison, before
starting its parallel target review. It recomputed the provider's exact
preflop terms from independently calculated probabilities and required the
resulting serialized floating-point numbers to have identical bytes.

Read-only diagnosis of the two saved generations found:

| Generation | Largest policy difference | Largest scalar cashflow difference |
|---|---:|---:|
| 1 | 0 | 1.42e-14 |
| 2 | 1.11e-16 | 2.84e-14 |

The first generation's vector reduction differs with one versus two BLAS
threads. The second generation's independent normalization differs by one
floating-point rounding step. These differences are below the existing
1e-10 policy/exact-term tolerance, but necessarily produce different hashes.

The version 2 audit handles two distinct questions separately:

1. **Did the stored evidence change?** Reconstruct the original producer
   calculation with its two-thread setting and verify its recorded policy,
   exact-term, and update hashes. The producer is reused only for these seals.
2. **Are the numbers independently reproduced?** Keep the independent
   policy calculation, scalar cashflow sums, forward board traversal, sampled
   target review, reservoir replay, and accumulated root-state checks. All
   original numerical tolerances remain unchanged.

The new identity helper was checked against both genuine saved generations.
All producer seals and update hashes matched. Eight deliberate corruptions
were rejected: changed policy/exact-term seals and numerically incorrect
policy/exact-term calculations in each generation.

`board_training_pipeline_readback_v2.py` registers and reruns the full audit.
On success only, it publishes its own result and a compatibility completion
record for the original failed audit, explicitly linked to the new
registration and result. The original failure and source files remain intact.
It does not fit, sample new deals, change model weights, or weaken tolerances.

The general sequence auditor contains the same old byte-comparison assumption.
It needs a separate version using this qualified identity helper before its
control/prefix/full-sequence checks can proceed. No such later audit is
represented as completed by this fix.
