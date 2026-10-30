# E018: mapped child CFV slots for training-up actions

Source candidate only. No numerical or performance result is claimed. Base is accepted E015 (`mod.rs` SHA256 `7de2cd46ef93742c603042306cfe2ad08a83ff52a2be1123efd9d201aca15f1a`). Rejected E016 and E017 are absent. The logical E018 dashboard row is reserved; the first measurement must be E018R1.

Only `gpu/mod.rs`, `gpu/plan.rs`, `gpu/kernels.cu` and `gpu/continuation_capacity.rs` change. Base/candidate copies, patch and exact hashes are preserved alongside this document. The parent owns builds, serialized execution, independent baseline comparisons and acceptance.

## Hypothesis and exact scope

The CUDA file is byte-identical to D031's compiler-probed candidate (`de0c0b34dbe89005c7a175618c5ece3f187686089f1775a97d781967c8c02ec4`). Training up substitutes `child_cfv_slots[cs+a]` for `cfv_slot[children[cs+a]]` in exactly four places; original arithmetic, operands, action order and arity dispatch remain. D031 supports a shorter static integer addressing sequence, not lower register/local storage, occupancy improvement or any speed claim.

The plan allocates a full `tree.children.len()` table initialized to SENTINEL. It fills only original child-vector indices belonging to visited action nodes. Every consumed child must be a valid node with a non-sentinel physical CFV slot smaller than cfv_blocks. Chance sentinels and every unvisited action position remain unconsumed SENTINELs. The original child vector, node IDs, worklists, arena offsets, physical CFV allocation and visitation order are unchanged; full-arena conversion does not alter this table.

GpuSolver uploads one immutable slice before any graph capture and binds it only at the single training up_action call. Down action, upward chance and independent evaluation keep their original children/slot inputs. E015's two graphs, paired reach reuse, standalone full sweeps, evaluation invalidation, locks and warm reconstruction semantics are unchanged. The new slice remains solver-owned and is never exchanged in the seven-buffer continuation workspace swaps.

## Cost and accounting

Every plan, including river, pays one allocation/upload of exactly `4 * tree.children.len()` device bytes and a temporary host table of the same payload size, plus sentinel initialization and visited-edge mapping. This is the full vector size, **not** just visited action-edge count. No benchmark-specific shortcut is present. Constructor, upload, JIT and all other setup costs stay in their original complete-cycle timing boundaries. Added allocation/teardown effects and the river regression guard remain relevant.

`training_metadata_bytes()` centralizes the exact checked byte count. With parent approval, `staging_bytes()` explicitly documents a traversal-working total including that metadata, so existing frozen exact-budget callers remain coherent. Constructor full-F32 selection and compact admission include it once and use checked arena/reserve additions. The 512 MiB reserve is not used to hide this added payload. Continuation accounting independently sums the new actual CUDA slice and estimated vector once; no staging total is added there. StoragePlan retains only its existing mapping arrays, so the new host vector is temporary and adds no retained host payload after construction.

The separate user-facing rough game.rs VRAM estimate is unchanged within the four-file experiment scope. Root was informed that explicit addition of this payload to that estimate may be needed if the candidate qualifies for integration.

## Prepared validation (not executed here)

- `gpu::plan::tests::child_mapping_handles_generic_menus_and_rejects_invalid_physical_slots` covers a >8-action menu, an empty visited list, and rejection of sentinel/out-of-range consumed slots before upload.
- `gpu::plan::tests::river_bounds_match_strength_comparisons` now checks every table entry against the original physical lookup for flop/turn/river with isomorphism off/on, requires actual chance and inactive-action sentinel coverage, checks exact additional bytes, and proves full-arena conversion preserves the map.
- The existing GPU lifecycle helper reads the device table back and compares it with the host plan for its F32/compressed, full/compact, DCFR/CFR+, lock, evaluation and warm cases. Its full-sweep reference shares the candidate up kernel and therefore does **not** independently prove original-up equivalence. Preserved-baseline versus candidate controls remain essential.
- Feature-gated `gpu::continuation_capacity::tests::child_mapping_matches_observed_metadata_for_turn_and_river` checks full table allocation/readback, observed-versus-planned metadata, stored-capacity planning and exact-once delta accounting.
- Existing budget-minus-one, full-state/menu (>8-action generic kernel), lock, resume, continuation/paging/storage checks and the frozen full-cycle performance gate remain required according to root's staged qualification protocol.

Syntax-only rustfmt parse and `git diff --check` passed. Mechanical checks verify the exact probed CUDA file, protected evaluator/store/arena hashes, byte-identical graph/iteration/generic/evaluation/lock/continuation methods, and a paired-sweep body identical after reversing its single argument substitution. No compilation, tests, CUDA context, solver run, commit, server mutation or deployment was performed by this builder. Independent source review is requested from menu_change_review and will be preserved separately under comparisons/E018-source-review.
