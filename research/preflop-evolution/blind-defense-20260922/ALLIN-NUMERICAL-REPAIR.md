# Conditional-all-in evaluation: diagnosed precision repair

The original v1 evaluation stopped on its first 16-deal CPU/CUDA control batch.
No responder was selected and no held-out test deals were generated. Preserve
all v1 evidence; this is a separately registered v2 attempt.

Reconstructing all 78 generations reproduces both saved averages exactly. Two
of 7,278 queried rows exceed the unchanged 0.0001 policy tolerance. The largest
difference is 0.00012653795 (0.01265 percentage points), at a river decision.
Small float32 score differences near zero alter positive-score normalization
and are amplified by own-reach weighting. For example generation 69's ancestor
raise score differs by about 1.56e-7, producing different small path weights.
This is distinct from the earlier hybrid candidate's discrete argmax flip.

## Repair and validation

Versioned dense CPU and CUDA evaluators exactly widen the stored float32 weights
to float64 before matrix arithmetic. The complete ordered played bank, legal
masks, regret-matching rule and own-reach average remain unchanged. No weights,
training data, fit settings or stopping rules are changed.

The complete 78-model, 256-existing-deal numerical control passes: maximum policy
difference 1.943e-14 and payoff difference 2.842e-14 bb. A separately reconstructed
scalar float64 reference for the failing row matches within 7.106e-15. The
artifact readback must also pass before the v2 evaluator is admitted.

## Unchanged strategic test

Use checkpoint 1399fcadc1ff016081bc95a668eccd576212865ecde7e019ea8f4aabbf59fd83,
played generations 0 through 77; exclude unused generation 78. Keep response-
training seed 79101 with 8,192 deals, test seed 79102 with 16,384 deals, minimum
16 training examples per class, and 16-deal batches. The original sampled-board
evaluator remains in use. The separate conditional evaluator is not substituted.

Keep five BB comparisons at family alpha .025 and three BTN-versus-jam
comparisons at family alpha .025, with the original response rules and bounds.
Versioned BTN scripts change only source wiring and integrity checks, preserving
the original training registration and original scripts as evidence of the
predeclared test. Registration freezes replacement sources before any new test
outcomes. All original numerical tolerances and resource guards remain.

This repair establishes numerical consistency, not poker strength. No production
or preview deployment, retraining, checkpoint selection, tolerance relaxation or
automatic retry is authorized by this protocol. Stop on any failed stage.
