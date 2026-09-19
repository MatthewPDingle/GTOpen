# Per-hand convergence refinement

Same ranges, boards, rake and action menus as the registered first pass. Select
every first-pass job where any of the eight OOP probe hands has a conditional
best-response gain above the preregistered 0.05bb threshold. Selection is by
numerical convergence only, not by disagreement with Balanced or Wizard.

Rerun selected jobs with a separate executable and separate output directory.
Require the original 0.05%-pot GPU and transported CPU global targets AND the
0.05bb per-probe gain threshold. Cap each at 5000 iterations. Preserve failures
and stop for review rather than silently accepting their values. Reuse passing
original jobs in the final fixed 40-board paired-menu panel.

This is an additional convergence diagnostic, not a guarantee of accurate
counterfactual hand values. Low-weight hands also require range-floor sensitivity
if their estimates materially affect the conclusions. Original data remain intact.
