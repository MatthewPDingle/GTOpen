# E020 terminal server audit preparation

Root runs `python -B audit.py` only after the server build, V020-server-unit and isolated smoke have all completed. This script is file-only: it imports no runner, spawns no process and makes no HTTP/GPU/native calls. It writes a one-shot report at comparisons/E020-server-qualification/report.json with input hashes and an audit manifest; it refuses an existing output directory and preserves failures separately.

The audit binds the exact frozen implementation/acceptance/source maps, both Cargo terminal logs, emitted executable/manifests/dependencies, and expected E020/opposite-absent CUDA source. It checks the21-name default inventory and20passed/1ignored summary, unit binary identity,100-iteration GPU API result, all finite root/child values and strategy normalization, copied requests, owned PID/port/executable identity, cleanup, released test port, unchanged live snapshots and live executable hash. Build/unit/smoke timestamps must be sequential. It produces no performance claim and leaves deployment blocked.

Prepared with Python AST validation only. No audit, build, unit test, smoke, process inspection or GPU operation was executed by this preparation. Root will review and execute after all terminal evidence exists. Existing evidence and frozen scripts are unchanged.
