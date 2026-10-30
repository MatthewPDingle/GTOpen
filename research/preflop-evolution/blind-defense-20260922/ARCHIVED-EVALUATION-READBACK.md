# Complete evaluation readback from compressed batches

25 September 2026. This is a storage/transport control on existing evidence,
not a new poker experiment or a change to either live matched training trial.

The completed `root-retained-wider-cpu-control-v1` fixture contains 338 training
and 128 population-test deals in 30 batches. A new, separate copy retains its
batch evidence as gzip members with compressed and original byte hashes, plus
authenticated manifests. Original files and metadata were left unchanged.

`wider_root_readback_v3.py` preserves version 2's scalar statistical checks and
adds injectable artifact access. `archived_evaluation_reader_v1.py` verifies
the manifest identity, bounded decompression and original hashes before the
readback parses bytes. No archive extraction or original-file deletion occurs.

The control passed three complete readbacks: the old reader on original files,
the new reader on original files, and the new reader on compressed batches.
All returned identical results: both chance streams, 169 response choices,
both stability halves and all six final intervals reconciled. Maximum scalar
error remained 1.14e-13 bb. A separate byte-for-byte check covered all 195
original files. Five invalid manifest/path cases were rejected.

| Representation | File bytes |
| --- | ---: |
| Original logical evidence | 193,561,122 |
| Original recorded NTFS compressed allocation | 56,433,576 |
| New gzip copy, including manifests and metadata | 25,017,569 |

The new copy is approximately 13% of the original logical size and 44% of the
original recorded NTFS allocation. These are fixture measurements, not a
general compression guarantee. This control **adds** about 25 MB because it
preserves the originals; it does not reclaim existing research storage.

Execution took 227.515 seconds including a fresh inventory of all three research
roots, copy/archive creation, full readbacks and integrity checks. Admission
reserved this control's entire 500 MB cap, the queued trial's entire 12 GB cap
and the existing 2 GB margin within the 800 GB research ceiling. It used no GPU,
new poker deals, model fitting or production changes.

Evidence: `archived-wider-readback-control-v1-registration.json` and
`archived-wider-readback-control-v1-result.json`. The existing registered runs
retain their original formats and readers. This does not establish range
accuracy or explain the earlier volume-wide free-space discrepancy.

The separately versioned writer and native integration have now passed the
additional controls recorded in ARCHIVED-EVALUATION-WRITER.md. New owned native
temporary files are released only after verified archive publication. Existing
evidence is not retrofitted or deleted. Future large evaluations still need
prospective statistical plans and independent resource admission; power-loss
recovery and arbitrary larger-tree geometry are not established by these tests.
