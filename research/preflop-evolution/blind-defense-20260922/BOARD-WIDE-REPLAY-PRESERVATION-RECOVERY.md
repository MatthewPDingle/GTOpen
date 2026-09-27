# Compression progress publication recovery

The first bounded compression attempt stopped after 85.719 seconds because its
second progress update used immutable publication instead of explicit progress
replacement. Three per-file compression receipts were already complete and are
preserved. No source checksum mismatch was reported. The parent and all compact
workers were confirmed absent before recovery.

Version 2 keeps the original script, registration, failure and receipts. It uses
the qualified atomic publisher's explicit `replace=True` only for its own new
mutable status file. All registrations, per-file receipts and final results
remain immutable. Recovery binds the old failure and inputs, retains the old
allocation baseline, and checks each old receipt against the current full hash,
size, modification time and allocation before reusing it. Unreceipted files are
fully checked against their original historical hash before compression.

The operation, exact sixteen paths, historical hashes, four workers and all
resource limits remain unchanged. A separate version 2 readback will independently
hash the sixteen logical files after completion and reconcile allocation totals.
Actual savings and full-study admission remain unproven until those stages pass.
