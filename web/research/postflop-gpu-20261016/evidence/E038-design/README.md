# E038: U16 zero-upload proof scan draft

Status: off-tree source draft only, pending the fixed family's outcome and a final baseline identity check. This is not an activation, build, test, timing, qualification or adoption result. The current E020 arena input is archived byte-exact; none of the four family candidates changes this file. Any later baseline must be explicitly bound before execution.

## Production scope

Only gpu/arena.rs can_upload_zeros changes: the U16 arm keeps the exact positive-zero scale-bit check and omits its q-word OR reduction. The comment now distinguishes signed and unsigned inputs. I16/F32 behavior, initial/inactive snapshot guards, all upload/decoding/transfers/synchronization/readback code, host stores, CUDA, layouts, budgets and allocations are unchanged. Reversing those two production text regions restores the entire original production prefix byte-for-byte.

Actual store.rs decode_u16 computes k = scale / 65535.0, then q as f32 * k. Every u16 converts exactly to a finite nonnegative f32, so a +0 scale yields +0 for every quant. This only proves the decoded GPU image. Never clear or canonicalize host q: cfr.rs solved_strategy_into normalizes U16 quants without scale, so nonzero quants with zero scale can still affect CPU strategy queries and saved input state before the existing sync. Signed I16 values and nonpositive-zero/nonfinite scales retain their existing rejection behavior.

This removes a host read/reduction; it introduces no production allocation, device buffer, layout, module or compatibility requirement. Compiled/runtime behavior is not yet tested. D041 already identified this unimplemented idea. D042's whole-U16 predicate medians total150.1862ms, 1.5425% of its historical9736.4349ms complete cycle; scale/snapshot work remains, so this is an optimistic direct ceiling, not measured q time or a predicted gain. The current1% policy and final baseline must be applied prospectively; no historical sample pooling.

## Narrow CPU coverage (written, not executed)

The existing nonzero-quant rejection test is retained for signed values1,-1,i16::MIN,i16::MAX. Its obsolete unsigned rejection is replaced by one new test, gpu::arena::tests::zero_upload_accepts_all_u16_quants_with_positive_zero_scale, which invokes the real decode_u16 on all65536 U16 values at+0 scale and checks exact output bits. The same quants populate a real U16 Store for both full/compact predicate layouts and both snapshot indices; host quants/scales remain intact. Existing F32 and bad-scale cases are unchanged. The existing reused-snapshot test now runs its original assertions for both I16 and U16.

Local declaration count4->5: one new unignored CPU test, no ignored-test change. If the eventual base remains E020, prospective GPU-only inventory is85passed/4ignored. Recompute against any newly adopted base; this is not an executed count. No independent full/compact GPU upload proof is supplied by these predicate tests.

## Bounded future native control proposal (not implemented or authorized)

Use one existing small real Spot configuration with nonzero U16 q patterns at exact+0 scales and compare the pinned original upload path with the candidate. Exercise a verified full layout and a genuinely compact layout with inactive siblings (reuse the existing tight-budget/warm fixture rather than inventing a broad matrix). Require actual layout selection and device element counts, exact raw decoded GPU arrays, and complete host q/scale bits. Before any sync, compare solved_strategy_into and existing save serialization observations against each arm's pre-upload state; construction must not rewrite them. Then compare complete raw stores after the existing sync, after CPU symmetric materialization, and after the next sync, covering inactive preservation. Preserve negative-I16, nonzero/bad-scale warm fallback and reused-snapshot guards through existing focused controls. Keep normal allocation/wait/readback behavior and use independent original upload logic; do not merely compare two candidate paths. No new runtime harness is prepared here.

After independently reviewed source and focused correctness pass, root may separately authorize a fresh fixed complete-cycle screen/confirmation under the1% and no-repeatable-slowdown policy, with all required exact state/checkpoint, broader, holdout and cumulative gates. No timing extension or rescue is proposed.

## Static preparation evidence

Read repository AGENTS.md and README; destination was absent before creation. Current arena SHA matches archived E020. Exact production reversal and git apply --check --whitespace=error passed without editing the checkout. No Rust/Python solver, compiler, test binary, CUDA or GPU work ran. Initial test draft passed a usize length to Store::u16; source-signature inspection caught this before compilation. draft-r1 preserves those bytes and its patch; the candidate uses a lossless u64 cast for65536. No further source files are owned.
