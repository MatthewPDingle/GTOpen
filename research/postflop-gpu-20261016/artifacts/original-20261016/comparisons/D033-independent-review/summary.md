# D033 independent runtime review

**PASS for exactness and protocol execution; materially perturbed timing diagnostic.** D033R1 ran once from the frozen R2 binary, returned one passing test, and preserved all three samples. R1 remains a documented no-run compile failure (E0425); R2 changes only the versioned getter identifier. Build/input/archive hashes and all163 source identities match, and the build finished before native launch.

All four raw-before-evaluation checkpoints140/160/180/200 passed direct word comparison: 4,426,132,436 raw f32 word pairs total across regrets, strategy, reaches and weights, plus discount and iteration checks. Full compressed stores matched at all four checkpoints;140 is enforced in frozen control flow before graph setup. All10 original convergence anchors matched. Both final full state objects equal original B038 and accepted E015C1, including all arena metadata/hashes and root strategy bits; final fingerprint`65fb2853a11f3acc`, exploit bits`4595130701932466176`.

Each original graph contains63 kernel nodes/62 chain edges. Its clone adds64 events and126 boundary edges, keeping every original kernel/argument/order. All378 node samples are finite and retained; none was marked near timer resolution. No invalid, panic or cleanup-error marker appeared through native process exit.

| Batch end | Native20 iterations (ms) | Instrumented20 iterations (ms) | Increase |
|---|---:|---:|---:|
| 160 | 459.606 | 776.333 | 68.91% |
| 180 | 460.857 | 793.228 | 72.12% |
| 200 | 462.522 | 791.062 | 71.03% |

Median instrumented/native ratio is1.7103x. Native host-wall durations track their device envelopes; this does not remove instrumentation perturbation. The three final-replay combined graph envelopes are31.631,31.820,32.130ms, with0.000576ms intergraph gaps. These are final-replay samples, not20-iteration means.

| Family | Event-perturbed paired-replay median ms | Range ms |
|---|---:|---:|
| up_action | 10.460 | 10.364-10.683 |
| up_show | 7.666 | 7.639-8.089 |
| down_action | 5.541 | 5.526-5.639 |
| up_fold | 3.457 | 3.421-3.635 |
| up_chance | 2.480 | 2.396-2.503 |
| down_chance | 1.856 | 1.847-2.127 |
| copy_root | 0.081 | 0.077-0.094 |

The ordering up_action > up_show > down_action repeats across all three instrumented final replays. The heaviest individual action samples are graph1 ordinal38 (grid127302, median1.338ms), graph1 ordinal34 (grid141120,1.313ms), and graph0 ordinal34 (grid141120,1.183ms). This prioritizes where to confirm a hotspot; the69-72% outer slowdown prevents treating these values as native shares or predicted gains.

If another diagnostic is justified, use a new prospective sparse-event design around the selected up_action ordinals with exact descriptor checks, native outer controls and the same numerical protections; optionally retain up_show29 as a comparator. Confirm perturbation is reduced before drawing native-time conclusions. Do not modify this run, resurrect rejected changes, or accept/deploy an optimization from these timings.

Admission reported5,900,635,904 payload bytes per arm and13,948,755,456 combined required bytes including reserve, against32,496,418,816 free. Host additional requirement was12,852,342,584 against103,306,436,608 available. These are admission observations/reservations, not measured peak usage. Whole native test took37.09s; process wall was37.437s including startup, checks, hashing and cleanup, not primary benchmark time.

The adjacent audit script, parsed raw records and validation JSON preserve all source/data hashes, chronology, checks, node medians/ranges, exact anchors, overhead envelopes and limitations. No GPU/build, production edits or dashboard changes were performed by this reviewer.
