# Parallel native evaluation throughput

A bounded CPU-only control on September 25 measured 2.79 times faster native
evaluation with four workers than with one. Every output matched its saved
reference byte for byte. The live GPU training and registered study pipeline
were unchanged.

Two authenticated historical batches were reused: each has 64 physical deals
and five complete profiles. Each stage evaluated 16 alternating batch jobs.
Worker counts ran in the fixed order 1, 2, 4, 4, 2, 1. Repeating those batches
does not produce additional independent poker evidence.

| Concurrent workers | Combined time for both 16-job stages | Throughput ratio |
| --- | ---: | ---: |
| 1 | 10.298 s | 1.00x |
| 2 | 5.672 s | 1.82x |
| 4 | 3.687 s | 2.79x |

This includes native process launch, input reads/parsing, evaluation and result
hashing. The stage measurements are short and use cached, repeated inputs under
concurrent training load. They do not establish the same gain for cold reads,
different trees, eight-profile comparisons, or the complete inference/evaluation
pipeline. The control used no GPU and created 4.54 MB of result files.

The useful next integration is a bounded queue of independent native evaluation
batches, keeping each batch's deals and policies together and merging outcomes
in their original registered order. GPU averaging, CPU preparation and evidence
publication would still need their own measurements; serial stages limit the
overall gain. Preserve deterministic paired contrasts, failure handling, output
ownership and storage limits. No live source was changed for this control.

Evidence: `native-evaluation-parallel-control-v1-registration.json`,
`native-evaluation-parallel-control-v1-result.json`, and its successful status.
The registration SHA-256 is
`477e8d935c9885cb5f37b6c5fce9df95536ea979fd7ab2f7e323227f7e45eb24`.
