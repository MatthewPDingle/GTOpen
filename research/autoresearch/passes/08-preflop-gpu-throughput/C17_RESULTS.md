# C17: four terminal warps per block — rejected

The first large paired run was **167.39% slower** with the packed
warp scheduler. Numerical results matched exactly, but the registered timing
gate failed. The candidate was archived and removed; runtime restored to
9c242ce. No extended campaign or broad regression run was justified.

| Measurement | C14 control | C17 candidate | Candidate / control |
| --- | ---: | ---: | ---: |
| Complete run | 53.277495 s | 142.456666 s | 2.6739 |
| Warm iteration median | 2.873844 s | 6.271542 s | 2.1823 |
| Warm check median | 5.027538 s | 16.506840 s | 3.2833 |

## What changed

One warp evaluated each terminal, with four independent terminal warps packed
into a 128-thread block. Each lane processed up to six hands sequentially.
Warp-private metadata and a warp barrier replaced block-wide coordination.
No probability table was copied, rebuilt or compressed; no additional launch
or queue was introduced. The C14 arithmetic helper remained unchanged.

This scheduling tradeoff lost badly on the measured fixture. Processing hands
serially changes memory reuse and concurrency, but the benchmark does not
isolate cache behavior, instruction latency or another specific hardware cause.
Unchanged register usage alone did not predict performance.

## Evidence

- 4,032 paired direct-kernel cases passed exactly across both terminal entry
  points, all 2–8 opponent counts, mixed active/inactive/zero-probability warps,
  partial final blocks, partial batches, nonzero sample offsets and recovery.
  Output guards and non-live values were unchanged.
- Six expanded solver tests passed (one manual test ignored), preserving full
  arenas, terminal and prefix values, roots, gaps/EVs, locks/frozen players,
  capture and stop/synchronization behavior.
- Both saved allocation plans matched C14. Registers remained 40 per thread;
  shared memory grew from 44 to 176 bytes per block, exactly four independent
  terminal metadata records. No local-memory spills were reported.
- Compiler evidence confirms only the selected terminal entry changes in each
  module. Every other PTX entry is identical; control PTX equals the qualified
  C14/R03 archive.
- All six benchmark checkpoints and the final full-arena fingerprint match
  each other and the archived C14 fixture. The independent checker verifies
  immutable sources, input/executable hashes and runtime restoration.

The qualified R03 frozen server and port 56708 are unchanged. This experiment
does not alter the retained performance line or establish convergence progress.

[Protocol](C17_PROTOCOL.md), [verification](raw/c17-verified.json),
[checker](check_c17.py), [runner](run_c17.py). Source snapshots, compiler outputs,
raw timings and GPU snapshots remain archived.
