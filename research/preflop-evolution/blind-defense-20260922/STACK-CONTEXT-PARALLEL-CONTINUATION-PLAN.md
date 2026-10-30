# Parallel continuation of the admitted matched-stack study

The user requested parallel comparison runs and better use of the 5950X,
128 GB RAM and 24 GB RTX 3090 on 2026-09-30. Light desktop and video playback
may share the machine; active solves and heavy workloads still take priority.

The four arms are independent. A cycle within an arm depends on its preceding
model and must remain sequential. Run up to four separate arm coordinators,
each using the existing four CPU target workers, one CPU board worker, and
the original CUDA inference/fitter. This permits up to twenty CPU target/board
workers plus the coordinators. Actual throughput must be measured after the
handoff; no fourfold speedup is assumed from hardware utilization alone.

Preserve the original registration and every existing checkpoint. The adapter
calls the original training loop with only its process-local arm order narrowed
to one arm. It does not change the cycle update, contexts, data, seeds, sample
budgets, reservoir insertion order, fitting arithmetic, 64-cycle horizon, model
averaging, held-out depths or final evaluation gates. The original 72-hour
scientific deadline remains in force. There is no fresh scientific attempt and
no recollection of an already started cycle.

Qualify process-local scheduling and boundary draining, then check simultaneous
CUDA inference in four processes against the serial full-policy reference using
the actual retained first-cycle models and existing native preflop catalogs.
This qualification does not fit models or draw scientific hands. It does not
establish a full-cycle speedup or independently replay concurrent fitting.
Existing deterministic CUDA fitting and process isolation remain assumptions
to monitor; per-arm source/model/stream identities continue to be enforced.

The existing serial runner has no cooperative early-stop input. Preserve it
until its already-registered 12-hour invocation ends at a completed, archived
cycle boundary (approximately 2026-09-30 23:18 Adelaide). The handoff helper
must retain the actual Windows process handle for PID 32368, creation time
1790732866.143808, observe exit code zero, verify its terminal boundary status
and released lock, and reject any failure or partial next-cycle directory.
Do not inject code, edit registered sources, kill the live trainer or launch
a second owner into the same arm. If observation times out, keep waiting on
the same handle. A missing or abnormal process without exit proof is not a
successful handoff.

Before parallel admission, save a separate operational amendment. Each CUDA
process retains the existing 2 GB allocation limit; combined maximum is 8 GB.
Require at least 12 GB free VRAM and 40 GB available RAM at admission. Preserve
the existing running RAM, free-SSD, active-solve and heavy-GPU guards. Isolate
per-arm status files and use one supervisor for global storage measurement.
Reserve 70 GB of new logical study evidence rather than 45 GB to accommodate
simultaneous raw cycles, only if the existing 800 GB allocated research cap
permits it. Leave at least 40 GB free on S:. Historical evidence is untouched;
retirement still applies only to verified new duplicate cycle files.

The supervisor owns the research lock. On a peer error it tells the other arms
to finish their current cycle and stop before starting another. Preserve every
failure and do not automatically retry partial scientific work. Normal
twelve-hour parallel invocations may continue only from complete checkpoints.
The prepared evaluation and independent reader must record the amendment in
their final provenance before scientific interpretation.

No production 56708 changes, GitHub push, deployment, new scientific design,
test-selected checkpoint, accuracy claim or broad-goal completion is authorized
by this scheduling change.
