# Weighted retained-data numerical control

Qualify a separately typed weighted reservoir and grouped regression objective.
Do not connect to native poker training or overwrite old reservoir/checkpoint
formats. Uniform Algorithm R retains visits together with their source-deal
weight. Weights multiply squared losses, not advantage target values. Grouping
uses weighted means and masses, with a weighted residual variance constant so
grouped loss plus that constant equals the direct ungrouped objective.

Use twelve previously inspected catalog observations with explicitly synthetic
varying legal arities, signed targets and weights. Retain 37 of 120 visits.
Require exact all-ones equivalence with the old reservoir, same RNG state and
selection, checkpoint restoration and continued insertion equality. Require
grouped versus direct float64 gradient error below 1e-10 and loss decomposition
error below 1e-12. Reject invalid weights without consuming a reservoir draw,
incompatible old/new checkpoint formats and altered game identity.

If the production app is idle or confirmed closed, research locks are free,
the GPU is below 20% utilization with over 4GB free memory, and host RAM has
over 20GB available, compare eight Adam steps on CPU/CUDA float32 with the same
initial model and weighted objective. Maximum parameter difference 1e-4. Record
an explicit skip if resources are busy. No live solve or user process is stopped.
Maximum total control time 180 seconds; metadata and tiny fixture checkpoints only.

Passing these tests qualifies numerical components only. Source-deal mapping,
root accumulation, weighted preflop tables, model/checkpoint versioning and the
full training-loop integration remain separate gates before a poker pilot.
