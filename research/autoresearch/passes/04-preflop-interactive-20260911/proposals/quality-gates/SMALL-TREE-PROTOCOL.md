# Registered small-tree execution protocol

Written before executing the small-tree driver. Corpus thresholds and independent range definitions remain those registered in `registration.json`.

The first run is `three-solver-development`, full `coupled_deck_v1` and frozen `coupled_preview64_v1`. The other two registered cases remain holdout controls until this driver and model family are fixed. No silent sizing reduction is allowed if the registered case exceeds 20,000 nodes or 128 MiB arenas; record the failed preflight instead.

Command (from the isolated lab, never the running server):

```
preflop_preview_small CORPUS.json CASE MODEL EQUITY_CACHE NEW_OUTPUT_DIRECTORY THREADS [CANDIDATE_CAP]
```

`THREADS` is fixed identically for paired runs, 1..4. `NEW_OUTPUT_DIRECTORY` must not exist and its parent must already be within the current lab's `target/research-preview` directory. Native checkpoints and one run.json are the only outputs. No live API or GPU is used.

- Full reference: at most 500 learning iterations, gap checks every 10, stop when summed learning-seat gap is below 0.005 bb/hand. Save its stopping/final state. If capped, explicitly report not-converged.
- Preview64: at most 100 learning iterations; checks every 10 and at iteration2. Save at2/10/30/50/100, plus any early own-model convergence/final state. Own-model target remains0.005, but meeting it cannot establish reference quality.
- After the initial100-iteration curve, an explicitly recorded optional candidate cap1..500 can run a longer fresh trajectory in a new output directory. This does not change the fixed reference500 limit or any quality threshold. The driver does not silently extend a run or resume/overwrite an earlier checkpoint. A cap argument is refused for the full reference.
- Both start fresh with their actual model identities. The all-solver case uses untouched uniform initial averages. The fixed/frozen case seeds all strategy sums using `1 + ((node*3 + action*7 + hand*11) % 19)` before freezing seat2, identical in both models; regrets stay zero. This is an artificial control, not inferred poker data.
- Static and adaptive synthetic profiles retain the registered call=.4/raise=.2/jam=0 per-class policy and standard legal-action routing. Adaptive seat0 responds freely from25% of stack. Hero stays off.
- After the pair, evaluate each saved preview state with `preflop_preview_quality` against the same final full reference. Keep excess-gap0.02, unilateral mean0.01, max0.03 bb/hand fixed. Reference not-converged means no global quality qualification.
- Timing records separate initialization, iteration time, checkpoint time and elapsed end-to-end time. Native checkpoint writes affect elapsed time; they are offline capture overhead and must be disclosed, not silently used as interactive UI latency. Future actual UI delivery timing remains separate.

Candidate weights/indices were selected without the new terminal holdout data. The initial source log is frozen in `frozen-herding64.json`. The independent terminal command accepts MC count0 for coupled-only/rebuilt-existing-reference checks or100000 for the new physical references; do not tune the frozen64 candidate after reading these results.

This protocol measures a CPU small-tree quality trajectory. It cannot by itself certify a10x desktop end-to-end speedup on the million-node GPU workloads.
