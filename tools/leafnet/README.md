# Leaf-net training harness

Tools for training and searching the Preflop Lab's leaf-value net on the
pooled flop solves (docs/contribute-compute.md), on the GPU, next to the data
generator. The plan behind it is the [leaf net plan](https://claude.ai/artifact/FqjQDLENZ5cTvkoNteJant).

| file | role | who edits it |
|---|---|---|
| `prepare.py` | freezes a data snapshot, prices it once with the realization models, caches prices per job file | frozen |
| `harness.py` | data on the GPU under a VRAM cap, scoring, paired bootstrap, keep rule, export + Rust parity, results.tsv, test-split evaluation | frozen |
| `train.py` | CONFIG + `run()`: the model and how it is trained | the agent / you |
| `sweep.py` | Optuna over train.py's numeric CONFIG | frozen |
| `program.md` | the autoresearch loop's rules | frozen |

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
& $py tools\leafnet\harness.py noise --seeds 5                   # seed spread of the current CONFIG (also sets the first best)
& $py tools\leafnet\train.py --desc "what changed"               # one run: trained, scored, kept or discarded
& $py tools\leafnet\sweep.py --trials 20                         # Optuna over numeric CONFIG
& $py tools\leafnet\harness.py status
& $py tools\leafnet\harness.py final                             # milestones only: the test split
```

Every run is appended to `WORK/results.tsv`. The current best's net is
`WORK/runs/<snapshot>/best_leaf_net.bin`, in the format the Preflop Lab
loads (`cache/leaf_net_v1.bin` is v1).

## Using a kept net in the Preflop Lab

Tick "learned flop values" and pick a net under it: v1, or any run the keep
rule kept (each snapshot's best is starred). The server finds the work
folder through `LEAFNET_WORK`, else `leafnet_work/` in the repo,
`../leafnet-work` or `../GTOpen-research/leafnet-work`. Nets are named
`SNAPSHOT/RUN` and saves keep that name, so a saved game reloads with the
net it was solved with as long as the run folder is still there.

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
- A run is kept only if it is deployable (plain Linear/ReLU stack within 2x
  v1's multiply-adds, reproduced by the Rust loader), significantly better
  than the best on validation class error (paired bootstrap over jobs) by
  more than the seed spread, not significantly worse on range error, and not
  significantly worse on any real-leaf set.
- `harness.py final` is the only command that reads the test split.
