# Leaf-net autoresearch: rules for the agent

You are improving GTOpen's leaf-value net: a small MLP that corrects the
Preflop Lab's "balanced" realization model at heads-up flop leaves. The plan
it serves is the agreed leaf net plan
(https://claude.ai/artifact/FqjQDLENZ5cTvkoNteJant). Setup and commands are in [README.md](README.md).

## What you may change

- **Only `tools/leafnet/train.py`.** Never edit `prepare.py`, `harness.py`,
  `sweep.py`, this file, the data, or anything under WORK. The harness is
  the referee: if you think it is wrong, stop and say so instead of
  working around it.
- `train.py` may change anything inside it: the architecture, the loss,
  the optimizer, the schedule, the batch size, regularization, input
  handling inside the model, ensembling, distillation.
- **Stay deployable.** `run()` must return a `torch.nn.Sequential` of
  `Linear` and `ReLU` layers (Dropout and Identity are ignored). Fold
  anything else into Linear layers before returning: batch norm folds into
  the neighbouring Linear layer, and averaged ensembles become one wider
  block-diagonal stack. The model must cost at most 2x leaf net v1's
  multiply-adds per leaf (the harness enforces both, and checks that the
  Rust loader reproduces the outputs).
- New input features or layer types the Rust loader can't run are out of
  scope for the loop. Write them up as a proposal instead (they need
  leafnet.rs and leafnet_io.py changes with a parity test first).

## The loop

1. Read `results.tsv` (in WORK) and `git log -- tools/leafnet/train.py` to
   see what has been tried on this snapshot.
2. Pick ONE idea. Prefer structural ideas: loss, normalization, optimizer,
   output structure, architecture shape. Numeric tuning (learning rate,
   width, weight decay) is the sweep's job: run
   `python tools/leafnet/sweep.py --trials 20` after a structural change,
   copy the winning values into CONFIG, and continue.
3. Edit `train.py`, then run
   `python tools/leafnet/train.py --desc "<one line: what changed>"`.
   Every run gets the same fixed step budget and wall-clock cap from the
   harness. Respect `budget.done(step)`.
4. Read the last line: `VERDICT: keep`, `discard` or `rejected`.
   - **keep**: `git commit -m "leafnet: <desc> (val class X, gain Y)" -- tools/leafnet/train.py`.
   - **discard** or **rejected**: `git checkout -- tools/leafnet/train.py`.
     The run stays in results.tsv, so nobody tries it again blindly.
5. Repeat. Every ~10 runs, write two lines in `WORK/notes.md`: what has
   worked, what hasn't, and what to try next.

## The keep rule (enforced by the harness, never bypass it)

A run is kept only if all of these hold:

- it exports and passes the Rust parity check, within the cost limit;
- the paired bootstrap over validation jobs puts its class-error gain over
  the current best above zero (95% interval);
- the gain is larger than the measured seed spread (`harness.py noise`);
- its range error is not significantly worse;
- it is not significantly worse on any real-leaf set (the leaves real
  Preflop Lab solutions reach).

Never look at the test split. `harness.py final` is for milestones and is
run by a person.

## Good habits

- One change per run, so the result says what helped.
- A gain smaller than the seed spread is noise, however good it looks.
- If something wins by a lot, rerun it with `--seed 1` and `--seed 2`
  before building on it.
- When the snapshot changes (a new data milestone), the first runs re-train
  the previous round's top configurations: rankings at small data don't
  always survive more data.
- Don't spend runs on cosmetic changes, logging or refactoring.
