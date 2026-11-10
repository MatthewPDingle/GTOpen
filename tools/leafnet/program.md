# Leaf-net autoresearch: rules for the agent

You are improving GTOpen's leaf-value net: a small MLP that corrects the
Preflop Lab's "balanced" realization model at heads-up flop leaves. The plan
it serves is the agreed leaf net plan
(https://claude.ai/artifact/FqjQDLENZ5cTvkoNteJant). Setup and commands are in [README.md](README.md).

## What you may change

- **Only `tools/leafnet/train.py`.** Never edit `prepare.py`, `harness.py`,
  `referee.py`, `flops.py`, `sweep.py`, this file, the data, or anything
  under WORK. (train.py may define its own variants of what flops.py has.) The harness is
  the referee: if you think it is wrong, stop and say so instead of
  working around it.
- `train.py` may change anything inside it: the architecture, the loss,
  the optimizer, the schedule, the batch size, regularization, input
  handling inside the model, ensembling, distillation.
- **Shared side data goes in `prepare(cfg, data)`.** If the recipe needs
  something every run shares and that takes longer than a run may (a bank
  of teachers), build and cache it in `train.py`'s `prepare()`. The harness
  calls it before a run's clock starts, and `train.py --prepare` runs it
  alone. It must do nothing when the cache is complete, give each cached
  piece its own fixed seed (never the run's), name its cache files by every
  setting that changes them, and read only training and validation data.
  A change that needs a new bank costs GPU time next to the generator: say
  so in the run's `--desc`, and keep one preparation under about an hour.
- **Stay deployable.** `run()` must return a `torch.nn.Sequential` of
  `Linear` and `ReLU` layers (Dropout and Identity are ignored). Fold
  anything else into Linear layers before returning: batch norm folds into
  the neighbouring Linear layer, and averaged ensembles become one wider
  block-diagonal stack. The model must cost at most 4x leaf net v1's
  multiply-adds per leaf (the harness enforces both, and checks that the
  Rust loader reproduces the outputs).
- **Accuracy comes before speed.** A bigger net inside the limit is fine
  when it passes the keep rule; don't shrink a net to save solve time.
  When a kept net is larger than the best it replaces, say so in the
  `--desc` and give the error of the best net at the old size next to it,
  so the cost of the extra accuracy stays visible.
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
4. Read the last line: `VERDICT: keep`, `near`, `discard` or `rejected`.
   - **keep**: `git commit -m "leafnet: <desc> (val class X, gain Y)" -- tools/leafnet/train.py`,
     then train the same train.py with `--seed 1 --replicate RUN` and
     `--seed 2 --replicate RUN` (RUN = the kept run's id), so the new best
     has three seeds for later confirmations.
   - **near**: a small gain that passed everything but the seed spread. Don't
     throw it away: train `--seed 1 --replicate RUN` and
     `--seed 2 --replicate RUN`, then
     `python tools/leafnet/harness.py confirm RUN RUN_S1 RUN_S2`. It compares
     the seed averages with the best's seeds, with the spread threshold
     shrunk for the averaging. On `VERDICT: keep`, commit as above; on
     `discard`, check out train.py.
   - **discard** or **rejected**: `git checkout -- tools/leafnet/train.py`.
     The run stays in results.tsv, so nobody tries it again blindly.
5. Repeat. Every ~10 runs, write two lines in `WORK/notes.md`: what has
   worked, what hasn't, and what to try next.

## The keep rule (enforced by the harness, never bypass it)

A run is kept only if all of these hold:

- it exports and passes the Rust parity check, within the cost limit;
- the paired bootstrap over validation jobs puts its class-error gain over
  the current best above zero (95% interval). The score is `val_cv` when
  the snapshot has a referee (validation targets with the flop luck taken
  out, so small real gains are visible), else raw validation; the log line
  and the reason say which (`[val_cv]`);
- the gain is larger than the measured seed spread (`harness.py noise`),
  or, for a near miss confirmed on three seeds, larger than the spread
  scaled for seed averages (`harness.py confirm`);
- its range error is not significantly worse;
- it is not significantly worse on any real-leaf set (the leaves real
  Preflop Lab solutions reach), nor, when the score is val_cv, on raw
  validation.

Never look at the test split. `harness.py final` is for milestones and is
run by a person.

`harness.py ensemble` is also run by a person, after a loop: it averages
the best's seed copies into one net file for the Preflop Lab. An ensemble
is how the best recipe is deployed, never a candidate: keep comparing
single nets, and don't try to pass an averaged model through the keep rule.

## Good habits

- One change per run, so the result says what helped.
- A single run's gain smaller than the seed spread may be noise. A gain that
  holds on every seed is not: that's what `near` and `confirm` are for.
- If something wins by a lot, rerun it with `--seed 1` and `--seed 2`
  before building on it.
- When the snapshot changes (a new data milestone), the first runs re-train
  the previous round's top configurations: rankings at small data don't
  always survive more data.
- Don't spend runs on cosmetic changes, logging or refactoring.
