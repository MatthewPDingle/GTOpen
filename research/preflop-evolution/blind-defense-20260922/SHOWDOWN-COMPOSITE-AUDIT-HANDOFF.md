# Local handoff from training to independent audit

`showdown_composite_audit_handoff_v2_20260927.py --run` identifies the live
continuation worker and controller by PID, creation time, command, role, and
research-lock owner. It waits at most two hours for those exact processes to
terminate. Missing processes alone are not success: it requires the completed
78-update result, successful controller exit, final verified restore, unchanged
registration and audit sources, released research locks, and idle production.

Only then does it launch the existing independent composite auditor in a hidden
process. That auditor retains its full evidence gates and six-hour limit. The
handoff allows a further two minutes for process startup/exit. It does not start
evaluation, change training, retry failed work, or claim improved poker strength.
It is a local process pipeline, not a system service that survives a reboot.

The initial v1 handoff failed after 30 seconds because its status writer used an
exclusive-create helper for a repeated status update. It never launched the
auditor and did not touch training. Its source, registration, and failure result
remain preserved; its initial status file is stale. The v2 status writer uses the
same temporary-file replacement approach as the continuation controller.
Repeated waiting, auditing, and terminal status writes passed a local check; an
injected write failure preserved the previous valid status. Live process identity
and rejection of a mismatched creation time were also checked. These are handoff
checks only, not a scientific audit result.

Use the versioned handoff result and the auditor's own completed result for
completion evidence. A waiting status or a registered handoff is insufficient.

## Subsequent implementation-control handoff

`showdown_control_after_audit_20260927.py --run` now waits on the exact live
auditor and its supervisor. After both terminate, it requires the successful
handoff result and complete 78-update audit, including their registration/result
hashes. Only then does it launch the already prepared composite evaluator with
`--control`, followed by its independent scalar `control` review. The evaluator
keeps its own fresh resource admission and all four-bank provenance checks.

This stage is limited to the 64 previously inspected deals. It cannot launch the
65,536-deal fresh study and makes no strength claim. It refuses an existing
control attempt and does not retry failures. Its waiting allowance is 21,720
seconds; outer control/review process allowances are 15,000/21,720 seconds to
include startup and exit, without changing the children's own four/six-hour
limits. It preserves the source files it registered and stops on a failed child.

The live auditor identity and PID creation time were checked before launch.
The incomplete-audit success gate was exercised and rejected before creating
handoff artifacts. Status writing reuses the tested version-2 atomic writer.
Do not start a competing manual control while this handoff is live. Its result
and the child's result/review, rather than its waiting status, prove completion.
