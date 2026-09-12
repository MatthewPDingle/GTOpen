# Fixed-unit GPU update: standalone arithmetic proof

Research only. No deployment, live mutation or ordinary continuation API.

The standalone `pf_up_fixed_history_units` kernel preserves stored histories
and divides future regret/average increments by fixed per-node units. It is
compiled only by the research test module at this checkpoint.

## Verified experiment

`fixed-history-kernel-tests-v1` completed successfully in 86.25 seconds including
compilation; the test executable reported 2.40 seconds. These are test runtimes,
not solve speed measurements. The independent verifier checked all four cases:
raw/calibrated continuation crossed with unit-one/unequal-unit arrays.

Each case covered 526 nodes, 11 depths, all four traversers, 129,454 learning
entries across eager/captured execution, a frozen seat and a point lock.
Histories were reset between traversers to isolate arithmetic. Unequal learning
units span 0.001 to 1; fixed nodes retain unit-one metadata.

- Unit-one updates and propagated values matched native bit for bit.
- Graph replay matched eager outputs bit for bit.
- Unequal-unit propagated values matched native exactly.
- Maximum transformed-native regret-reference discrepancy: 0.000955312.
- Maximum average-reference discrepancy: 0.000006373.
- Fixed and non-traverser histories remained unchanged.
- The tiny 1e-11 initial-history policy stayed at probability 1 in both current
  and average down passes, avoiding the earlier rescaling floor counterexample.
- Actual two-array device allocation: 4,208 bytes (8 bytes/node). Extrapolating
  this representation alone to 1,567,754 nodes gives 12,542,032 bytes; total
  large-engine allocation and runtime are not measured here.

The arithmetic reference transforms native increments after f32 accumulation;
subtraction then division loses precision, particularly for the 0.001 unit.
The pre-registered absolute discrepancy limit was 0.002; value tolerance was
0.0002 bb. These tolerances do not become large-game accuracy tolerances.

## Remaining work

Integrate stable unit buffers into complete learning iterations and enforce
admission before mutation: dimensions, finite positive bounds, fixed-node
ownership, incompatible research modes, and overlapping branch ownership.
Persist and verify branch masses, ownership, history ages and save hashes for
research continuation; ordinary resume remains unsupported. Test discounting,
full iteration capture, native final evaluation and restoration independently.
Then execute a registered matched small continuation screen before the large
experiment. Neither the 0.005-bb global gate nor all 27 conditional gates has
been qualified by this kernel test. The objective remains active.
