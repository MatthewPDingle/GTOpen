# Preflop interactive performance experiment

Four-hour research window: **10 September 2026 23:03:27 UTC to 11 September 03:03:27 UTC**. In progress; no approximation is qualified for default use yet.

The target is time to a useful preflop strategy and exported postflop spot. This pass allows explicitly versioned evaluator approximations, measured separately from implementation-only speedups. It does not train player-behavior ranges or restore the old product-of-heads-up-equities shortcut.

## Current evidence

**Earlier availability is demonstrated;10x faster qualified time to accuracy is not.** No compressed model is approved for default use.

- **Exact early publication:** paired API-c export took12.266s instead of299.078s, a24.38x availability improvement. Final Reference native bytes, gaps and EVs match exactly. This exposes an unconverged iteration2 strategy; the paired50-iteration runs both stop at their iteration limit, not the accuracy target. [API evidence](proposals/early-preview/API-QUALIFICATION.md).
- **32 and64 particles:** both fail independent overlap-equity guards.64 reaches the large global policy tolerance after1000 iterations, but physical and local failures remain. Faster fixed work or4s API export does not qualify those policies. [Rejection evidence](proposals/quality-gates/RESULTS-32-AND-AA-SUPPLEMENT.md).
- **128 particles:** reserved physical checks pass. Large50 fails global policy gates; large1000 passes them in734.92s total. Its own/full gaps still exceed0.005, large local tails are unmeasured, and small constrained/local failures persist. [Physical results](proposals/quality-gates/RESULTS-HERDING128.md), [native results](proposals/quality-gates/RESULTS-LARGE128.md).
- **Selected-branch refinement:** full-payoff refinement improves five of six tested conditional gaps and keeps the better baseline in the sixth. Three-case runs take4.8–4.9s including load/audits and exact restoration. Arriving-range quality and original-continuation local failures remain unvalidated. [Conditional results](proposals/quality-gates/RESULTS-NATIVE128-AND-CONDITIONAL.md).
- **Large warm starts:** both scale0.01 experiments fail after100 fresh full iterations: gaps0.42837 and0.51659, taking780.45s and772.06s, excluding source creation. All native audits pass, but neither achieves the accuracy/excess-gap gate. Larger scales are unrun on this fixture. [Warm-start results](proposals/continuation-ensemble/WARMSTART-LARGE-RESULTS.md).

The curated production candidate contains exact Reference publication and lifecycle improvements, not compressed models or research warm starts. Its Rust qualification finished without errors; the dedicated qualification report owns final counts. Production API/UI checks and session-preserving deployment are still pending. The active production API run is not treated as completed evidence. [Integration checklist](proposals/early-preview/PRODUCTION-INTEGRATION-CHECKLIST.md).

ResearchH's37 frozen test executables passed272 tests with26 existing ignores. Their original wrong-working-directory missing-fit failures and corrected repeat remain recorded. Later publication/lifecycle changes have separate checks. API-a's regenerated1024-sample cache remains distinct from corrected API-b/c's20000 cache; API-d's runner-assumption failure is also retained, followed by API-e's successful pause/save/reload checks. [H checks](H-CHECKS.md), [cache resolution](proposals/early-preview/BENCH-API-DISCREPANCY.md).

Private research browser smoke passed navigation/export/provenance checks and identified a1280px layout issue corrected in the curated source. Final production browser qualification is separate. The adaptive128 fixed500 follow-ups are prepared but unrun in evidence reviewed; they cannot change earlier thresholds or failures. [Follow-up protocol](proposals/quality-gates/HERDING128-ADAPTIVE-FOLLOWUP.md).

See [the draft final results and pending checklist](FINAL-RESULTS.md), [registered gates](proposals/quality-gates/README.md), and [research contract](program.md). Raw logs and frozen protocols are in `raw/`; large native checkpoints remain in the isolated lab's ignored `target/research-preview/` directory.

## Isolation

Experiments use a separate worktree and owned private processes. The guard polls the user's server on56708 and stops the research child if a solve/report starts. No experimental model has been deployed to that server during this pass.

Candidate names identify different payoffs. A saved preview solve must never be relabeled or resumed as a full-reference solve. Policy comparisons copy average strategies into a fresh evaluation workspace; they do not reuse approximate regrets as reference learning state.
