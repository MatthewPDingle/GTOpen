# Captured gradients across earlier training stages

The prespecified replay control passed at updates 1, 26, and 52 of the saved replication trial, for both players. Every candidate and fresh reference reproduced the historical network weights and all non-timing fit metrics exactly after the complete original 512-step fit. Together with the separate update-78 control, this covers eight historical player/checkpoint fits with substantially different retained-data sizes.

| Update | Player | Reference complete fit | Captured complete fit |
| --- | --- | ---: | ---: |
| 1 | BB | 4.796 s | 0.875 s |
| 1 | BTN | 1.078 s | 0.594 s |
| 26 | BB | 50.984 s | 11.782 s |
| 26 | BTN | 9.828 s | 3.593 s |
| 52 | BB | 52.828 s | 13.406 s |
| 52 | BTN | 18.813 s | 5.766 s |
| Total | Both | 138.327 s | 36.016 s |

The combined six measured calls took 3.84 times less time. These are one-pair controls with alternating method order, not repeated throughput measurements. Startup overhead affects the smallest fits, and these timings do not estimate a complete study's speedup. The controller completed in 222.360 seconds, including checkpoint restoration and checks outside the fit calls.

The same saved reservoirs, seeds, feature definitions, loss weights, chunk order, precision, learning rate, Adam settings, and step count were used. Neither new training data nor a new poker policy was selected. Frozen input hashes were verified again before publishing results. Production remained unchanged.

The controls support using this implementation in a separately registered next research training trial with explicit implementation metadata. They do not establish better poker accuracy, validate every possible reservoir/configuration, or modify existing saved trials.

Evidence: `cuda-gradient-graph-early-control-v1-registration.json`, `cuda-gradient-graph-early-control-v1-result.json`, `cuda-gradient-graph-early-control-v1-status.json`, and `cuda-gradient-graph-early-control-v1.log`. Source: `tools/research/hu_gradient_graph_early_control_20260925.py`.
