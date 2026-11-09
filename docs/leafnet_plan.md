# Leaf-value net: plan

The plan for the Preflop Lab's learned leaf values ("leafnet"): what training data to collect, how to search architectures and hyperparameters as the data grows, and what comes after 300,000 examples. Contributor instructions are in [contribute-compute.md](contribute-compute.md).

Adopted 2026-11-09. Figures marked *measured* come from the maintainer's RTX 5090, the 6-max limp preset solved under `leafnet` (2,000 iterations) and the 57,400 examples of the first checkpoint.

## Status

| step | status |
|---|---|
| 50k go/no-go | **passed** at 57,400 examples: the net removed 10.1% of the pot of balanced's error on held-out jobs |
| Generator v3 (pot-type mix, straddled pots, live rake) | **done** in this change; v2 uploads stay valid |
| Leaf check weights leaves by every seat's reach | next (see "Known issue") |
| Autoresearch harness (GPU) | planned |
| Snapshots at 100k, 150k, 200k, 300k | planned |
| Targeted data from real solutions | after 300k, or when the learning curve flattens |

## Known issue: the leaf check's leaf weights

`solve-cli datagen leaves` picks the leaves that carry the most chips. It weights each heads-up flop leaf by the product of the two **live** players' reach masses, so seats that folded along the way don't count. A line that starts with a limp the solution almost never makes is weighted as if it were common. *Measured* on the 6-max game: the export's ten highest-weighted leaves all have a true line probability that rounds to zero. Of its top 300 leaves, the export puts 86% of the frequency in 4-bet pots; the true figure is 7%.

The fix is to weight leaves by the product of **every** seat's reach mass. Then re-run the leaf check. Leaf checks run before the fix scored the net on ranges real solutions rarely reach.

## Where heads-up flops come from (*measured*, 6-max limp preset)

| how the hand ends | share of hands |
|---|---|
| won preflop (everyone folds) | 67.9% |
| heads-up flop: srp / 3bet / 4bet / limped | 18.0% / 5.6% / 2.8% / 1.3% |
| 3-way flop | 4.3% |
| 4-way flop | 0.1% |

86% of flops are heads-up. Of the heads-up flops:

| pot type | share of HU flops | share of HU flop chips | generator v2 | generator v3 |
|---|---|---|---|---|
| srp | 65.1% | 31.0% | 45% | 58% |
| 3bet | 20.1% | 25.3% | 28% | 15% |
| 4bet | 10.1% | 43.0% | 12% | 10% |
| limped | 4.7% | 0.7% | 15% | 17% |

This preset caps preflop at three raises with no all-in, so every called 4-bet sees a flop. That inflates 4-bet pots compared with real play. Limp-heavy live games see far more limped pots than this preset does.

Cost per pot type (*measured*, 57,400 v2 examples, 67.8 GPU-hours):

| pot type | share of v2 examples | share of solve time | mean solve |
|---|---|---|---|
| limped | 14.9% | 27.4% | 7.84 s |
| srp | 45.2% | 57.3% | 5.39 s |
| 3bet | 27.9% | 13.0% | 1.98 s |
| 4bet | 12.0% | 2.3% | 0.80 s |

3-bet and 4-bet examples are cheap. Moving to the v3 mix costs about 12% more GPU time per example, in exchange for more examples where hands actually go. The mix can be revisited with per-pot-type learning curves: the share of the next phase should go where an extra GPU-hour removes the most held-out error. Training can also reweight examples (by real-game frequency × pot) without regenerating anything.

## Generator v3

- **Pot types:** limped 17%, srp 58%, 3bet 15%, 4bet 10%.
- **Straddles:** 25% of spots come from a 2 bb UTG straddle game, with larger pots per pot type:

  | pot type | pot (no straddle) | pot (straddled) |
  |---|---|---|
  | limped | 2–3.5 bb | 4.5–8 bb |
  | srp | 4.5–7.5 bb | 9–17 bb |
  | 3bet | 15–26 bb | 24–45 bb |
  | 4bet | 38–55 bb | 55–100 bb |

  Examples record `"straddle": true`. Today's net doesn't read that field: it sees pot, stack, rake and the raise-count pot type. A later net can add it as an input, with leafnet.rs and leafnet_io.py changed together under their parity test.
- **Rake:** 30% none, 35% at 5% with a cap of 1–4 bb, and 35% at 10% with a cap of 2–10 bb. The last covers the live presets.
- **Stacks, ranges, flops and menu:** unchanged from v2 (starting stack 25–200 bb log-uniform, SPR at most 40, broad range sampling, frequency-weighted flops, `lean-v2`).
- **Job numbers:** v3 jobs start at `3 << 20` inside each contributor's block, so they never reuse an uploaded v2 job number. The validator accepts v2 and v3 files: `SUPPORTED_GENERATOR_VERSIONS`, and `--generator 2` on `inputs`/`spot`/`sizes` regenerates v2 inputs.

## Autoresearch loop

Karpathy-style: a frozen harness the agent can't edit, one training file it can, a fixed time budget per run, and keep-or-revert on a single metric with every run logged.

**Harness (frozen per data snapshot)**
- A pinned list of job files and their hash.
- Every example priced once with the realization models (balanced, static, calibrated, raw) through solve-cli, and cached with features and targets as arrays. The go/no-go took about 12 hours end to end, mostly that pricing plus a numpy trainer on the CPU; with caching, a trial is pure training.
- A validation set chosen once by job hash and never changed, so scores at 62k, 150k and 300k are comparable. The test jobs stay locked until a milestone.

**On the GPU, alongside datagen** (*measured* on the 5090 while datagen ran; synthetic data of the real shape, 686 inputs and 338 outputs):

| examples | net | batch | s/epoch | validation scoring |
|---|---|---|---|---|
| 300k | 2×512 | 4096 | 0.21 | 0.1 s |
| 300k | 3×1024 | 4096 | 0.31 | <0.01 s |
| 1M | 2×512 | 4096 | 1.60 | <0.01 s |
| 1M | 3×1024 | 4096 | 1.21 | 0.04 s |

Peak VRAM was 0.8 GB at 300k and 2.3 GB at 1M. Datagen draws trees up to 80% of the card, so the loop keeps its data on the GPU in fp16 and stays under about 3 GB. Blackwell cards (sm_120) need a CUDA 12.8+ PyTorch build; older wheels fail with "no kernel image".

**Per experiment (about 10 an hour)**
1. Train within a fixed budget: 5 minutes at 300k, 10–15 minutes at 1M.
2. Score on the validation jobs: milliseconds. The labels are exact solves already in the dataset.
3. Paired bootstrap against the current best over validation jobs. Both nets are scored on the same examples, so the flop-to-flop spread (most of the raw error) cancels. At 57k the 95% interval on the class-error difference was about ±0.00045 with 56 jobs. About 300 validation jobs at 300k should give about ±0.0002, roughly 2% of the net's gain over balanced (0.010).
4. Keep a change only if the interval's lower bound is above zero and the gain exceeds the seed spread (the baseline config trained with 5 seeds). Finalists rerun with 3 seeds.
5. Rescore on the already-solved real leaves (after the leaf-weight fix): seconds.

**Per snapshot** (100k, 150k, 200k, 300k; top 1–2 nets): the end-to-end check. Re-solve the reference preflop games with the candidate net (6-max, 8-max straddled, HU; about 5–10 minutes each), export their leaves, solve them exactly (1–2 GPU-hours), and run the leaf check. This is the only step that takes hours.

**Comparing across data sizes**
- **Usually transfers:** structural choices such as the inputs, predicting the residual over balanced, output structure (per-class shared heads, low-rank outputs), the loss and normalization. Screen these on current data.
- **Doesn't transfer:** capacity and regularization (width, depth, weight decay, dropout, epochs). These are re-tuned at every snapshot with an Optuna sweep.
- **Pick finalists by learning curves:** train on nested 25%, 50% and 100% subsets, fit `error(N) = E∞ + a·N^(-b)`, and compare at the target size. With sub-second epochs this costs minutes.
- **The same curve says whether 300k, or 1M, is worth collecting.** Most raw class error is flop-to-flop spread that a flop-blind model can't remove; the reducible part is about 0.010. When another 100k barely moves validation error relative to its interval, random data has stopped paying.

**What ships without Rust changes.** The Rust loader runs any plain ReLU MLP over the fixed inputs. That covers width, depth and training settings, batch norm folded into the weights, low-rank outputs folded into the last layer, and ensembles written out as one wider block-diagonal MLP. New inputs or per-class shared heads (which also smooth neighbouring hand classes) need leafnet.rs and leafnet_io.py changes first.

**Who drives it.** Optuna does numeric tuning with no LLM cost. An agent (Claude Code or Codex, with a program.md) only proposes structural changes, each followed by a short Optuna sweep.

## Splitting GPU time

- **Data first:** the net is data-limited until the learning curve says otherwise.
- **The loop runs in datagen's idle gaps,** at a cost of at most about 10% of datagen's jobs per hour. Measure it: jobs per hour over two hours with and without the loop.
- **Heavy sweeps and the exact-solve checks only at snapshots.**

## After 300k

1. **Targeted data:** seed jobs from ranges real Preflop Lab solutions reach. Export leaves (fixed weighting) from a set of reference games, perturb those ranges, solve them, retrain, and repeat. The seed ranges go into a pinned, versioned range bank in the repo so jobs stay regenerable (a generator version bump). GTOpen's own solves only.
2. **A straddle input for the net,** trained on the v3 data that records it.
3. **3-way flops:** about 4% of hands in the 6-max preset, more in limp-heavy games. The 3-way postflop solver can produce them.
4. **A bet-menu input,** so values aren't tied to `lean-v2`.

## Data volume and contributors

- GTO Wizard hasn't published its training-set size. DeepStack trained its turn network on about 10 million random situations and its flop network on about 1 million, whose targets came from depth-limited solves plus the turn network ([arXiv 1701.01724](https://arxiv.org/abs/1701.01724)).
- Each GTOpen example is a full exact flop-to-river solve of a smaller target: 169 hand classes, averaged over flops by the Preflop Lab. 300k is a reasonable first goal; the learning curve decides beyond it.
- At about 4.2 GPU-seconds per example on a 5090, 240k more examples is about 280 GPU-hours. Rented GPUs, each under its own contributor login, shorten that in proportion.
