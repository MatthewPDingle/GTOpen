# Stack and price learning: first comparison failed the accuracy gate

The registered experiment completed, but the learned policies are not accurate
enough. Explicit public economics help in some comparisons; they do not by
themselves make the current small network generalize reliably to new boards and
depths. Do not promote these diagnostic models or start broad stack self-play
on the strength of this result.

## What ran

`stack_price_learning_run_v2.py` completed in 490.547 seconds. Each of four fits
used 8,192 Adam updates of 4,096 rows, with equal budgets and paired initialization
and batch seeds. The two representations have 302 visible-card/history inputs
and 362 inputs including the 60 explicit public economics features. Each has two
64/64-hidden-layer player heads. All four selected their 8,192-update checkpoint
using validation data; selection was frozen before final-test labels were built.

The source has 24 fitting, eight validation and eight test boards, all distinct
under the registered full-board suit grouping, excluding reference probes.
All 1,081 physical hero holdings remain equally weighted on each board. Fitting
uses 476 native terminal river fold/call states at 20/40/100/200/400 bb. Test adds
60/150 bb, which were excluded from fitting and model selection. Opponent holdings
are uniform among legal cards. This is a conditional decision diagnostic, not
the betting-induced opponent range or a full-game equilibrium.

The first implementation, v1, failed before board preparation or training because
it called NumPy's integer maximum property as a function. Its source, registration,
admission and interruption are preserved. The separately registered v2 changed
that call to a property access, with the same scientific choices and budgets.

## Decision quality

The primary mean below gives equal weight to the two unseen depths, after
normalizing each depth's regret by starting stack. Regret is the value lost by
the actual mixed policy compared with the exact better legal action.

| Initialization seed | 302 inputs | 362 inputs | Relative reduction | Registered gate |
| --- | ---: | ---: | ---: | --- |
| 9296401 | 3.5416% of stack | 3.3562% | 5.23% | Fail |
| 9296402 | 3.6139% of stack | 2.4134% | 33.22% | Fail |

The gate required at least 20% improvement in both seeds and mean regret no
greater than 0.1% of stack at each unseen depth. Both miss the absolute target;
seed 1 also misses the relative target.

| Seed | Depth | 302 mean loss (bb) | 362 mean loss (bb) | Target (bb) |
| --- | ---: | ---: | ---: | ---: |
| 9296401 | 60 | 2.43977 | 1.86617 | 0.060 |
| 9296401 | 150 | 4.52544 | 5.40327 | 0.150 |
| 9296402 | 60 | 2.45773 | 1.27484 | 0.060 |
| 9296402 | 150 | 4.69742 | 4.05318 | 0.150 |

Seed 1 gets worse at 150 bb, despite its average improvement. On the eight new
boards at the fitting depths, seed 1's 362-input model is also worse than its
302-input baseline at every depth. Seed 2 improves at each of those depths.
The richer input is useful information, not yet a reliable accuracy improvement.

There are substantial tail errors. At 150 bb, 362-input 99th-percentile regret
is 76.20 bb (seed 1) and 64.13 bb (seed 2). The finite test's errors are concentrated
in pair and two-pair categories, with much smaller mean losses for most stronger
made hands. Full seat, price, hand-category and quantile breakdowns are retained
in the result. These are exact finite-grid comparisons, not confidence intervals
for all river boards. They do not measure preflop exploitability.

## Integrity and resources

The factorized adapter matched all 952 retained native observations exactly,
including visible features and active one-hot fields, without fabricating own
histories. Independent CPU matrix inference replayed all 23,245,824 final-test
rows across the four models and seven depths. It verified 270 files and the
frozen selection, and reproduced both gate failures. The largest difference
between CPU and CUDA context mean regret was 4.94e-7 bb.

The four fits, including validation and checkpoint saves, took 68.27, 63.55,
64.55 and 64.44 seconds. Peak CUDA allocation was 175.26 MB, with 216.01 MB
reserved. Completed study data uses 4.36 MB logical / 3.99 MB allocated across
110 files. Factoring cards and public states avoided large duplicated feature
tables. Owned worker jobs ended with no active descendants; no production
session was modified. Light desktop GPU sharing remains enabled, while active
production solves and heavier work retain priority.

## Evidence

- Registration: `stack-price-learning-v2-registration.json`, SHA256
  `f4b0f0a3a6f6b530a43eb5ee4aa812776698e9caa6d5c0c96fa7f33a0e61acd9`.
- Main result: `stack-price-learning-v2-result.json`, SHA256
  `fc416fc7ea01e0ad96e1a87a2544e30e859cf4b3b53507ea1091c9578daf8a99`.
- Independent readback: `stack-price-learning-v2-readback-v1.json`, SHA256
  `7a4bf8fd5000d3c2f057afcb174c68dbd1766d3ae26eee90a0190c7874d58775`.
- Weights, board/count factors, selection and admission:
  `S:/GTOpen-research/stack-price-learning-v2`.

The next analysis separates training fit from unseen-board errors and compares
three ways to turn the same frozen predictions into actions. It uses only the
existing fitting/validation boards and fitting depths. It is exploratory error
diagnosis; it cannot rescue the failed registered result or turn the already
viewed test into a fresh holdout.

## Completed error diagnosis

`stack_price_learning_diagnosis_v1.py` completed in 216.859 seconds, with no
training or new boards. It used the frozen checkpoints at fitting depths only,
separately on all fitting and validation boards. It did not use test-board data
or held-out-depth labels. The original validation means replayed to 1.68e-8 bb.

| Seed / representation | Fitting regret, % of stack | Validation regret, % of stack |
| --- | ---: | ---: |
| 9296401 / 302 | 0.41789% | 2.57159% |
| 9296401 / 362 | 0.01232% | 2.26062% |
| 9296402 / 302 | 0.39328% | 2.43770% |
| 9296402 / 362 | 0.03653% | 2.12507% |

The richer input lets the model fit its training boards much better. However,
new-board decision loss remains about two percent of stack. Choosing the larger
predicted legal value instead of mixing lowers the two 362-input validation
figures only to 2.25557% and 2.10729%. Fixing the analytically known fold value at
zero gives similarly small changes (2.25446% and 2.10776%). The main validation
failure is therefore not the output-to-action conversion.

This isolates generalization across boards as the immediate learning bottleneck;
it does not prove that simply collecting more boards will solve it. The next
bounded experiment should compare a nested 24-board fitting set with broader
coverage, preserving architecture, optimizer and update count, and using fresh
validation/test boards. Do not extend training on the failed experiment or tune
against its already viewed final test.

Diagnosis registration SHA256:
`61adb3f3bf0d676b53a271ba3f61aaa4b86180e92b095cb36102f77429bfe21b`.
The result and per-board/context decomposition are in
`stack-price-learning-diagnosis-v1-result.json` and
`S:/GTOpen-research/stack-price-learning-diagnosis-v1`. New allocated evidence is
0.213 MB; peak CUDA allocation 167.93 MB. The registered negative result remains
unchanged. There is no production-ready model yet.
