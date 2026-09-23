# Preserve completed evidence with less SSD space

23 September 2026. The S drive had about 77 GB free while the fresh averaging
trial was running. That met its 40 GB free-space guard but would constrain a
materially larger follow-up evaluation.

Native NTFS compression was applied only to the completed stores
`sampled-physical-hybrid-allin-evaluation-v1` and
`sampled-visible-hybrid-completion-evaluation-v1`. Both had completed independent
evaluation audits. The compressor ran without a window and at below-normal
priority. No files were deleted, moved, renamed or converted to a new research
artifact format. The active training store and production application were not
modified.

Every file was hashed before and after compression. The complete path sets,
decoded bytes, sizes and last-write timestamps match: 8,706 files per folder,
17,412 total. Original readers and hash references therefore remain valid.

| Completed store | Logical data | Compressed data reported by Windows |
| --- | ---: | ---: |
| Combined 269-input evaluation | 10.815 GB | 4.231 GB |
| Visible 302-input evaluation | 10.828 GB | 4.250 GB |

The Windows summaries indicate about 13.16 GB saved. Drive-wide free space
increased from 77.16 to 90.15 GB; concurrent training writes account for some
of the difference. Compression and full verification took 262.97 seconds.
Training continued, although its overlapping iteration times are not suitable
for performance benchmarking; concurrent disk work can slow them down.

This is reversible with NTFS uncompression when sufficient space is available.
It changes storage attributes, not evidence bytes. New files in these completed
folders inherit compression; no new files are expected there. No strategic or
solver-performance claim follows. Future larger studies still require explicit
storage admission using measured free space rather than the earlier 800 GB
estimate.

Evidence: `completed-evidence-ntfs-compression-v1-registration.json`, both
full-file manifests and compressor logs, and the result/status JSON files.
