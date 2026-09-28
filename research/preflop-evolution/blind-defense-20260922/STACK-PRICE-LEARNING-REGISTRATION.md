# Frozen execution choices for the first exact-target learning comparison

This implements STACK-PRICE-LEARNING-PLAN.md without changing the qualified
reference. It remains a restricted river decision diagnostic, not a preflop solve.

Board seed 9296500 selects 40 distinct full-board suit-isomorphism groups,
excluding all twelve oracle-qualification groups. In draw order, 24 boards are
fitting, eight validation and eight final test. Preserve turn/river order in
visible inputs; the broader full-board grouping only makes split separation
more conservative. Every physical hero holding retains equal weight.

Fit seeds 9296401 and 9296402 each compare 302 and 362 inputs. Run seed 1 as
302 then 362 and seed 2 as 362 then 302. Each player uses the established seeded
269-input initial network expanded by zero columns to 302 or 362, with actor
seed offset 1000. Thus the two representations start from the same function.
CPU initialization must agree to 1e-7 absolute on qualified feature examples.

Adam uses learning rate 0.001, default betas/epsilon, no weight decay,
foreach=False; float32 fitting/inference, deterministic Torch, TF32 disabled.
Two heads evaluate each batch and the actor selects its head; no target is an
input. A separate CUDA generator seeded fit_seed+100000 draws identical batches
for both widths. Contexts are uniform; state indices use floor(U*N) with CUDA
float64 U in [0,1); boards/physical holdings are uniform integer draws.

Each fit receives 8192 optimizer updates of 4096 rows, with mean squared error
over the two legal outputs. Fold target is zero; call target is the exact
call-minus-fold value divided by starting stack. Illegal outputs do not affect
loss or policy. Model inference uses float32 scores widened to float64 for the
positive-score regret matching calculation. This diagnostic precision is not a
claim of bit-identical inference in the existing float64 strategy-bank code.

Validation at 0,1024,4096,8192 evaluates the full Cartesian product of validation
boards, physical hero holdings and eligible public states at each fitting depth.
Select the lowest context-balanced mean regret divided by starting stack; ties
choose the earliest step. Write all four selected checkpoint identities to an
immutable selection record before preparing test-board labels or held-out-depth
strategic labels. Then evaluate all selected models once on eight final-test
boards at fitting depths and at 60/150 bb. Validate held-out terminal cash flows
before scoring; this occurs only after candidate selection is frozen.

Primary diagnostic gate: for both seeds, the 362-input model must select a
noninitial checkpoint, reduce the held-out-depth context-balanced mean normalized
regret by at least 20% compared with the 302-input baseline, and keep mean regret
at each held-out depth <=0.001 of starting stack. A zero baseline cannot establish
a relative improvement. Results are exact for this finite test grid; they are
not population confidence intervals or full-game exploitability.

Report each depth, seat, price band [0,.1,.2,.3,.4,.5,1.01], and made-hand category.
Report mean,95th,99th and maximum regret in bb, normalized means, legal-output
value MSE, constant fold/call regrets, and majority-action errors outside
|call-minus-fold| <=0.0001*starting_stack. Indifference ties prefer fold in the
analytic oracle; either action has zero regret there. The majority-error metric
does not replace regret of the actual mixed policy.

Execution cap is 3600 seconds including admission, preparation, all fits and
final scoring. New evidence cap512 MB plus128 MB reserve; global allocation800 GB,
S: free>=40 GB, RAM admission28 GB/during24 GB, combined research CUDA<=4 GB plus
2 GB external headroom. Eight hidden CPU workers maximum for board preparation.
Light desktop GPU sharing allowed; production/heavier work has priority. An
interruption preserves artifacts and reports incomplete; no automatic extension
or test-driven rerun. No production/session modification, push or deployment.
