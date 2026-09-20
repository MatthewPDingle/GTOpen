# SSD storage study — in progress

Production 56708 is unchanged. This study tests storage for the isolated connected preflop/postflop research solver.

## Completed gates

- **Exact disk parking:** all 720 board/player passes matched resident reference values and all four state arrays bit-for-bit. Nine format/failure checks passed. Unused candidate pinned staging was released. Six small states occupy 113.24 MB rather than 180.13 MB before suit-based packing. The guarded run took 97.89 seconds; buffered reads may hit Windows cache. See `ssd-paging-v1-review.json`.
- **Physical SSD I/O:** both 16-GiB write/read repetitions passed full CRC checks using aligned unbuffered, write-through access to a new regular scratch file on S:. Combined direct I/O rates were 1.489 GB/s write and 1.485 GB/s read. Including verification and guard checks, rates were 0.941 and 0.935 GB/s. Total writes and reads were 32 GiB each. This bypasses Windows file caching, not the SSD's internal cache; it is not a drive-wide sustained benchmark. See `physical-v1-review.json`.
- **Initial additional compression screening:** exact zero-word masking would save only 2.9% on the small 60-iteration snapshots. Zlib level 1 reduced them to 42.4% of original size; its measured encoding cost is too high to assume useful solver throughput. LZ4 default mode reduced them to 50.6%, with exact decompression, encoding 113 MB in 0.140 seconds and decoding in 0.089 seconds in this Python screen. Larger and mature states still need checking. See the registered codec protocol and machine-readable results.

## What the SSD result means

Space is ample, but repeated writes can dominate. With the current full-record-per-player design, just 20 GB of cold state over 2,000 iterations would read and write 80 TB each. Applying this short test's direct I/O rates gives approximately 30 hours of I/O alone, before solver work and storage processing. No such long run has been launched or authorized by this estimate.

## Connected comparison: exact results, unacceptable first-version overhead

All four variants produced exactly equal scientific checkpoint outputs at iterations 1 and 20 on the registered three development boards, with both called pots and evolving preflop ranges. Native probability, rake conservation and gap checks passed. This is equivalence evidence, not a converged poker solution.

| Storage | Total seconds, including setup/evaluation |
|---|---:|
| Resident explicit reference | 13.46 |
| Canonical parked RAM | 135.43 |
| Canonical parked SSD | 392.65 |
| 800 MB RAM budget plus SSD | 247.30 |

The sequential pilot is not a controlled production benchmark, but the overhead is clearly unacceptable. The first integration repeatedly reconstructs full host strategies, even for all-in equity, which does not depend on strategy arrays. Both disk variants together wrote 86.40 GB of strategy payload, within the registered 128-GiB bound. Their reported read counters count training sweep loads only and omit evaluation/all-in rereads. See `connected-v1-review.json`.

A registered follow-up is testing direct GPU scatter/gather of the same exact canonical blocks, keeping explicit traversal and original policy tying. It also avoids strategy reconstruction for all-in equity and drops duplicate retained CPU planning tables. Full device arrays as well as outputs must match. No large training or deployment is justified yet.

## Direct GPU restoration: qualified small comparisons

The corrected GPU storage preflight checks the actual GPU work list; the rejected v2 preflight incorrectly included unreachable tree nodes. All 720 v3 diagnostic passes match returned values, reconstructed arrays and full device arrays (including unused space) exactly. The connected v2 comparison also matches every scientific checkpoint value against both its fresh resident reference and the original v1 reference. No numeric tolerance was relaxed.

| Storage | v2 seconds, including setup/evaluation |
|---|---:|
| Resident explicit reference | 12.37 |
| Canonical parked RAM | 38.45 |
| Canonical parked SSD | 217.20 |
| 800 MB RAM budget plus SSD | 133.10 |

This removes much of the avoidable overhead, but parked RAM still costs about 3.1 times resident runtime in this short sequential pilot, and SSD about 17.6 times. These are not long-run throughput measurements. The shared full/compact GPU workspace is 1.661 GB; retained per-game metadata is additional. Total disk payload writes across the two disk variants remain 86.40 GB. Read counters still exclude checkpoint materialization. Production 56708 remains unchanged.

Next: audit all retained CPU and GPU metadata, constructor and evaluation transients, and mature state compression before choosing a larger training panel. A capacity expansion is useful only if its runtime permits the accuracy experiment.

## Larger-state codec screening (details)

On all six completed 20-iteration connected states (1.376 GB), LZ4 default stored 0.923 GB (67.0%) with exact round trips. Encoding took 2.19 seconds and decoding 1.06 seconds in the Python screen. Fast mode stored 0.937 GB and encoded in 1.78 seconds. Zero-word masking again saved only about 2.9%. Zlib level 1 stored 0.761 GB but took 27.14 seconds to encode. These are early states and include Python allocation; they do not establish native throughput or a mature 164-board capacity bound. Fast lossless compression is promising for capacity, but its repeated cost must be measured before adoption.

## Full payload accounting

The CPU capacity planner matched every retained CUDA slice and the shared workspace for all six constructor fixtures. Its 328-game CPU-only projection agrees exactly with the previous arena counts. Full 164-board payload totals: canonical strategy arrays 89.481 GB, retained host Spot/mapping/span data 12.570 GB, total host payload 102.051 GB. Retained device metadata is 11.816 GB and the shared workspace 1.865 GB, for 13.680 GB steady device payload; conservative constructor overlap is 15.294 GB. This is substantially more host storage than the array-only estimate.

These totals exclude CUDA modules/context/driver overhead, allocator bookkeeping, process baseline, CPU planning transients and evaluation scratch. No full-forest GPU allocation was attempted. With roughly 100 GB available host RAM and a 20 GB reserve, the 164-board all-RAM forest still cannot be admitted. Device payload itself is below the 24-GB card's capacity, subject to the live GPU budget and extra overhead. See `capacity-v1-review.json` and `CAPACITY-PROTOCOL.md`.

Next gates are a longer resident-versus-RAM connected comparison and outcome-blind registration of a broader panel that fits the measured host budget. Preserve full-164 results as an evaluation reference; do not call re-used boards independent validation.

## Longer trajectory and next-panel registration

The unchanged retained v2 binaries matched all scientific outputs exactly at iterations 1, 20, 100 and 500. Final restricted three-board gap was 0.019092 bb in both modes. Total time was 68.482 seconds resident and 616.173 seconds RAM parked. The 100-to-500 checkpoint interval averaged 0.10963 versus 1.18899 seconds per iteration, including evaluation at 500. Thus the short pilot's 3.1-times RAM overhead was not representative of longer steady work: the total ratio is about 9.0 and the later interval about 10.85. No SSD state writes occurred. PCIe was observed at generation 4, width 16 during the RAM run; that snapshot does not measure actual DMA bandwidth. See `long-ram-v1-review.json`.

Outcome-blind candidate training panels of 128, 112 and 96 flops and a disjoint fresh 95-board validation panel are frozen. Capacity alone selects the largest admissible training panel. Validation excludes all candidates and the prior 164 comparison boards, covering 15,320 of 22,100 physical flops in its eligible population. It is not a full-deck metric.

Chance-only diagnostics show maximum pocket-pair set/quads opportunity differences from the full entering-range population of 2.83, 4.34 and 3.83 percentage points for the 128/112/96 candidates, and 5.30 for reserved95 (5.17 against its eligible population). No panel was redrawn. The registered large-panel pilot is a resource/accounting test, not an accuracy improvement claim. Before long training, consider a separately registered chance-balanced weighting/control arm, preserving the original panel as a reference; do not choose weights by looking at poker outcomes. Repeated RAM transfers also need cost reduction or an explicit long runtime budget.

## Large resource pilot: capacity worked, runtime gate failed

The 112-board / 224-continuation forest constructed successfully with 61.718 GB of canonical state arrays. The smallest sampled free host memory was 25.144 GB and free GPU memory 12.213 GB. No strategy was written to SSD. The guarded process reached its registered 1,800-second limit (1,804.3 seconds including guard response) before the iteration-20 checkpoint was saved. Only checkpoint 1 is retained. There is no phase timing between those checkpoints, so the evidence does not identify the last completed update or distinguish unfinished training from unfinished final evaluation.

This is a failed runtime gate, despite successful capacity admission. The unchanged larger run will not simply be extended. The queued transfer candidate correctly stopped until this failure was reviewed. See `expansion-pilot-v1-failure-review.json`; next work targets exact transfer/allocation costs on the existing small fixtures before another large experiment.

## Chance-balanced weights: independently verified, no strategy claim

The separate outcome-blind weighting candidate keeps all 112 selected training boards and fits positive weights using only physical-card chances and the fixed entering ranges. An independent total-minus-blocked-card calculation enumerated and verified all 22,100 physical flops, reproduced the metrics, and rejected negative, non-normalized, non-finite and scrambled board weights.

| Geometry diagnostic | Equal weights | Candidate weights |
|---|---:|---:|
| Maximum relative entering private-class mass error | 5.127% | 0.680% |
| Maximum pocket-pair set/quads opportunity error | 4.339 pp | 0.400 pp |
| Maximum fitted board-feature probability error | 7.452 pp | 0.235 pp |
| Effective sample size | 112.00 | 93.18 |

The weights pass the preregistered geometry gate. They cannot create missing trips or very-low-high-card boards, and matching these moments does not establish better strategic accuracy. No EV, action-frequency or strategy output was used to choose them. The equal-weight resource pilot remains unchanged; the reserved validation panel is unchanged. See `CHANCE-WEIGHT-PROTOCOL.md`, `chance-weight-v1-result.json` and `chance-weight-v1-review.json`.

## Owner-only downloads: small exactness gates passed

The applied research-only candidate retains the existing full upload, traversal, math and projection, but downloads only the player whose regrets and accumulated strategy changed in that sweep. The opponent's parked arrays stay untouched. All 720 full-device/restored-state/value comparisons passed. Both the RAM and SSD connected runs matched every scientific checkpoint exactly at iterations 1 and 20. SSD complete-generation read/write counts remain unchanged.

Measured strategy transfer traffic fell from 110.086 GB to 82.565 GB over the identical 20-iteration fixture: exactly 25% less. Candidate total elapsed times were 36.987 seconds RAM and 193.059 seconds SSD, including construction/evaluation. These are single sequential qualification runs, not a controlled speed comparison. See `owner-download-v1-review.json`.

The longer owner-only run also matched all scientific checkpoint outputs exactly at 1, 20, 100 and 500 against both retained resident and original RAM trajectories. It took 464.587 seconds total; the 100-to-500 interval averaged 0.86918 seconds per iteration including the final evaluation. Transfer traffic remained exactly 75% of the original, with no SSD state writes. Final three-board gap stayed 0.019092 bb. These are correctness/observed-timing results, not fresh paired speed evidence. See `owner-download-v1-long-review.json`. The separate allocation-reuse candidate can now enter qualification. Production 56708 remains unchanged.

## Reproduction details and scope

Protocols: `PROTOCOL.md`, `CONNECTED-PROTOCOL.md`, `LOSSLESS-CAPACITY-PROTOCOL.md`, `FAST-CODEC-PROTOCOL.md`. Tools live under `tools/research/ssd_*_20260920.py`. GPU guard logs and resource samples are in the sibling `representative-coverage-20260919` directory. Installation of the codec is isolated under `target/ssd-codec-python`; the wheel version and hash are recorded in `lz4-install-report.json`.

Scratch files are confined to named directories under `S:/GTOpen-research`. They are research artifacts, not user saves or a crash-resumable whole-game checkpoint format.
