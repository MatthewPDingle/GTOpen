# Build ownership paired runner (prepared, not executed)

Register both binaries in the existing pass build-binaries.json before running. Each must have a unique executable SHA256, actual source_commit and harness_sha25671d629ae17f951a4d270b773a5260861c2a502228679109df9cab879e209ccb9. Candidate source CLI must match that entry. Current lab frozen example source must also match. Baseline defaults to archived build-control-5cc6b3f.exe.

Screen one pair per requested mode under a unique ID:

```powershell
python research/autoresearch/passes/03-preflop-20260910/proposals/build-action-ownership/run_build_pairs.py --candidate ABS_CANDIDATE_EXE --candidate-source COMMIT --id ownership-screen-a --rounds 1 --small-sanity
```

Only after review, five independent alternating pairs with a new ID:

```powershell
python research/autoresearch/passes/03-preflop-20260910/proposals/build-action-ownership/run_build_pairs.py --candidate ABS_CANDIDATE_EXE --candidate-source COMMIT --id ownership-confirm-a --rounds 5
```

Use --modes fresh-from-config or --modes load to select one mode; default runs both. --small-sanity adds one separate three-seat fresh pair. --stop-before-utc bounds the run deadline; default is the research deadline. Each child timeout is capped at remaining time/600seconds, with existing live-work guards. Calls are sequential.

Before the first process, runner freezes input/cache/binary hashes and exact pair order in a new lab/target/research-build/ID/protocol.json. Baseline/candidate order reverses each round. Large native8 fresh and load are separate groups; fresh does not transport saved profiles/model/iteration. Files are retained under that unique directory (roughly42GB for20large roundtrips); disk capacity checked before starting. No original files are overwritten/deleted. No automatic retry or resume into used IDs.

Each process goes through run_guarded.py with PREFLOP_MEASURE_MEMORY=1. Successful exit, reason=null, one timed then one verified record, executable identity, memory observations, expected mode/input/output are required. Exact typed config/profile/locks/metadata, topology+action labels, all native arena fingerprints/lengths and saved bytes are checked after each pair. Missing verification or identity mismatch stops further work. Vec/String capacities are reported separately, never required equal. Five pure comparator tests pass normally and under python -O, including a real Windows extended-prefix file-identity test.

comparison.json reports paired reduction median/min/max, raw timings, capacity deltas and RSS/OS-peak observations. Only operation_ms is measured build/load time. Memory is WHOLE PROCESS, including untimed verification/save, not isolated build RSS. No automatic promotion: gains below2%, increased retained String capacity or higher RSS require explicit review. One-pair screening is not confirmation evidence. Larger retained capacity is a tradeoff, not an accuracy mismatch.

This proposal has not launched any build/solver/hardware job.

Comparator correction: expected input/output paths are checked with OS file identity (Path.samefile), accepting existing Windows extended-prefix aliases without stripping strings. Missing/inaccessible or different files fail closed. The first screening run stopped on the former textual-path gate after one pair; its original protocol/output and failure provenance remain unchanged. Confirmation uses a new ID.
