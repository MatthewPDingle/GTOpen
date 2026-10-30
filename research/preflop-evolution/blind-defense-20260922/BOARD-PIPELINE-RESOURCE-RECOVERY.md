# Recovery after the production app was offline

The fixed evaluation and its independent audit completed successfully. The
pipeline rendered the full report, then stopped before starting its GPU control.
The storage inventory used an older activity probe that always queried port
56708. That probe raised a connection-refused error while the app was offline.
The dependent prefix queue then stopped because its upstream queue had ended.

Both original failure records are preserved. No candidate training was started
by those failed queues. The completed evaluation and report are retained.

`global_research_inventory_v2.py` keeps the existing allocation and link checks,
but uses the already established production-activity wrapper: a verified absent
listener is idle; a listening server must pass all activity API checks. Errors
are not treated as proof of inactivity. The new filesystem control passed and
also rejected active, unknown, and newly active production states.

`board_pipeline_resource_recovery_v1.py` resumes only the unstarted, unchanged
GPU control after fresh resource and global storage admission. It preserves the
old registration and failure, records its own source bindings and inventory,
and authenticates any eventual recovered pipeline result with both records.
It does not rerender the report, alter the learning method, start the full
78-generation study, or restart production.

The follow-up queue and later drivers still need an explicit recovery path for
their dependency checks and the same legacy inventory call. A successful GPU
control alone does not imply that those remaining stages have resumed.
