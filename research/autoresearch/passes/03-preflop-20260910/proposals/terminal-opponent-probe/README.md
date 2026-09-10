# Opponent-count kernel register probe

Source-only proposal against5f4f42c. `probe.patch` adds only prepared terminal entry points `pf_multiway_terminal_o2`, `_o3`, `_o4` to kernels.cu. Existing generic preferred and minimal entry bodies remain unchanged. No host dispatch, list ordering, allocation, graph or arithmetic grouping change is included. `register_test.rs` is an optional ignored test to insert inside the existing gpu.rs test module after applying the kernel probe. It creates a CUDA context, compiles/loads the same default-options PTX for the detected architecture and queries registers/local/shared memory; it runs no solver/kernel launch. Parent owns compilation/execution. Source-only patch applicability passed against extracted5f4f42c.

Each probe is copied from the prepared terminal body, replacing the shared9-entry opponent-base array with exactlyO entries, using a thread0-local filling index, and replacing the runtime opponent-count switch with the same existing pf_multiway_sum<Q,O> instantiation. O2/O3 use Q2; O4 uses Q3. Probability, ascending opponent order, within-sample/quadrature order, payoff and per-batch accumulation are unchanged. No max-register cap, reciprocal approximation or precision change is proposed.

These kernels are **not safe for arbitrary mixed-live-count lists**: each must receive only terms with O+1 live seats (and still returns when the traverser is not live). The probe does not launch them. Any production dispatcher must prove that invariant with host list coverage tests before use.

## Decision

If O2/O3 remain at64 registers, defer the host split this pass. If materially lower without spills, a short host-split experiment is justified. Lower register count alone does not prove faster execution: occupancy thresholds, shared memory, instruction count, extra launches and actual live-count distribution matter. Keep launch width and numerical controls fixed while testing that hypothesis.

## Minimal subsequent integration

Stable-partition the existing mw_terms vector by live.count_ones() (3..9), preserving node order inside each group. Use its existing GPU allocation; retain only seven (start,count) host spans. Preparation uses the reordered terms and writes probability at that reordered index, so each specialized terminal computes index=start+blockIdx.x for both term and probability lookup. No separate worklist or GPU map is needed. ValuePlan assigns every terminal a unique value slot; changing inter-terminal launch order cannot change an individual terminal's sample/batch accumulation sequence. CDF slot planning/work spans remain unchanged.

Keep sample batches outermost, then launch nonempty live-count groups in ascending order, preserving every terminal's original sample accumulation order. The original minimal-metadata path may keep its generic kernel/one launch over the same full terms list. Extra GPU bytes are zero; literal B/cache planning inputs remain the same. Host spans cost7 pairs, and graph nodes increase from one terminal launch to at most7 per sample batch. For8seat there are at most6 groups; small/empty groups should not launch.

Tests must prove exact term coverage/no duplicates, O+1 live count, stable intra-group order, probability index alignment, unique terminal value slots, unchanged CDF count/budget/B/cache, exact fixed-state terminal bits and full arenas/gaps across graph replay, zero-own/live/folded reach and ungated recovery. Existing tests that replace d_mw_terms with a single terminal must reset its grouped span too; this is the main integration hazard. No correctness tolerance changes are justified.

This is moderate work, not a no-risk launch tweak. With roughly30-45minutes for experiments, compile/register evidence should come first; only then spend the bounded integration/benchmark window. Long final gates take priority over retaining an unvalidated dispatcher.
