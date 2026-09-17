# Native shallow correction: fresh-policy feedback

Research only. Production port 56708, server code, binaries and defaults were unchanged.
The frozen 18-coefficient model was ported into an explicitly selected offline CUDA kernel.
No coefficients were refitted using these ranges or reference labels.

## Integration and stability

Python, native CPU and CUDA agreed on 126 range/stack fixtures (42,588 values).
Exact zero-stack and stack-transition tests conserve the pot. Native complete action
values agree with an independent Python tree reconstruction within 0.000004bb.
Eleven complete-tree fixtures also passed the stack-boundary checks; the largest
action-value movement across a boundary perturbation was below 0.000006bb.
Disabled, sparse-range, and three/eight-player guard fixtures reproduced baseline values.
Saved strategies were checked unchanged during each native evaluation.

| Policy | Root action movement, 1500 to 3000 | BB vs open movement | Stability screen |
|---|---:|---:|---|
| baseline | 0.1051 pp | 0.0662 pp | Pass |
| shallow | 0.0248 pp | 0.0028 pp | Pass |

These are small 40bb heads-up games. A small frozen-range gap is not proof of
full-game equilibrium when the continuation values themselves depend on ranges.

## Changed strategy

| Decision / action | Baseline | Shallow |
|---|---:|---:|
| SB first in: Fold | 15.29% | 10.40% |
| SB first in: Limp 1 | 33.03% | 42.97% |
| SB first in: Raise 2.5 | 51.68% | 46.62% |
| SB first in: All-in 40 | 0.00% | 0.00% |
| BB vs 2.5bb open: Fold | 37.75% | 38.45% |
| BB vs 2.5bb open: Call 2.5 | 40.50% | 40.40% |
| BB vs 2.5bb open: 3-bet 7.5 | 21.75% | 20.57% |
| BB vs 2.5bb open: All-in 40 | 0.00% | 0.59% |

## Fresh postflop references

All 150 solves passed the CPU and GPU 0.1%-pot checks; maxima were 0.09959% and 0.09965%.
The same 50 stratified boards were solved in three contexts using the corrected
policy's final reaching ranges. All comparisons below hold those new ranges fixed.
They do not measure the full-game EV improvement of one policy over another.

| Context | Previous model MAE | Shallow MAE | Reduction | Qualified pair mass |
|---|---:|---:|---:|---:|
| call | 0.222bb | 0.222bb | 0.0% | 100.000% |
| threebet-call | 0.886bb | 0.886bb | 0.0% | 100.000% |
| fourbet-call | 4.280bb | 2.622bb | 38.7% | 100.000% |

MAE is legal-pair-weighted mean absolute hand-value error across both players,
using an equity control variate. The direct estimates and paired, stratified
5000-resample intervals are retained in evaluation.json. Unsettled individual
hands remain excluded even when the whole-node solve passes.

## Does the gain reach the preflop decision?

| Comparison | Estimator | Previous model error | Shallow error | Qualified classes / mass |
|---|---|---:|---:|---:|
| call_vs_fold | direct | 0.2888bb | 0.2888bb | 107 / 50.8% |
| call_vs_fold | corrected | 0.2024bb | 0.2024bb | 107 / 50.8% |
| call_vs_raise | direct | 0.2140bb | 0.2199bb | 41 / 25.8% |
| call_vs_raise | corrected | 0.2133bb | 0.2053bb | 41 / 25.8% |

These action comparisons keep later preflop choices fixed. The call-versus-raise
screen requires support for both actions; unsupported hands are not evidence of
agreement. All-in leaves retain cached equities. Full postflop menus and folded-card
effects remain outside this test.

## Cost and decision

Median 1000-iteration time after warmup: baseline 1.874s; shallow 2.141s (14.2% slower).
Three alternating-order pairs isolate learning time from setup. This measures
the 40-node fixture only, not the large multiway trees in the live app.

Predeclared accuracy feedback screen: FAIL.

- shallow_corrected_improvement: pass
- shallow_qualified_mass: pass
- shallow_direct_nonregression: pass
- call_vs_fold_direct_nonregression: pass
- call_vs_fold_corrected_nonregression: pass
- call_vs_raise_direct_nonregression: fail
- call_vs_raise_corrected_nonregression: pass

Integration is deliberately not deployed. The shallow model was trained only at
SPR 0.2 and 0.75; this game tests one shallow SPR (17.5/45). Below 0.2 its residual
scales to zero, and from 0.75 to 1 it blends into the old model. Those transitions
are numerically verified assumptions, not new accuracy evidence.

See CONCLUSIONS.md for the interpretation and next recommendation, PROTOCOL.md for
the predeclared screen, implementation-freeze.json and manifest.json for input hashes,
and evaluation.json for all 169 hand classes.
