# Combined direct-preflop and conditional-all-in experiment

The prior direct-preflop experiment increased calling but also increased jams.
The dense conditional-all-in experiment reduced jams from 7.28% to 1.80%,
without materially improving calling. Neither qualifies for deployment.
The missing combination tests both changes together, in the same BB-versus-BTN
200 bb physical-card game. It does not update the UTG/LJ preview or production.

## Fixed experiment

- Reuse the original 78 updates of 512 deals, sampler/action/reservoir seeds,
  262,144-record capacity, 512 fitting steps, network sizes and optimizer.
- Use direct regret matching on retained preflop information-set mean regrets;
  unsupported preflop rows fall back to the network. Postflop remains neural.
- Use independently reviewed exact private-pair all-in counts, integrating all
  1,712,304 possible boards only at preflop all-in terminals. Other terminal
  values remain sampled. Labels never enter policy features.
- Keep the explicit format-3 native transport and format-2 hybrid checkpoint.
  The checkpoint config identifies the terminal estimator and cache hash.
- Evaluate the complete equally weighted played bank (generations 0 through 77)
  with own-history reach weighting; exclude unused generation 78. No last-only
  policy, inspected-hand patch, or result-driven stopping rule.

First run four complete updates through the actual new worker in a separate
control namespace. Replay every dealt card, action seed, reservoir insertion,
checkpoint and direct table. Check every covered preflop policy row against its
retained mean, including nonuniform rows for both players. Native traversal
checks must verify both query lookup and independent cashflow paths. Neural
fitting is the previously controlled unchanged fitter; the replay does not claim
to rerun gradient descent or independently recalculate every network output.
The four-update control is never an accuracy candidate. The full trial starts
from scratch and is admitted only after the control's terminal audit passes.

## Evaluation fixed before training

Use fresh response-training/test seeds 89101/89102, respectively 8,192 and
16,384 deals. Keep the original sampled-board evaluator for the primary test,
so this experiment isolates the training change. The five BB alternatives are
the separately trained first-action response and each of fold/call/raise/jam.
The three BTN alternatives versus BB jam are the separately trained response,
always fold and always call. Each family uses alpha .025. Reuse the established
minimum 16 response-training observations per hand; insufficient classes retain
the original strategy. Freeze response choices before opening the test stream.

Use checked float64 inference of stored weights, with table overrides before
own-history reach weighting. Verify CPU/CUDA agreement before fresh evaluation.
Both players' full-bank evaluations and independent artifact audits are required.
Future exact-all-in evaluation would be a separately registered variance-reduction
study, not a replacement chosen after seeing these results. No new test deals
are drawn by the training or four-update control scripts.

## Resources and interpretation

Stop for production activity, failed integrity, three-hour execution cap, or
falling below 20 GB host RAM / 3 GB VRAM / 40 GB free SSD. Limit the trial store
to 40 GB. Preserve failed evidence; do not automatically retry or extend.

Success is not defined as resembling Wizard or producing more calls. Examine
independent profitable deviations, hand allocation and uncertainty, with both
players changing strategy. No paired significance claim across different test
streams. This restricted two-player game cannot establish general preflop
accuracy, and no result automatically authorizes deployment.
