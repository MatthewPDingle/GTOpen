# D039: conditional composition of D038 with E020

**Source-only conclusion: compatible under the existing input and layout contracts.** This is an additive note, preserving sealed D038's accepted-E015 scope. E020 final acceptance is a prerequisite to any candidate based on E020. No source activation, candidate files, build, GPU work or performance claim is authorized by this note.

In the pinned E020 `up_show`, `ro_sh` is copied before the first barrier, together with the immutable `card_pos_sh` table. The sorted reach fill follows that barrier. No card-position read occurs until the final hand-output loop, after the sorted-fill/CFV-zeroing barrier and all prefix-scan barriers. Once the original-order reach stage is removed, its first barrier has no remaining required consumer: the existing barrier after direct sorted reach fill publishes **both** `reach_sh` and the earlier `card_pos_sh` writes before either is consumed across threads.

Keep the card-position copy in its existing order, gather `reach_sh[k]` from the exact original `ro_g[o_idx[ob+k]]`, and read the sentinel-guarded same-hand correction from `ro_g[sc]`. All card loop indices, strength comparisons, scan operations, float additions/multiplications and remaining barriers retain their order. The global reach stride remains `nh_o`.

For `m = m_o`, the prospective dynamic shared layout is:

| Region | Byte interval | Size |
|---|---:|---:|
| Sorted f32 reaches | `[0, 4*m)` | `4*m` |
| f32 prefix | `[4*m, 8*m)` | `4*m` |
| u32 card positions, exactly `2*m` entries | `[8*m, 16*m)` | `8*m` |

Each base is four-byte aligned under the same shared-base alignment assumption as E020, and the regions are disjoint. With `m=0` they are empty; the existing count/sentinel guards still prevent invalid dereferences. Keep the static `chunk_sum[257]` declaration and every scan barrier unchanged. This is not the rejected E008 prefix recurrence or E019 fold reduction.

Both `eval_up` and `paired_sweep` reservations in pinned `gpu/mod.rs:627,854` must change from `16*riv_max_cnt[opponent] + 4*nh_o` to `16*riv_max_cnt[opponent]`. Per-slot `m_o <= riv_max_cnt[opponent]` remains the sizing invariant. There are no added persistent buffers, admission-table bytes, transfers, graph variants or launches. Existing graphs simply capture the updated shared-size argument if a later candidate is built.

The unchanged contracts matter: reach input must remain immutable and separate from CFV output throughout the launch; `o_idx` and non-sentinel `same_p` indices must be within `nh_o`; card offsets must remain contiguous with exactly `2*m_o` valid positions; the block-uniform count return must precede all barriers, and every active thread must reach the retained sorted-fill barrier. Distinct shared regions permit card-position and sorted-reach writes to proceed without the removed barrier. Current E020 callers already require global reach/CFV separation and serialized traversal. This note introduces no new lifetime or workspace-swap policy.

Computed dynamic reservations would be: rainbow 6300→5024 and 5060→4032 bytes; the full-range turn shape 21808→17296; the conservative 1326-hand bound 26520→21216. These are formulas, **not queried candidate occupancy or observed speed**. In particular, they do not establish recovery of E020's theoretical wide-range residency reduction.

The tradeoff remains D038's: direct sorted global gathers can be less efficient than the original coalesced copy followed by shared gathers, and same-hand corrections add global reads. Logical float source reads become `m_o + same_count`, potentially nearly `2*m_o`, rather than `nh_o`; these are not DRAM transactions. E020's integer-cache copy cost remains. Reduced shared capacity and one fewer barrier may still lose overall, especially with broad overlapping ranges, and compiler register usage can change. E020's existing holdout result cannot be inherited as this unbuilt composition's performance evidence. Any later candidate must preserve exact state and pass its own complete-cycle and relevant broad-range checks; source compatibility alone grants neither acceptance nor a gain.
