# Test explicit hand strength relative to the visible board

Prospective controlled experiment; not yet run. This follows the completed
training-budget comparison and must not begin until its CPU error decomposition
has reproduced both selected models' original validation means. Longer training
was not a reliable fix. The decomposition examines whether familiar absolute
hand categories obscure what the player's cards actually add to the board.

## The single model change

Preserve the original 362 inputs and append 25 deterministic features computed
only from the player's two cards and the five visible river cards:

- Board-only best-five category (9 indicators) and padded tiebreak ranks (5).
- The player's relation to that board: plays it exactly, improves only the
  tiebreak within the same category, or improves the category (3 indicators).
- Five normalized tiebreak differences when the category is unchanged; otherwise
  zero. Preserve the original cards and full made-hand rank as well.
- Minimum private cards required for the player's best rank: zero, one or two
  (3 indicators). Determine this from the board alone and each board-plus-one-card
  rank compared with the full seven-card rank; no opponent cards are inspected.

These are redundant visible-card facts, not equity estimates or opponent-range
features. Do not enumerate opponent hands, read showdown labels, use future cards,
consult GTO Wizard or import a learned target into the inputs. Exactly 25 new
features make the candidate width387. Padding ranks uses zero for absence and
(rank+1)/13 for present ranks, as in the existing summaries.

Qualify the feature implementation before training: independent five-card
subset rank oracle on deterministic retained qualification boards and holdings,
direct-vs-canonical agreement, hole/flop permutations, all suit permutations on
fixed probes, and invalid/future/duplicate-card rejection. Existing probe boards
stay excluded from fitting and all later fresh tests. Check exact initial output
parity when the new columns are zero-weighted. Preserve failed attempts.

## Paired learning experiment

Use the same512 fitting boards and fitting depths20/40/100/200/400bb. Keep the
64/64 two-player networks, target, optimizer, batch4096,8192 updates and original
positive-score action conversion. Fresh seeds9296901/9296902; width362 versus387
from matching baseline weights. Initialize the extra first-layer columns to zero;
the candidate has3200 extra first-layer parameters across both player networks
(1600 each), so this is an input-feature
comparison rather than an exactly equal parameter-count test. Preserve paired
initial outputs and batch draws.

Fresh board seed9296900 selects32 validation and64 final-test board groups,
excluding all692 previously selected groups (596 before the budget test plus96
from that test). Freeze membership and candidate order before running. Select
among steps0/1024/4096/8192 using only the context-balanced normalized validation
regret, tie earlier step. Freeze all four model identities before generating
fresh final-test labels. Neither old final boards nor the error-diagnosis boards
become new training data.

Final evaluation uses the96-split plan's64 test boards at the five fitting depths
and60/150bb. Those latter geometries have been studied before, so report only
their exclusion from fitting/selection, not globally unseen stacks. Require at
least20% primary mean reduction in both seeds and mean regret at most0.001 of
starting stack at each excluded depth. Retain tails, seat/price/category slices
and unfavorable results. Independently replay selected predictions and gates.
Do not extend, retune or change thresholds after seeing the final test.

This deliberately leaves the fitting-board coverage fixed to isolate the feature
change. The random fitting/validation corpus has weak coverage of rare board-made
hands; a separate stratified-coverage study may be needed regardless of this
outcome. A pass would authorize a subsequent multi-decision reference comparison
with a capable independently checked responder, not production deployment or a
claim of full preflop accuracy. Eventually the method must handle betting-induced
opponent ranges, other positions, stack sizes, rake, sizes and multiple players.

## Resource boundaries

Maximum whole invocation3600 seconds,256MB new evidence plus128MB reserve;
research CUDA4GB and2GB external headroom, RAM28GB admission/24GB during,
Sfree40GB and global allocated research storage800GB. Use bounded hidden CPU
preparation workers and the qualified fast inventory. Reuse original fitting
board/count files; store only extra feature arrays and new validation/test inputs.
Production/heavy workloads take priority. Prepare/control CPU work while the GPU
is busy; do not start GPU training until its normal admission check passes.
No deployment, new GitHub push, historical deletion or in-place source mutation.
