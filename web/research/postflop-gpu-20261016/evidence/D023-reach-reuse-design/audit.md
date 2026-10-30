# D023: reuse one player's reaches within a paired training iteration

Status: source-only design, not an implemented or measured candidate. No production edits, builds, tests, CUDA compilation, kernel launches, or status/dashboard writes were performed. Recommendation: next bounded candidate after E014 outcome, subject to exact runtime validation. No speedup is established.

The proposed minimal change is entirely in the Rust training dispatch. First p=0 sweep remains full. Only the immediately following p=1 sweep within iterate/iterate_profiled passes down_nh1=0 to the existing copy_root, down_action, and down_chance launches. Real self.nh values remain unchanged for every up kernel and evaluation. Generic standalone sweep defaults to full down; never infer reuse solely from p==1. No new CUDA entrypoint, signature, compile flags, plan order, launch count, or floating-point arithmetic is needed.

## Immutable source basis

Line references below use the accepted E004 commit 5e021499, preserved byte-for-byte under e004-source/. manifest.json records full commit, hashes, and the separately observed current checkout identity. E014 was being prepared concurrently and its current-source hashes differ in plan/mod/kernels; D023 does not treat that unqualified candidate as an accepted baseline. The kernel zero-count proof was also checked against current source, whose first down kernels are unchanged. Source copies make the proof independent of later edits.

## Dependence and call-order proof

- kernels.cu:28-94: down_action_impl chooses actor-specific regrets, reach pointer, hand count and source slot. At an actor0 node it writes only reach0; at actor1 only reach1. Its regret matching and lock path do not read the other player's reaches or regrets.
- kernels.cu:124-140: down_chance updates each player's reaches independently from that player's parent vector, immutable masks and the dealt card.
- plan.rs:145-165 and 168-205: action edges update only the actor's reach owner; chance edges update both. plan.rs:412-426 maps distinct owners to distinct physical slots, rather than recycling slots across levels. Per-player reach and CFV allocations are separate (mod.rs:365-370). Thus first-down player1 reaches survive the entire p0 up sweep.
- kernels.cu:328-403 and mod.rs:945-974: up_action receives only d_regrets[p] and d_strat[p] as writable learning buffers; reaches are const. p0 updates only player0 learning state. Other up kernels likewise read reaches and write CFV, not reach arrays. No p0 update changes the inputs of player1 reach propagation.
- mod.rs:393-434: ordinary iterate queues p0 then p1 on the same stream, either eagerly or as g0 then g1. No root, lock, evaluation, or workspace mutation occurs between the two sweeps. Therefore recomputing player1 reaches in the second down would repeat identical operations from identical inputs. Reusing the first result preserves it bit-for-bit in principle; runtime proof remains required.
- mod.rs:440-449: profiled iteration follows the same pairing; the explicit mode must also reach this path so diagnostics measure the intended candidate.

## Why passing nh1=0 is source-safe in the three down kernels

- copy_root, kernels.cu:16-24: the reach1/w1 access is inside k<nh1. Zero makes it empty. reach0 uses unmodified nh0. Existing grid and positive stride stay unchanged.
- down_action_impl, kernels.cu:43-94: actor1 nh_a becomes zero. It still reads valid node metadata, including action count, lock offset and reach source. parent_reach computes reach1 + src*0, the valid base pointer; it is never dereferenced. A locked node forms its already-valid lock_sigma+loff pointer, but all sigma indexing and writes are inside i<nh_a. The unlocked regret reads, uniform pr/na division, child reads and reach writes are also inside that empty loop. No division by nh_a/nh1, no modulo, and no barrier exists here. Actor0 continues with its real nh0 and unchanged offsets.
- down_action wrapper, kernels.cu:97-120: it dispatches the same 2/3/4/generic specialization after valid metadata reads. No shared memory, barriers or hand-count division.
- down_chance, kernels.cu:124-140: pr1 becomes reach1+rsrc1[pn]*0 (valid base); mask1/pr1/child reach1 accesses are wholly inside j<nh1. Player0's loop is unchanged. No barrier or division.
- Retain the actual allocated reach1, regrets1, weights1, lock buffers and pointers; zero is a loop-bound override, not a zero-sized allocation or altered layout. Existing zero/empty solver handling is not expanded by this proposal.
- Keep true nh_p, nh_o, nh_max and show shared-memory sizing for the upward pass. Do not overwrite self.nh, globally redefine nh1, pass zero to fold/show/action-up, or alter eval_down.
- Metadata work and actor1 CTAs still execute their prologue. Eliminated hand visits do not translate directly into time saved, and this design does not remove launch overhead.

## Entry-point and lifecycle boundaries

1. Exploitability overwrites d_reach using average-strategy propagation: mod.rs:477 and 522 call eval_down; its implementation starts at545. Every iteration's p0 first down must always recompute BOTH players in full, regardless of what ran before it. No cross-iteration reuse or dirty flag is proposed.
2. Graph capture: mod.rs:400-423 captures both sweeps, then425-428 launches both in order. The p1 graph can have down_nh1=0 recorded, provided every ordinary graph pair always launches g0 full first. Capturing a graph is not execution and creates no dependence on pre-capture device contents. Capture emits no extra device allocation or new kernel load. A resumed solver can have iteration>0 at construction (mod.rs:377) and capture on its very first iterate, so safety must come from ordered g0 execution, not an assumed warmup.
3. Lock updates: mod.rs:1033-1044 synchronizes, replaces tables, invalidates training/eval graphs. The next p0 down is full and sees the updated lock. No lock update may occur between the paired sweeps; current public &mut self call structure provides that boundary.
4. Standalone continuation: mod.rs:171-193 accepts arbitrary p, t and new own/opponent roots, uploads roots, and dispatches one sweep. It must explicitly request full down even for p1. It has no preceding-p0 guarantee.
5. Projected continuation: continuation.rs:119-136 calls that same single-sweep bridge and then project/transport. Keep full down; do not infer safety from caller p or t.
6. Paging: continuation_paging.rs:88-128 swaps all arena/reach/CFV workspace buffers, uploads learning state, dispatches a single continuation sweep, synchronizes and swaps back. Reaches may belong to another board. Full down is mandatory.
7. Stored/compact/disk continuation: continuation_storage.rs:301-359 swaps workspaces, uploads/restores/possibly transports state, dispatches wrapper.sweep, synchronizes and restores buffers. Full down is mandatory regardless of whether two consecutive calls happen to have p0 then p1.
8. Sync/readback paths need no change. Error paths must not independently retry only a reused p1 sweep; the reuse mode is private to complete pairs.

## Minimal host design sketch (not code applied)

Keep sweep(p, prof) as the full-down wrapper used by standalone research. Add a private paired helper taking an explicit reuse_player1_reach flag (or a small enum), assert reuse implies p==1, and use a separate local down_nh1 = if reuse {0} else {self.nh[1]}. Change only the three down launch argument sites in that helper (E004 mod.rs:774,806,832). Ordinary iterate capture/eager and iterate_profiled explicitly request false for p0 and true for p1. All upwards arguments still derive from true self.nh. This keeps the hazardous optimization visible at the paired callsites rather than silently changing the meaning of a generic p1 sweep.

## Structural work estimate (not timing)

D001-action-census.log is preserved with its hash. work-counts.json recomputes actor counts by summing per-level nodes_by_actor and checks the total against the recorded training_down_hand_visits_per_iteration.

| Fixture | Hands 0/1 | Action nodes 0/1 | Baseline down-action hand visits/iteration | Avoided player1 visits | Fraction avoided |
|---|---:|---:|---:|---:|---:|
| rainbow |257/319|274801/248732|299938730|79345508|26.453905%|
| two-tone |258/320|167213/151349|183145268|48431680|26.444407%|
| river |233/280|6/6|6156|1680|27.290448%|

On each flop chance edge, avoided player1 hand visits are nh1 of the baseline 2*(nh0+nh1): 27.690972% rainbow and27.681661% two-tone. River fixture has no chance work. These are hand-loop visit counts, not action-weighted FLOPs, bytes, kernel duration or whole-cycle savings. They exclude evaluation, up sweeps, initialization, readback and retained metadata/dispatch. D020 synchronized profiling only prioritizes investigation; its distorted host spans do not establish an absolute performance ceiling or expected complete-cycle gain.

## Historical scope

prior-search.json contains exact matched old metadata line numbers and hypotheses. Old E009 compacted reach-owner storage; E023 specialized action arity; E030/E030A captured evaluation. Prior postflop-eval-proposal.rs reuse concerned fixed-strategy evaluation. None of the searched evidence implemented one unchanged player's reach reuse inside ordinary alternating training. Current E005/E014 specialize up-action arity; E006/E007 cap registers; E008 changes showdown prefix; E009/E010 quantize readback; E012/E013 alter host encode codegen. They do not test this dependency elimination. Search is bounded, not a claim about every unsearched branch. No historical research was resumed.

## Minimum next evidence before performance qualification

- An ignored diagnostic or bounded internal test first captures raw d_reach[1] bits after full p0 down/up and after the legacy full p1 down, demonstrating that the omitted recomputation is identical. Compare entire device vectors, not just compressed final fingerprints. A two-instance legacy/candidate test then compares both reach arrays plus live regret/strategy/CFV bits at matched valid boundaries; CFV scratch before initialization should not be compared as meaningful state.
- Exercise first eager iteration, first capture and steady graph launches; exploitability then another iteration; lock changes then iteration; nonzero saved-state resume; compressed and F32 storage; full and isomorphic compact plans; DCFR and CFR+; single,2/3/4,generic action counts. Generic standalone continuation must still recompute both arrays after changed roots, including p1 without a p0 predecessor and workspace/paged restoration. A poisoned reach sentinel can make failure to refresh obvious.
- Signed zero, denormal and nonfinite payload preservation must be judged by raw bits rather than compressed values; the proposed arithmetic is unchanged, but quantization could hide divergence. Valid production ranges and solver state remain the benchmark domain.
- Kernels source and compiled resources should remain unchanged with the host-only nh1 variant. Keep frozen evaluator/config/target/stops untouched. After exactness, run serialized paired full-cycle measurements under the existing aggregate and per-fixture guard. No mathematical settings may change to pass.

No implementation or runtime proof is included in D023. Root decides sequencing after E014; this artifact is a bounded next-hypothesis recommendation only.
