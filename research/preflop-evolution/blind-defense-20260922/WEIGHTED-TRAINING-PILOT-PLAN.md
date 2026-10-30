# Complete weighted-training implementation pilot

Run two complete 512-deal class-stratified generations, with sixteen native
32-deal subbatches each, both players' weighted reservoirs and eight CUDA Adam
steps per fit. Keep the original 302/64/64/4 representation and 0.003 learning
rate. Capacity 8192 per player exercises bounded retained data. This is an
implementation control, not a trained range or convergence experiment.

The typed checkpoint must contain the complete ordered played bank (excluding
the final unplayed model), sampler, action RNG, both weighted reservoirs and the
weighted root and exact BTN states. All 169 root classes must be covered each
generation. The exact BTN population update occurs once per generation without
sampling weights. The entire 512-deal sample is drawn once before native slicing.

Restore after generation one, replay generation two and require identical native
artifacts, retained arrays/weights/RNG, learned models and checkpoint references.
Check current-model CPU/CUDA float64 widened-weight inference at 1e-10 tolerance.
Use native own-history bank queries to compare CPU/CUDA policy averaging and an
independent scalar average that applies policy overrides before own-action reach.
Reject changed configuration, old readers and unplayed average members.

Admission requires the production app idle or confirmed closed, both research
locks free, CPU below 70%, over 20GB host RAM and 4GB VRAM free, and GPU utilization
below 20%. Take an exclusive research lock, use hidden native subprocesses, keep
at least 40GB disk headroom, and release only the lock owned by this process.
Maximum 1200 seconds and 2GB generated artifacts; no application restart or
production deployment. Record stage timings to guide measured throughput work.

A development smoke run can execute one generation before registration, writing
separate artifacts. The published run binds sources and native binaries before
execution. Neither run establishes improved poker accuracy or faster convergence.
