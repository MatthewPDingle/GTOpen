# Pre-normalized multiway reach proposal

Proposal only, based on isolated source at commit `3295571` in `target/autoresearch/preflop-20260910`. No production/worktree edits, compilation, benchmarks, GPU jobs, or server interaction.

Apply `normalized-reach.patch` to that baseline. Full proposed `gpu.rs` and `kernels.cu`, source hashes, and a reproducible generator are included. Read-only `git apply --check --ignore-space-change` passed against the isolated checkout. The existing 192-thread coupled terminal launch and learning-only active gating are preserved.

## Work removed

The old CDF kernel executes `reach[block*169 + order[particle*169 + index]] / mass[block]` for each hand and each of 1,024 particles. The proposal inserts one normalization kernel immediately after preparation/active marking and before the particle loop. One 192-thread block handles each statically needed slot and divides each of its 169 class weights once. CDF scan kernels then gather the saved values in particle rank order.

No reciprocal, approximate divide intrinsic, reduced precision, or compiler fast-math option is introduced. The expression remains plain f32 `reach[...] / mass[block]`; its f32 result is stored in a device array and later loaded as the original scan's f32 input. CDF scan arithmetic/order and all quadrature/sample processing remain unchanged. This is intended to preserve the float results, but CUDA compiler transformation/rounding equivalence still requires empirical parity checks rather than an untested bitwise claim.

## Correct invalidation

Normalization runs on every `terminals_masked` call, after the prepared probabilities and (when enabled) active mask. It is not attached only to `down`, because internal tests and other callers may replace reach inputs before calling `terminals` directly.

- Learning (`gate=1`): skip unmarked slots and zero-mass blocks, matching CDF's guards.
- Average/BR checks (`gate=0`): ignore stale active flags and refresh every positive-mass slot in the traverser's work span, matching the ungated CDF behavior.
- Skipped normalized storage can retain old values because the consuming CDF has the same guards. Zero-counterfactual terminal writes remain unchanged.
- All buffers have fixed addresses during graph capture/replay; launches have fixed bounds and run on the same stream. No host readback or synchronization is added.

## Memory and expected tradeoff

Extra allocation is `slot_count * 169 * 4` bytes. The constructor checks multiplication overflow and reserves that storage before choosing particle-batch size; public VRAM estimation includes it too. This is approximately the storage of one additional CDF particle per slot (676 versus680 bytes).

Consequently, a memory-bound32-particle workload may fall to31 particles, changing32 particle batches into34. Total samples remain1,024. Extra value updates/launches and normalization memory traffic could outweigh the saved divisions; measure both GPU lifecycle memory and end-to-end iteration/checkpoint time. Dense and sparse workloads may differ substantially.

This version is an unconditional optimization for coupled games: a workload barely fitting one CDF particle could now fail the GPU fit check. Before retaining globally, test that boundary. An optional fallback to the old unnormalized CDF path would avoid increasing minimum required VRAM, but was deliberately not mixed into this first bounded candidate. Do not silently switch models or reduce samples to fit.

## Correctness and performance checks

1. Existing coupled all-hand terminal comparisons across 3/6/9 players and32/7/1 batches, plus full GPU/CPU parity and graph-replay tests.
2. Existing active-slot regression cases: zero own reach, zero live/folded opponent reach, and positive-zero-positive changes across traversers. They replace input reach arrays directly, which specifically exercises this proposal's placement in `terminals`.
3. Add or run non-unit-mass reach inputs. Use a distribution such as scaled[1,2,4] at three classes, changing both scale and class positions between calls; compare normalized slot values against direct f32 division and terminal values against the unnormalized control. Unit-mass cases alone would not meaningfully exercise this optimization.
4. Explicitly test `gate=0` after a gated zero-reach call with stale/empty active flags, then restore positive inputs. Compare every hand and verify no old normalized values survive.
5. Poison the normalized buffer before a positive call and verify needed entries become finite. Poisoning should not be required for correctness, but exposes missing refreshes.
6. Record actual chosen batch size, memory allocation, cold initialization, fixed-iteration throughput, checkpoint latency, complete strategy/gap/EV fingerprints, and time to the same accuracy target. Compare against3295571 under the same workload and GPU conditions.
