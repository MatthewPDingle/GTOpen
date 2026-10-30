# D036 additive preparation revision 2

R1 remains immutable at `../D036-fold-shuffle-probe`. Its prepared manifest SHA256 is `aa00b819764e2693d5c37c63f0c668308851b249d130274b6ad567d325ebadfa` and is copied as `source-r1-prepared-manifest.json`.

The only executable-source change adds `"max_threads_per_block": f.max_threads_per_block()?` to the existing full-kernel resource rows. Installed cudarc0.19.7 core.rs:2427 exposes this read-only function-attribute query. A query error follows the existing failure path. CUDA sources, corpus, protocol, all numerical checks, stage schedule and runner bytes are unchanged. No build or GPU call was performed for this revision.

The copied README describes the unchanged protocol and R1 command. Execute R2 only, after root owns the serialized slot and independent reviews pass:

```powershell
& 'C:\Program Files\Python312\python.exe' -B 'S:\GTOpen-research\postflop-gpu-20261016\runs\D036-fold-shuffle-probe-r2\run.py' --execute
```

The copied `prepare.py` and `seal.py` are historical reproducibility inputs; do not rerun them over sealed files. The prepared manifest in this directory seals R2 and records its R1 parent. This addition supplies a resource limit; it is not a numerical/candidate change or performance evidence.
