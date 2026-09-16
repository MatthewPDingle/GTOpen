# N38: unchanged blend extension

Completed 2026-09-16 20:41:55 UTC. The extension did not reach the registered 0.005 bb target.

| Iteration | Gap (bb) | Learning seconds for block | Maximum action change | Maximum weighted hand TV |
|---|---:|---:|---:|---:|
| 1250 | 0.010067042 | 275.541 | 0.007594 | 0.008699 |
| 1500 | 0.007918070 | 273.138 | 0.003414 | 0.003888 |

The selected-node changes passed their 0.01 limits in these extension intervals, but the gap did not. Cumulative learning work from iteration 500 was 1125.505 seconds (18.8 minutes). The observed work ratio to N35 control ending at 1000 was 2.1583, with different final iteration counts: this is neither a throughput nor a time-to-target comparison. The N35 control also missed its gap target.

This adaptively registered extension preserves the failed N35 screen. It changes no model coefficients, blend weight, kernel or empty-range handling. No fresh blend accuracy references were generated because N35 prerequisites failed. No deployment is qualified.

Independent audit verified 53 frozen inputs, 2 snapshots, normalization, per-seat gaps, selected-node changes and cumulative learning time. The separate repair-inputs file was also verified. Original scheduler failure and repaired scheduling provenance remain archived. Experimental saves must not be loaded in the ordinary app.
