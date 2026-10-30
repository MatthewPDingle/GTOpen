# Eight CPU workers with guarded waiting

Prepared 2026-09-28 while the four-worker pilot was qualifying its restart.
This extends EIGHT-WORKER-TRAINING-PLAN.md without changing its executed files.

The optional `board_training_pipeline_eight_v2.py` and
`river_training_pipeline_eight_v2.py` are derived from the guarded-wait pipelines.
They change only the imported physical worker pool, retaining the qualified
worker functions, ordered insertion, random streams, target definitions,
fitting and joint checkpoint publication. Board workers remain at four.
The old eight-worker v1 pipeline copies contain the obsolete parent timeouts
and must not be used for later runs.

`eight_worker_training_control_v3.py --run` is the required dispatch check:
32 tasks across two models, both target methods and repeated old fixtures;
all output artifacts must match the original qualified fixtures exactly.
It imports the guarded future helper so an observation timeout cannot be
mistaken for a worker failure. Its original 90-second overall budget and
resource/production guards remain. It introduces no new poker deals or GPU
work, and does not change the active four-worker pilot.

Run only during the pilot's excluded qualification with spare CPU/RAM, or
after its verified successful termination. The check refuses measured
training/evaluation overlap. Passing is dispatch equivalence, not a measured
speedup or end-to-end training qualification. A subsequent bounded full-update
comparison must check complete state equality and wall time before promoting
the wider pool. Keep existing scientific results and historical failures.
