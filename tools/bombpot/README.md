# Bomb pot net: training tools

Self-play training of the bomb pot net (heads-up stage). The engine side is
`crates/solver/src/bombpot/` (`range.rs`, `net.rs`, `deepcfr.rs`) and the
`bombpot` tool; this folder holds the PyTorch side.

| file | role |
|---|---|
| `train.py` | fits a net to example files and writes it in the engine's format; `--check` compares its outputs with the engine's |
| `loop.py` | the whole loop: self-play, training, exact scoring every few rounds; resumable |

## One flop, start to finish

```bash
cargo build --release -p solver --bin bombpot
python tools/bombpot/loop.py --spec spec.json --work WORK --exe target/release/bombpot \
    --iters 60 --score game.json --score-every 10 --warm
```

`spec.json` is a `GenSpec` (`deepcfr.rs`): the game (boards, antes, stacks,
bet sizes), how many games and walks a run plays, and how many turn and
river cards each walk draws. With no boards in the game, every game draws
its own flop; `held_out` flops are never drawn. `game.json` is one game
(`BpConfig`) to score on.

```json
{"game": {"boards": ["AsKd7c"],
          "tree": {"players": 2, "ante": 6.0, "stack": 98.0,
                   "sizing": [{"bet": [{"PotPct": 66.0}], "raise": [{"PotPct": 100.0}]},
                              {"bet": [{"PotPct": 66.0}], "raise": [{"PotPct": 100.0}]},
                              {"bet": [{"PotPct": 66.0}], "raise": [{"PotPct": 100.0}]}]}},
 "games": 1, "walks": 12, "turn_draws": 3, "river_draws": 2, "keep": [1.0, 0.5, 0.2]}
```

`WORK/log.jsonl` gets one line per event. A `score` line says what a perfect
opponent would gain against the strategy net: `gain_avg` in chips per hand
and `gain_pct_of_pot` as a share of the starting pot. Scoring tries every
turn and river card, so it is exact; `--score-turns` / `--score-rivers`
sample instead (quicker, reads a little high).

## On a shared machine

`--low-priority` runs the loop and the engine below normal priority and
`--threads N` caps the engine's threads. Training needs a PyTorch build for
the machine's GPU (see `tools/leafnet/README.md` for the RTX 50-series) and
takes a few GB of GPU memory at the default `--cap`.

Run one training job at a time on a small CPU-only machine: two PyTorch jobs
on four cores crawl.

## Net shapes

`--width N` (loop and trainer) makes two-sided nets: one side reads the hand
on its board, the other the board and the betting, and each action's output
is a weighted sum of the two (`N` numbers in between). The engine then runs
the hand side once per board and the other side once per decision for all
hands, so games and scores run several times faster than with the one-piece
net (`--width 0`), also with a much bigger net. `--hidden` and `--layers`
size each side.

In a spec, `"spread": true` makes the walks of a run share one shuffled deck
(each takes the next cards) instead of each drawing its own: the same work
covers the turn cards evenly, which steadies the flop examples.

## What score to expect

`bombpot tables game.json --rounds 80 --every 10` trains plain tables the
same way (seats take turns) on the cards of one sampled walk, in under a
minute. Its score at a round is about what a net that fitted every example
perfectly would reach there, so read a net's score against it before
blaming the net. `--regret-power` and `--avg-power` set how much later
rounds count (round t counts t^power times); the loop's `--power` and
`--avg-power` are the same for the nets. On the README's game tables with
power 1 need about 70 rounds to get under 3% of the pot, with power 2 about
30.

`bombpot mix game.json --nets none,adv_0001.bin,... --net avg_NNNN.bin`
scores the exact average of the nets that played beside the strategy net,
on the same sampled cards: a gap between the two is the strategy net's own
loss.
