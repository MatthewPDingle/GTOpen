# Coherent-range diagnostic: failed qualification

1/6 cases passed. Original thresholds and the earlier independent-input stress failure remain unchanged. No production promotion.

| Mode | Board | Same-state CFV / mass | Immediate root difference | Final root drift | Final average/BR value difference / mass | Same-policy quotient difference / mass | Passed |
|---|---|---:|---:|---:|---:|---:|---|
| abrupt_pair | KsQs2d | 0.00001296 | 0.07029098 | 0.00062898 | 0.00835161 | 0.00000257 | False |
| abrupt_pair | KsQs2s | 0.00001296 | 0.03780073 | 0.00063950 | 0.03005594 | 0.00000202 | False |
| abrupt_pair | KsQh2d | 0.00001084 | 0.05853564 | 0.00000000 | 0.00000000 | 0.00000000 | False |
| smooth_pair | KsQs2d | 0.00001026 | 0.00000006 | 0.00197506 | 0.03617265 | 0.00000404 | False |
| smooth_pair | KsQs2s | 0.00001121 | 0.00000006 | 0.00162044 | 0.02593313 | 0.00000202 | False |
| smooth_pair | KsQh2d | 0.00001163 | 0.00000006 | 0.00000000 | 0.00000000 | 0.00000000 | True |

Root differences are probability units, not bb. Value columns are bb divided by opposing reach mass. These are short, narrow diagnostics, not a full connected-game acceptance result.

The smooth rainbow case passes and has identical independent GPU trajectories. The other smooth cases pass the immediate-update and same-policy evaluation checks but fail final independent-trajectory value agreement. This localizes a remaining issue to training trajectories rather than demonstrating an evaluation-only error; it does not prove that floating-point order is the sole cause.

The abrupt rainbow case has identical independent GPU trajectories and final values, yet fails the CPU-versus-GPU immediate-average check. Source inspection identifies a relevant semantic difference: cfr.rs returns before updating averages when every opposing reach is zero, whereas kernels.cu updates average sums from the traverser reach even when the opposing reach is zero. The diagnostic deliberately includes whole-seat zero reaches. This is a concrete mismatch in the compared update rules, not evidence that every abrupt failure comes from suit compression. A focused zero-opponent update test should confirm its contribution before altering any implementation or test.

That discrepancy does not explain the smooth two-tone and monotone final-value failures. Preserve all failures, align the intended zero-reach update contract in a separate experiment, and trace the remaining independent-trajectory differences. Do not relax the thresholds or treat the successful same-policy evaluator as qualification of the full training bridge.

The test executable exited 101 after printing all six cases. The guard retained the failed status and verified its frozen inputs. The separate own-average transfer candidate uses full arenas and its own exact parity gates; these results neither qualify nor disqualify that different change.
