# Complete update prepared; GPU qualification pending

`board_training_pipeline_v1.py` stages a private copy of the mutable training
state, overlaps bounded CPU board calculations with physical target processing
and GPU work, and publishes the caller's state only after a complete checkpoint
and metrics record. Its syntax and input preflight pass. Its complete CUDA
execution has not yet been tested; do not admit it for a scientific trial yet.

`board_training_board_workers_v1.py` passed a two-worker replay of two native
board fixtures in 15.406 seconds. Model/tree/value records matched exactly,
requests were semantically identical, CPU worker CUDA visibility was disabled,
and the parent's CUDA setting was unchanged. The first worker-control attempt
incorrectly required identical byte hashes for JSON requests produced by two
different serializers. Native records had already matched. V2 verifies each
request's own hash and compares parsed request content. The failed control and
its original registration are preserved; the worker implementation was unchanged.

The next complete control is defined in BOARD-TRAINING-PIPELINE-CONTROL-PLAN.md.
It includes actual physical target processing and GPU fits, two deliberate
interruptions, complete recovery, a replay with a different physical-worker
count and CPU/GPU policy comparison. Passing it still requires independent
readback before a matched learning trial.

The queue `board_training_pipeline_queue_v1.py` waits for the existing complete
evaluation queue's successful result, including independent review. It then
renders `weighted_final_findings_v1.py` and, after checking GPU/production/RAM/
disk availability, runs the bounded GPU control. It does not interrupt upstream
work, overwrite outputs, retry failed stages or start a scientific training
experiment. It records the upstream PID and creation time, and verifies frozen
source bindings before dispatch. Visual review and interpretation of the final
study report remain agent work after rendering.

Future turns: inspect this queue's live PID and registration before manually
rendering the final report or launching the GPU control. Those tasks already
belong to the queue once it has started; do not duplicate them.
