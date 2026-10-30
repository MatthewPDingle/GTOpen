# Prospective test of later-weighted output averaging

Design prepared 23 September 2026 after the generation-attribution audit.
**Not yet registered or launched.** Freeze runnable source, controls, all seed
values and the final evaluation contract before starting training.

## Hypothesis and intervention

Early policies dominate two independently verified all-in errors. Test whether
a fixed output-weighting rule reduces these errors on a fresh training run.
Use the visible 302-input architecture and unchanged training method. Do not
reweight advantage targets, reservoir sampling, or regret tables in this test.

Train one new bank from scratch for exactly 78 updates of 512 deals, using fresh
training, action, reservoir and fitting seeds distinct from previous studies.
Evaluate two complete banks built from those same played generations 0–77:

- Equal: each generation receives weight 1.
- Later-weighted: generation g receives weight g+1, giving weights 1–78.

Both players use the same declared schedule, with normal own-action-reach
weighting at later decisions. Keep every played generation; exclude the unused
next generation 78. No latest-only selection, tail cutoff, exponent search,
intermediate quality stopping, or post-result adjustment.

The same training trajectory isolates output averaging from changes in training
data or network fitting. It does not test a different learning algorithm.
There is only one seed replication; a positive result would justify replication,
not a general claim of robustness.

## Evaluation stages

1. Independently reconstruct both averages, including histories with nontrivial
   own reach. Verify CPU/CUDA agreement and preserve all 169 root distributions.
2. Use the existing complete equity cache to evaluate the same exact BB
   restricted fold/shove and BTN fold/call endpoints. Recompute values for
   all four BB-average/BTN-average pairings. Do not reuse original-candidate
   values against the new opponents. Report both gains separately, all pairings,
   and all classes. This avoids hiding an opponent change inside a comparison.
3. Require both exact endpoint gains for the jointly later-weighted pair to be
   at least 25% below the jointly equal pair before scheduling a larger test.
   This is a prospective practical screening threshold, not a full-game accuracy
   bound. If either fails, report the result and do not launch the costly
   follow-up automatically. Cross-pairings remain descriptive diagnostics.
4. If it passes, separately register the improved non-all-in evaluation using
   exact fold/shove components plus sampled call/raise continuations, materially
   better class coverage, and independent test deals. Do not qualify or deploy
   from the narrow endpoint screen.

All-in endpoint calculations exhaust the finite incoming private-card support
and boards; no test-deal sampling interval applies to those exact calculations.
They remain conditional on the fixed game, incoming ranges, action menu and
model implementation. They do not test general positions or stack depths.

## Controls and resources before launch

- Confirm the output schedule is applied to policy reach, not to regret targets.
- Check a synthetic history where simple per-node averaging gives the wrong
  result, using independently calculated weighted realization probabilities.
- Complete a short fresh-run checkpoint/reload and training-replay control.
- Set training ceiling to four hours, informed by the prior run's 186.8 minutes
  of training rather than its exceeded three-hour limit. Stop at 78 updates or
  the cap, whichever comes first; incomplete runs are not quality results.
- Retain resource guards: 20 GB host RAM, 3 GB VRAM, 40 GB SSD free, no concurrent
  production solve or report generation. Preserve resumable completed checkpoints.
- Keep production port 56708 and the range preview unchanged.

## Research basis and limits

[Brown and Sandholm, 2019](https://ojs.aaai.org/index.php/AAAI/article/view/4007)
study both regret discounting and output-strategy reweighting. That literature
motivates this test, but its results are not a guarantee for this sampled neural
implementation or this raked game. The proposed change only affects the output
average and must not be described as a complete Linear CFR/DCFR implementation.
