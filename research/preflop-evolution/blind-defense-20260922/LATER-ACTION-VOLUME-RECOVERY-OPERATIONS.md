# Prepared storage continuation — not yet qualified or launched

The live replication still writes to T: under its original 40 GB free-volume
floor. These new programs do not edit that trial, its supervisor, or any frozen
source. No older save/archive compression is performed here.

If the original pipeline stops, the following sequence preserves the scientific
trial rather than starting a new seed or reducing its 78-update budget:

1. Confirm the original controller, GPU worker, and supervisor are terminal.
   Preserve their logs, final statuses, resource history, and incomplete files.
   The current supervisor stops its other owned child on failure, so the first
   trial's CPU audit may also need a separately recorded recovery attempt.
2. Run `hu_later_action_prefix_audit_20260925.py --run`. It takes the latest
   durable checkpoint pointer, verifies the complete prefix from generation
   zero, and retains the original planned count. It charges the entire old
   controller runtime, including the unfinished update, against the original
   six-hour training allowance. It cannot run while the original trial is live.
3. With the GPU lock free, run
   `hu_checkpoint_volume_replay_control_20260925.py --run`. This copies the
   audited pilot's generation-1 checkpoint into a newly compressed directory
   on S:, then executes the unchanged generation-2 update. The checkpoint,
   native artifacts, fit results excluding timers, full reservoirs,
   accumulators, played bank, and next random streams must match the original.
   Its fixed 400 MB allowance is charged in addition to the two preceding
   storage controls. This control is prepared; it has not passed yet.
4. Only after both checks pass, run
   `hu_later_action_volume_continuation_20260925.py --run`. A fresh global
   inventory must admit the copied state, remaining updates, 8 GB evaluation
   reserve, and 2 GB metadata reserve within 800 GB. It copies only the latest
   checkpoint's dependency closure. Earlier raw evidence stays on T:. The
   original batch identifiers, seeds, configuration, fitter, and complete
   played history remain unchanged. There is no automatic retry.
5. After all 78 updates complete, run
   `hu_later_action_segmented_review_20260925.py --run`. It reconstructs every
   update across the two explicitly registered storage segments. Passing a
   partial-prefix audit never replaces this full audit.
6. Restore the unchanged complete-policy evaluation sequence using the audited
   complete trial identity. The existing automatic supervisor and evaluation
   prefix mapping must not be silently repointed. Record the identity-routing
   amendment before the heldout seed is drawn. Both seed pairs, all eight
   profiles, all 65,536 heldout deals, and the original one-look analysis remain
   required. No partial quality claim or deployment follows from recovery.

New S: work reserves 40 GB on its destination volume. Its T: guard reserves
1 GB for bounded small metadata, because the old T: training evidence is only
read. This does not lower the existing live T: worker's 40 GB threshold.

The three launch preflights were exercised while the original replication
controller was alive. Each refused before creating a registration or output
store, and the original process remained live. See
`volume-recovery-active-owner-gate-check-v1.json`. This is a safety gate check,
not proof that GPU replay or continuation has passed. Syntax checks passed;
the existing split-history pilot audit and four corruption/boundary tests are
documented separately in `SPLIT-HISTORY-READBACK-FINDINGS.md`.
