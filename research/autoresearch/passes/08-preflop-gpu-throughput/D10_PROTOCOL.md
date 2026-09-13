# D10: bounded terminal-tile probability-table inventory

Registered before extraction. Retained runtime: C01+C07+C09+C14 at 7a8e9f4.
GPU preflop only. Port 56708 stays read-only; one guarded workload at a time.

## Hypothesis

Keep original terminal order and produce probability tables for contiguous
terminal tiles, then consume the tile before replacing its tables. This lies
between materializing all tables and C16's costly per-terminal recomputation.
It differs from D07's rejected global sorting: no terminal permutation occurs.

Read the two immutable mature saved games without advancing learning. Run the
existing GPU down/prepare/normalize operations. Intern normalized rows with full
bitwise equality after hash lookup, including signed zero. Current-policy work
uses the original positive-counterfactual mask. Average-policy baseline includes
all positive-mass rows in each retained cohort; tile consumers only require rows
of positive-probability terminals. Never gate by the traverser's own reach.
Preserve ordered opponent multiplicity in the witness, although table sets may
share exact identical distributions.

For tile sizes 128, 512 and 2048 positions in the original full terminal list,
measure total distinct table rows rebuilt across tiles, maximum rows resident,
nonempty tile count and required producer/consumer launch counts at batch 32
and 1024 samples. Learning is inventoried per seat; average checks share the
same retained cohort groups from the verified C14 fixture layout. No normalized
values are inferred from raw CPU reaches; they come from existing GPU division.

## Admission gate

Admit a separately designed GPU prototype only if one of the three fixed tile
sizes has <=1.25 times the baseline distinct CDF construction work on BOTH
current and average large-state inventories, maximum CDF storage <=4 MiB, and
small-state construction work <=1.30 times baseline in both modes. These are
feasibility gates, not performance predictions. Report launch counts even on
failure. The 4 MiB budget reserves room for other cache traffic; no cache-hit or
hardware-stall claim follows from satisfying it. Do not search more tile sizes
after seeing this screen's results.

Synthetic tests must cover bit differences, forced hash collisions, repeated
opponents, empty tiles, partial final tiles and gaps in terminal indices. Write
compressed witnesses and independently reproduce aggregate tile metrics in
Python. Check full regret/average-strategy arenas and iteration unchanged.
Archive input/source/executable hashes, failed runs and output. Extraction caps
are 180 seconds per fixture; build/test cap 300 seconds. No CDF or terminal
kernel changes and no speed, convergence or deployment claim in this diagnostic.
