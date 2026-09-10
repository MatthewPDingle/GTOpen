# Initial64 quality results and frozen32-v2 follow-up

Sources: `raw/ensemble-audit-b.log`, `independent64-a.log`, `independent64-physical-a.log`, `small-reference-development-a.log`, `small-preview-development-a.log`, and `quality-development-002/010/020-a.log`. Parent executed these; this review ran no benchmarks. Registered thresholds are unchanged.

## 64 terminal results

All24 independent physical references completed100,000 accepted compatible deals per hand.

| Independent case |64 physical MAE / worst (pp) | Full1024 MAE / worst (pp) |
|---|---:|---:|
| Asymmetric3 |1.368 /3.444|1.120 /1.684|
| Mixed4 |1.363 /3.498|1.018 /2.441|
| Sparse6 |1.537 /1.928|1.216 /2.340|
| Overlap asymmetric4 (stress) |2.423 /5.025|1.246 /3.871|

The three independent core cases remain comfortably inside the stated core error bounds. The new overlap stress increases mean error by1.1775pp and worst error by1.1537pp relative to full1024. Applying the same conservative overlap guard gives a nominal mean miss of0.1775pp over the+1pp allowance; this is within the registered uncertainty band (per-hand95% half-widths up to0.293pp). Mark it borderline/inconclusive, not a complete physical-validation pass. The registered historical premium-only stress itself passed its relative gates. This distinction must not be averaged away.

Rebuilt BB regression for64: mean1.2509pp, worst1.8779pp, passing the existing BB limits. KQo equity24.7066% versus physical23.3060%; call-minus-fold showdown surplus+0.87770bb versus+0.77126bb. Original BB also passed in the preceding seen audit. These retain the cheap-call correction.

Repeated CPU terminal timing in the physical-run log: full0.70627ms versus64 ensemble0.08705ms, **8.11x terminal-only** on that one range context. This is not a whole-solver speedup or a10x accepted-preview result.

## Small development tree: global pass does not erase local failures

The registered three-seat tree has70 nodes. Both models reached their own0.005 gap threshold at iteration20; reference gap0.00145374, preview own-model gap0.00176172. Recorded elapsed time is0.08342s reference versus0.03640s preview (2.29x), including driver initialization/checkpoint capture. Initialization dominates this tiny fixture. Do not extrapolate this ratio to large games.

| Preview iteration | Excess full-reference learning gap | Mean / max unilateral positive loss (bb) | Global gates |
|---:|---:|---:|---|
|2|0.4568566|0.1309950 /0.2326598|Fail|
|10|0.0107335|0.0033383 /0.0063268|Pass|
|20|0.0018681|0.0005220 /0.0008937|Pass|

At20, BTN root and BB path[2,1] pass the selected local tail gate; SB[1] and SB[2] fail. The small global gap does not certify all conditional choices.

- **SB[1]**, after BTN limps: joint reach0.000208676 (about0.0209%). Candidate conditional mean action loss0.052351bb is below the reference's0.056258bb. The full reference also leaves poor local choices in a very rare branch. This explains the weak oracle there without converting the candidate's48.64% worst bad-action mass into a pass.
- **SB[2]**, after BTN raises2: joint reach0.0153455 (about1.53%). Candidate mean local loss0.007507bb versus reference0.004397bb. For **Q2o**, call Q=-0.384848bb versus fold Q=-0.500000bb, so fold loses0.115152bb. Candidate folds65.08%; the reference expected loss implies only about0.0174% fold in this two-action node. Q2s folds26.97% despite a0.269169bb reference call advantage. These are candidate-specific tail failures, not merely reference weak play or harmless near ties.

The safe interpretation is **global policy gates passed, selected local gates failed**. Keep the local flags. Supplemental longer fixed-iteration trajectories can separate incomplete learning from persistent payoff approximation error. Any node-specific refinement is a separately measured behavior, not justification to waive these gates. Future output now includes explicit hand labels/reference probabilities for easier inspection.

## 32-v2 is frozen before its independent results

`coupled_subset_exchange_v2_32` uses training-only coordinate exchange. Seen results: core MAE2.0072pp, worst6.4223pp, maximum case mean2.4821pp; original BB mean2.5229pp/worst4.3175pp. Premium-only mean5.8855pp/worst14.4144pp improves on the full reference's physical errors. It nominally passes these seen gates. Rebuilt BB and independent32 results remain pending at freeze.

Exact indices and the `ensemble-audit-b.log` SHA are in `frozen-exchange32-v2.json`. The independent driver now permits only the registered64-v1 or32-v2 IDs, checks expected count/weight and exact index equality against the source audit, and never trains on holdout output. Acceptance still requires subsequent independent and policy-quality results.
