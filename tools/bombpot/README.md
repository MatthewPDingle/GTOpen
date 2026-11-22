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

On a GPU shared with another job, `--gpu-free-gb N` holds each training run
until that much memory is free, and a smaller `--cap` lowers what training
takes (about 1 GB per 8 million examples). `--keep-rounds N` keeps only the
last rounds' example files on disk.

Run one training job at a time on a small CPU-only machine: two PyTorch jobs
on four cores crawl.

## Net shapes

`--width N` (loop and trainer) makes two-sided nets: one side reads the hand
on its board, the other the board and the betting, and each action's output
is a weighted sum of the two (`N` numbers in between). The engine then runs
the hand side once per board and the other side once per decision for all
hands, so games and scores run several times faster than with the one-piece
net (`--width 0`), also with a much bigger net. `--hidden` and `--layers`
size the hand side; `--spot-hidden` and `--spot-layers` size the situation
side, which costs almost nothing in play and is where size pays most (on one
round's examples a 512x3 situation side beside a 128x2 hand side explained
0.83 of the river values, against 0.65 with both sides 128x2).

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

`specs/one_flop_fixed_cards.json` (`"fixed_cards": 1`) makes the net loop
play the very cards `bombpot tables` and `bombpot score --turns 6 --rivers 6`
draw with seed 1, every round. Run with `--score-turns 6 --score-rivers 6`,
the loop's scores then compare with the tables' round for round on the same
small game, where a net sees every spot every round. A gap there is the
net's fit; a gap only on the full game is too few cards seen per round.

## Solving the river instead of learning it

On the full game the nets' river play stopped improving after about ten
rounds and then got worse (a net sees each of the 2,352 turn and river
boards of a flop too rarely), while on fixed cards the same net stays ahead
of the tables. So the river can be left to arithmetic: with
`"river_solve": N` in the spec the nets play the flop and the turn only,
and each river spot a walk reaches is solved on the spot, in N rounds, for
the ranges that arrive (`Walker::river_iters`); no river examples are
written. `bombpot score --river-solve N` (the loop's `--river-solve N`)
scores that same mix: the strategy net to the river, then the solution for
the ranges it brings. `bombpot tables --river-solve N` is the plain-tables
reference for it: with N = 100 it reaches in 20 rounds what plain tables
need about 35 for, and a reply that starts on the river gains about 1% of
the pot (5% with N = 30). `specs/one_flop_river_solved.json` holds the
settings; a half round of it solves 384 boards (about a minute of one
core per 50).
