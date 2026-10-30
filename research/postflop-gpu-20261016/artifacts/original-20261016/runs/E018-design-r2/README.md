# E018 design revision 2: public VRAM estimate

This additive archive preserves the sealed four-file E018-design and its source review. All twelve sealed parent artifact hashes were verified. The four original E018 candidate files remain byte-identical, including exact D031 CUDA SHA256 de0c0b34dbe89005c7a175618c5ece3f187686089f1775a97d781967c8c02ec4.

Root explicitly authorized a fifth source file, crates/solver/src/game.rs. Spot::vram_estimate_bytes now includes exactly 4 * tree.children.len() bytes for the immutable training child-slot table, in addition to its existing reach/CFV estimate, learning arenas and reserve. The new multiplication and final additions are checked for overflow. No unrelated traversal, allocation, solver, kernel or estimate component changes. This corrects the public-estimate limitation recorded in the sealed parent README without rewriting that evidence.

The focused CPU test game::tests::vram_estimate_counts_unused_child_mapping_entries appends three unused sentinel child positions to an already built spot: reachable nodes, hands and arenas remain unchanged, while the estimate must grow by exactly twelve bytes. This verifies that the full child vector is counted even when entries are unused. It is prepared but not executed.

Base/candidate snapshots for all five files, the complete five-file patch and hashes are present. game.rs syntax-only parsing and git diff --check passed. No compilation, tests, GPU work, commit, main checkout/server operation or evaluator/control/runner change was performed. Runtime and performance qualification remain root's work; first measurement ID is E018R1. Independent critic requested an additive r2 review.
