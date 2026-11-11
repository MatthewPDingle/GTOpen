# Leaf-net training harness

Tools for training and searching the Preflop Lab's leaf-value net on the
pooled flop solves (docs/contribute-compute.md), on the GPU, next to the data
generator. The plan behind it is the [leaf net plan](https://claude.ai/artifact/FqjQDLENZ5cTvkoNteJant).

| file | role | who edits it |
|---|---|---|
| `prepare.py` | freezes a data snapshot, prices it once with the realization models, caches prices per job file | frozen |
| `harness.py` | data on the GPU under a VRAM cap, scoring, paired bootstrap, keep rule, export + Rust parity, results.tsv, test-split evaluation | frozen |
| `referee.py` | once per snapshot: a flop-aware referee teacher and validation targets with the flop luck taken out (`val_cv`, the keep rule's low-noise score) | frozen |
| `flops.py` | flop tables, the flop-aware Teacher model, each example's flop (used by referee.py and train.py) | frozen |
| `train.py` | CONFIG + `run()`: the model and how it is trained | the agent / you |
| `sweep.py` | Optuna over train.py's numeric CONFIG | frozen |
| `program.md` | the autoresearch loop's rules | frozen |
| `scaling.py` | net size x data fraction grid and the fitted scaling law (WORK/scaling/) | frozen |
| `report.py` | the loop's progress and the training data as one self-contained HTML page (WORK/dashboard.html); read-only | anyone |

## Setup (once)

PyTorch must support the GPU's architecture. RTX 50-series cards (Blackwell,
sm_120) need a CUDA 12.8 or newer build; older wheels fail with "no kernel
image is available". Keep the environment outside the repo:

```powershell
python -m venv ..\leafnet-venv
..\leafnet-venv\Scripts\python -m pip install torch --index-url https://download.pytorch.org/whl/cu128
..\leafnet-venv\Scripts\python -m pip install numpy optuna huggingface_hub
```

Build solve-cli from this checkout (the harness prices examples and checks
exports with it):

```powershell
cargo build --release -p solver --features gpu --bin solve-cli
```

Data, prices, snapshots and runs go to `$LEAFNET_WORK` (default:
`leafnet_work/` in the repo, gitignored). Nothing there is committed.

## Use

```powershell
$env:LEAFNET_WORK = "..\leafnet-work"
$py = "..\leafnet-venv\Scripts\python.exe"
& $py tools\leafnet\prepare.py                                   # download/refresh the dataset, freeze a snapshot
& $py tools\leafnet\prepare.py --attach --name SNAP --leafcheck datagen_leafcheck_v2   # add a real-leaf test set
& $py tools\leafnet\referee.py                                   # low-noise validation targets (GPU, ~10 min), before noise
& $py tools\leafnet\harness.py noise --seeds 5                   # seed spread of the current CONFIG (also sets the first best)
& $py tools\leafnet\harness.py rescore                         # snapshot that had runs before its referee: add val_cv to them
& $py tools\leafnet\train.py --prepare                         # build the recipe's shared side data (its teachers): ~50 min on a new snapshot, nothing when cached
& $py tools\leafnet\train.py --desc "what changed"               # one run: trained, scored, kept or discarded
& $py tools\leafnet\sweep.py --trials 20                         # Optuna over numeric CONFIG
& $py tools\leafnet\train.py --seed 1 --replicate RUN --desc "seed 1"   # another seed of RUN (not judged)
& $py tools\leafnet\harness.py confirm RUN RUN_S1 RUN_S2           # keep rule on seed averages (near misses)
& $py tools\leafnet\harness.py ensemble                         # one net file that averages the best's seed copies (CPU, a minute)
& $py tools\leafnet\scaling.py run                               # size x data grid (~1.5 h plain, hours with the teacher), outside the keep rule
& $py tools\leafnet\scaling.py fit                               # fit error = E + A/N^a + B/D^b, predict milestones
                                                                 # (fractions >= 0.25 only; check the full-data miss before trusting a prediction)
& $py tools\leafnet\harness.py status
& $py tools\leafnet\report.py                                    # WORK/dashboard.html: every run, the kept runs, the data
& $py tools\leafnet\harness.py final                             # milestones only: the test split
```

Every run is appended to `WORK/results.tsv`. The current best's net is
`WORK/runs/<snapshot>/best_leaf_net.bin`, in the format the Preflop Lab
loads (`cache/leaf_net_v1.bin` is v1).

## Using a kept net in the Preflop Lab

Tick "learned flop values" and pick a net under it: v1, any run the keep
rule kept (each snapshot's best is starred), or an ensemble ("mean of 3
nets", starred when it averages the best's seed copies). The server finds the work
folder through `LEAFNET_WORK`, else `leafnet_work/` in the repo,
`../leafnet-work` or `../GTOpen-research/leafnet-work`. Nets are named
`SNAPSHOT/RUN` and saves keep that name, so a saved game reloads with the
net it was solved with as long as the run folder is still there.

## Ensembles: averaging seed copies

Seed copies of one recipe (same train.py, different `--seed`) disagree at a
real solve's leaves by about 1.2% of the pot, which moves borderline hands
by as much as a whole loop's improvement does. Their average is steadier
and scores a little better, so that is what to solve with:

```powershell
& $py tools\leafnet\harness.py ensemble                 # the best and its seed replicates
& $py tools\leafnet\harness.py ensemble RUN RUN RUN --name my-ens   # any kept runs
```

It writes `WORK/runs/<snapshot>/ens3-<best run>/leaf_net.bin`: one file
holding every member (`leafnet_io.write_ensemble`), which the solver loads
like any net and evaluates as the mean of the members' outputs. The file
is checked against solve-cli, scored on validation, val_cv and the
real-leaf sets, and logged to results.tsv with the verdict `ensemble`. It
must score no worse than its members' average on every set (it always
does unless the file is wrong, because squared error is convex) and may
hold up to 16x v1's multiply-adds in total. Solve time grows with the
total size only through the leaf-value refresh, which runs on the CPU
once every 50 iterations and before an accuracy measurement that does
not fall on one of those.

An ensemble never becomes the best and is not a keep-rule candidate.

## Real-range data: exact solves of the ranges preflop solves produce

The pool's ranges come from a sampler; the ranges a preflop solve brings
to a flop do not. A solve also steers its ranges toward the leaves where
its net pays too much, so a net is too generous on the ranges of its own
solves. On six games solved with the loop 4 nets those nets give both
players together 0.9% of the pot too much and v1 0.2%; on the leaves of a
game solved with v1 it is v1 that gives 3.6% too much and loop 4 1.7% too
little. A set of real leaves therefore measures the net whose solve chose
its ranges, and says little about any other. Teacher labels cannot fix
this (the teachers are further off than the nets), so the cure is exact
solves of the ranges a net's own solves produce, trained on next to the
pool, and checked by solving again with the retrained net:

```powershell
# per preflop game (solved and saved in the Preflop Lab): export its heads-up flop leaves, solve them exactly
.\target\release\solve-cli.exe datagen leaves SAVE --leaves 70 --boards 2 --seed 1 --out PILOT\g01
.\target\release\solve-cli.exe datagen solve PILOT\g01
# PILOT\manifest.json lists the games: {"games": [{"id", "folder", "held_out", "source", "config"}, ...]}
& $py tools\leafnet\realrange.py pack PILOT --out PACK
& $py tools\leafnet\prepare.py --files-from SNAP --extra PACK\train --leafcheck datagen_leafcheck_v2 `
      --leafcheck PACK\realrange-heldout --name SNAP-real --side
& $py tools\leafnet\referee.py --snapshot SNAP-real
& $py tools\leafnet\train.py --snapshot SNAP-real --prepare          # this snapshot's teachers
& $py tools\leafnet\train.py --snapshot SNAP-real --desc "..."      # and --seed 1, --seed 2 with --replicate
& $py tools\leafnet\realrange.py compare --snapshot SNAP-real --arm pool=RUN,RUN,RUN --arm real=RUN,RUN,RUN --out compare.md
```

- Whole games are held out (`"held_out": true`), never single leaves: a
  game's leaves share their ranges' ancestry. `pack` turns the training
  games' leaves into job files that land in the training split and the
  held-out games into one real-leaf check set, and refuses a held-out game
  whose twin (the same config solved under another realization) would be
  trained on.
- `--files-from SNAP` freezes exactly SNAP's pool files, so the new
  snapshot has SNAP's validation and test examples in the same rows and
  differs only by the extra training rows. `--side` leaves the current
  snapshot alone: the experiment's runs name theirs with `--snapshot`.
- `compare` scores any nets on one snapshot's sets with numpy alone, so the
  pool-only nets (trained on SNAP) and the new ones meet on the same
  examples: class error, range error and the "total" (both players'
  predicted range values minus the solve's, % of the pot; zero is right),
  per pot type and per held-out game, with intervals over leaves. Read a
  real-leaf set's total next to the net that solved its games: the same
  net scores differently on another net's ranges.
- `train.py`'s `real_weight` and `real_distill_mix` change how much, and on
  which target, the net's loss counts those rows.
- **Publishing.** `realrange.py publish PILOT --contributor NAME --set round1
  --out PUBLISH` writes one game file per solved game
  (`PUBLISH/real/NAME/round1/<game>.jsonl`: the solved examples as they are,
  under a header with the game's config, its model and net, the exported
  lines and the held-out flag). `tools/datagen/upload.py --real PUBLISH`
  sends them to the public dataset and the validator re-solves a sample, see
  [docs/contribute-compute.md](../../docs/contribute-compute.md#real-range-game-files).
  `pack` also reads a folder of such files (a download of the dataset's
  `real/` tree) when there is no manifest, taking each game's held-out flag
  and its place in the manifest from its header: a set packs to the same
  files from its published games as from the solver's folders.
- **Only ranges GTOpen solved are published or trained on.** Reference
  charts from anywhere else are never training data and never uploaded;
  `publish` refuses a folder that did not come from `datagen leaves`.

## Sharing the GPU with the generator

- The harness caps its own VRAM at 3 GB (`torch.cuda.set_per_process_memory_fraction`).
  The generator sizes its trees to 80% of the card, so both fit; a game on
  the same card can still squeeze them.
- Before leaving the loop running, run it for an hour and compare the
  generator's jobs per hour with the hour before. Keep it if the generator
  loses less than about 10%; otherwise pause between runs or run at night.

## Rules the harness enforces

- Splits are gonogo.py's (job hash: 0 test, 1 validation, rest train), so
  held-out jobs never change as the data grows. Real-leaf sets are test
  sets and are never trained on.
- A run is kept only if it is deployable (plain Linear/ReLU stack within 4x
  v1's multiply-adds, reproduced by the Rust loader), significantly better
  than the best on validation class error (paired bootstrap over jobs) by
  more than the seed spread, not significantly worse on range error, and not
  significantly worse on any real-leaf set.
- A run that passes all of that except the seed spread is a `near` miss.
  Train two more seeds of it with `--replicate`, then `harness.py confirm`
  applies the same rule to seed averages. It compares with the best's own
  seeds, and the spread threshold scales by sqrt((1/n + 1/m) / 2), which is
  about 0.58x for three seeds against three. That way small but steady
  gains aren't lost to the single-run threshold.
- `harness.py final` is the only command that reads the test split.
