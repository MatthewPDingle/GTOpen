# Read-only benchmark/API discrepancy audit

**Resolved setup discrepancy:** parent subsequently verified the frozen sourcecache header is20000samples, while the APIbaseline and preview-api-a privatecache headers are1024. The prior APIrunner pinned`PREFLOP_EQ_SAMPLES=1024`, causing`EquityTable::load_or_build` to regenerate its private cache. The benchmark reads the frozen20000header. These are different pairwise equity inputs despite the same original copiedcacheSHA. This is a more direct explanation than the initially investigated fit-path possibility below. APIa remains valid only as a same1024configuration preview-off/on parity test. Its files are unchanged. New verification derives samples from the frozen header and verifies cachehashes after load/build and at end; a new20000run is required for benchmark-comparable quality/timing.

Observed inputs: pass04`raw/reference-eight-timing-a.log` reports final50 gap1.4955166257;`baseline-eight-50-a.json` reports1.3456196020. Root action frequencies also differ, so this is not merely sum ordering or a status display issue. Both logs report the same1,567,754nodes,1024particles,B32,388,082compactCDFslots,HUcache enabled and119,099calibratedterminals.

The source audit does not explain the discrepancy as a preview side effect:

- Benchmark`g.iterate(&mut s)` delegates directly to`try_iterate(s,None)`. API passes`Some(false stop flag)`, adding atomic checks between seat sweeps. Those checks do not alter updates when never stopped.
- GPUiteration reads the host solver's iteration counter for the discount; learning strategies/regrets remain device-owned. `sync_to_cpu` downloads both device arenas and copies to CPU arenas. It does not upload or modify device strategy, regrets, reach scratch, graphs or iteration.
- `node_view(&self)` reads host strategies/reaches and constructs response vectors; no solver/GPU mutation occurs on these all-solver nodes.
- Both perform the same GPU`gaps_and_evs` after50iterations. The extra benchmark synchronization before that check does not feed host arenas back into the GPU.
- Fullreference table generation remains the same deterministic1024particle build; new runtime sample count resolves1024 for`coupled_deck_v1`. `kernels.cu` has no diff againstff54279. The deployed baseline executable still matches its frozen SHA, and contains the exactff54279CUDA source bytes. The benchmark executable at its original path has since been rebuilt, so checking its current bytes cannot certify the original timing binary.

Unresolved provenance gap: the benchmark's`guarded_run.py` inherits`REALIZATION_FIT` without recording the child environment. `RealizationFit::load_default()` gives that variable priority over the cwdcache. Matching cwdcachefile hashes therefore does not by itself establish the resolved fit used by the earlier benchmark. The API baseline explicitly pinned its privatefitpath and recorded it in ownerenvironment. The benchmark also inherited other`PREFLOP_*`variables; current GPU production uses only diagnostics among those flags, whilePREFLOP_PRUNE affectsCPUtraversal. Confirming the actual historical invoking environment would close this gap; current environment alone cannot establish it.

The planned same-candidate APIreferencefalse/true qualification is the discriminating preview gate: identical inputnativebytes, privatefit/cache, budget, executable and checkpoint; exact final nativeheader/allarenaSHA plus gaps/EVs. If it passes, preview publication itself is not responsible for the observed cross-binary discrepancy. Until that gate completes, do not assert early-preview parity or compare the differing harness and API finalquality metrics as the same trajectory. No builds, servers, solver runs or GPU jobs were performed for this audit.

## Completed API-a qualification (supplement to the preceding audit)

The gate described above has now completed. `preview-api-a-summary.json` records `passed: true` for all four cases. Individual records remain in the isolated lab's `target/interactive-api/preview-api-a/{reference-control,reference-preview,fast-preview,small-api}/result.json`; this review inspected those records and their private cache headers without rerunning them. All four headers are1024 and each recorded owner environment pins `PREFLOP_EQ_SAMPLES=1024`. The server source default is20000 when that variable is absent (`crates/server/src/main.rs`, equity-cache initialization). Parent independently verified no such override in the live server process; this API-a configuration must therefore not be described as its current equity input.

`early_preview=false` and `early_preview=true` on the full1024 coupled model have **exactly matching native header, both full-arena SHA256 values, final gaps and EVs, and whole native-file SHA256** (`659716b929bd60ad19c0f4d42513e07fa13135d9e799279950fd7645e699845b`). Both finish at iteration50 with gap1.345619601999294 and stop reason `iteration_limit`, not convergence. This establishes that early publication did not perturb this tested trajectory; it does not certify iteration2 decision quality.

| API-a case | First published strategy | First successful export | Final stopped status observed |
|---|---:|---:|---:|
|Full model, preview off|304.062s, iteration50|304.359s, iteration50|304.062s|
|Full model, preview on|12.093s, iteration2|63.859s, iteration10|302.437s|
|64-particle preview model|3.937s, iteration2|8.375s, iteration10|29.468s|

Times are measured from solve request and are polling observations, not exact kernel completion times. Whole test-case times331.250s,333.625s and62.750s also include load/save/reload checks and must not be mixed with solve timing. The early exports correctly report unknown accuracy and `converged: false`; the approximate50-iteration gap1.2491191137713666 is under different payoffs and is not a full-model quality certificate.

The small API case rejected invalid/duplicate model queries without changing its session, rejected saving while running, stopped at iteration714, and preserved native model identity through reload/roundtrip. Reload clears stale accuracy metadata rather than carrying a convergence claim. All four cases completed with no guard failures. The existing summary's exact checkpoint-field and native-parity assertions passed.

The earlier standalone-versus-API mismatch remains a **different-input comparison**, now explained by regenerated1024-sample pairwise caches versus the standalone20000-sample cache. A new header-pinned20000 API run is needed for matched benchmark/live-input timing. No raw records, native saves or cache files were rewritten for this documentation update.
