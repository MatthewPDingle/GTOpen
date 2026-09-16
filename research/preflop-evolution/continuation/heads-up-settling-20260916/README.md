# N27: heads-up settling with exact legal-pair chance

The N24 multiway control suggests that the large residual gap is associated
with learned values, rather than legal-pair accounting alone. Test whether it
also occurs when the whole preflop game starts heads-up, where the research
interface has an exact compatible-card prior and no heads-up-entry reset.

Two prespecified fresh fixtures: 40bb and 100bb, SB0.5/BB1, zero rake and ante,
limps allowed, 2.5bb opening, 3x re-raises, maximum three raises, all-in enabled.
Use the unchanged N20 double kernel, frozen N15 weights and research executable.
Compare ordinary Balanced, paired-card Balanced and paired-card learned values.
Alternate ordinary/paired/learned order at500, reversed order for500->1500.
Warm-up zero. Record gaps, EVs, selected strategy views and every snapshot hash.

This is a diagnostic, not a new model or a performance benchmark. The ordinary
path has different chance accounting. The paired Balanced path is a fixed
approximate continuation game; the learned path freezes range-conditioned
values for its gap calculation. Neither solves full postflop poker. Exact
heads-up chance does not make the learned frozen-value gap a full-game
exploitability certificate. No claim that more mixing is more accurate.

Report all six arms at both checkpoints, without threshold selection or
choosing a favorable stack. A persistent excess learned gap would show that
the effect can arise without the multiway reset; a smaller gap would instead
motivate investigating interaction with the larger game. Either outcome remains
limited to these fixtures. Use .005bb as the previously used diagnostic gap
reference, not as a fresh qualification or convergence theorem.

Freeze protocol, helpers, fixture definitions, source saves, caches, kernel,
model and executables before GPU execution. The new seed example only creates
fresh small save files offline and refuses an existing output directory.
Run after N21 releases the GPU, with at least20minutes before20:49:02UTC.
No live-server calls or changes to existing binaries, kernels or production.
