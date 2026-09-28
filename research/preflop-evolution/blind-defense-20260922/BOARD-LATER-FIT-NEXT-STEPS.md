# Next steps after the later-play fitting diagnostic

The completed 512 / 2,048 / 8,192-step comparison does not support longer fits.
Across four datasets, mean postflop training error fell 25.34% at 8,192 steps,
while validation error rose 9.32%. This is consistent with overfitting.

The subsequent training-row readback checked the same streets on both sides:

| Street | Training error reduction at 8,192 | Validation error increase at 8,192 |
|---|---:|---:|
| Flop | 11.70% | 10.16% |
| Turn | 22.98% | 11.03% |
| River | 30.71% | 8.54% |

Every player/run/street had lower training error and higher validation error at
both longer budgets. Thus this is not explained merely by averaging different
streets in the original chart. Direct raw-row training losses reproduce grouped
loss plus within-input variance within 7.31e-8. See
`board-later-fit-training-phases-v1-result.json`.

## Immediate bounded follow-up

`board_later_fit_early_budget_v1.py` compares 64, 128, 256 and 512 steps on the
same four datasets and original validation partition. It reuses the qualified
fitter, architecture, initialization, normalization and source weights. The
512-step model and its validation loss must reproduce the earlier baseline
within 1e-7. It scores no final-test rows. This is further tuning on reused
validation data, not independent confirmation of a model improvement.

Choose one common budget by equal-dataset mean postflop validation loss. Preserve
all results, including failures. More data or a different representation remain
necessary candidates if shorter fitting does not help. No output from this
diagnostic replaces the production model.

## A concrete representation hypothesis

The current network receives 269 lossless visible-card/history inputs plus 33
card-strength/texture summaries. Suit symmetry is already handled in the native
observation representation; do not propose suit relabeling as an unimplemented
fix. The network still has to infer pot, remaining stack and call price from
the public branch and action history within one fixed game context.

Explicit public betting-state inputs are a plausible next experiment, not a
proven fix. The native `research_sampled/observation_v1.rs` already reconstructs
the public `State` from context, public branch and action tokens in
`Observation::legal_actions`. `research_sampled/state.rs` exposes committed
amounts, actor and street. A new exporter could derive pot, remaining stacks,
amount to call and call price using this same public state, with no opponent
cards, future cards or evaluation outcomes. Preserve the existing lossless
inputs. Any new implementation must be checked against native legal actions and
cash-flow values, including different stacks and postflop branches.

Keep target rescaling separate from an input-feature experiment. A positive
constant rescaling of all action scores at one information set leaves regret
matching unchanged, but learning targets, fitting weights, fallback behavior
and changing game contexts require explicit tests before using that property.

## Requirement before adopting a promising candidate

Better validation loss alone is insufficient. Run a separately registered full
training comparison, evaluate complete resulting policies on fresh deals, and
check range consistency, value and runtime. The current spot remains a restricted
200bb BB-versus-BTN subtree with inherited incoming ranges. Other stacks,
positions and multiway play remain outside this evidence.
