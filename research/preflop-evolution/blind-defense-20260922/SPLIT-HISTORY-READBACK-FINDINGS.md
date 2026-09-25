# Independent verification across storage volumes

The two-update later-action pilot can now be independently checked with update
1 on T: and update 2 on S:. The test passed in 124.969 seconds, reconstructing
1,024 root decisions, 22,835 postflop learning targets, and all 24,856 reservoir
insertions. Its counts and numerical error summaries exactly matched the
original independent pilot audit.

The test copied 274,491,183 bytes of update-2 evidence into a new directory on
S:. Its checkpoint objects came from the separately verified checkpoint-copy
control. Every original file remained in place and unchanged. No GPU, new
training samples, model fitting, or live trial changes were involved.

The new history reader uses explicit contiguous iteration segments. It keeps
the original configuration's planned update count, distinguishes a prefix from
a complete history, and authenticates each update's native records and referenced
checkpoint objects. The numerical reconstruction loop was checked against the
original reader's syntax tree: only the source locations and surrounding
iteration bound changed. All numerical calculations and assertions in the loop
remain identical.

Four additional boundary tests passed: missing/overlapping history segments,
incorrect iteration identity, corrupted checkpoint objects, and changes to
native evidence after its snapshot are refused.

The 350 MB copy allowance was charged on top of the registered full replication
and evaluation projection, together with the earlier 250 MB checkpoint-copy
allowance. The projected total remained below the 800 GB research budget.

This qualifies storage routing and complete pilot readback. It does **not**
qualify resuming the active training job on another volume. Before that can
happen, the old job must be terminal, its last durable prefix must be audited,
the remaining time and storage budget must be admitted, and a GPU continuation
replay must pass. No partial training history may substitute for the planned
78-update comparison. No strength or range-quality conclusion follows here.

Evidence: `split-history-readback-control-v1-registration.json`,
`split-history-readback-control-v1-evidence.json`, and
`split-history-readback-control-v1-result.json`. Registration SHA-256:
`12f78142ba88210e01d1657d40ddc5e6d6bf483113d4179f4b2ae9723e5f7c12`.
