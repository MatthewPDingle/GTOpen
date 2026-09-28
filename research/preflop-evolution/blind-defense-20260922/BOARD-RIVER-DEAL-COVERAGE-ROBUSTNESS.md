# Deal-level robustness of the coverage comparison

This supplemental analysis was registered before final scoring. It changes no
training, data, primary metric or advancement gate. Positive differences favor
broad-exact. The original gates remain: {'coverage': True, 'target': True}.

| Reference arm | Metric | Full evaluation difference | Deals favoring broad-exact | Median deal difference | Leave-one-deal-out difference range |
|---|---|---:|---:|---:|---:|
| dense-exact | mse_bb2 | 436.5837 | 18/32 | 257.7294 | 329.7538 to 540.0649 |
| dense-exact | fold_call_decision_cost_bb | 3.8600 | 20/32 | 2.9025 | 3.2041 to 4.3446 |
| broad-sample16 | mse_bb2 | 152.5986 | 22/32 | 127.1676 | 97.6092 to 185.1011 |
| broad-sample16 | fold_call_decision_cost_bb | 1.2644 | 17/32 | 0.1519 | 0.9239 to 1.3833 |

Each omission removes the physical deal from every bank/actor/repetition and
recomputes each model's mean over remaining states before averaging models.
The range shows sensitivity to single deals. It is not a confidence interval,
significance test or full-game EV result. A fragile result stays fragile even
if the descriptive primary gate passes; a failed gate remains failed.

Equal state counts per deal within every model: True. If false, the
per-deal summaries have different weighting from the primary model/state mean.
All saved predictions and primary metrics were reconciled, maximum discrepancy
1.78e-15. Full per-deal and omission records are in `board-river-deal-coverage-v1-robustness.json`.

Costs are per selected river decision, not bb per dealt hand or demonstrated
preflop-range improvement. No settings were chosen from these diagnostics.
