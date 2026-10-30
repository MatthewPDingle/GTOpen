# River input reuse audit

The first seed's 30-round baseline and candidate continuations both finished.
Their recorded update times total 1,801.845 seconds and 5,544.326 seconds,
respectively (about 3.08 times as much for the candidate). These are descriptive
update timings, excluding some outer orchestration. Accuracy evaluation is pending.

A separate CPU-only diagnostic replayed archived A-river update 79, batch 00.
The first audit covered the first two chunks. The second covered the entire
19-chunk batch in its original history/selected order. Every native output
matched its archived byte count and SHA-256 exactly. Manifest coverage was
checked against all 38 archived requests, and the requested target-key set
matched the archived overlay. No new deals, inference, fitting or evaluation
were performed. The current scientific implementation and settings were unchanged.

| Diagnostic | Input rows | Unique rows | Repeated rows | Repeat share |
|---|---:|---:|---:|---:|
| First two chunks | 100,599 | 92,233 | 8,366 | 8.32% |
| All 19 chunks | 916,635 | 826,608 | 90,027 | 9.82% |

For the full batch, the larger history exports contain 821,558 input rows,
of which 30,142 (3.67%) repeat earlier inputs. The smaller selected-pair exports
contain 95,077 rows, of which 59,885 (62.99%) repeat. Existing native deduplication
already removes repeated keys inside each individual export.

Identity checks include every visible observation field. Own-history indices
are converted to their referenced global keys before comparison, so differing
batch-local indices do not masquerade as different states. A small remapping
check also verified that changing a prior action changes the identity.

This evidence does not justify expecting a large gain from caching whole policy
queries in this batch. It does not measure cache runtime, prove a percentage
speedup, or establish behavior across other batches. Feature-level reuse and
individual target-generation costs remain separate questions. A future cache
would still need model/context invalidation, bounded memory and numeric parity
checks before adoption.

Both audits used a single CPU worker with production-activity and memory guards;
the native exporter is sequential. The full audit took 47.656 seconds including
checks and used at most 431,087,616 bytes of sampled Python resident memory.
This is not a complete child-process peak or an isolated benchmark. The audits
overlapped continuation training; their exact wall-clock intervals are saved in
the results. Raw exports were checked in memory, not retained as new copies.

Evidence: `river-query-reuse-audit-v1-result.json` and
`river-query-reuse-audit-v2-result.json`, plus their corresponding versioned
scripts in `tools/research`. Both include the pinned fixture, model, context,
native-executable and source-code identities. The main continuation remains live;
completion of the second seed, fresh evaluation, and independent final review are still required.
