# Combined CPU pipeline and captured GPU fit

After the full-length weighted CUDA fitter and bounded CPU pipeline pass their
separate controls, replay the serial pilot's second complete generation with two
CPU workers and the captured weighted fitter. Keep the original pilot's eight
fit steps and all random seeds/configuration identical so the final checkpoint
must match exactly. Full 512-step numerical fit equivalence is separately covered
by `weighted-graph-fit-control-v1-result.json` on both actual player reservoirs.

Require the same checkpoint, learned model, native artifact hashes, retained
values/weights, RNG/sampler state, played bank and numerical fit diagnostics.
Only timing and explicitly identified fitter-runtime fields may differ. The
checkpoint's algorithm remains the same ordered weighted gradient with Adam;
the execution runtime is identified in per-generation metrics.

Use the same resource admission, bounded queue, exclusive research lock, hidden
native processes, inherited NTFS compression and storage limits as the CPU
parallel control. One through the configured maximum workers may execute tasks;
do not require every permitted worker to be busy. Confirm pool shutdown. No
production change or poker-accuracy claim is authorized by a passing replay.
