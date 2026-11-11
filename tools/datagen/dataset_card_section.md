## Real-range game files (`real/`)

Besides the pooled jobs under `data/`, the dataset holds exact flop solves of
the ranges GTOpen's own preflop solves produce: one file per solved preflop
game under `real/<contributor>/<set>/`, with the same example fields as the
pooled jobs and a header that describes the game. See
[real/README.md](real/README.md).

The data pipeline behind this dataset (generator, validator and training
tools) was built with [Claude](https://claude.com/claude-code).
