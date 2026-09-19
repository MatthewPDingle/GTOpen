# Response ambiguity check

Added after inspecting the analytically computed all-in thresholds, before a
complete postflop panel was available. This does not change the registered
400 jobs or select their outcomes.

At the starting policy, TT and AKo have almost zero gain from calling rather
than folding a jam. Their mathematically exact switching points are smaller
than one millionth of AA's call frequency. They are sensitive to the finite
convergence error and sampled equity cache. An arbitrary pure tie-break can
move AA's jam value by many bb despite costing LJ almost nothing.

For every registered q, bound AA's jam value over all LJ response policies
whose total best-response loss is at most 0, .0001, .001, or .01 bb per reached
jam decision. Solve the resulting 169-variable linear programs independently.
Report the resulting value envelopes alongside the unique pure best response.
These are numerical robustness envelopes, not statistical confidence intervals
or claims about human behavior. Do not combine them with board-bootstrap
intervals into an alleged complete uncertainty interval.
