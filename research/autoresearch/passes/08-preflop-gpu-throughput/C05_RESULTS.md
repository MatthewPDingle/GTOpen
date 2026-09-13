# C05: aligned probability writes - rejected

The first large complete-run pair was9.49% slower:71.756s retained-C01 control
versus78.566s candidate. Warm iterations regressed4.37%; checks regressed8.61%.
The prototype is removed. C01 remains the retained implementation; port56708
was not changed.

## What was tested

CDF stride192 with leading bias31 aligns logical CDF1 on128-byte boundaries.
All170 prefix values, scan order, direct reads, aliases,1024 samples and batch32
remain unchanged. Added steady CDF storage was1,092,839,040 bytes. Construction
briefly needs the entire new9,537,503,360-byte buffer while preserving the old
valid allocation; explicit9.8GB headroom covers that peak under the23GB test
budget. The dashboard now includes this CDF growth in its extra-memory column.

Two prefix/allocation tests passed, including exact logical prefixes, aliases,
compact/union layouts, offsets, partial batches, sparse/dense/subnormal inputs,
poisoned unused regions, overflow/headroom and safe denial. Four full C01 tests
passed with original/C01/C05 comparisons covering2..8 opponents, fixed/frozen
policies, zero reach/recovery and graph replay. Six large checkpoints and final
full-arena fingerprints matched exactly.

## Follow-up phase diagnosis

A separately registered eager phase pair cannot overturn the rejection. It
shows the intended writer optimization did not produce a benefit:

| Phase | Control | Candidate | Change |
|---|---:|---:|---:|
| Learning CDF | 1,571.26ms | 1,665.36ms | +6.0% |
| Learning terminals | 1,974.05ms | 2,055.60ms | +4.1% |
| Check CDF | 3,205.63ms | 3,693.57ms | +15.2% |
| Check terminals | 4,030.11ms | 4,205.73ms | +4.4% |

Both phases regress. These are eager event timings, not hardware transaction
counts; a precise cache/traffic cause is not proven. Do not spend the next trial
on a slightly different padded stride merely because its footprint is smaller.
No extended retention pairs or unrelated full regression qualification were run.

`check_c05.py` independently audits all prefix/full-solver prerequisite results,
source/input/executable hashes, output equality, memory size and diagnostic
phase counts. Changed sources are archived under `artifacts/c05-rejected`;
unchanged sources are resolved from the pinned source commit. Local frozen
executable `target/c05-benchmark-frozen.exe` SHA256:
`be6eb0ed6fecd8a5e236accc0bff7236effa7093ca9e62160742babf69de4f5a`.

## Next

Investigate cross-player sharing during an accuracy check. `queue_evaluation`
does one average-policy down sweep and then independently reconstructs CDFs for
each traverser. Unlike alternating learning, these average reaches remain
unchanged throughout the check. First measure exact distribution overlap and
memory requirements for evaluating players in pairs. See `D04_PROPOSAL.md`.
