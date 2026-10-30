# Posterior64 control v2 preflight correction

The first attempt stopped before registration or computation with KeyError
`d000-9266201-board-root/new/export.json`. The archive manifest uses native
Windows separators; its lookup was accidentally constructed with slashes.
Preserve the v1 source and empty output directory. This new v2 runner uses
`str(Path(case)/relative)` to match the existing manifest exactly.

The mathematical implementation, case list, K=64, seeds, controls, 25% query
reduction gate, runtime and storage limits remain the original plan. No case
has been computed or inspected by v1. Add this correction to registered inputs.
