# Research-only shallow integration and policy feedback

Production :56708 stays unchanged. No production API, UI, configuration, solver
default or binary is changed. Select the shallow kernel explicitly in the offline
research driver; the baseline remains the frozen N15/N20 kernel. No refitting.

The frozen 18-coefficient correction is used unchanged from SPR .2 to .75. Below
.2, its .2 residual scales linearly to zero, preserving the all-in limit. From
.75 to 1, a smoothstep convex blend connects its .75 prediction to the existing
N15 prediction at SPR 1. At and above 1 the previous N15 path is unchanged.
The interpolation outside the measured band is a research assumption, not new
accuracy evidence. The extension is enabled only for two-player games.

Qualification before solving: Python/native CPU/CUDA probe error <1e-9 in pot
fractions, conservation error <1e-9, continuity at .2/.75/1 under +/-1e-7 SPR
perturbations (<1e-5 share difference), and whole-tree action-value agreement
within 2e-5bb. Saved strategies must not change during evaluation. Exact zero
stack, folds, unsupported inputs and disabled research mode preserve the old path.

Re-solve the same 40bb heads-up SB/BB fixture from a fresh game for both baseline
and shallow arms, checkpoints 500/1500/3000. Check gaps, conservation, strategy
movement and run time. A frozen-range gap is not true game exploitability when
continuation values depend on ranges. Do not equate a small gap with stability.
Movement diagnostic: at the root and BB versus open, compare 1500 to 3000;
0.5 percentage point maximum aggregate-action movement and 1% mean hand total
variation are the provisional stability limits. Report failures rather than
silently extending the solve until they pass.

Export the shallow arm's 3000-step tree. Generate 50 independently selected
stratified boards for each of the three original BB continuation contexts
(call, called 3-bet, called 4-bet). This is a fresh full-population random panel;
incidental overlap with earlier boards is allowed. The resulting ranges and
reference labels are excluded from fitting. Both GPU and materialized CPU gaps
must be <=0.1% pot, with 2000 iterations maximum. Preserve failures.

Compare native shallow, previous N15, and Balanced values on exactly the same new
ranges. Repeat call/fold and call/3-bet screens with 5000 paired, stratified
bootstrap samples. Original action support >=.0001 and per-action propagated BR
gain <=.025bb remain the reliability gates. Report qualified mass and sparse
classes. Primary feedback screen: the shallow 4-bet value MAE must improve >=10%
over the old fallback with >=95% qualified pair mass; direct MAE must not regress
>5%. At the action level the new model should not worsen either direct or
equity-adjusted MAE over N15 on the same qualified hands. No deployment from this
single fixture, even if it passes. Remaining small-ace bias is reported, not fixed
with hand-specific overrides.

Performance diagnostic: three alternating-order pairs of fresh 1000-step runs
after 100 warmup steps, on this same 40-node fixture. Compare median learning
time, separating compilation/setup; >10% slowdown is a concern to report, not a
reason to modify this frozen candidate. It does not establish large-tree speed.
The new 50-board panel uses seed `shallow-native-feedback-v1` (10 per stratum),
with bootstrap seed 2026091704. Freeze implementation before preflop solves and
freeze the generated ranges/evaluator before any new reference labels.
