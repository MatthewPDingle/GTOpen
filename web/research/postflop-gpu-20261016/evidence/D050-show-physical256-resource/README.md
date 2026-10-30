# D050: physical256 showdown threads with the original logical128 scan

Compiler/source preparation only, against accepted E020. D047 rejected a naive launch-width change because it changes floating chunk grouping. This candidate instead fixes logical scan width at128 when the physical x-width is256; valid other one-dimensional widths keep their original geometry. It is one fixed candidate, not an adaptive or rescue policy.

All128 logical lanes retain their exact original chunk bounds, +0 accumulator, ordered local prefix and chunk_sum[tid+1] write. Thread0 retains chunk_sum[0]=+0 and the full128-step left-to-right += recurrence, including unused tail entries. Only the lower128 threads read/apply their chunk bases. Upper128 physical threads do neither scan stage, but every physical thread reaches all existing barriers. The257-float array and E020 cache/shared layout stay unchanged. For zero opponents all128 logical lanes still write+0 and the full recurrence remains; the guarded total reads no prefix. Original floating expressions/order are retained; actual compiled/native equality remains unproved.

Only already independent staging, sorted gather, CFV zeroing and per-own-hand output loops use the physical stride256. Their writes are disjoint and each hand's arithmetic/card loops retain order. Eight other CUDA entries and the up_show ABI are unchanged. This is distinct from rejected E008 carry rewriting and E022 prefix-tail deletion; neither is included.

The no-launch probe compiles accepted/candidate CUDA in one context with production architecture-only NVRTC options. It queries up_show at baseline128 versus candidate256 for dynamic shared sizes6300,5060,21808,26520bytes: two accepted rainbow allocations, the frozen wide-turn allocation, and a conservative1326-hand bound. It records registers/local/static shared, maximum supported threads, active blocks and warps. Ten markers comprise one device record, eight resource rows and completion.

Admission requires the requested thread/shared capacity and positive residency. There is no arbitrary non-worsening register/block/warp gate when comparing different physical widths. Resource changes are tradeoffs, not speed predictions. Independent source/PTX review must verify exact logical scan/float dependencies, barriers, ABI and unchanged eight entry bodies before any later native decision. The runner leaves that review pending; no candidate acceptance follows from capacity.

Host changes are deliberately unimplemented. A later separately authorized candidate would change ONLY both up_show launch sites in gpu/mod.rs (evaluation695, training925) to(256,1,1), preserving grid/shared sizes/arguments, profiling and graph order. Every other launch stays unchanged. Current accepted source map remains162 entries.

This narrowly reuses D049/D046 orchestration: pinned D047 proposal and terminal D049 rejection, protected source/dependency hashes before/after, shared GPU lock, live-solve refusal,50GiB free plus1GiB output reserve,600second stage bounds,10second heartbeat, immutable raw logs and owned-child cleanup. No telemetry polling during execution. Root alone executes after frozen independent review:

`python -B run.py --execute --prepared-manifest-sha256 SHA256`

No compiler, NVRTC, native solver or GPU call occurred during preparation. D045 selected event intervals are not whole-family or complete-solve shares. A later actual complete up_show differential and full raw/compressed/F32/evaluation/lock/resume plus complete-cycle controls remain required if this is feasible. No broad harness, native candidate or outcome-triggered alternative is authorized here.
