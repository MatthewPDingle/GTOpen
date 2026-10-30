# Hardware use during the first matched trial

A read-only five-minute sample on September 25 confirms substantial unused
hardware capacity in the current research pipeline. The run continued from
34 to 36 completed updates during the observation; neither training nor the
production application was changed.

| Measurement | Observed value |
| --- | ---: |
| Elapsed observation | 299.985 seconds |
| Main Python worker CPU | 0.916 logical cores on average |
| Whole-computer CPU | 15.82% on average |
| Whole-device GPU utilization | 14.27% on average |
| Maximum whole-device GPU memory | 5,486 MiB |
| Minimum available host memory | 106.106 GB |
| Maximum main-worker resident memory | 1.539 GB |

The CPU counter excludes native subprocesses; GPU measurements include other
applications. Periodic snapshots can miss short bursts. These figures describe
this interval, not isolated GPU accounting or a controlled throughput comparison.
The earlier 25-second observation used a different workload and should not be
used to calculate an improvement ratio.

The qualified captured-gradient fitter is already in this training run. Its
separate frozen-reservoir control measured 3.55 times faster complete fits with
exactly matching weights. That gain does not remove serial preparation,
validation, data transport, and evidence recording elsewhere in the pipeline.
The current single-policy predictor still imports the scalar feature builder;
the bulk builder already used by fitting and full-bank averaging is a concrete
remaining opportunity. A separate candidate must qualify before adoption.

The registered scheduling amendment also overlaps the first CPU audit with the
second GPU training run. It retains both mandatory audits and their failure
gates. The time saved by that overlap has not yet been measured.

Further work should measure end-to-end gains from bulk current-policy inference
and bounded parallel independent evaluation batches. Maximizing utilization
alone is not the objective: preserve equivalent outputs, resource reserves,
and the scientific comparison. No range-quality conclusion or production
deployment follows from this hardware sample.

Evidence: `later-action-hardware-sample-v1-registration.json` and
`later-action-hardware-sample-v1-result.json`. Registration SHA-256:
`7c41b4fc933e116a071c747d72546e36cc4f35fa43127306021b524c5fe994b6`.
