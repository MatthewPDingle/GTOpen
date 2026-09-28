# Faster feature preparation: complete fitted-network parity

The queued GPU control finished successfully (session 31237, exit 0). All eight
fixtures reproduced their original saved model-80 networks, advantage scales and
every non-timing fit metric exactly. This covers both players in baseline and
river arms for training seeds A and B.

Across the eight paired fits, original time totaled 93.514 seconds and vector
time totaled 64.111 seconds: 31.44% less measured fitting time, or 1.459 times
the original throughput. One pair was run per fixture with alternating order.
These are descriptive component timings under current desktop conditions, not
a general end-to-end training speed guarantee.

| Arm | Player | Original fit (s) | Vector fit (s) | First implementation |
| --- | ---: | ---: | ---: | --- |
| A-baseline | 0 | 15.500 | 9.813 | original |
| A-baseline | 1 | 9.234 | 5.875 | vector |
| A-river | 0 | 14.937 | 9.547 | original |
| A-river | 1 | 8.890 | 5.547 | vector |
| B-baseline | 0 | 13.875 | 9.610 | original |
| B-baseline | 1 | 9.047 | 7.000 | vector |
| B-river | 0 | 12.968 | 11.078 | original |
| B-river | 1 | 9.063 | 5.641 | vector |

The entire control took 193.016 seconds, including fixture restoration, repeated
validation and resource checks. Its maximum recorded reserved CUDA allocation
was 499,122,176 bytes, below the 4 GB own-allocation cap. It used the existing
production-priority guards and allowed light desktop GPU use. No new evaluation
deals were drawn; no learning bank or production game was modified.

Each fit retained the original seed, 512 optimizer steps, 4,096-row chunks,
learning rate 0.003, float32, deterministic CUDA settings and disabled TF32.
The candidate changes feature preparation; the objective and learning settings
remain those of the original implementation. The earlier CPU control separately
verified exact feature bytes for 1,558,846 rows.

Complete-update qualification is the next gate. It combines this feature change
with the separately checked query-preparation change in the river pipeline and
requires each replay to reproduce the original archived update. The checkpoint
bulk-loader candidate is separate and is not part of that comparison.

This runtime result is not evidence of more accurate poker ranges. Original
registered study sources remain unchanged. No deployment or push was performed.

## Evidence

- [Plan](VISIBLE-FEATURE-VECTOR-GPU-PLAN.md)
- [Registration](visible-features-vector-gpu-control-v1-registration.json), SHA256
  cd7486c738c613e789f790b9a0703459a0a4d476dc3711ad182099b8710f6f77
- [Result](visible-features-vector-gpu-control-v1-result.json), SHA256
  1996352403a5586faffbebb10266f4ee8fe24f4879efb4dc7a852c50ff3420f4
- Eight individual case records accompany the result.
