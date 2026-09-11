# Bounded development warm-start results

Source: isolated lab `target/research-preview/warmstart-development64-a/run.json`, executed by parent. This is a70-node, three-seat development fixture with four CPU threads, not an independent holdout or large-game speed test. Full-reference500 has learning gap0.0000015212bb/hand. The source64-particle500 policy already passes the global gates but has excess full-reference learning gap0.00169328bb/hand and mean/max unilateral positive loss0.00048054/0.00078044bb/hand.

The registered initializer transfers source average probabilities as fresh positive regrets scaled by0.01,0.1 or1.0. Learning averages start at zero, target iteration starts at0, and subsequent learning uses full1024 payoffs. Approximate regrets, average accumulator mass and iteration counters are not resumed or relabeled. All nine recorded target native roundtrips are exact. This all-solver fixture has no forced or frozen nodes, so its results do not independently test those constraints.

## Measured quality improvement, with a remaining failure

All nine scale/checkpoint combinations pass the global policy gates against the same full-reference500. With scale0.01 and50 full iterations, excess learning gap falls to0.0000128762bb/hand and unilateral mean/max loss to0.0000007456/0.0000010422. This is a measured improvement in the fixed full model, not proof of physical-deal or postflop accuracy.

The table lists maximum probability on a strongly inferior action among meaningful hands at each selected path; the unchanged limit is10%. Root BTN passes in every run.

| Initial regret scale | Full iterations | SB after limp [1] | SB after raise [2] | BB after raise/call [2,1] |
|---:|---:|---:|---:|---:|
|0.01|50|88.4195% fail|0.3089% pass|0.1697% pass|
|0.01|100|88.4195% fail|0.0392% pass|0.0215% pass|
|0.01|500|88.4195% fail|0.000317% pass|0.000174% pass|
|0.1|50|48.6392% fail|36.7335% fail|18.3483% fail|
|0.1|100|48.6392% fail|4.9202% pass|2.3278% pass|
|0.1|500|48.6392% fail|0.0398% pass|0.0188% pass|
|1.0|50|47.6916% fail|97.3325% fail|80.2088% fail|
|1.0|100|47.6916% fail|84.9526% fail|68.8484% fail|
|1.0|500|47.6916% fail|15.5299% fail|6.3858% pass|

Scale0.01 repairs the selected raise-response tails quickly. It does **not** produce an all-local-gates pass: SB[1] fails at every scale and checkpoint. Its reference-path independent joint reach is only1.43306e-8, compared with0.00531269 for[2] and0.00319294 for[2,1]. This explains why a small global gap can coexist with poor conditional choices; it does not exempt the branch. The full reference itself has weighted conditional action loss0.0562581bb there, while scale0.01 is worse at0.2374974bb. No subgame-optimality claim is justified from these root-weighted solves.

## Timing and scope

At scale0.01,50 full iterations consumed0.12626s of learning and0.15972s elapsed including quality/save work;100 consumed0.22966s learning/0.31603s elapsed, and500 consumed1.08016s/1.22225s. These figures exclude constructing the500-iteration preview seed and cannot establish an end-to-end speedup. Other scales have similar bounded timings. Selecting0.01 because it performs best here is development selection and requires separate holdout validation before generalization.

The evidence supports a follow-up hypothesis: a cheap policy can initialize fresh full-payoff learning and improve some reached decisions. It does not yet establish10x faster usable solving, a robust rare-node policy, or safe default deployment. The independent overlap failure of the frozen64 payoff model remains recorded; full-payoff refinement does not retrospectively convert that terminal model into a physical-validation pass.

## Later large64 source-policy qualification

`raw/preview64-eight-1000-a.log` and `raw/quality-large64-1000-a.log` now provide a separate1,567,754-node, eight-seat test. This is the **preview source policy**, not a completed large warm-start/refinement test. The fresh64-particle run uses the20000-sample pairwise cache, stops at the fixed1000-iteration limit, and has own-model learning gap0.0051307185bb/hand; it has not reached its0.005 own-model target. Its native roundtrip is exact.

Frozen-policy evaluation under full1024 payoffs gives learning gap0.0068750129bb/hand. The separately available full reference at iteration1024 has gap0.0047837546, so excess gap is0.0020912583, below the unchanged0.02 gate. Across all eight unilateral replacements, mean positive EV loss is0.0003419911 and maximum is0.0011929683bb/hand (BB), below0.01 and0.03 respectively. The reference is below0.005, and both recorded global gate flags pass. These calculations use fresh full-payoff evaluation workspaces with no learning or input mutation.

This makes the source policy a **candidate initializer that passes the tested global gates**. It does not qualify all local decisions, eliminate the frozen64 terminal model's failed overlap guard, or establish safe default approximate solving. Large local strong-action tails, physical accuracy and the refinement outcome remain separate and unverified by this run.

Recorded solver time is461.6539s and total harness time470.5585s; the independent global-quality audit took96.2467s. Do not present the audit cost as part of a normal production solve unless that audit is actually required there, or omit it from the research cost. There is no matched fresh full1000-iteration timing in this comparison: the full reference was resumed under a different timing history. No whole-solver speedup ratio or10x quality-qualified claim can be derived from this pair.

Input provenance is pinned in `large-1000-inputs-a.json`: candidate SHA256 `263c608c23f856d0c45efde4f5659dcff98d8b9312a827a18b887fc64574d705`; reference `4bc33937a5a8602fb204c8f2b211294f72f34f0859c989e3071cf014abbb5bab`. The candidate remains natively `coupled_preview64_v1`; the full reference remains `coupled_deck_v1`. No raw records or source code were changed for this result note.

## Conditional local experiments: two different quality questions

`raw/conditional-small-development-a.json` and `raw/conditional-large-full-a.json` evaluate the registered development paths by normalizing their fixed arriving ranges and solving the descendant game under full payoffs. The local conditional gap measures the updated policies playing against each other. The original source-continuation action-loss metric instead chooses one updated action and then follows the **old source continuation**. They answer different questions and neither should be substituted for the other.

Small path[1] improves its conditional learning gap from0.274175 to0.000005376bb in100 local iterations (0.3239s method compute). However, its maximum strongly inferior-action probability **under the original continuation** rises from47.04% to99.98%, even while its weighted old-continuation loss falls from0.05626 to0.00791bb. The old continuation is weak in this rare branch; jointly changing future responses changes which current action is best. This explains the disagreement without waiving the original local gate: that original metric still fails. Paths[2] and[2,1] have final conditional gaps0.000002105 and0.000000964bb. All three restore source arenas and outside/forced/frozen regions exactly, and write no source native save.

For the large source, all three100-iteration conditional results are below0.005:

| Selected BB path | Original conditional gap | Recomputed conditional gap | Compute seconds | Old-continuation bad-action mass, before / after |
|---|---:|---:|---:|---:|
|BTN raises6, SB folds|0.0002749|0.0009287|0.2683|0.1577% /7.8606%|
|BTN raises10, SB folds|0.0751654|0.0039543|0.2596|78.4678% /98.3181%|
|CO raises6, BTN calls, SB folds|0.7164131|0.0017932|0.5969|90.8411% /99.9999%|

The first baseline was already better than the reset/refined result. A production design should compare the measured baseline and candidate and retain the better acceptable baseline instead of replacing it automatically; the present experiment merely measures this choice and does not implement it. The other two conditional gaps improve substantially, but their old-continuation tail gates still fail, so these results establish conditional-game convergence rather than a global original-policy certificate.

Total large harness time is4.4295s, including1.2191s input load and backup/restoration/audit overhead. Individual compute figures are under one second; that is not the complete user-visible latency. All three source-restoration and outside-arena checks are exact. These all-solver development cases do not independently validate modeled/frozen/adaptive transitions, and no improved local policy was merged into the parent game. Conditional refinement remains a promising separate quality scope requiring explicit UI evidence, holdout validation and retention of the original gate results.
