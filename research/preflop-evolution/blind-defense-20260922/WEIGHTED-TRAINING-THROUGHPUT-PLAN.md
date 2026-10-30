# Next throughput test: preserve the weighted training result

The one-generation development control took 49.42 seconds for 512 deals:
15.98 seconds ingestion, 12.39 seconds integrated root derivation, 5.56 seconds
current-policy inference, 4.67 seconds in the three native query/update/trace
stages, and 2.92 seconds fitting (including initial CUDA setup). Publication was
0.25 seconds. This is direct stage timing, not a sampled utilization graph.

The initial published run's second generation took 51.45 seconds, with 19.44
seconds ingestion, 11.30 root integration, 8.39 inference and 0.47 fitting. These
measurements motivate parallel CPU preparation/validation before optimizing the
small fitting kernel. They do not establish a speedup or poker convergence.

After the serial pilot and exact restart checks pass, benchmark one, two and four
workers on the same frozen model and source generation. Keep sampling and action
RNG in the coordinator. Generate/infer each subbatch under the same immutable
policy. Workers may run native verification, tracing, target validation and root
integration independently; keep real reservoir insertion and root reduction in
original subbatch/visit order. Worker outputs must carry their source bindings.

Reuse admitted cache/targets within each worker rather than reloading them for
every subbatch. Bound the pending queue to avoid retaining every query/trace in
RAM. Include worker startup, serialization and output costs in wall-clock timing;
record a warm-repeat timing separately. Preserve complete validation and exact
RNG/retained rows/model/checkpoint equivalence, not only aggregate frequencies.

Admit workers based on current CPU load, free RAM, application status and research
locks. Start with at most four workers; test more only if these measurements
justify it and other applications have headroom. Do not run concurrent GPU fits.
Use inherited compression for a new long-study directory to reduce storage growth
without changing logical evidence bytes. Do not alter older registered sources.

Only a measured, equivalent winner should feed the longer matched baseline versus
stratified comparison. That comparison still needs fresh independent evaluation;
coverage and fitting loss alone are not accuracy or convergence evidence.
