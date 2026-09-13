# D03: retained-C01 GPU phase diagnosis

Registered before implementation/run. C04 failed badly; refresh the phase split
instead of choosing another memory representation without current measurements.

Add cfg(test)-only CUDA event markers around C01 prepare, normalize, duplicate
classification, CDF construction and coupled terminal evaluation. Reuse the
existing eager phase tracer. Kernels, particles, scan arithmetic and solver
updates remain unchanged. Production builds compile out the markers.

First prove the tracer leaves full regret/strategy arenas and every checkpoint
unchanged on small fixtures, with forced/frozen policies and batch5/32. Check
phase interval counts and event total consistency. Run retained C01 adversarial
coverage too. Build/test cap240s.

Then run one unprofiled and one profiled six-iteration/check sequence from each
immutable small and large save, with two warmup iterations. Require the exact
same checkpoint gaps/EVs and final arena fingerprint. Hash all sources, inputs
and executable. Cap each run180s; run07 serial live-app guard applies.

Report medians of the last four phase durations and their share of event time.
Eager instrumentation adds overhead and bypasses graphs: these are bottleneck
diagnostics, not a speed improvement or time-to-convergence result. Do not add
D03 as a performance candidate to the graph. Use the result to select a bounded
next hypothesis; no live deployment and no CPU performance work.
