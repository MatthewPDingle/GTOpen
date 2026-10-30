# Bulk preparation for current-strategy prediction

The CPU qualification passed on two previously audited training histories.
Bulk feature preparation reduced prediction time by about five times on these
saved batches, with byte-identical network scores, action probabilities, and
identical exact-table coverage. This candidate is not installed in the active
matched training experiment or production.

| Frozen model | Decisions | Reference, two runs | Bulk, two runs | Ratio of total times |
| --- | ---: | --- | --- | ---: |
| Two-update later-action pilot, generation 1 | 29,019 | 5.875 / 6.000 s | 1.172 / 1.047 s | 5.35x |
| Original complete first trial, generation 77 | 29,048 | 5.844 / 5.609 s | 1.141 / 1.125 s | 5.05x |

Order alternated between implementations. CPU numerical libraries were limited
to one thread; CUDA was disabled. The independent full training run remained
active, so these are short paired observations under concurrent load, not an
isolated or whole-study throughput benchmark. Full control elapsed time was
98.859 seconds, including loading/authenticating historical models and inputs.

The candidate's exact-initial prediction function is structurally identical to
the reference except for importing the previously qualified bulk feature
builder. Scores still use widened stored float32 weights and the same float64
arithmetic. Root and exact BTN overrides remain unchanged. The later-action
version-7 adapter also produced identical probabilities and coverage on the
pilot fixture. No hidden cards, new features, altered probabilities, or model
fitting were introduced.

The first control attempt passed the pilot case but failed on its second raw
training-query fixture: that transport omits `own_history`. The unchanged live
trainer supplies an explicit structurally initial-action view before inference.
V2 uses that same adapter. V1's source, registration, and failure record remain
preserved; the failed attempt is not counted as a successful qualification.

This supplies a candidate implementation for the next training runtime.
CUDA-path and end-to-end update replay/timing remain to be qualified after the
registered GPU sequence releases the device. Neither matched trial is switched
mid-experiment. Faster inference does not establish better preflop ranges.

Evidence: `single-bulk-cpu-control-v2-registration.json` and
`single-bulk-cpu-control-v2-result.json`; original failed registration and
`single-bulk-cpu-control-v1-failure.json`. The control authenticates its source
inventory, historical trial metadata, and query fixtures before and after use.
