# Continuous reservoir control v2

The v1 attempt completed every positive case, exact audit comparison,
source-weight/RNG check, negative-input rejection and save/load check. Its
final required overflow gate failed: actor 0 had 54 overflow insertions but
actor 1 had none, because reservoirs were reset for each one-deal case.
Preserve the v1 failure and all eight result artifacts. This is incomplete
qualification, not a passed integration control.

Version 2 keeps separate baseline/oracle/candidate reservoir pairs for each
policy continuously across source offsets 0..3. This exercises real batch
continuation and both actors' Algorithm-R replacement. Capacity stays 7;
all data, models, exact targets, source/native seeds and K=64 remain unchanged.
Use the original v1 fixture identity for native batch IDs and target draw seeds
so generation evidence stays directly comparable. Only output paths and the
control's reservoir lifetime change. Count overflow insertions incrementally,
not by repeatedly summing cumulative excess over capacity.

All original checks remain, including the requirement of positive overflow
counts for both actors, unchanged source weights and RNG versus baseline,
agreement with independent oracle insertion, unchanged original three audits,
all staged rows, rejection before mutation and checkpoint round trips. V2
does not omit any v1 case or alter a target based on results. It registers
the original plan, registration and terminal failure as inputs.

The original 300-second/512-MB/CPU-only limits apply to this version. Expected
additional raw evidence is around the first attempt's 40 MB. No fitting,
deployment, GPU work, push or deletion. Fresh range-quality testing still
follows, after qualified integration and bounded storage transport.
