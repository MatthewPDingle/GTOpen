# Finite handoff for the already registered comparison

Version 2 additionally handles a normal subprocess exit racing process identity
inspection. An authoritative completed child handle wins that race; a genuinely
live handle with a mismatched identity still requires review. Preserve the first
version's ordering qualification. Neither version has launched scientific work
as part of software qualification.

The active trainer and its four workers remain unchanged. A separate small
observer waits for those exact process identities and terminal evidence. It
does not start another training invocation while the current one is live,
replace an existing owner, change admission gates, or restart a failure.

The original trainer has a 12-hour invocation bound checked only between
complete cycles. If it exits successfully at that boundary, the handoff checks
the unique invocation, each successful arm outcome, and the exact hashes of
published progress files. It then invokes the unchanged qualified trainer
again, continuing the same streams/checkpoints/cycle order toward 64 cycles.
This is continuation of completed work, not repetition of a partial cycle.
The original total 72-hour training deadline remains enforced. A missing,
failed, incomplete or ambiguous terminal record requires review.

After all four actual banks have completed 64 cycles, ownership is released and
resources are available, the handoff runs these existing qualified consumers:

1. `stack_context_final_bank_throughput_v2.py --run`: the retained-hand actual
   complete-bank CUDA/reference resource gate.
2. `stack_context_matched_evaluation_v3.py --run`: the registered fresh
   4,096-deal/seven-depth comparison, admitted only by that consumer's gates.
3. `stack_context_matched_readback_v4.py --run`: independent evidence readback.

Each consumer enforces its original qualification, immutable input identities,
model/chance selection, storage/resources and scientific gates itself. The
handoff adds ordering and ownership checks; it cannot replace those controls.
The supervisor stops if an admitted consumer ends without its required result,
including a partial evaluation needing explicit review. It does not resume
that evaluation automatically. A wholly unstarted, explicit resource deferral
may be polled again; an attempt/registration/store proving actual admission
prevents that repetition. Every child invocation and its stdout/stderr hashes
are retained under a unique path, including failed launches.

The service-owned handoff is one demand-started Windows task, with no trigger,
automatic task restart or second active instance. Its own immutable attempt
and owner marker refuse duplicate launch even if Task Scheduler is invoked
again. It waits quietly with low process priority. Admission uses the existing
light-desktop/video sharing policy and yields to active production/heavier
work. No app is stopped. An admitted child is never terminated because an
observer timeout or the handoff admission window elapsed. A new child must
start within 96 hours of this handoff's start; each scientific consumer keeps
its own original deadline. No actual scientific attempt is retried.

Successful handoff means only that the ordered registered consumers completed.
The plain-English scientific analysis still needs to be written. The separate
prediction diagnostic, production readiness, full preflop/GTO Wizard/multiway
accuracy and broad goal completion remain outstanding. No new scientific
trial, production change on 56708, GitHub push, deployment or Jev work is
performed. Preserve all old and new failures.

Qualify the ordering/boundary controls against synthetic states and retained
successful fixture metadata before starting this observer. Do not call those
software controls an actual full-bank resource or scientific evaluation result.
