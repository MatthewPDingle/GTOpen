# Captured GPU gradients: exact replay and timing

The September 25 control passed for both saved final training reservoirs. Capturing the repeated ordered GPU gradient calculation substantially reduced its runtime, while preserving every exported network weight and every non-timing fit metric from the historical full fits. This is an implementation-equivalence result, not improved poker accuracy or a whole-study speed benchmark.

## Measured results

Each fit performed the same 512 full-gradient steps, with the original seed, learning rate, chunk order, precision, and Adam updates. Adam remained outside graph capture. Reference and candidate order alternated by player; there was one pair per player.

| Saved reservoir | Reference optimizer | Captured optimizer | Reference full fit | Captured full fit |
| --- | ---: | ---: | ---: | ---: |
| BB | 46.266 s | 6.594 s | 55.625 s | 15.265 s |
| BTN | 23.203 s | 3.375 s | 27.797 s | 8.250 s |
| Combined | 69.469 s | 9.969 s | 83.422 s | 23.515 s |

The combined optimizer phase was 6.97 times faster. Complete fit calls, including preparation and capture, were 3.55 times faster. Both methods already used the separately qualified bulk feature preparation. The result does not establish the same benefit for every earlier reservoir size or for a complete training run.

## Why this helps

The small network previously required many repeated host-side instructions to launch GPU work. A CUDA graph records the ordered gradient operations and replays them with much less host overhead. It changes how that work is submitted, while retaining the mathematical operations and their order in this controlled test.

The control verified exact network equality against the frozen historical fit separately for both the fresh reference and captured candidate. All non-timing fit metrics also matched. Frozen input hashes were checked again before publishing the result. The controller completed successfully in 148.203 seconds; this includes work beyond the four measured fit calls.

## Hardware context and next steps

The separate 25-second sample of the preceding paired-continuation diagnostic showed approximately one logical CPU core used by its main worker, 6.1% mean whole-device GPU utilization in periodic snapshots, and at most 2,257 MiB of device memory used. This sample excludes native-child CPU time and is not a full-run utilization trace. Nevertheless, there is substantial hardware headroom. Additional RAM or a faster GPU would not remove serial preparation and submission overhead by themselves.

Next admission should qualify the captured fitter on representative earlier/smaller reservoirs before using it in a new learning trial. Independent evaluation batches are also candidates for a bounded two-/four-worker throughput control, with unchanged inputs and output equivalence checks. Neither change should be described as improved range quality. The scientific next step remains reducing noisy later-decision training targets.

Production on port 56708 was not modified. This control did not launch a new learning trial or qualify any experimental ranges for deployment.

## Evidence

- `cuda-gradient-graph-control-v1-registration.json`: prospective inputs, limits, and source identities; SHA-256 `612404ee4149b44ed9a6fce437488572cd97edda53fff7a3c656ba501b59f932`.
- `cuda-gradient-graph-control-v1-result.json`: complete metrics, timings, and exact-equality results.
- `cuda-gradient-graph-control-v1-status.json`: successful controller completion.
- `cuda-gradient-graph-control-v1.log`: four measured fit calls.
- `tools/research/hu_gradient_graph_control_20260925.py`: control implementation.
- `tools/research/sampled_visible_gradient_graph_fit_v1.py`: experimental captured fitter.
- `paired-continuation-v1-hardware-sample.json`: earlier diagnostic hardware samples.

No accuracy promotion, production deployment, or whole-study throughput claim follows from this control alone.
