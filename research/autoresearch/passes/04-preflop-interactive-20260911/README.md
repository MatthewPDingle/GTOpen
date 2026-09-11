# Preflop interactive performance experiment

Four-hour research window: **10 September 2026 23:03:27 UTC to 11 September 03:03:27 UTC**. Research completed; exact early publication is deployed on port 56708. No compressed approximation is qualified for default use.

The target is time to a useful preflop strategy and exported postflop spot. This pass allows explicitly versioned evaluator approximations, measured separately from implementation-only speedups. It does not train player-behavior ranges or restore the old product-of-heads-up-equities shortcut.

## Current evidence

**Earlier availability is demonstrated;10x faster qualified time to accuracy is not.** No compressed model is approved for default use.

- **Exact early publication:** paired API-c export took12.266s instead of299.078s, a24.38x availability improvement. Final Reference native bytes, gaps and EVs match exactly. This exposes an unconverged iteration2 strategy; the paired50-iteration runs both stop at their iteration limit, not the accuracy target. [API evidence](proposals/early-preview/API-QUALIFICATION.md).
- **32 and64 particles:** both fail independent overlap-equity guards.64 reaches the large global policy tolerance after1000 iterations, but physical and local failures remain. Faster fixed work or4s API export does not qualify those policies. [Rejection evidence](proposals/quality-gates/RESULTS-32-AND-AA-SUPPLEMENT.md).
- **128 particles:** reserved physical checks pass. Large50 fails global policy gates;1000 passes, and adaptive500 also passes in396.53s through native audit (global audit separate). Its own/full gaps still exceed0.005 and large local tails are unmeasured. The small constrained100 failure improves to a global pass at adaptive500 with identical first100 native state, but its local[1] failure and absolute-gap miss remain. [Physical results](proposals/quality-gates/RESULTS-HERDING128.md), [native results](proposals/quality-gates/RESULTS-LARGE128.md), [adaptive follow-up](proposals/quality-gates/ADAPTIVE128-FOLLOWUP-RESULTS.md).
- **Selected-branch refinement:** full-payoff refinement improves five of six tested conditional gaps and keeps the better baseline in the sixth. Three-case runs take4.8–4.9s including load/audits and exact restoration. Arriving-range quality and original-continuation local failures remain unvalidated. [Conditional results](proposals/quality-gates/RESULTS-NATIVE128-AND-CONDITIONAL.md).
- **Large warm starts:** both scale0.01 experiments fail after100 fresh full iterations: gaps0.42837 and0.51659, taking780.45s and772.06s, excluding source creation. All native audits pass, but neither achieves the accuracy/excess-gap gate. Larger scales are unrun on this fixture. [Warm-start results](proposals/continuation-ensemble/WARMSTART-LARGE-RESULTS.md).

The production build passed 232 tests with zero failures, paired API/native-parity and stop/resume checks, and a 1280px browser review. Final-binary export was available in 12.469 seconds versus 305.641 seconds (24.512x earlier), with identical final native strategy bytes. Total case duration was 338.344 versus 333.781 seconds: this improves availability, not convergence speed. The qualified build is deployed on port 56708 with both native sessions restored exactly: preflop iteration 102 and postflop iteration 210, board Kd6s5c. Code integration `5c978d6` is pushed to GitHub. [Production qualification](PRODUCTION-QUALIFICATION-REPORT.md).

ResearchH's37 frozen test executables passed272 tests with26 existing ignores. Their original wrong-working-directory missing-fit failures and corrected repeat remain recorded. Later publication/lifecycle changes have separate checks. API-a's regenerated1024-sample cache remains distinct from corrected API-b/c's20000 cache; API-d's runner-assumption failure is also retained, followed by API-e's successful pause/save/reload checks. [H checks](H-CHECKS.md), [cache resolution](proposals/early-preview/BENCH-API-DISCREPANCY.md).

Private research browser smoke passed navigation/export/provenance checks and identified a1280px layout issue corrected in the curated source. Final production browser qualification is separate. Both adaptive128 fixed500 groups completed with the limitations above; neither changes earlier thresholds or failures. [Follow-up protocol](proposals/quality-gates/HERDING128-ADAPTIVE-FOLLOWUP.md).

See [final results](FINAL-RESULTS.md), [registered gates](proposals/quality-gates/README.md), and [research contract](program.md). Raw logs and frozen protocols are in `raw/`; large native checkpoints remain in the isolated lab's ignored `target/research-preview/` directory.

## Isolation

Experiments use a separate worktree and owned private processes. The guard polls the user's server on56708 and stops the research child if a solve/report starts. No experimental model has been deployed to that server during this pass.

Candidate names identify different payoffs. A saved preview solve must never be relabeled or resumed as a full-reference solve. Policy comparisons copy average strategies into a fresh evaluation workspace; they do not reuse approximate regrets as reference learning state.
