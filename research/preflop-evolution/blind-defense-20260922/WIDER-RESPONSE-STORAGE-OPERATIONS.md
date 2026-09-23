# Storage operations during the fixed wider evaluation

23 September 2026. The evaluation retained its registered model, streams,
sample counts, decision rule, confidence procedure and 40 GB disk reserve.

During evaluation, volume free space fell faster than the sum returned by
Windows' compressed-file-size API. At about 74,000 combined training/test
deals, the active store contained about 32.35 GB of logical files with 12.58 GB
of reported compressed allocation, while volume free space had fallen from
89.61 GB to 44.17 GB. The cause of the extra volume consumption is unresolved.
Neither compressed allocation alone nor the initial admission extrapolation
adequately predicted this run's volume-wide space requirement.

Two bounded probes touched only already completed training batches:

- Flushing 384 files in the first 64 completed batches preserved all bytes,
  lengths and last-write times. Volume free space changed by only about 2.4 MB.
- Forcing lossless NTFS recompression of 192 files in the first 32 completed
  batches also preserved all bytes, lengths and last-write times. The free
  space change was only about 4.6 MB.

Concurrent test writes affect these small volume-wide differences. Neither
probe demonstrated useful space recovery. They do not establish a filesystem
cause. They also mean elapsed evaluation time includes external storage I/O;
this run should not be used as a clean speed benchmark.

To provide room without changing or restarting the experiment, the separate
`completed-evidence-reserve-v1` operation was registered to losslessly compress
nine explicitly completed, independently audited older study stores. It
checks every decoded file hash, length, path and last-write time before and
after each directory. It does not delete or relocate evidence and does not
touch the current candidate's training store or the active evaluation store.
Its terminal result and status determine whether that operation succeeded;
this note alone is not a completion claim.

Evidence: `later-average-wider-study-v1-flush-probe.json`,
`later-average-wider-study-v1-storage-reclaim-control{,-registration}.json`,
and the `completed-evidence-reserve-v1` registration, manifests, logs and
terminal status/result when available. The original study controller retains
its resource checks and will stop if its reserve is breached.

## Terminal outcome

The original evaluation stopped at its disk-reserve check after 7,501.64 seconds.
All 43,264 training deals and 34,752 test deals had complete retained batches;
the next test batch is partial. No final result or confidence interval was
produced. Both evaluation processes exited and the original run is preserved.

The first older store finished compression and passed verification of all
8,706 files. Its reported allocation became 4.43 GB for 10.98 GB logical data.
However, volume free space fell to 38.92 GB during subsequent verification,
despite having temporarily risen above 48 GB. The reserve operation was then
explicitly stopped before compressing the second folder. No child compressor
was present. This contradicts treating NTFS compression as dependable reserve
recovery on this volume. The cause is still unknown; no system storage settings
were changed. See `completed-evidence-reserve-v1-operator-stop.json`.

Next: build and validate an explicit recovery protocol on T:, which currently
has roughly 272 GB free. Preserve the failed S: run. Reuse only hash-verified
complete batches, replay the original random streams, reconstruct the identical
frozen responder before processing test data, and finish exactly the originally
planned sample count. Admit space using uncompressed bytes with a generous
volume-wide margin. A new attempt identity and passing recovery controls are
required before launch; do not restart the original controller or silently
extend its budget. An interrupted study is not a poker-strength result.
