# Signed board attribution of preflop deviations

Post-hoc diagnostic of the two completed independent95 evaluations. No
additional solves, board selection, acceptance gates or production changes.

Choose one alternative entering action per private combination using values
averaged over the entire 95-board panel. Hold that choice fixed on every
future board, with later preflop and postflop actions unchanged. Decompose its
gain over the original policy into signed board contributions. Keep losing
boards as well as winning boards. These contributions sum to the previously
measured root-only deviation, rather than to board-by-board best responses.

| Source | Root-only gain (bb) | A-high contribution | K-high contribution | Q-high contribution |
|---|---:|---:|---:|---:|
| 10 training flops | 1.788991 | +0.997520 | +0.415237 | +0.466973 |
| 47 training flops | 0.447695 | -0.603203 | -0.437969 | +0.667782 |

These are different deviations against different frozen opponents and
continuations. The columns are neither head-to-head performance differences
nor instructions to choose an action after seeing the flop. Board weights
include the legal private-card distribution; ordinary chance-only averages
would give different answers.

The 47-flop source's net gain contains substantial cancellation across future
boards. The 10-flop source has a different pattern. This helps locate
sensitivity in the finite-panel valuation; it does not demonstrate which
component caused the discrepancy or establish a full-deck error bound.
Matched training-panel reconstruction remains necessary before attributing
the transfer gains solely to board coverage.

Both results independently reconstruct their existing decision diagnostics
within 0.00000001 bb. A synthetic hidden-chance control gives zero legitimate
gain but one unit under a deliberately invalid board-specific choice; the
new diagnostic preserves the positive and negative contributions that cancel.

Evidence: validation95-{ab,report47}-board-attribution.{json,md}. The JSON
retains every board's contribution by hand class, all selected private-combo
actions, panel weights and input hashes. Reproduction:
tools/research/transfer_board_attribution.py, using the shared root traversal
in tools/research/transfer_decision_diagnostics.py.
