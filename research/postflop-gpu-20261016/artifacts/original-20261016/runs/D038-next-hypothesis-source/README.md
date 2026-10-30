# D038: remove original-order showdown reach staging

Source-only, one distinct hypothesis. Baseline is **accepted E015**, not the still-unaccepted E020 candidate. No production edit, compiler invocation, GPU work, new harness, timing or acceptance change occurs here.

## Concrete opportunity

In accepted `gpu/kernels.cu:220–229`, `up_show` copies all `nh_o` global opponent reaches to `ro_sh`, synchronizes the block, then gathers the same values into sorted `reach_sh`. The only later original-order use is the guarded `ro[same_p[i]]` at line282. The card-removal loops use `reach_sh`, not `ro_sh`.

A distinct minimal hypothesis is to gather `reach_sh[k]` directly from `ro_g[o_idx[ob+k]]`, read the guarded same-hand correction directly from `ro_g[sc]`, and remove `ro_sh` and its first barrier. Sorted reach and prefix arrays would begin at `shraw` and `reach_sh+m_o`; the global source stride remains `nh_o`. Both training/evaluation shared reservations (`gpu/mod.rs:627,854`) would drop their `4*nh_o` component. All sorted indices, loops, float operands/operations, scan steps and other barriers stay unchanged. No persistent table, allocation, workspace swap, graph variant or kernel launch is introduced.

## Why this could matter, and why it could lose

It applies to every training showdown terminal for both players and to terminal evaluation sweeps, rather than only one menu or fixture. Per CTA it removes `nh_o` shared writes, the original-order shared gathers and one block barrier, and saves exactly `4*nh_o` dynamic shared bytes. At the already documented rainbow reservations that means3788→2512 and3044→2016 bytes; the1128/1081 wide-turn shape becomes13160→8648, and the conservative1326/1326 shape15912→10608. These are arithmetic resource formulas, **not queried candidate occupancy or measured improvement**. Static shared scan storage remains.

The tradeoff is substantial: a coalesced global copy followed by shared gathers becomes global sorted-order gathers plus additional same-hand global reads. Scalar logical global reads change from `nh_o` to `m_o + same_count`, where `same_count` is the number of valid own hands present in the opponent range; this may approach `2*m_o`. These counts are not memory transactions or DRAM bytes. Existing caching/coalescing may make the original staging faster, and lower shared usage might not alter actual residency. Register lifetimes/code generation can also change. Runtime NVRTC/JIT stays in the complete-cycle metric; there is no extra constructor payload to hide. No percentage speed estimate is supported.

## Exactness boundaries

The existing kernel already requires reach input to remain immutable and separate from output CFVs for the launch. The same original indices therefore select the same f32 load bits, including signed zero/subnormal values, before the same arithmetic. Keep the sentinel test before the same-hand access and permit `m_o=0` without touching sorted storage. **Retain** the barrier after sorted reach fill/CFV zeroing and all scan barriers; only the barrier protecting the deleted original-order buffer is redundant. Recheck shared offsets/alignment and both host launch sizes. Source equivalence is not compiled or native proof: future codegen/resources and the existing exact-state/F32/menu/resume/continuation controls would still be required if root authorizes a candidate. This note requests no new broad standalone numerical harness.

## Novelty and rejected alternatives

This is separate from E008's prefix carry rewrite, E019's fold reduction, current E020's integer card-position cache, E003's alias qualifiers, the closed launch/arity/child-slot specializations, and E016/E017 reach-work reuse. It changes where immutable reach values are staged, not any reduction tree, strategy probability or traversal reuse. The scoped older postflop results include shared-reach work on **fold** kernels (E011B), not this showdown removal; no exhaustive claim about every historical branch is made. Do not silently combine with E020 while its adoption remains unresolved.

A proposed extra sigma cache was screened out: preserved accepted-source PTX already uses the same normalized registers in value and strategy updates on common2/3/4-action paths. For example, baseline.ptx:3694–3742 computes `%f302`/`%f306` once and reuses them in the strategy FMAs. There are only2+3+4 division sites across those paths. The generic path still differs, but adding another cache there would target uncommon menus and potentially increase local storage; it is not a strong separate recommendation. Existing evaluation terminal reuse and average-strategy down sharing are also already implemented in `gpu/mod.rs:456–555`.

A bounded independent source critique by menu_change_review found no concrete flaw in the stated relocation: preserve global stride/sentinel handling, retained barriers and both shared-size updates. That is an informal source-only assessment, not approval of any unbuilt candidate. The next falsifiable question is simply whether removing staging yields better complete-cycle behavior without changed exact output; source savings or occupancy alone cannot answer it.
