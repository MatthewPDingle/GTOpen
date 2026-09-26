# Lossless storage feasibility for the next crossed-policy evaluation

All probes used three fixed, already-inspected batches from the previous 65,536-deal evaluation: first, middle, and last. They ran on the CPU in memory while the new training and scalar readback continued. No legacy archive was changed, no compressed copy was written to disk, and no new poker sample was drawn. The only new files are code, registrations, results, and this note.

| Layout | First batch | Middle batch | Last batch | Approximate payload for 2,048 similar batches |
|---|---:|---:|---:|---:|
| Existing per-member gzip | 3,202,216 B | 3,192,753 B | 3,208,104 B | 6.56 GB |
| Whole original bundle, XZ level 6 | 1,271,664 B | 1,269,608 B | 1,272,256 B | 2.60 GB |
| Whole original bundle, XZ level 9 | 1,245,232 B | 1,242,736 B | 1,245,564 B | 2.55 GB |
| Four distinct policies, binary64 byte planes, XZ level 6 | 984,724 B | 986,752 B | 987,160 B | 2.02 GB |
| Same, with exact probability-bit residuals | 796,740 B | 794,328 B | 798,920 B | 1.63 GB |

GB here means decimal gigabytes. Projections exclude filesystem allocation, manifests, active scratch, and other run outputs. They are not a storage admission or a guarantee that the new policies compress at the same ratio.

## What is preserved

The eight crossed profiles repeat four distinct policies, sharing their observation identities. The columnar representation stores those four policies and reconstructs the eight original profiles. It rejects a mixed profile if doing this would lose any difference.

Version 2 predicts the largest probability in each row from the other three, then stores the exact signed difference between the predicted and original binary64 bit patterns. The decoder restores that difference. It does not round probabilities or adjust them to sum to one. Exact reconstruction is checked against the entire original JSON byte stream, so number spellings, signed zero, action identities, and source strings must also survive unchanged.

All seven original files in each of the three sampled batches were restored byte-for-byte after compression and decoding. Controls also rejected a changed mixed profile, truncated input, trailing bytes, and noncanonical serialization. Original archived file hashes were rechecked after each probe. The version-2 profile transformation took about 3.0–3.9 seconds per batch, with another 1.4–1.5 seconds for compression in this concurrent workload.

Artifacts:

- `evaluation-lossless-xz-probe-v1-{registration,result}.json`
- `evaluation-lossless-columnar-probe-v1-{registration,result}.json`
- `evaluation-lossless-columnar-probe-v2-{registration,result}.json`
- `tools/research/crossed_profile_columnar_v1.py` and `crossed_profile_columnar_v2.py`

## Remaining gates

This is an in-memory codec qualification, not a qualified disk writer or scratch-retirement procedure. Before using it for new evaluation evidence, implement and test bounded durable writing, authenticated manifests, independent restoration, and refusal to retire any source that lacks a verified archive. The old reader must receive the exact reconstructed bytes, without silently treating this format as an old gzip archive.

Only newly owned evaluation scratch may be retired after readback. Existing legacy evidence remains untouched. Confirm the final actual training footprint and allocated storage before admitting evaluation. The active training controller retains its existing 4.25 GB output guard; model objects and recovery files must be included alongside batch archives when projecting its final footprint.

No inference, learning rule, sample budget, statistical interval, or poker-accuracy conclusion changed in these storage probes.

## Durable writer and existing-reader control

The next gate passed in `columnar-evaluation-archive-control-v1-result.json`. The new writer saved a real batch of newly owned copies, flushed the archive, restored all original files, and only then published the manifest and retirement receipt. A 19,553,284-byte original batch became a 797,908-byte archive, excluding its small manifest and ownership records.

All seven files were byte-identical after restoration. The existing scalar evaluation checker consumed those restored bytes through the new reader and verified all 32 deals and 14,528 observations. It recomputed the original policy crossings, hashes, legal probabilities, payoff identities, and paired differences. This checks compatibility with the existing evaluation readback; it does not rerun GPU inference or native poker evaluation.

Negative controls rejected a missing durable receipt, wrong owner, parent traversal, changed temporary source, corrupted archive, changed archive behind a populated reader cache, unregistered batch/path, and ambiguous plain/archive evidence. The temporary originals survived failed retirement attempts. A simulated interrupted retirement, with one already verified duplicate removed, recovered successfully; repeating completed retirement was safe. Legacy source hashes were unchanged afterward.

The control took 26.72 seconds on CPU. Its new output root is `S:/GTOpen-research/columnar-evaluation-archive-control-v1`; it is a small control artifact, not a new evaluation run. New source modules are `owned_columnar_evaluation_archive_v1.py` and `columnar_evaluation_archive_control_20260926.py`.

Actual fresh evaluation remains gated on completed and audited training, full-bank inference checks, the prospective statistical protocol, and allocated-storage admission. No existing archive has been migrated to this format.
