# Retained target CPU profile

The fixed fixture is the first history/selected chunk in batch zero of the first context in the completed A-relative cycle 2. It contains 40,534 history rows and 5,671 selected rows. No new poker deals or training targets were generated.

The ordinary CPU replay took **2.523 seconds preparing inputs** and **0.378 seconds running inference** across these two query batches. Preparation accounted for 87.0% of their combined scoring time. Both the ordinary replay and a separate instrumented replay reproduced the original saved probability arrays exactly, including which actions have zero probability. CUDA was not initialized. One math thread and below-normal process priority were used.

The instrumented call profile highlights three areas: repeated preflop-table scans across postflop rows; construction/validation of visible and public input features; and river-relative card features on cache misses. In the history replay, the four table scans took about 1.02 instrumented seconds. They validate every row before skipping postflop rows, although these tables can only replace preflop policies. Neural inference took about 0.34 instrumented seconds. These profiler timings include instrumentation overhead and are not reliable standalone speedup predictions.

A possible next implementation change is to validate shared conditions once, route only the preflop rows through preflop tables, and preserve original indices, table precedence, probability support, and all rejection behavior. It needs equivalence checks on both representations, original and learned generations, all street types and malformed inputs before adoption. The currently pinned training sources and live helper have not been changed.

This profiles scoring for one retained chunk, not the complete river-target generator: posterior construction, native transport, archives and other CPU work are outside this measurement. It complements the six-cycle timing audit but does not measure parallel end-to-end throughput or prove an accuracy improvement.

The first launch stopped before admission on a Windows path-separator lookup in the profiler. The lookup was corrected before any attempt/output existed; no scientific process or target generation was repeated. Successful diagnostic run: 8.969 seconds, no new samples, fits, native execution or production changes.

Detailed identities, timings and top function costs are in `stack-context-retained-cpu-profile-v1-result.json`; the two `.pstats` files retain the complete call profiles.
