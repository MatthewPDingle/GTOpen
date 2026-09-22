# Visible hand and board summaries: preparation, not an accuracy result

The next proposed representation experiment gives the postflop network explicit
summaries of information already visible to the player. It does not add the
opponent's cards, unrevealed board cards, equity labels, Wizard probabilities,
or hand-specific calling rules. This work does not change production or the
UTG/LJ range preview.

## Why test this

The prior dense exact-all-in model's remaining retained-target fitting error was
concentrated after the flop, especially on the turn and river. Most later-street
observations were unique, so noisy sampled targets remain a plausible cause;
that diagnosis does not establish that the representation is the sole problem.
The hypothesis is that visible summaries make useful postflop relationships
easier to learn across hands and boards, improving continuation values and
eventually preflop choices. Better training loss alone will not qualify it.

## The proposed change

Append the already controlled 33 visible poker summaries to the original 269
one-hot inputs. All appended inputs are zero preflop. Hidden layers, outputs,
loss, optimizer and direct preflop tables retain their meanings. The added input
weights start at zero, while the original weights reproduce the same seeded
initial network. There are 23,812 parameters per player instead of 21,700. This
is a representation-plus-capacity intervention, not proof that poker summaries
outperform any other equally large representation.

Format-3 visible-feature models and checkpoints identify the exact feature
order and width. Old 269-input readers reject them; the new reader rejects old
models. The original reservoir observations remain 269-input records, and the
summaries are derived when preparing the fitting or inference tensors. Exact
preflop table lookup retains the original visible-key geometry.

Average-policy evaluation overrides preflop network predictions with supported
table rows *before* multiplying the player's previous action probabilities.
It retains the complete played model bank in generation order. The final unused
trained model is excluded, as in the existing experiments. Stored float32
weights and prepared float32 features are exactly widened for float64 reference
evaluation; this does not retrain or smooth their policies.

## Completed controls

- `sampled-visible-hybrid-checkpoint-control-v1`: exact save/restore and continued
  checkpoint hashes, reservoir arrays and random-generator states; preserved
  preflop tables; 7,277 inference observations; 12 invalid-format/context/state
  cases rejected. The fixture's appended weights were zero, so this check alone
  does not establish that new columns affect inference.
- `sampled-visible-hybrid-fit-control-v1`: raw-visit versus grouped objective
  gradients and an independent full-tensor Adam reference agree within numerical
  tolerances; repeated fits are identical, and new input weights change.
  These are two **capacity-64** old fixture reservoirs containing 64 BB visits
  and 44 BTN visits. The registration's shorthand "two 64-visit" wording should
  be read as capacity, not as their actual retained counts. This is eight fitting
  steps for a numerical control, not a candidate poker training run. The fixture
  has zero within-observation target variance, so that case is not exercised.
- `sampled-visible-hybrid-bank-control-v1`: 7,277 old observations, three frozen
  synthetic generations, and two sets of per-player model weights. Independent
  Torch double forward/scalar history accumulation agrees with the NumPy bank
  to less than 1.7e-14 in both policy and reach. Nonzero added weights have a
  measurable effect; naive unweighted averaging differs, confirming this is not
  a vacuous test. Eighteen supported preflop rows across the synthetic bank are
  overridden. Hidden batch labels have no effect; nine invalid cases reject.

- `sampled-visible-hybrid-fit-cpu-control-v1`: a follow-up deliberately adds
  noisy duplicate targets to the old observations, producing 128 BB and 88 BTN
  visits with positive within-observation variance. The grouped gradient agrees
  with the raw-visit reference to 1.2e-7; the optimizer reference agrees to
  3.0e-8. Repeated fits are identical. These are synthetic numerical fixtures,
  not additional poker evidence. The corresponding CUDA control has now passed.

## GPU and integration checks completed

The full combined 269-input study finished all its registered evaluations and
independent reviews before these GPU checks began. Its findings are recorded in
`SAMPLED-PHYSICAL-HYBRID-ALLIN-FINDINGS.md`.

- `sampled-visible-hybrid-gpu-bank-control-v2`: CPU/CUDA bank inference agreed
  across 7,277 observations, model chunks of 1/2/3, and equal/unequal weights.
  Maximum policy error was 9.55e-15 and reach error 3.74e-14. Version 1 stopped
  because the deterministic cuBLAS workspace setting was missing. The failed
  source and registration remain preserved; version 2 fixes that launch setting.
- `sampled-visible-hybrid-fit-cuda-control-v1`: noisy duplicate-target controls
  passed independent objective, gradient and full-tensor optimizer comparisons.
  Maximum optimizer discrepancy was 1.35e-7; repeated fits were identical.
  Synthetic targets are numerical tests, not poker evidence.
- `sampled-visible-hybrid-allin-control-v1`: all four fixed training updates
  completed in 195.86 seconds. Independent replay verified 2,048 deals and 4,096
  native traversals, reservoir contents/random states, model progression, and
  reconstructed preflop tables. The first update matched the original 269-input
  control's uniform trajectories and targets. This is an integration test, not
  a trained candidate qualified for strategic use.

The first saved-policy replay control stopped because training queries do not
contain the own-action histories required by the averaged-policy reader. Its
failed registration and source remain preserved. Version 2 retains exact replay
of every saved single-model training policy, and separately compares the four
trained models' complete CPU/CUDA bank on an existing history-bearing fixture.
It does not invent histories or draw additional deals.

Version 2 passed: all 929,214 saved policy rows reproduced exactly. The complete
four-model CPU/CUDA bank agreed on 7,277 history-bearing observations, with
maximum policy error 2.29e-14 and reach error 2.00e-14. It took 141.13 seconds.
All short numerical and integration gates are now complete; these checks do
not establish strategic improvement.

## Remaining admission gates

1. Freeze a full candidate budget, training settings, fresh evaluation seeds,
   complete-bank evaluation and acceptance criteria before training. Compare
   against the combined 269-input model. Keep payoff-estimator changes separate.
2. Evaluate on untouched deals and report uncertainty and hand-level behavior.
   Better training loss or resemblance to Wizard alone cannot qualify the model.

No full visible-feature candidate or new strategic evaluation stream has been
launched. Production and the UTG/LJ preview remain unchanged.
