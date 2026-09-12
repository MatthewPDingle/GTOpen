# GPU control-variate screen

This prototype is rejected for deployment in its current form.

The numerical checks passed on the registered four-player fixture:
- Full-particle corrections cancel exactly: all arenas and full-check gaps match.
- Refreshing every iteration with 64 particles has maximum normalized arena
  difference 0.00000028655 versus the full gradient (limit 0.0002).
- Zero extra-memory allowance rejects initialization before allocating CV arrays.

Actual GPU convergence measured on the unchanged six-player fixture:

| Seed | Refresh | Iterations | Seconds through final full check |
| --- | ---: | ---: | ---: |
| 42 | Disabled | 275 | 3.277 |
| 42 | 32 | 275 | 5.889 |
| 42 | 64 | 275 | 5.552 |
| 314159 | Disabled | 325 | 3.801 |
| 314159 | 32 | 325 | 6.787 |
| 314159 | 64 | 300 | 5.976 |

Each run passed two canonical full-model global checks. Extra storage was
127,603,176 bytes. Fewer iterations in one case did not offset reference and
launch costs. These are small-fixture global-convergence screens, not broad
conditional qualification. Native roundtrip checks passed in every run.

The eight-player memory probe rejected initialization: 12,196,748,616 extra
bytes required, exceeding the registered 4-GiB cap, in addition to the existing
roughly 13-GB engine. No large-game learning occurred in this probe.

Potential follow-up: a shared policy reference and compact per-live-seat cache,
then captured GPU learning graphs. That is a new design requiring validation;
it is not an optimization demonstrated by these measurements.
