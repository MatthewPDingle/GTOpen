# Final pipeline check recovered without retraining

The two-generation GPU integration control finished both training updates,
both deliberate interruption checks, and the deterministic replay with a
different worker count. Its final CPU/GPU comparison then stopped because it
passed the older native query transport directly to the policy reader.
That transport omits `own_history`.

The training pipeline already uses `first_action_view` for this transport.
It adds an empty history only at the initial BB decision and the BTN's first
response to a direct all-in. Those nodes structurally have no earlier own
action. It leaves all other observations and the saved native file unchanged;
it cannot reconstruct later histories or be used to average policies.

`board_pipeline_query_recovery_v1.py` completes the missing comparison using
that existing adapter and the original saved second-generation model. It
reproduces the missing-field error, checks that the adapter only annotates
those initial nodes, rejects an invented earlier action, verifies source and
artifact hashes, restores and compares the matching replay checkpoints, and
requires the original interruption evidence. No new deals, fits, policy
changes, or seed choices are involved.

The recovered comparison passed on **14,550 observations**, with maximum
CPU/GPU probability difference **2.89e-15**, below the original 1e-10 limit.
The recovery itself took about 10 seconds. All original failures and original
evidence remain intact. The completed control and pipeline queue results
explicitly link the separate recovery registration; the original failed
process is not represented as having completed normally.

This establishes mechanical integration only. The independent trained-state
audit is still required before the planned learning experiment. The separate
follow-up queue must be resumed explicitly, and the legacy global storage
scan used by the next study still needs the already qualified offline-server
activity check. No full training study or production deployment is authorized
by this control result alone.
