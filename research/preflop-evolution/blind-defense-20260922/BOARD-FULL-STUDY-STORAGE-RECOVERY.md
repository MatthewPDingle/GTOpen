# Space recovered for the complete board-root experiment

The first admission correctly refused a projected 847.662 GB against the 800 GB
research ceiling. The projection includes all 152 remaining learning updates,
full buffers, growth margins and evaluation/readback reserves. The experiment
was not shortened and its future-compression credit remains zero.

The following completed evidence was compressed transparently in place:

| Completed evidence | Files checked | Bytes recovered |
| --- | ---: | ---: |
| Wide replay checkpoints | 16 | 38,969,093,504 |
| Wide maturity snapshots | 4 | 5,585,197,920 |
| Population diagnostic and board-precision repeat | 5,480 | 5,444,694,064 |
| **Total** | **5,500** | **49,998,985,488** |

These are measured sums of before/after file allocation, not a claim about
drive-wide free-space change. No file was deleted, relocated or renamed.
All logical hashes, lengths and modification times were checked before and
after, then independently read again. Hard-linked files and redirected paths
were excluded. Original binary snapshot hashes came from the historical
successful reviews. A first replay progress-publication failure and its partial
receipts are retained; version 2 reused verified work and completed the job.

Evidence:

- `completed-wide-replay-preservation-v2-independent-review.json`
- `completed-wide-maturity-preservation-v1-independent-review.json`
- `completed-precision-evidence-preservation-v1-independent-review.json`

The operation changes physical storage and future I/O timings, not model content
or the scientific endpoint. It does not establish better ranges or repeat native
checkpoint restoration. Production remains unchanged. The unchanged full-study
admission is rerun under the separate `after-preservation` attempt; its actual
result, rather than these savings alone, determines whether training may start.
