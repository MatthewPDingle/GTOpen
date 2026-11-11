# Real-range game files

Exact flop solves of the ranges that GTOpen's own preflop solves produce.

The pooled jobs under `data/` use broad random ranges. The files here use the
ranges a solved preflop game really brings to its heads-up flops:

1. A preflop game is solved in GTOpen's Preflop Lab.
2. Its heads-up flop situations (one preflop line that ends with two players
   seeing a flop) are exported, the ones that carry the most chips first,
   spread evenly over limped, single-raised, 3-bet and 4-bet pots, each with
   a few random flops (`solve-cli datagen leaves`).
3. Each one is solved to the river with the same bet menu (`lean-v2`) and
   accuracy target (0.5% of the pot) as the pooled jobs
   (`solve-cli datagen solve`).

No ranges from charts, other solvers or any other outside source are part of
this dataset. Every range here is the output of a GTOpen solve.

## Layout

`real/<contributor>/<set>/<game>.jsonl.gz`: one file per solved preflop game.
A set is one batch of games, for example one round of solves with one net.

The first line is the header:

| Field | Meaning |
| --- | --- |
| `format`, `format_version`, `menu` | `gtopen-real-range`, 1, and the flop bet menu the solves used. |
| `contributor`, `set`, `game` | Where the file sits. |
| `position` | The game's place in its set, counted from 0. `pack` numbers a game's training jobs by it, so a set packs to the same files wherever it is packed. |
| `examples`, `asked` | Examples in the file, and how many the export asked for (a game can be published before every tree is solved). |
| `target_pct`, `max_iterations` | The accuracy target and iteration limit of the flop solves. |
| `config` | The preflop game: seats, stacks, sizes, rake, the realization model and, under `leaf_net`, the name of the net it was solved with. |
| `source` | The model whose solve chose these ranges: `leafnet` (learned flop values) or `balanced`. |
| `held_out` | Whether GTOpen's own training keeps this game out as a check set. Whole games are held out, never single leaves. |
| `preflop` | The solve's iteration count, how many heads-up flop leaves the game has, how many were exported and the share of the chips they cover. |
| `leaves` | For each leaf in the file: its number, the preflop line, the seats, pot, stack, number of raises and how often the line is reached. |

Then one line per example with the same fields as a pooled example (`board`,
`pot_type`, `pot_bb`, `stack_bb`, `rake_pct`, `rake_cap_bb`, both 169-class
`range`s, and per class `reach`, `eq` and `value` for both players, plus how
the solve went). `job` is 900000000000 plus the leaf's rank within its game,
and `index` is the number of the flop drawn for that leaf, so numbers repeat
from game to game. A `done` line ends the file.

## Whose solve chose the ranges matters

A preflop solve steers its ranges toward the flop situations its value model
overrates. Measured against these exact solves, every model GTOpen has tried
is at its most optimistic on the ranges of its own solve and reads lower on
another model's. So a set of real ranges measures the model named in `source`
and `config.leaf_net`, and says much less about any other. Label results by
the model that chose the ranges.

## How these files are checked

A pooled job's inputs are regenerated from its job number. These inputs come
from a preflop solve and cannot be, so for now game files are accepted only
from the project's maintainers. Every file is checked for plausible inputs
and values, and a sample of its examples is solved again and compared, like
any other upload.

## Training on them

```sh
python tools/leafnet/realrange.py pack FOLDER_WITH_THE_DOWNLOADED_FILES --out PACK
```

turns the games into training job files and one held-out check set, following
each header's `held_out` flag and `position` (sets follow each other by
contributor and set name). `tools/leafnet/README.md` in the
[GTOpen repository](https://github.com/MatthewPDingle/GTOpen) has the rest.

Licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), like the
rest of the dataset.
