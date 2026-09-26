# Preparing the matched showdown-model comparison

Training and independent readback remain in progress. No new accuracy result or production deployment is implied here.

The new read-only bank loader (`tools/research/compact_showdown_bank_v1.py`) binds the experiment registration, independent readback registration and result, every audited completion marker and metric, the ordered played models, and the final recovery checkpoint. Baseline version-7 models use their existing validated version-6 inference representation. Corrected version-8 models retain their separate type and coefficient identity. No corrected model is relabelled as a baseline model.

For evaluation, the loader requires all four registered 78-update arms to finish, the selected arm's complete independent audit, and matching final experiment/arm results. It includes played generations 0–77 with the pre-existing weights 1–78 and excludes the unplayed generation 78. An explicitly labelled implementation control can use an audited recovery prefix; that identity is not evaluation-qualified.

## Verified so far

`compact-showdown-bank-control-v1-result.json` records a CPU-only test using the real, independently audited eight-update baseline prefix. Its average over 265 initial observations matched a separately constructed weighted average of the saved policies actually played before those eight updates. Maximum probability difference: 2.22e-16. Own-action reach was exactly 36 for every initial observation, matching the sum of weights 1–8.

The control rejected partial training submitted for evaluation, an unknown purpose, an unknown arm, and a boolean update count. It took 33.31 seconds, used no GPU, and did not modify the production app or training evidence.

This qualifies the tested prefix admission and initial-policy averaging only. It does not qualify full-arm admission, corrected-arm admission, GPU inference for the full new banks, postflop averaging, or poker strength.

## Remaining comparison work

1. Finish the four fixed training arms and independently read back every update in each arm. Preserve failures and partial runs rather than selecting a favorable prefix.
2. Exercise the loader against the complete baseline and corrected banks; verify CPU/GPU inference on reused native history queries before drawing evaluation deals. Existing two-generation corrected CPU/GPU checks are useful prerequisites, not substitutes for this full-bank check.
3. Register the fresh crossed-policy payoff evaluation, fixed sampling budget, stopping rule, and retained evidence before sampling. Use original game payoffs, not variance-corrected learning targets. Report both seeds and all eight paired comparisons with simultaneous uncertainty intervals.
4. Admit evaluation storage against the actual remaining allocation. The previous evaluation's roughly 6.5 GB evidence layout cannot simply be reused under the current ceiling. Qualify a smaller lossless representation or a fully reproducible, independently checked retention protocol before launching it. Do not compress or delete legacy evidence without authorization.
5. Compare root stability across independent training seeds alongside payoff evidence. Lower training-target variance alone does not prove better ranges, faster convergence, or a generally accurate preflop model.

Scope remains the restricted BB-versus-BTN 200 bb research game. A successful result here would support the next research step; broader positions, stack depths, trees, and multiway play still need separate validation.
