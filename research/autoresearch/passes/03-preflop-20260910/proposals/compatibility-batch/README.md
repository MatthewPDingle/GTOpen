# Preserve original accumulation grouping with optimized storage

Proposal only; based on optimized GPU source **739c68d**. `compatibility.patch` changes only `crates/solver/src/preflop/gpu.rs`; no CUDA arithmetic or launch geometry changes. `gpu.rs` is the full proposed source. `planner.rs` and `tests.rs` are review extracts, not additional modules to install. `generate.py` reproduces the patch. Source-only `git apply --check` against an extracted 739c68d copy passed. No compilation or hardware execution was performed for this proposal.

## Decision rule

1. Compute the old union-CDF plan without allocating it. Use the current common corrected forced-policy allocation, then the original fixed metadata, MB-to-byte floor, maximum batch 32, and old post-CDF HU-cache fit decision.
2. Retain that batch and HU-cache mode with compact physical CDF storage. Normalized reach is optional at the required batch: choose direct division if normalization would displace either the batch or an originally enabled HU cache. An originally disabled HU cache stays disabled even if compaction frees room.
3. If extra optimized metadata prevents that exact batch/cache combination from fitting, return an explicit unsupported-layout error through the existing CPU fallback. Do not silently choose a different batch or precision. The existing compact-map planner is unchanged; this narrow proposal does not add union retry or claim preservation of every old minimum-VRAM fit.
4. Only when the old union scratch could not fit one particle, retain the optimized planner's existing capacity-extension behavior. Logs identify this as having no original same-budget GPU grouping to preserve. This branch can fit a model that formerly needed CPU, and requires the existing CPU/GPU parity gates.

The original planner chooses B before deciding whether its HU equity cache fits. This matters: the reduced modeled-six fixture predicts B=23/cache-on at 19 GB, B=27/cache-off at 21 GB, and B=30/cache-on at 23 GB. Preserving only B would miss the 21 GB cache transition. The extra fixed metadata and optional normalization must not accidentally reverse those decisions.

## Expected physical layout, not benchmark claims

The reduced modeled-six cost fixture uses base 5330 MB, reference fixed 171096 bytes, optimized fixed 26008848 bytes, union 846156 slots, compact 432300 slots, and HU cache 302708744 bytes. Host arithmetic predicts:

| Budget MB | Reference batch | Reference HU cache | Optimized planned MB |
|---:|---:|---|---:|
| 19000 | 23 | on | 12712.124392 |
| 21000 | 27 | off | 13585.271648 |
| 23000 | 30 | on | 14769.872392 |

At 23 GB, keeping B30 uses 588 MB less CDF scratch than optimized B32. It needs 35 particle batches instead of 32, and the four-warps-per-CDF-block layout incurs some extra padded work. Measure the throughput tradeoff; do not infer it from allocation size. Physical memory remains substantially below the original union allocation even though accumulation grouping is retained.

## Host coverage

Five tests independently reproduce original reference arithmetic; exercise the 19/21/23 GB transitions; verify normalization yields to batch/cache; preserve cache-off; explicitly reject metadata regressions; and identify old-no-fit capacity extension, complete no-fit, overflow, and invalid base inputs. These are planner tests, not substitutes for GPU execution.

## Required integration gates

- Apply independently of the diagnostic environment cap. This proposal contains no environment override. If diagnostic cap30 is temporarily applied first, remove it before evaluating production compatibility behavior.
- Run all existing GPU planner/constructor/internal tests, including direct/normalized one-particle and compact/union boundary parity. Existing tests that deliberately derive old greedy-budget transitions may expose changed assumptions; inspect them rather than weakening correctness assertions.
- Capture layout JSON at 19, 21, and 23 GB on original common-forced-accounting control and this candidate. Require original B and original HU-cache mode where the original fits. Require actual candidate allocations within budget. Verify the live modeled fixture, an all-solver control, and frozen/locked policy fixtures.
- At matched iterations and otherwise identical inputs, compare full native regret/strategy arenas and all-node effective policies. The immediate decisive gate is the modeled six-iteration original B30 control versus candidate B30. Root-only gaps/EV or small weighted mean error do not excuse large conditional policy differences.
- Follow with the frozen time-to-accuracy checks and matched-iteration longer checkpoints. Preserve frozen inputs, sample count, precision, checkpoint cadence, and original files.
- If exact matched-B parity fails, investigate remaining arithmetic/cache/terminal differences; do not describe this planner as a universal bitwise guarantee.

## Scope and limitations

The compatibility reference includes the **shared forced-allocation correction**, not the old buggy under-accounted budget. It is computed at GPU construction, so model changes that alter forced storage must reconstruct the plan and graphs through the existing lifecycle. No allocation or planning changes occur during graph replay.

Native saves do not record the historical GPU batch or cache mode. This restores compatibility with the corrected original planner for the *same current configuration and supplied budget*, not with an arbitrary previous device, budget, saved run, or solver revision. Capacity-extension runs have no corresponding original same-budget GPU execution. Direct and normalized arithmetic have previously passed parity tests, but this proposal still requires their boundary gates after integration.

The existing preferred-layout `vram_estimate_mb` is unchanged and may conservatively exceed the actual compatibility allocation; layout diagnostics report the selected batch/cache and physical allocations. GPU allocation failures continue through the existing caller behavior. This proposal makes no server changes, no accuracy changes, and no promise that a marginally unsupported old fit stays on GPU.
