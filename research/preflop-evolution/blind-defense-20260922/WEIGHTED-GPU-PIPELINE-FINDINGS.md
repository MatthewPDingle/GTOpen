# Faster weighted research pipeline, with exact replay

The combined two-worker CPU pipeline and shared-stream GPU fitter completed the reference generation in 24.52 seconds versus 51.45 seconds for the original serial pilot (about 2.10x faster). The checkpoint, model, native artifacts, reservoir contents, sampler and random states were identical. This is a research-training throughput result, not faster strategic convergence, more accurate ranges, or a production deployment.

## GPU fit control

Both real pilot reservoirs passed exact exported-weight and numerical-diagnostic comparisons for 512 Adam steps. Optimizer time changed from 3.875 to 0.828 seconds for BB and 2.172 to 0.453 seconds for BTN. Total fitting time was 6.343 versus 1.219 seconds and 2.328 versus 0.672 seconds respectively. The first direct fit includes cold initialization, so its total ratio overstates the reusable runtime improvement. These small reservoirs do not establish large-reservoir scaling.

The full-generation replay deliberately retains the original eight-step pilot configuration for exact comparison. Its cold fitting setup took 3.02 seconds. The separate 512-step comparison provides the full-length fitter check; there is not yet a 512-step-per-generation production-scale throughput claim.

## Repeated-fit memory issue and resolution

An additional resource probe found that V1 retained 64 MiB more after each fit, rising from 96 MiB to 416 MiB across six fits even after collection and cache release. Reusing one CUDA capture stream per device in V2 eliminated that observed growth: allocated and reserved memory both held at 128 MiB across eight additional fits after the two equivalence tests. A per-stream workspace cache is the suspected mechanism, not a proven allocator diagnosis. This API supports sequential fits; concurrent fitting has not been qualified. V1 evidence and source remain intact, but V2 is the candidate for long studies.

## Hardware use and limits

Admission checks require idle/closed production, no competing research lock, low GPU and CPU activity, and RAM/VRAM/disk headroom. CPU workers run hidden, use bounded queues, and join before GPU fitting. Two workers capture most of the measured CPU gain; a four-worker ceiling added little because the coordinator still spends about nine seconds on inference. Merely increasing worker count will not occupy the remaining cores productively.

The combined V2 run wrote about 302 MB logical / 191 MB allocated compressed file bytes. The source data and production service were unchanged. All control processes have finished. Next is the matched baseline-versus-stratified accuracy study, with independent evaluation; stronger poker ranges remain unproven.

## Evidence

- weighted-parallel-completion-v1-result.json (CPU results and original controller reporting recovery)
- weighted-graph-fit-control-v1-result.json (initial fit equivalence)
- weighted-graph-resource-probe-v1.json (V1 growth diagnostic)
- weighted-graph-fit-control-v2-result.json (512-step equivalence and memory plateau)
- weighted-parallel-graph-control-v2-result.json (combined exact-generation replay)

Each registered control binds its inputs by SHA-256; preserve those source bytes.
