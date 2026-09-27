# Evaluation queue after stratified training

The hidden queue is tied to the admitted trainer and training-audit process
identities. It waits for their completed results, then runs these stages:

1. Full 78-policy CPU/GPU equivalence control on reused deals.
2. Independent scalar review of that control.
3. The fixed 65,536-deal comparison using the recoverable v2 driver.
4. Independent review of every evaluation batch and the final statistics.

CPU activity, available RAM and production activity are checked before each
stage. GPU stages additionally require the exclusive research lock, low GPU
activity and adequate free VRAM. The queue does not restart a missing upstream
process or automatically retry a failed stage. Failure preserves evidence for
inspection; an interrupted study can subsequently resume its committed prefix.
The overall queue has a 24-hour bound, with shorter per-stage limits.

The routed reader passed a control spanning two real archive attempts, 64 reused
deals and 29,077 observations. Serial and parallel results matched exactly;
independent scalar statistics differed by at most 2.14e-14. The reader rejected
an escaping archive route, a missing initial batch, a wrong owner and a changed
summary identity. It used no GPU and drew no new evaluation deals.

The final study reviewer is prepared but has not reviewed new stratified results.
Its missing-evidence rejection was checked with only the CPU utilization probe
mocked; its ordinary resource guard also correctly declined an observed CPU
spike. The full numerical and scientific gates remain mandatory.

Queue script: `weighted_complete_evaluation_queue_20260927.py`.
Registration and redirected log: `weighted-complete-evaluation-queue-v1-*` and
`weighted-complete-evaluation-queue-v1.log` in this directory. Each stage gets a
separate log. Mutable progress files and empty logs do not prove a process is
live; verify the process identity when checking status.

Completing the queue does not establish general preflop accuracy. Interpretation
of the fixed comparison, remaining uncertainty and next research steps are still
required after independent readback.
