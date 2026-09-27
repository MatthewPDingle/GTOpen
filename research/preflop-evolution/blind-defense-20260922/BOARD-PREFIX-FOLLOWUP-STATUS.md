# Follow-up queued, numerical qualification still pending

The hidden follow-up queue was started on 27 September 2026 at 21:01 Adelaide
time. Its registered upstream is the original pipeline queue, PID 5428 created
at 18:53:51. The new queue is PID 21036. These are launch records, not a claim
that the processes will remain live; verify their creation times and commands
before any later process action.

`board-prefix-followup-queue-control-v1-result.json` passed all seven synthetic
driver cases in 0.516 seconds: ordered success, waiting for busy resources,
changed upstream process identity, changed source, a failed stage, a changed
previous result and child timeout. Only the simulated child and its descendant
were terminated in the timeout case. No real subprocesses or GPU work were
launched by the control. Its 135 fixture files total 81,081 logical bytes.

The actual unqualified CUDA control also rejected execution before resource
probing while the genuine training/readback results were missing. Its import
check left CUDA visibility unchanged and did not import Torch. This validates
waiting and refusal behavior; the numerical CPU/GPU comparison has not run.

The queue now waits for the original evaluation and pipeline stages. It then
performs the sequence in `BOARD-PREFIX-FOLLOWUP-PLAN.md`, including the already
specified two-generation prefix and independent audit. It does not launch the
full 78-generation study or deploy a model. The source-bound queue registration
is `board-prefix-followup-queue-v1-registration.json`; future completion or
failure has the same prefix with `-result.json` or `-failure.json`.

At the preceding live check the current evaluation had completed 54,272 of
65,536 deals (82.8125%). This is progress only, not an interim outcome analysis.
