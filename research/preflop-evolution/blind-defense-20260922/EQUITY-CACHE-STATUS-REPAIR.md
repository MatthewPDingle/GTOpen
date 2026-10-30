# Equity-cache controller status repair

The first `complete-private-allin-cache-v1 --run` attempt failed before creating
an enumeration directory or calculating any equity cases. Its status writer used
the immutable-artifact `save` helper, which opens files exclusively, to update the
already existing prepared status. The same error in the final status write then
prevented lock cleanup. The prepared status is preserved, with the actual failure
recorded in `complete-private-allin-cache-v1-launch-failure.json`.

The recorded owner PID 22028 was verified absent, the enumeration directory was
verified absent, and only that dead owner's research lock was released. No worker
was killed and no computation result was discarded.

The v2 controller changes status updates to an atomic temporary-file replacement
and makes lock cleanup unconditional even if the final status write fails. A
three-transition prepared/running/complete control passed. Cache-building logic,
private population, reviewed source caches, equity evaluator, numeric checks,
resource caps and independent review calculations are unchanged. All 28,438
reviewed cases are reused and the same 19,040 remaining cases are enumerated.

V2 has a separate registration, store and results. The exhaustive BTN and BB
fold/shove endpoint scripts also receive separate v2 names and output paths to
admit the v2 cache. Their policy selection and mathematical calculations are
unchanged. The stopped v1 follow-through queue is not restarted or rewritten.
