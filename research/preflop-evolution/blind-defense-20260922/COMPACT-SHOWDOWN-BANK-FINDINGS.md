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

## Prepared complete-arm CPU control

`tools/research/compact_showdown_full_bank_control_20260926.py ARM` checks one
completed, independently audited 78-update arm without waiting for the other
arms to finish. It uses the archive-aware version-2 loader, requires the final
arm result, checks played generations 0–77 and weights 1–78, then compares its
initial-policy average against the separately saved policies actually played
before all 78 updates. Own-action reach must equal 3,081 at all 265 initial
observations. Baseline and corrected banks retain their appropriate CPU readers.

The `--check-ready ARM` mode is read-only. While the first arm was at update 71,
it correctly reported the missing final arm and full-audit results. Invoking
the full control also refused before creating a registration or result.

## First complete baseline arm: verified

The seed-9266201 baseline completed all 78 updates (39,936 training deals) and
verified restoration of its final checkpoint. Training took 12,209.44 seconds
(3 hours 23 minutes). The second, corrected arm then started automatically.

`showdown-training-readback-v2-9266201-baseline-0078-result.json` records the
independent CPU audit of all 39,936 roots, 906,637 postflop learning targets,
and all 78 retention markers. It reconstructed the chance/action streams,
root and exact-response state, and checkpointed reservoirs. Maximum root-state
error was 4.55e-12, target error 5.68e-14, and policy error 5.94e-12, within
the pre-existing tolerances. The audit's 10,590.69 seconds includes waiting
for training, so it is not a standalone audit-throughput measurement.

`compact-showdown-full-bank-9266201-baseline-v1-result.json` then passed the
complete-bank CPU control in 64.95 seconds. All 78 played generations (0–77)
were included with weights 1–78; generation 78 was excluded as unplayed.
Across all 265 initial observations, the resulting average matched the
separately saved played-policy average to 5.55e-16. Own-action reach was
exactly 3,081 throughout. The source registration hash is
`e846c5bf8c5c964b51c9f5dcf1b70e8d6c920069632cfe0adf2d84b7cbdfe18d`.

This qualifies complete baseline admission and initial-policy averaging for
this seed. The other three arms, full-bank GPU/later-action checks, and fresh
payoff evaluation remain pending. No poker-strength improvement or production
change follows from these implementation checks.

## First complete corrected arm: verified

The seed-9266201 corrected arm also completed all 78 updates (39,936 training
deals), with its final checkpoint restored and verified. Training took
12,887.20 seconds (3 hours 35 minutes). The seed-9266301 baseline then began
automatically under the unchanged four-arm registration.

`showdown-training-readback-v2-9266201-corrected-0078-result.json` passed the
independent reconstruction of 39,936 roots and 906,566 postflop learning
targets. Maximum root-state error was 3.18e-12, target error 5.68e-14, and
policy error 1.07e-12. Its 14,387.58-second duration includes waiting for
training; it is not a standalone throughput measurement.

The queued `compact-showdown-full-bank-9266201-corrected-v1-result.json`
passed in 59.47 seconds. All 78 played generations were included, with
weights 1–78 and the unplayed generation 78 excluded. Across all 265 initial
observations, the CPU average agreed with the separately saved played-policy
average to 5.55e-16; own-action reach was exactly 3,081. Its registration
hash is `f86c09c9b5d654b2297352cf5ec29005f2a36c90fc9c0dce1942bde4494744bc`.
Result bindings and all registered source inputs were checked after completion.

The first matched pair now has complete training, independent readback, and
CPU initial-policy averaging checks. Both second-seed arms, full-bank
GPU/later-action checks, and the fresh payoff comparison remain necessary.
These results verify implementation consistency, not better poker ranges.

## Second-seed baseline: verified

The seed-9266301 baseline completed all 78 updates (39,936 training deals),
verified its final checkpoint restore, and took 14,140.30 seconds (3 hours
56 minutes). The final corrected arm then began automatically.

`showdown-training-readback-v2-9266301-baseline-0078-result.json` passed the
independent audit of 39,936 roots and 903,099 postflop learning targets.
Maximum root-state error was 2.73e-12, target error 5.68e-14, and policy
error 8.89e-13. The 18,055.33-second audit duration includes waiting for the
worker. Its result hash is
`f8d6a2800e0aa0c5433e9f8a10933a70ec3522988cbaa22bf37640933d0ad508`.

The queued complete-bank CPU control passed in 65.66 seconds. Its average
over all 78 played generations matched the independently saved played-policy
average within 7.77e-16 at all 265 initial observations; own-action reach
was exactly 3,081. Generation 78 remained excluded as unplayed. Registration
hash: `e7c9e28c5b393fc4e89bd87533f71163a1d7da21625f2d6dadb09b148a83053b`.
The audit's 932 registered inputs and bank control's 87 inputs were rechecked
after completion, and their result-to-registration bindings matched.

Three arms now have complete training, independent readback, and CPU
initial-policy averaging checks. The final corrected arm, full-bank GPU and
later-action checks, and the fresh payoff comparison remain necessary.
