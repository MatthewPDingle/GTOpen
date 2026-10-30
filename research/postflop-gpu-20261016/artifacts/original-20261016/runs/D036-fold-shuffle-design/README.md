# D036: exact fold-reduction shuffle tail

**Recommendation: GO for one bounded compiler/numerical probe, not an accepted optimization.** Prospective E019 specializes only the current128x1x1 up_fold launch. It replaces the last five shared-memory reduction steps with warp shuffles, retaining the original addition tree and one final block barrier. No host metadata, allocation, extra kernel, traversal reorder or persistent cache is required. Root owns implementation authorization and all serialized execution; this note performs neither.

Accepted base is E015. Exact accepted source copies and hashes accompany this note. D033's temporary test module is excluded from the copied base. E016/E017/E018 remain rejected, and their changes are not reused.

## Concrete redundant synchronization

In kernels.cu:173-182, each of128 threads first sums its original strided opponent hands into a float partial. After publishing partials, the shared reduction runs64,32,16,8,4,2,1. Each step ends with a full block barrier. After64 and32, all values required for the remaining steps belong to the first warp. The last five barriers can therefore be replaced by shuffle synchronization within that warp and one final block barrier before the whole block reads T. Net saving is **four block barriers per128-thread fold CTA**, not five; the two earlier reach/partial publication barriers remain unchanged.

Archived D021 PTX comes from the byte-identical accepted CUDA source. Its up_fold entry contains a real reduction-loop bar.sync at line2185 (with partial publication at2169). The compiler has not already replaced it with a shuffle tail. Lines2180-2183 show shared loads, add.f32 and a shared store. Notably PTX lists the loaded right operand before the left in that addition, despite the source compound-add expression: numerical proof must compare compiled baseline/candidate outputs and inspect operand lowering, rather than assume source spelling establishes NaN payload behavior.

## Minimal prospective source boundary

Keep all loads, card sums, per-thread partials, amount/valid/CFV arithmetic and stores unchanged. Keep total_parts[256] and the128-thread host launch. Only replace the reduction block, with a uniform branch for `(blockDim.x == 128 && blockDim.y == 1 && blockDim.z == 1)`:

1. Execute original shared steps64 and32 with their original `threadIdx.x < step` guards and block barriers.
2. In warp0 only (`threadIdx.x < 32`), load `v = total_parts[threadIdx.x]`.
3. For step16,8,4,2,1, **all32 lanes first execute** `rhs = __shfl_down_sync(0xffffffffu, v, step)`. Only then, lanes with `threadIdx.x < step` do `v = v + rhs`. Keep inactive lanes' v unchanged; do not add artificial zeros or move the shuffle inside the guard.
4. Lane0 writes total_parts[0]=v. A block-wide barrier **outside** the warp branch precedes the existing `float T = total_parts[0]` and hand-output loop.
5. Every other launch shape executes the original reduction loop byte-for-byte. The probe compares fallback outputs against the same launch shape, never against128-thread outputs whose partial grouping differs.

Every last-stage pair is the same left and right f32 value as the original shared tree. The shuffle transfers bits rather than performing floating arithmetic. No wider accumulator, reassociation, new reciprocal, FTZ/fast-math setting, block-size change or prefix scan is introduced. Signed-zero/subnormal equivalence still requires the differential test. **No NaN payload equivalence is claimed without execution.**

## Synchronization and integration obligations

The two retained shared barriers publish all64 then32 partials. Warp0's32 lanes must remain active for every full-mask shuffle, even when only a subset updates. The final full block barrier publishes lane0's result to every thread that computes CFVs. Existing card-sum `s[]` initialization already precedes the unchanged partial-publication barrier. Non-warp0 threads may arrive at the final barrier early; they must not read T early.

Current production up_fold launches are only the training and evaluation call sites in mod.rs:635/863, using cfg's128x1x1 block. Both automatically use the candidate kernel; no host change is needed. Locks, warm starts, compact/full layouts, chance isomorphism, eager/profiled execution and captured graph replays retain all pointers and dependencies. Continuation calls use the same kernel implementation. Kernel arguments, graph shapes and allocation/admission accounting stay unchanged.

## Falsifiable small probe before solver integration

Use immutable accepted CUDA bytes plus a standalone temporary candidate differing only in the above reduction. In one serialized context compile both with exactly the production architecture/default NVRTC options. Preserve source/PTX hashes and commands. Query up_fold registers, local/static shared bytes and occupancy at block128 with the actual dynamic opponent-reach shared bytes, plus representative maximum hand-count capacity. Count the original and candidate barrier/shuffle paths in PTX, and inspect f32 add operations/operand roles. No resource-only outcome establishes a speedup.

Then run a small standalone GPU differential oracle for the exact original versus candidate per-thread-partial/reduction sequences, writing raw total bits with guard words. Use the same input buffer, no source mutation, and the same block size for each pair. Cover current128 and unchanged fallback16/32/64/256. Include lengths0,1,31,32,33,63,64,65,127,128,129,255,256,257,319 and1326; realistic nonnegative reach magnitudes/zeros, deterministic random exponents, rounding-boundary mixtures, positive/negative zero, subnormal values, tiny-plus-large finite magnitudes and adversarial finite cancellation. Preserve fixed seeds and every case/result. Any nonfinite test outputs must be reported explicitly; do not silently compare with tolerance. An injected expected-bit/guard mismatch must cause failure before any timing interpretation.

Also compare raw full up_fold CFV outputs from the actual baseline/candidate kernels on representative saved or constructed reaches, both players, multiple pots/fold outcomes, asymmetric ranges and identical-hand correction. The reduction-only oracle proves a narrower operation sequence; full-kernel codegen/register pressure and downstream amount/card arithmetic remain separate obligations. All results must be bitwise, with output bounds and input immutability checked.

Only after this probe passes should the one-kernel candidate enter the frozen native complete-cycle screen and independent raw/state/control comparison against accepted E015. Keep all3 fixtures, the existing2% aggregate gate and repeatable fixture-regression guard; require F32/compressed, menus/locks, evaluation and resume/continuation controls before acceptance. Preserve any failure without favorable retries or cross-cohort gains. A failed resource/numeric check is sufficient to stop; an unchanged occupancy count alone is not proof that timing cannot improve.

## Why this is plausible, and why it may fail

The mathematical operation count barely changes, but four full block waits disappear for every fold terminal CTA across both traversers, every iteration and evaluation. No constructor allocation or upload is added, so this avoids the setup-cost failure mode of table/readback experiments. The source change is much smaller than arity-specialization or persistent-cache changes. Registers may nevertheless rise, reducing occupancy; the new block-shape branch and shuffles have cost; barriers may be largely hidden or not dominate native execution. A measurable kernel gain may still miss the complete-cycle gate.

D033R1's dense-event outer envelopes were68.9126%,72.1199%,71.0325% slower than their corresponding native20-iteration controls. Its perturbed paired up_fold family intervals were3.4214,3.4574,3.6346ms. These are **not native kernel shares or a quantitative performance upper bound**. They supply only weak priority guidance alongside concrete source barriers. Exact raw/control audit of that diagnostic is separate; this note does not qualify it or infer an uninstrumented speedup from its ratios. `D033-context.json` retains all three values and the raw input hash.

## Novelty and alternative considered

The bounded historical search covers current E001-E018 ledger descriptions and deduplicated postflop entries in research/autoresearch/results.tsv. Older E011D established the current deterministic f32 fold tree; rejected E011/E011B/E011C changed atomics/precision/card sums. Preflop E035 optimized a different reach reduction. No same postflop shuffle-tail experiment was found in this scoped search; that is not a global historical absence claim.

A separate, source-feasible showdown hypothesis would cache the current river's contiguous o_card_pos indices in shared memory. Plan.rs345-354 stores each sorted opponent hand in two distinct card lists, giving exactly2*m_o entries; copy them before the existing first barrier, replace only `o_card_pos[t]` with `local[t-card_base]`, and preserve all card/float loop order. Both training/eval show_shared capacities would grow from `8*riv_max+4*nh_o` to `16*riv_max+4*nh_o` (plus unchanged static shared allocation). This could remove repeated global integer lookup loads, but adds per-CTA copy work, shared-memory pressure and bank-conflict risk; those global loads may already hit cache. It is distinct from rejected E034's card-run reordering, but the fold tail is the smaller first probe. Do not combine the hypotheses.

Independent source critic menu_change_review found no synchronization/math blocker in the bounded fold shape, emphasizing full-mask participation, unchanged guards, final barrier and raw/codegen checks. No source edits, build, profiler or GPU invocation were performed for D036.
