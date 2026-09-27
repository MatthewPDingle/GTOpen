# Preserve completed raw evidence with first-time NTFS compression

The fresh inventory exceeds the established research allocation ceiling. A
separate, bounded preservation operation is admitted to reduce physical disk
usage while preserving all scientific evidence. It changes no poker method,
model, source bytes, sample count, result or logical artifact path.

Scope is only `queries.json`, `profiles.json`, `policies.json` and `updates.json`
below seven explicitly named completed S:/GTOpen-research owners:
sampled-physical-dense-evaluation-v1, sampled-physical-allin-evaluation-v2,
sampled-physical-hybrid-evaluation-v2, sampled-physical-dense-pilot-v1,
sampled-physical-allin-pilot-v1, sampled-physical-hybrid-pilot-v1 and
sampled-physical-hybrid-allin-pilot-v1. The three evaluations have terminal
16384-deal results; the four training runs have terminal 78-generation results.
Verify those results, evaluation registration hashes, store paths and absence
of active owners before mutation. Hash the exact per-file manifest first.

Exclude current evaluation/queue registered inputs, every model/checkpoint
object, packed archive, user save and hand history. Reject linked/reparse paths.
No files may be deleted, moved or renamed. Only initially uncompressed files
are eligible. NTFS compression must preserve SHA-256, length and modification
time for every admitted file; record before/after file allocation.

Qualify eight representative copies first: smallest and largest admitted file
for each of the four names. Check hash/path rejection and exact logical bytes
after compression. The operation has four CPU/I/O workers, batches of at most
32 files, a two-hour invocation bound, a five-minute batch bound, a 64 GB logical
input bound, at least 20 GB available RAM and 40 GB free on S:. Start below 50%
CPU use with production idle. Retain completed per-batch journals for verified
resume after interruption. Keep processes hidden and preserve the active GPU
evaluation; no global GPU/training lock is taken because its evidence is outside
the admitted paths. A dedicated preservation lock prevents duplicate writers.

This corrective operation may create at most 100 MB of sample copies plus
manifests/journals despite the existing allocation overrun. It may not use that
exception to launch training or evaluation. Verify all final files again in a
separate readback and refresh the full inventory before new study admission.

Original logical hashes remain valid. Historical storage throughput measurements
for these directories no longer describe their newly compressed physical form;
any later benchmark must disclose that change. Actual savings are measured, not
assumed. This amendment supersedes the earlier prohibition on changing legacy
storage only for the exact manifest admitted here.
