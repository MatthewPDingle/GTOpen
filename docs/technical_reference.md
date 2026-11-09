# Technical reference

Engine details, runtime settings, historical benchmarks, and scripting interfaces.
For installation and the app workflow, start with the [README](../README.md).

## Runtime settings

Optional environment:

| var | default | meaning |
|---|---|---|
| `PORT` | 3737 | HTTP port |
| `GTOPEN_HOST` | `127.0.0.1` | HTTP bind address: an IPv4/IPv6 literal, not a hostname. A non-loopback value exposes the unauthenticated API (solves, locks, saves, the served `docs/`/`research/` files) to the network. The Windows launcher probes and opens the selected address. Wildcards use a loopback URL in the same family: `0.0.0.0` opens `127.0.0.1`, and `::` opens `[::1]`. `::1` remains IPv6-local-only; `0.0.0.0` and `::` expose the listener to the network |
| `SOLVER_THREADS` | physical cores | rayon worker threads (SMT hurts this workload; 12–16 is the sweet spot on a 5950X) |
| `SOLVER_COMPRESS` | 1 | `0` = full-precision f32 arenas instead of 16-bit compressed |
| `SOLVER_GPU` | 1 (if built with `gpu`) | `0` forces the CPU engine even when CUDA is available |
| `SOLVER_GPU_MEM_MB` | live free VRAM − 512 MB | manual VRAM cap for the GPU engine; spots over budget fall back to CPU |
| `SOLVER_MEM_MB` | 80% of free RAM (≤48 GB) | solver-arena + tree RAM budget; bigger builds are refused |
| `PREFLOP_EQ_SAMPLES` | 20000 | Monte-Carlo samples per hand-class pair for the Preflop Lab equity table |
| `PREFLOP_MAX_NODES` | RAM-derived | Preflop Lab tree-size limit; the lab shows a live estimate + this machine's caps before BUILD |
| `PREFLOP_MAX_ARENA_MB` | ~40% of free RAM | Preflop Lab regret/strategy memory limit (MB) |

## Postflop all-in threshold units

`POST /api/spot` and the nested `spot` in `POST /api/reports/run` use
**percent of effective stack** for `allin_threshold`. Omission defaults to
`85` (85%). Numeric values must be in `[1, 100]`; invalid values return HTTP
422 before building a tree or replacing the current session.

| HTTP value | Meaning | Solver/CLI fraction |
| --- | --- | --- |
| omitted or `85` | 85% | `0.85` |
| `1` | 1%, preserving the existing HTTP convention | `0.01` |
| `100` | 100%; keep sizes until they reach the stack | `1.0` |
| `{"percent": 0.85}` | intentional 0.85% | `0.0085` |
| bare `0.85` | HTTP 422: likely copied CLI units | — |

For intentional thresholds below 1%, use the explicit object form
`"allin_threshold": {"percent": 0.85}`. Its `percent` must be finite, greater
than zero, and at most 100. Extra object keys are rejected. Status and report
readbacks use this form for sub-1% values so they can be submitted again;
ordinary thresholds continue to serialize as numbers. The setup UI performs
this encoding automatically and displays percent values.

CLI `SpotConfig.tree.allin_threshold`, including `bench_spot.json`, continues
to use a **fraction**. Convert a CLI fraction to an HTTP percent by multiplying
by 100: CLI `1` becomes HTTP `100`, not HTTP `1`. Units are never auto-detected.
Clients that deliberately sent numeric values below 1 must migrate to the
explicit percent object. Values above 100 are now rejected; use 100 to retain
configured sizes until they reach the stack. Existing solver save formats and
their tree configuration are unchanged.

## Engine

- **Algorithm**: Discounted CFR (α=1.5, β=0, γ=2) with alternating updates,
  vectorized over hands. CFR+ and Predictive CFR+ (PCFR+) are selectable per
  solve (`POST /api/solve {"algorithm": "pcfr+"}` or `SOLVER_ALGO` in the CLI).
- **Compressed arenas (16-bit)**: regrets stored as i16 and strategy
  sums as u16, quantized per node against the node's max magnitude — half the
  memory of f32, and faster on big trees because CFR is memory-bandwidth
  bound. Accuracy regressions compare it with f32; this is not a universal
  error bound for every game. CPU updates use reproducible stochastic rounding
  to retain small changes. Save files stay full-precision f32 and load into
  either mode. [CPU convergence details](postflop_convergence.md).
- **Zero-allocation traversal**: all per-node-visit scratch vectors come from
  a thread-local buffer pool instead of malloc.
- **CUDA GPU solver**: level-synchronous CFR with f32 working arenas in VRAM
  (`--features gpu`). On the current RTX 3090 benchmarks, the 1.35M-node
  rainbow/two-tone flop cases take **51.8 / 31.4 ms per iteration**.
  Exploitability also runs on the GPU, with reusable evaluation graphs and
  batched root downloads. Node locks, DCFR/CFR+, and both CPU storage modes
  are supported; PCFR+ uses the CPU. Compressed CPU arenas decode on upload
  and re-encode on sync. Visited action blocks are packed where worthwhile,
  value scratch is reused between tree levels, and inactive state is preserved
  for exact save/resume and CPU browsing. The server uses CUDA when available;
  `SOLVER_GPU=0` opts out. The default VRAM budget is **live free VRAM minus
  512 MB headroom**, with `SOLVER_GPU_MEM_MB` as a manual override. The final
  GPU plan is checked at solve time; allocation or CUDA failures fall back to
  CPU. The UI's conservative full-tree estimate can exceed that final plan.
  See [current performance and validation](../research/autoresearch/gpu-pass.md).
- **Terminal evaluation**: O(n) sorted showdown sweep with exact card-removal
  (blocker) accounting via per-card prefix sums; precomputed 7-card strengths
  for every river runout.
- **Exploitability**: true best-response traversal both ways, reported as % of
  pot — a best-response measure for the configured game; locks change the game being evaluated.
- **Parallelism**: rayon across chance branches; arenas use disjoint unsafe
  slices (each tree node's data is touched by exactly one branch).
- **Suit isomorphism**: chance branches that are suit-symmetric (given the
  board and ranges) are solved once and mirrored exactly — ~1.4x on two-tone
  flops, ~2.2x on monotone, no effect on rainbow. Exact (verified against the
  non-isomorphic solver). Read-only CFV traversals can skip zero-opponent-reach
  subtrees; learning traversals still update their own strategy averages there.
- **Trees**: per-street/per-player bet, raise and (OOP) donk sizes, all-in
  threshold conversion, raise caps, NL min-raise rules, rake (% + cap),
  flop/turn/river root. EVs use the pot-share convention (EV OOP + EV IP =
  pot).
- **Accuracy tests** (`cargo test -p solver --release`): hand evaluator vs an
  independent reference on 20k random deals; range parser round-trips; the
  clairvoyance game converges to its known closed-form solution (bet-ratio
  1/3 bluffs, MDF 50% calls, EVs exact); equity matches brute-force
  enumeration; full flop trees reach <1% pot exploitability; node-lock
  semantics; save/load roundtrip (both storage modes); compressed-vs-f32
  exploitability equivalence; PCFR+ convergence; exploit-view best response
  vs a locked station (bets the nuts, never bluffs, BR EV dominates);
  per-hand locks land on the right combos across suit-isomorphic runouts;
  preflop CFR vs an independent fictitious-play Nash oracle on HU jam/fold,
  plus multiway limp-tree chip conservation and rake-drain direction.

## Trust the read (postflop)

A postflop profile lock fixes the villain's whole tree, and the hero's
re-adapted strategy is a full best response to that read. `Solver::set_trust`
adds Restricted Nash Response (Johanson, Zinkevich & Bowling 2007): with
probability p the villain plays the profile locks, otherwise he plays freely
and learns against the hero. The hero does not know which villain he faces,
so his strategy keeps updating that belief along the hand; a line the profile
never takes tells him he faces the free villain.

- **Semantics**: profile locks are the read. Manual point locks and running
  fits bind both villains. The read villain is today's locked villain: he
  re-adapts wherever the profile leaves a node open (deep raise lines below
  its mass cutoff, for example) in the main arenas. The free villain has his
  own regret and strategy arenas while the dial is on, copied from the main
  ones when it turns on. The two must not share open nodes: a shared node
  learns only from the free villain's values while the read plays it too,
  and on the deep bench flop trust 0.9 then stalled at 0.12% pot instead of
  reaching 0.001%.
- **p = 1** (or unset) is today's lock-and-re-adapt solve; **p = 0** is the
  unlocked solve, bit for bit on the CPU (`tests/rnr.rs`).
- **Engine**: each iteration runs the hero's pass and two villain passes: the
  read villain's (an ordinary locked pass) and the free villain's (profile
  locks off, his own arenas). The hero's pass carries the villain's reach as
  two stacked blocks (read, free) and evaluates terminals against
  p × read + (1 − p) × free, which is exact because terminal values are
  linear in the opponent reach. The GPU keeps the free villain's arenas and
  one extra copy of the villain's reach, filled by a second down sweep and
  mixed before the hero's up sweep (`tests/gpu_rnr.rs`). The villain's two
  sweeps share the reaches the hero's sweep computed. On the 5090 bench flop
  (1.35M nodes) an iteration with the dial on costs 33 ms against 19 ms for
  the locked solve, the same at every trust level (`tests/rnr_bench.rs`).
- **Readout** (`Solver::trust_readout`, `GpuSolver::trust_readout`): the
  hero's EV against the read and against the mixture, and the EV of a villain
  who best-responds to the hero (profile locks off). In zero-sum games it
  also gives the hero's worst-case EV, which is the pot minus that number.
  While the dial is on, `exploitability` measures the trust game: the hero's
  best-response gain against the mixture plus p times the read villain's
  gain and (1 − p) times the free villain's gain, halved.
- **A new trust level** restarts the average strategy (`restart_averages`):
  otherwise DCFR's t² weighting keeps iterates of the old game and a
  warm-started sweep stalls. Locked nodes keep their pre-lock average, so
  re-applying a profile still rakes from the solve. The restart does not
  depend on the solver's own iteration count, which is stale while a GPU
  drives the solve. A warm sweep from trust 1 down to 0 on the bench flop
  converges to 0.3% pot in 80 to 200 iterations per level.

**Server and UI.**

- **Setting the dial.** `POST /api/trust {"trust": p}` sets the dial; `null` unsets it, which means full trust. A running solve picks the change up at once: a new level restarts the average strategy, and the iteration budget and the convergence chart start again. `/api/solve` also takes `trust` to set the dial before the run.
- **Readout.** When a solve ends with a villain profile locked, `status.trust_readout` gives the level's `TrustReadout`, computed on the GPU when the solve ran there. Any lock edit clears it.
- **Sweep.** `/api/solve` with `"sweep": [levels]` solves the levels in order, each warm-started from the last. An empty list means 1, 0.9, 0.8, 0.7, 0.5, 0.25, 0. `max_iterations` and the target apply to each level.
  - A sweep needs a profile lock.
  - `status.trust_sweep` lists the levels, the one being solved, and one point per finished level: the readout plus its iterations and seconds.
  - STOP ends the sweep with the levels it finished.
  - The curve stays through later plain solves, so you can pick a level and RE-SOLVE. A lock edit clears it.
  - While a sweep runs, `/api/trust` is refused.
- **Browse.** With a villain locked, the TRUST THE READ panel shows the slider (5% steps), the last readout and SWEEP. The sweep curve plots the hero's EV against the read (solid) and his worst case (dashed) over trust, and clicking a point sets that level.
- **Reports.** A vs-villain report takes `villain.trust`. The hero then re-adapts at that level, and each flop's `villain_lock.trust` holds the readout. The REPORTS form adds the level to the villain's name, so the library and Compare show it.

## Trust the read (preflop hero mode)

In Preflop Lab hero mode every other seat is frozen, and a seat with a profile plays it (its "read"). `PreflopSolver::set_trust(Some(p))` turns on the same dial as postflop (`preflop/rnr.rs`). Each profiled seat other than the hero is, independently of the others, its read with probability p and otherwise a **free type** that ignores its profile and keeps learning against the hero. Point locks bind the free type too. Solver and frozen seats without a profile are not affected. The hero solves against the mixture without knowing which types he faces.

- **Engine (CPU).**
  - Each free type has its own arenas, seeded from its seat's table regrets.
  - The traversal carries one extra reach per free type.
  - Terminals see each ruled seat at t · read + (1 − t) · free.
  - Each iteration runs the hero's pass, then one pass per free type, then discounts both arena sets.
  - The mix is exact wherever the terminal value is multilinear in the opponents' ranges: fold wins, heads-up pots, the coupled-deck and legacy multiway models, and side pots in chip EV. `tests/preflop_rnr.rs` checks it against the expectation over the four type pairs of two seats.
  - The 3-way table and ICM normalize the ranges they combine, so there the mixture is priced as one range. This is an approximation, and it matters only where two ruled seats meet in one pot.
- **Engine (GPU).**
  - Where a ruled seat does not traverse, it plays the behavioral mixture of its two types. `pf_rnr_mix` (`gpu/rnr.cu`) writes that mixture into the forced-policy table before each pass. The seat's reach is then exactly the mixed reach, so the down sweep and every terminal kernel (ICM and side pots included) run unchanged.
  - The free arenas sit after the main ones.
  - Each pass swaps in its own seat modes, forced offsets and arena offsets: all mixed for the hero, one seat free, or one seat read for evaluation.
  - Only the normal plan does this; the throughput variants decline the dial.
  - `tests/preflop_gpu_rnr.rs` matches the CPU in chip-EV, side-pot and ICM games.
- **Anchors.**
  - An unset dial is plain hero mode.
  - At 100% the hero plays the max exploit, while the free types learn a response that carries no weight for the hero. That response is what the readout's "if they adapt" number measures.
  - A new level restarts the hero's average (iteration 0).
- **Readout** (`trust_readout`, bb/hand): the hero's EV against the reads, against the mix, and against seats that adapt.
  - With three or more players an adapting seat maximizes its own EV, not the hero's loss. So "if they adapt" is not a strict worst case.
  - Under ICM, adapting seats can even help the hero.
  - While the dial is on, a ruled seat's gap is its free type's gap, and its EV is the trust-weighted EV of its two types.
- **Server.**
  - `POST /api/preflop/trust {"trust": p|null}` sets the dial; it is refused while a solve runs.
  - `/api/preflop/status` mirrors `trust` and `trust_seats` (the seats it acts on), and `trust_readout` is measured at each accuracy check.
  - Table, hero or lock changes clear the readout.
- **UI.**
  - Below HERO, the TRUST THE READ row appears in hero mode when another seat has a profile.
  - It has a 5% slider, OFF, the seats it applies to, and the last readout.
  - RE-SOLVE adapts the hero at the new level.

## Preflop continuation model

New preflop games use `coupled_deck_v1` at leaves with **three or more live players**, including all-in showdowns. A deterministic table of 1,024 samples (seed 90210) assigns coupled latent hand strengths. Each sample awards the pot to its winning hand(s), so the players' shares sum to the pot after the configured rake. This replaces the old product of separate heads-up equities, which could substantially undervalue multiway calls.

These latent strengths are an approximation, **not jointly dealt physical hole cards and boards**. Opponent card removal remains approximate: heavily overlapping premium ranges can still produce large errors. Pot conservation and a small best-response gap establish consistency within the configured model; they do not establish accurate real-game equity or a unique multiway Nash strategy.

**Exact 3-way table (opt-in, `three_way_table_v1`).** Pots with exactly three eligible players can instead use `cache/preflop_eq169x3.bin`. For every class triple it stores the hero's showdown share with all three hands dealt from one deck (20,000 Monte-Carlo boards per triple, seeded per triple), plus the fraction of combo triples that can be dealt together. Against opponent class distributions A and B the hero's share is `sum_ab A[a] B[b] w[h,a,b] e[h,a,b] / sum_ab A[a] B[b] w[h,a,b]`, so card removal among the three hands is exact at the class level. Pots with four or more players keep the coupled-deck model, as do 4+ way side pots; 3-seat side pots use the table. The Preflop Lab enables it with "exact 3-way equity"; the API takes `?multiway_model=three_way_table_v1` on `/api/preflop/spot`. `cargo run --release -p solver --example build_three_way_table` rebuilds the cache, and `three_way_model_compare` solves 3-handed spots under both models. On the GPU, `pf_three_way_terminal` prices single-pot 3-way terminals and `pf_side_pot_terminal` the 3-seat side pots; the throughput variants decline these games. A table lookup costs about 4.8M multiply-adds per 3-way terminal and seat, several times the coupled model's cost on CPU.

Multiway leaves use showdown expectation with the requested rake and cap, without a positional realization multiplier or future betting. New UI scenarios select `balanced` for heads-up leaves: relative hand-class priors divide one pot, then the configured rake is deducted explicitly. This is an accounting correction and a new approximation, not a retrained rake-free postflop solver. Legacy `calibrated`, `static`, and `raw` modes remain available; `calibrated` embeds its training rake. [Balanced model, units, and limitations](preflop_balanced_model.md). Neither continuation model solves a full postflop tree during a Preflop Lab solve.

`leafnet` (beta, opt-in) prices heads-up flop leaves with chips behind as `balanced` plus a learned correction. A small net (`cache/leaf_net_v1.bin`, or the file named by `LEAF_NET`) trained on exact flop solves from the [community dataset](contribute-compute.md) predicts how far each hand class's solved value is from the balanced value, given both players' ranges at that leaf, the pot, the stack behind, the rake and the pot type. The ranges move while the solve runs, so every 50 iterations (`PREFLOP_LEAF_REFRESH`) the solver walks the average strategies to every such leaf, runs the net, and blends the result half and half with the previous correction. A correction is held to what a hand can win or lose there. The correction is not saved: loading a game recomputes it from the saved averages. The net was trained on broad random ranges, not on ranges from real preflop solutions, and it does not cover multiway pots, ICM games (refused) or all-in leaves. On the GPU the learned leaves use the standard evaluation plan; the host refreshes the correction from a downloaded snapshot and uploads it. `cargo run --release --example leafnet_preflop -- GAME.json ITERATIONS` solves a game both ways and prints what moved.

The API identifies the active model as `multiway_equity_model` in build/load responses and session/status readbacks. Existing saves without this field load as `legacy_product`, preserving their payoffs, regrets, and strategy sums. **RE-SOLVE does not migrate a saved game**: save it first, then build and solve a fresh game to use the new model. New coupled-deck files use `GTOPREFLOP2`, so older binaries reject them instead of silently using the wrong payoff model; legacy games continue to save as `GTOPREFLOP1`.

Games with `balanced` or `leafnet` realization or separate 4-bet+ menus use `GTOPREFLOP4`, retaining both continuation models and all sizing overrides. Straddle games without those features use `GTOPREFLOP3`. Older binaries refuse unsupported versions.

## Per-seat stacks and side pots

`PreflopConfig.stacks` (optional, one bb amount per seat, before antes) gives each seat its own stack; `stack` stays as the all-equal default and should hold the deepest stack. Absent or all-equal `stacks` builds exactly the equal-stack tree, with bit-identical solves.

- **Tree.** A seat that cannot cover the bet may call all-in for less (even with limping off). A raise is capped at the deepest stack still able to call it, so a big stack's "all-in" against shorter seats is labelled with the amount that can be called. No raise is offered when no one behind can put in more chips. An all-in for less than a full raise does not reopen raising for a seat that already acted, unless the raises since add up to a full one (standard no-limit rule); seats that have not acted keep their raise.
- **Pots.** At a flop or showdown terminal the top contributor's uncalled chips are returned first. If live seats are all-in for different amounts, the pot is split into a main pot and side pots by all-in level (antes go to the main pot; folded chips go to every pot their contribution reaches). The node view lists them under `side_pots`.
- **Payoffs.** Expected value is linear in the pots, so each pot pays its amount times the seat's chance of holding the best hand among the seats eligible for it. Two-way pots use the symmetrized pairwise equity table, so they pay out exactly what is in them; three or more use the game's multiway model. Rake is charged once on the whole pot and shared in proportion to pot size. Every side-pot terminal has a live all-in seat, so it is priced as showdown equity under every realization model.
- **Exports.** SEND TO POSTFLOP uses the effective stack (the smaller of the two remaining stacks). SEND TO 3-WAY carries each seat's remaining stack. Neither is offered at a terminal with side pots or, for 3-way, when a live seat has no chips behind.
- **GPU.** Side-pot terminals have their own kernels. `pf_side_pot_terminal` runs after `pf_terminal` and prices heads-up pots with the symmetrized table (and 3+ way pots with the legacy product). Under the coupled model, `pf_side_pot_multiway` adds each 3+ way pot after every particle batch, reading the same CDF slots as `pf_multiway_terminal`, which skips these terminals. Pot amounts are uploaded already scaled by the terminal's rake. The shared-CDF throughput variants (retained cohorts, static CDFs) decline side-pot trees, so `new_throughput` picks the normal GPU plan for them. Equal-stack trees upload no side-pot data and launch the same kernels as before.
- **Saves.** Games with unequal stacks save as `GTOPREFLOP5` so older binaries refuse them rather than rebuild an equal-stack tree.

## ICM payoffs (tournaments)

`PreflopConfig.icm` turns a Preflop Lab game into a tournament spot: `{"payouts": [50, 30, 20], "field": [22.5, 40], "field_groups": [{"stack": 25, "count": 140}]}`. `payouts` is the prize for each finishing place among the players still in (first place first, any currency; only ratios matter). `field` lists the stacks in bb of players at other tables, who share the remaining places but take no part in the hand; `field_groups` adds many of them at once as counts of equal stacks. Every terminal then pays each seat the change in its Malmuth–Harville prize equity instead of its chip delta.

- **Units.** Values are big-blind equivalents: prize-equity change times total chips (table plus field, antes included) over total prizes. Winner-take-all payouts make prizes linear in chips, so they reproduce chip EV exactly; the build and session responses carry `icm` with `bb_per_prize`, each seat's and field player's prize equity before the hand, and the number of priced outcomes.
- **Exact ICM.** Malmuth–Harville by dynamic programming over the players already placed. Field players with equal stacks are interchangeable, so the state records how many of each group are placed (mixed radix) rather than which ones, and only the paid places are walked: a 1,000-player bubble with every off-table player at one stack prices in milliseconds. Fields with too many distinct stacks are refused (`MAX_STATES`). Players who bust in the same hand finish below every survivor, a larger starting stack higher; equal starting stacks split the places they cover.
- **Outcomes.** Stacks after a hand depend only on who wins each pot, so every terminal's outcomes (a winner per pot; the winner of a pot also wins each later pot it is eligible for) and every seat's prize change in each are computed once at build, with identical final-stack vectors priced once.
- **Pricing.** A seat eligible for pots 1..j wins exactly pots t..j when it holds the best hand among pot t's seats but not pot t−1's, so its own result comes from the same side-pot shares the chip game uses and is exact under the game's showdown model. Who wins the pots it loses is weighted by the other seats' range-against-range chances, which ignore the seat's own hand (an approximation that only matters with three or more live seats): each seat's chance of the best hand among a set is the product of its heads-up chances against the others, normalized. Ties count as fractional wins. The value is linear in the seat's per-pot win chances b[t]: V[j] + Σ b[t] (V[t] − V[t+1]), where V[t] is its average prize change when it first wins pot t.
- **Flop leaves.** Terminals with chips behind are a pot lottery: the continuation model's share b of the pot is the chance of winning the whole pot, otherwise the seat loses what it put in. On its own that prices the risk on the preflop pot but not on the chips still behind, so ICM would push hands from jams into cheap-looking flats. `icm.stack_off` (k, default 0.4; 0 turns it off) adds the stacks behind: the pot ends all-in with chance k / (k + SPR), SPR being the second largest stack behind over the pot. In that branch every live seat adds up to that stack, and a seat wins every pot it is eligible for with chance (b · pot + its added chips) / (the pots it is eligible for), which keeps its chip EV exactly b · pot − invested. The stack-off therefore changes prize equity only, never chip EV (winner-take-all payouts still reproduce chip EV), and the value stays linear in b, so the GPU blends it in `pf_icm_prepare` the same way. The Preflop Lab panel's Stack-off rate sets k. The default came from a sweep of k against the canonical Range Lab final table and bubble charts at 20bb: 0 left the BB folding almost never to a button open under ICM; 0.3 to 0.5 matched the charts' extra BB folds (0.5 at the final table, 0.3 on the bubble); 1 and above over-penalized flats (BB folds 55 to 63%, jams 25 to 39%) and converged slower. Low-SPR pots stack off more often, so non-all-in 3-bets from the blinds mostly turn into jams.
- **GPU.** Because the value is linear in the per-pot win chances, the chip-EV terminal kernels price ICM unchanged once the money is swapped: before each traverser's terminal pass, `pf_icm_prepare` (`gpu/icm.cu`) computes V[t] for every terminal from the other seats' reach and overwrites that traverser's pot amounts with V[t] − V[t+1] and its investment with −V[j] (fold wins pay −investment). Every multiway model, the 3-way table and side pots carry over. ICM games always take the normal GPU plan; the shared-CDF throughput variants decline them.
- **CPU cost.** The range-against-range chances cost a 169×169 product per pair of other live seats at every multiway terminal, so CPU iterations run slower than chip EV: about 2.4 times on an 8-handed 25bb tree (83 s against 35 s per iteration on four cores). Use the GPU for full tables.
- **Preflop Lab.** The Tournament payouts panel takes payouts (first place first), the number of players at other tables and their average stack, or a stage preset (final table, two tables, 10% left, bubble, half the field) that fills an approximate standard 1,000-player structure (15% paid, prizes falling as 1/place, min cash 1.5 buy-ins). After a build it shows what 1 bb is worth as a share of the prize pool and each seat's prize equity.
- **Limits.** ICM games need `rake_pct = 0`. ICM makes the game general-sum even heads-up (other players gain from a bust), so there is no Nash guarantee; best-response gaps still measure how far a solve is from one. Saves use `GTOPREFLOP6`, so older binaries refuse them rather than continue the arenas as a chip-EV game.

### Postflop ICM

Heads-up and 3-way postflop spots take the same payouts: `TreeConfig.icm` / `MwTreeConfig.icm` (and `icm` in `/api/spot` and `/api/mw/spot`) is `{"payouts": [50, 30, 20], "behind": [8, 21], "others": [15, 12, 30], "field_groups": [{"stack": 20, "count": 5}]}`. `others` and `field_groups` are every player still in who is not in the hand (folded players at the table and players at other tables). `behind` is heads-up only: each player's chips behind at the root, at least the effective stack; the deeper player's extra chips are never at risk but count for ICM (default: the effective stack for both). 3-way spots take each stack from `stacks`. A Preflop Lab flop export from an ICM game fills all of it in, and SETUP and the 3-WAY tab have a Tournament payouts panel.

- **Payoffs.** Every terminal pays each player the change in its Malmuth–Harville prize equity in bb equivalents, measured from the root with the pot split evenly between the players in the hand (a constant per player, so strategies do not depend on the split). Final stacks are exact: a fold or showdown settles the pot (side pots in 3-way) and adds it to what each player had behind. Winner-take-all payouts reproduce chip EV exactly. The game is general-sum, so exploitability compares each player's best response with its actual value, as with rake.
- **Heads-up.** Each player gets its own win, lose and tie value per terminal (`icm::postflop::HuIcmPayoffs`); the CPU evaluators and the GPU kernels read the traverser's values instead of the shared chip amounts.
- **3-way.** The evaluator writes each terminal as a 3×3 table over how each opponent's hand compares with the traverser's, which fixes every player's chips but, under ICM, not every player's prize: when both opponents beat the traverser (or both lose to it while contesting a side pot it is not in), and when the traverser has folded and the other two show down, the prize also depends on which opponent wins. `multiway::icm` stores the table for one order and corrections for the other order and for a tie; `eval::order_masses` computes the exact reach of opponent hand pairs in each order (pairs above the traverser's hand, below it, or anywhere when it has folded) by inclusion-exclusion over the four cards of the hands involved, with strength-sorted running sums, and `mw_icm_order` (multiway/kernels.cu) does the same on the GPU after each showdown level. Tests check both against brute-force three-hand ICM.
- **Saves** of ICM spots use `GTOSOLVE3` and `GTOMW2`, so older binaries refuse them rather than continue them as chip-EV games.
- **Limits.** Postflop ICM needs rake 0. The 3-way order kernel runs after every showdown level and does more work per hand than the showdown itself, so 3-way ICM iterations run slower than chip EV.

## Performance

The coupled-deck seven-seat validation game (1,003,570 nodes, 200 bb, RTX
3090) used approximately **13.1 GB VRAM**. A 500-iteration continuation
averaged **4.68 seconds per iteration** (39 minutes in iteration work, plus
accuracy checks and saves). This is substantially more computation than the
legacy product model. GPU scratch batches shrink to fit memory; CPU uses the
same model but large multiway trees are much slower. See the
[validation evidence](../research/multiway-equity-audit/README.md).

Historical performance baseline: **7 September 2026**, Windows, RTX 3090 24 GB,
Ryzen 5950X, 64 GB RAM, 16 solver threads. These are fixed workloads, not a
promise for every tree or machine. These preflop timings predate the coupled-deck model and should not be used as its performance estimate. The comparison below is the GPU
research pass versus fresh controls of the code at the start of that pass.

| Workload | Before | Current | Improvement |
|---|---:|---:|---:|
| Six-seat preflop, same accuracy target | 3.549 s | 2.317 s | 34.7% less time |
| Eight-seat preflop, same accuracy target | 8.926 s | 5.323 s | 40.4% less time |
| Rainbow flop, 0.3%-pot target | 12.067 s | 11.107 s | 8.0% less time |
| Two-tone flop, 0.3%-pot target | 7.219 s | 6.667 s | 7.6% less time |
| Six-seat preflop GPU allocation | 671 MB | 503 MB | 25.0% less |
| Eight-seat preflop GPU allocation | 1,711 MB | 1,309 MB | 23.5% less |
| Two-tone compressed postflop GPU allocation | 4,933 MB | 3,624 MB | 26.5% less |
| Rainbow compressed postflop GPU allocation | 6,241 MB | 5,906 MB | 5.4% less |
| Warm compressed two-tone full readback | 1,531 ms | 297 ms | 80.6% less time |

Target timings exclude tree construction and initial GPU upload. Preflop
still stops at 175/125 iterations, and the two flop cases at 200/200, with
identical checked states and final values. No precision, model, bet menu,
or accuracy target changed. MB are decimal; device allocations are measured,
while the UI shows estimates and a live memory budget.

The [current GPU report](../research/autoresearch/gpu-pass.md) contains all
comparisons, limitations, and 696 source/numerical audit checks. The
[progress image](../research/autoresearch/gpu-pass-progress.png) renders on GitHub;
the [interactive tracker](../research/autoresearch/index.html) can be opened
locally and includes 130 metric graphs, controls, and rejected trials.

The [first research pass](../research/autoresearch/report.md) additionally covers
CPU solving, profiles, reports, and loading: the measured six-seat CPU
iteration fell from 197.02 to 72.92 ms, report-line summaries from 199.18 to
77.63 ms, and warm f32 save loading from 47.49 to 37.20 ms. These earlier
comparisons have their own baselines; percentages across passes must not be added.
[Preflop](preflop_performance.md) and [postflop](postflop_performance.md)
notes summarize the latest results and preserve the earlier measurements.

RAM budgets cover solver arenas plus tree storage; actual process memory also
includes caches, staging, driver allocations, and other overhead. Compressed
CPU arenas use half the per-entry storage of f32, but do not halve total RAM
or GPU VRAM. The server refuses over-budget CPU trees. GPU packing and scratch
reuse reduce device allocation by different amounts on different trees.

## CLI

```bash
./target/release/solve-cli spot.json [max_iterations] [target_exploit_pct] [--save out.gto]
./target/release/solve-cli resume base.gto [iteration_delta] [target_exploit_pct] [--save next.gto]
./target/release/solve-cli batch spot.json boards.txt [max_iterations] [target]
```

`spot.json` matches the `SpotConfig` JSON schema (see `bench_spot.json`).
Env: `SOLVER_STORAGE=f32|i16` (default i16), `SOLVER_ALGO=dcfr|cfr+|pcfr+`
(default dcfr), `SOLVER_ISO=0`, `SOLVER_THREADS=N`, `SOLVER_GPU=1`
(gpu-feature builds). Storage and threads apply to every mode; the algorithm
and isomorphism switch apply to a fresh solve and to batch, realization and
datagen, while `resume` keeps the values the save recorded. Batch rows report
range-average root EVs weighted by reach × valid (the app's convention, so
`ev_oop + ev_ip = pot`).

**Saves and resume.** `--save` writes a `GTOSOLVE2` save after the run (an ICM
tree writes `GTOSOLVE3`, which older binaries refuse rather than continue as a
chip-EV game). The header records the spot config, the iteration count, any
locks and labels, and the algorithm and isomorphism switch; the four arenas
are full-precision f32 on disk whatever the in-RAM storage. `save`
materializes the isomorphic sibling branches first, so the file is
self-contained and reads correctly with isomorphism either on or off.
`resume` reloads a save and continues it: its iteration positional is a
**delta added to** the save's own count (default 300; zero is rejected). This
extends a saved solve, or a locked variant the app saved, without re-solving it
from iteration 0. Saves written before the header carried
`algo`/`use_isomorphism` resume as dcfr with isomorphism on;
`SOLVER_ALGO`/`SOLVER_ISO` override the recorded values only when explicitly
set, and warn when they do. PCFR+ prediction arenas are not part of a save,
so resuming PCFR+ is a **warm start**, not an exact continuation. The CLI warns
about this: restarting predictions can change the trajectory beyond the first
resumed iteration. DCFR and CFR+ retain their continuation state; keep the same
storage and engine settings when comparing an uninterrupted run. The server
checks the PCFR+ prediction-arena RAM budget even when the solve request keeps
the algorithm inherited from a save.

**Batch mode** solves the same ranges/tree across many boards (file with one
board per line, or an inline `b1,b2,..` list), prints one row per board
(iterations, exploitability, reach-weighted root EVs) and writes
`batch_results.json` — the raw material for multi-flop aggregate analysis.
Batch duration depends on each board, ranges, bet menu, target, and any
CPU fallback; the current single-board measurements above are not a full-set ETA. `SOLVER_BATCH_SAVE=1` also
writes `saves/batch_<board>.gto` per board.

**Datagen mode** (`solve-cli datagen run|job|inputs|spot|verify|block`)
produces the pooled value-net training data: seeded random heads-up flop
spots on the lean `lean-v2` menu, sized to the GPU (`--max-vram`), solved to
0.5% pot, written as JSONL job files with per-class values.
Datagen solves on the GPU by default in gpu-feature builds (`SOLVER_GPU=0`
forces the CPU). See [Contribute compute](contribute-compute.md); the
sampling and file format live in `crates/solver/src/datagen.rs`.

## API

Everything the UI does is plain JSON over HTTP — scriptable:

`POST /api/spot`, `POST /api/solve`, `POST /api/stop`, `GET /api/status`,
`POST /api/node {path}`, `POST /api/exploit {path, exploiter}` (per-hand best
response + EV gain vs the current strategy), `POST /api/lock {path, mode}`,
`POST /api/unlock`, `GET /api/locks`, `GET /api/locks/history`,
`POST /api/locks/undo`, `POST /api/locks/redo`, `POST /api/runouts {path}`,
`POST /api/range/parse`, `POST /api/save|load {name}`, `GET /api/saves`,
`GET /api/presets`.

Preflop lab: `POST /api/preflop/spot {config}`, `POST /api/preflop/solve`,
`POST /api/preflop/stop`, `GET /api/preflop/status`,
`POST /api/preflop/node {path}` (path = action indices),
`POST /api/preflop/export {path}` (heads-up flop node → postflop spot inputs),
`POST /api/preflop/save|load {name}` + `GET /api/preflop/saves` (whole-session
snapshots: config, seat models, point locks, full solver state — loading
resumes mid-convergence).

**Lock history.** `/api/lock` (with optional `"lock_path": true`), `/api/unlock`
and `/api/profile_locks` (POST and DELETE) each record one undoable edit and
return the updated history as `history: {undo, redo, profile_players,
locked_nodes}`, labels most recent first. `lock_path` also freezes (locks as
solved) every unlocked earlier decision on the path in the same edit and
reports how many as `frozen`. Undo restores the exact earlier lock strategies
rather than rebuilding them from the current solve. History is per session,
is not saved, and keeps at most 100 edits or 256 MB of lock data; an edit that
fails is rolled back.

Path steps: `{"type":"action","index":0}` / `{"type":"card","card":"Ah"}`.
Browse deep links: `/#line=a1,a1,cQh` opens BROWSE at that node (`a<i>` =
action index, `c<card>` = dealt card).
