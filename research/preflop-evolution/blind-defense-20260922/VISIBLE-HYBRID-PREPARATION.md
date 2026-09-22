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
  not additional poker evidence. CUDA mode is prepared but has not run.

All four are CPU correctness controls. They do not establish CUDA training
equivalence, strategic improvement, or suitability for deployment.

## Remaining admission gates

1. Let the registered combined direct-preflop/exact-all-in study finish its
   training and evaluations. Do not compete with its GPU or alter its sources.
2. Run the prepared `hu_visible_hybrid_gpu_bank_control_20260923.py --run` after
   the exclusive research lock is free. It compares CPU/CUDA bank inference on
   these frozen old observations, using chunks of one, two and three models.
   The CUDA implementation is prepared but has not passed this gate yet.
3. The separate native-traversal training controller and replay reviewer are now
   prepared under `VISIBLE-HYBRID-INTEGRATION-PLAN.md`. Complete their short CUDA integration run,
   including sampler/action/reservoir replay, reconstructed preflop tables,
   native cashflow checks, and saved-model inference checks. Check CUDA fitting
   against an independent objective/gradient reference on fixed old records.
4. Freeze the candidate budget, unchanged training streams/settings, fresh
   response-training/test seeds, full-bank evaluation, and acceptance criteria
   before launching a full candidate. Use the combined 269-input model as the
   immediate comparison. Keep payoff-estimator changes in a separate experiment.
5. Evaluate frozen policies on untouched deals and report uncertainty and
   hand-level errors. Do not select a generation, fit to inspected test hands,
   or treat resemblance to Wizard as sufficient evidence.

No full visible-feature candidate, new evaluation stream, or deployment has
been launched by this preparation work. The active combined experiment retains
its existing representation and protocol.
