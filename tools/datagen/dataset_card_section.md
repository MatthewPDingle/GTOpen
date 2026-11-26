## Real-range game files (`real/`)

Besides the pooled jobs under `data/`, the dataset holds exact flop solves of
the ranges GTOpen's own preflop solves produce: one file per solved preflop
game under `real/<contributor>/<set>/`, with the same example fields as the
pooled jobs and a header that describes the game. See
[real/README.md](real/README.md).

Files under `situations/` are lists of such situations (both ranges, pot,
stack and rake, without a flop) that a game mix hands to every contributor:
pooled jobs under `data/` then draw from a list on random flops, and those
examples carry `situation` (`LIST/ID`).

## Three-player flops (`three/`)

Files under `three/<contributor>/` are pooled jobs of three-player flops:
exact three-player solves of three random ranges (format
`gtopen-flop-values-3p`). Every example gives the three ranges and, per hand
class and player, reach, showdown equity and solved value as a share of the
pot. The fields are described in
[the contributor guide](https://github.com/MatthewPDingle/GTOpen/blob/master/docs/contribute-compute.md#three-player-job-files).

The data pipeline behind this dataset (generator, validator and training
tools) was built with [Claude](https://claude.com/claude-code).
