# New-batch archive publication and temporary-file release

25 September 2026. This extends the verified reader described in
ARCHIVED-EVALUATION-READBACK.md. Neither registered training trial was changed.

`wider_root_evaluation_v3.py` preserves version 2's sampling, fitted responder,
six alternatives and statistical calculations. It writes each new native batch
to an explicitly owned temporary directory, archives its complete evidence,
flushes and verifies the archive, and publishes a receipt before releasing the
temporary copies. Completed evaluation results include all manifest identities.

`owned_batch_archive_v1.py` uses a new owner identity and batch claims. Cleanup
authenticates every archived member, verifies the remaining temporary files,
checks resolved absolute targets, then removes only those exact files. It never
recursively deletes or adopts an existing source directory. Completed receipts
allow interrupted cleanup to resume; a missing receipt cannot authorize it.

The CPU-only control replayed the existing 30-batch fixture through the complete
new evaluation loop. It reused the recorded native payoffs; it did not call a
solver or draw new poker samples. All non-timing numerical results matched the
original evaluation exactly. The full scalar readback also matched: 338 training
deals, 128 test deals, 169 class choices and all six confidence intervals.
All 195 original evidence files remained byte-identical.

Eight lifecycle controls passed: missing receipt, interrupted cleanup, repeated
completed cleanup, damaged archive, changed temporary file, wrong owner,
out-of-root batch name, and existing batch. The interrupted-cleanup control
stopped after one temporary file removal, reopened the owner, and successfully
finished from the authenticated archive. Corruption cases retained their
remaining temporary files. Intentionally damaged **new test fixtures** are
preserved separately from the valid evaluation.

The maximum observed new-file footprint was 40,625,430 bytes, including the
retained failure fixtures. Runtime was 222.5 seconds including global storage
admission and integrity checks. Admission reserved 500 MB for this test plus
the queued trial's full 12 GB and the existing 2 GB margin. No GPU or production
session was used.

Evidence: `archived-evaluation-writer-control-v1-registration.json` and
`archived-evaluation-writer-control-v1-result.json`.

This establishes the fixture replay and temporary-file lifecycle, not a new
range-quality result. Native inference through the new directory layout still
needs a small integration check before a fresh large evaluation. The control
does not establish power-loss durability, automatic evaluation restart, a
worst-case large-tree compression ratio, or a cause for the earlier free-space
discrepancy. Existing evidence has not been migrated or removed.
