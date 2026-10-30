# D007 lifecycle diagnostic design

Prepared as a patch artifact only. No active checkout was edited, and no build,
GPU execution, or deployment was performed.

## Files and scope

- `lifecycle-diagnostic.patch`: conditional instrumentation of only
  `crates/solver/src/gpu/mod.rs` in the research checkout.
- `base-mod.rs`: exact source bytes used to prepare the patch.
- `candidate-mod.rs`: proposed source, for review; do not copy this whole file
  over a checkout containing later work.
- `manifest.json`: source/candidate/patch hashes and static validation results.
- `prepare_patch.py`: reproducible artifact generator. It refuses existing
  outputs and checks the active source remains unchanged.

The patch preserves solver arithmetic, loop order, transfer order, allocation
sizes/flags, and existing synchronization calls. It does not touch the frozen
benchmark, kernels, save format, or production checkout. The completed
`GpuSolver` is assigned to a local before return solely to mark construction.

## Recorded intervals

Set `POSTFLOP_AUTORESEARCH_LIFECYCLE_PROFILE=1` before starting the diagnostic
process. Every other value disables the timers and output.

Each completed operation emits one stderr line beginning `LIFECYCLE_PROFILE `,
followed by JSON. `phase` identifies `init`, `full_readback`, or
`caller_synchronize`. Records are ordered within each thread. Associate them
with the existing benchmark's `fixture_start`, `gpu_ready`, and
`timing_complete` messages. A failed constructor/readback can return before
emitting its completed trace; preserve the ordinary error log too.

| Phase | Intervals |
|---|---|
| Initialization | Plan and budget; context/stream/device information; cached PTX acquisition or compilation; module load; pinned allocation; arena layouts; four arena upload calls; lock/fold tables; function lookups, metadata uploads, and work-buffer allocation submissions |
| Full readback | Initial stream wait; for each player and each arena, DTOH host API call, existing stream wait, and CPU encoding/scatter/restoration; final iteration/symmetry publication |
| Public synchronize | The existing stream wait only, including its result status |

`dtoh_host_call` is CPU wall time spent in the copy API. It can include driver
blocking; it is **not** a measurement of GPU copy duration. `dtoh_stream_wait`
is time in the already-existing completion wait. Their sum is a useful
transfer-plus-wait interval, with small instrumentation overhead between them.
The local cudarc implementation issues `memcpy_dtoh_async`; plain host slices
do not add a synchronization, so the explicit existing wait remains necessary.

The final initialization interval can leave asynchronous work outstanding.
The first `caller_synchronize` record before `gpu_ready` measures the existing
caller wait. Initialization logging occurs before that wait and can let pending
device work progress, shortening the wait. Do not interpret the host submission
span or the residual wait as a standalone device-duration measurement.

The `bytes` field means pinned allocation size for the allocation span, logical
device arena bytes for initialization uploads, and actual copied bytes for DTOH.
E004 zero initialization does not transfer those logical arena bytes over PCIe.
For encoding spans, bytes describe the downloaded input image; inactive CPU
restoration traffic is additional. Active encoding and inactive restoration
remain combined in this first, minimal diagnostic. `sync_strategy` is outside
this patch because the frozen complete-cycle benchmark uses full readback.

## Apply only after E006 work has finished

Run these commands sequentially from PowerShell. They target the research
checkout, never `X:\Dev\GTOpen`:

```powershell
$diagRoot = 'S:\GTOpen-research\postflop-gpu-20261016\runs\D007-lifecycle-design'
$diagRepo = 'X:\Dev\GTOpen-gpu-research-20261016'
$diagPatch = Join-Path $diagRoot 'lifecycle-diagnostic.patch'
$diagSource = Join-Path $diagRepo 'crates\solver\src\gpu\mod.rs'
$diagManifest = Get-Content -LiteralPath (Join-Path $diagRoot 'manifest.json') -Raw | ConvertFrom-Json
if ((Get-FileHash -LiteralPath $diagPatch -Algorithm SHA256).Hash -ine $diagManifest.patch_sha256) { throw 'Diagnostic patch hash mismatch' }
if ((Get-FileHash -LiteralPath $diagSource -Algorithm SHA256).Hash -ine $diagManifest.source_sha256) { throw 'Source changed; review/rebase the diagnostic hunks first' }
git -C $diagRepo apply --check $diagPatch
if ($LASTEXITCODE -ne 0) { throw 'Patch check failed' }
git -C $diagRepo apply $diagPatch
if ($LASTEXITCODE -ne 0) { throw 'Patch apply failed' }
$env:POSTFLOP_AUTORESEARCH_LIFECYCLE_PROFILE = '1'
```

After an independent patch review, use the existing build/provenance workflow
to produce a separately named diagnostic binary. Run the unchanged primary
fixture suite through the existing serialized GPU runner under its
`gpu-run.lock`, with a diagnostic experiment ID. Preserve the emitted state
fingerprints and compare them with E004 controls. Keep the runner's fixed
fixture order, storage, convergence target, and Rayon thread setting.

Do not use this instrumented run for acceptance or speedup claims. The runner
inherits the environment variable; its benchmark parser should continue to
consume the unchanged `AUTORESEARCH_RESULT` records. Keep the lifecycle lines
as diagnostic evidence alongside the ordinary stage records.

## Remove without discarding unrelated changes

```powershell
Remove-Item Env:\POSTFLOP_AUTORESEARCH_LIFECYCLE_PROFILE -ErrorAction SilentlyContinue
git -C $diagRepo apply -R --check $diagPatch
if ($LASTEXITCODE -ne 0) { throw 'Reverse patch needs review; do not overwrite the source' }
git -C $diagRepo apply -R $diagPatch
if ($LASTEXITCODE -ne 0) { throw 'Reverse patch failed' }
git -C $diagRepo diff -- crates/solver/src/gpu/mod.rs
```

Check the source hash against the manifest if no other work touched that file.
Rebuild and attest any subsequent qualifying binary after removing the patch;
unsetting the environment variable does not remove instrumentation from an
already-built diagnostic executable.

## Source-based overhead estimate

These are operation counts, not measured latency estimates:

- Disabled: one environment lookup per instrumented method call, empty vector
  construction with zero capacity, and conditional checks. No clock reads,
  trace-buffer heap allocation, or JSON output.
- Enabled initialization: 9 marks, 11 monotonic clock reads including start
  and finish, one vector allocation reserved for 16 records, one JSON line.
- Enabled full readback: 14 marks, 16 clock reads, one vector allocation, one
  JSON line. Marking does not allocate individual records.
- Enabled public synchronize: 1 mark, 3 clock reads, one vector allocation,
  one JSON line.
- The frozen fixture calls public synchronize three times. Thus each fixture
  adds 36 clock reads, 5 trace-vector allocations, and 5 JSON lines, plus JSON
  formatting allocations and output. No timers run inside the iteration or
  per-node loops. The mark bookkeeping cost is included in adjacent intervals.

The source indicates bounded, small bookkeeping, but stderr/pipe output can
block for an unbounded duration. No defensible millisecond overhead figure is
available without execution. `wall_ms_before_logging` excludes that record's
JSON/output cost; the surrounding benchmark still includes it. Use this patch
to identify large stage costs, then remove it for paired performance tests.

## Decision target

The inspected E004 sample totals 11.184 seconds across three fixtures; a 2%
complete-cycle reduction needs about 224 ms. Its combined readback is 633 ms,
so readback alone would need roughly a 35% reduction. Pursue buffered overlap
only if transfer and CPU encoding costs support that amount of recoverable
wall time; investigate staging capacity only if pinned allocation is large.
This diagnostic does not establish either condition in advance.

Static checks passed: `git apply --check`, Rust syntax parsing through rustfmt
with child modules skipped, and equal synchronization/transfer/allocation-call
counts before and after. No compile/type check or runtime validation has run.
