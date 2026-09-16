# N06b: repeat fixed nonlinear choices with expanded training coverage

Specified 16 September before N03 training completes. N06's best mean result
missed the worst-family gate. Test the data-coverage hypothesis with the exact
same four network choices, two seeds, 500-step CPU-only fit and projection.
Do not expand the hyperparameter grid or weaken the thresholds.

Fit on the original 24 training cases, two N01 development cases and 36 N03
range bridges (62 total). Validate on the unchanged original 26 cases only.
For each family fold, remove every related case, including synthetic bridges.
Record a same-62-data ordinary shape/0.1 ridge control. Compare against both
that control and N06's original-26-data ridge control.

An eligible nonlinear model must improve equal-family mean error by at least
5% versus each control, and worsen no family by more than 5% versus either
control. Select the lowest mean among eligible models. Freeze the selected
62-case model and all hashes; otherwise record rejection and stop this path.

N03 evaluation may run independently during this CPU screen. No evaluation
labels are read or used here. Any selected model requires its own separately
specified fresh-board evaluation after its freeze, disjoint from all N03 and
earlier evaluation boards. Do not reuse N03 reserved evaluation outcomes to
select or qualify this candidate. Independent GPU correctness and <=10%
matched runtime overhead checks remain required before considering deployment.

Run `tools/research/continuation_nonlinear_expanded.py` only after all 720 N03
training references are complete and pass manifest/numerical checks. Previous
N06 scripts and artifacts stay immutable.
