# Proposed next comparison: board coverage and relative hand inputs

Status: proposal only, 29 September 2026. Not a registration, not launched.
The completed relative-input comparison and its final boards remain immutable.
The latest monitoring instruction explicitly prohibits another scientific
experiment. Execution requires that restriction to be lifted by the user.

## Decision this would resolve

Can more deliberate coverage of board structures make the relative-input model
reliably accurate on fresh boards, rather than merely improving its average?
The last comparison improved the final-test means in both seeds but failed the
absolute accuracy gate. Its validation means favored the baseline. This makes
coverage and selection stability worth testing; it does not establish their
causal role. Repeating longer training is not the proposed treatment.

This differs from the earlier BB starting-hand-class sampler. Each retained
river board already has all 1,081 legal hero holdings. The missing variation is
across boards and how those holdings relate to them, not empty starting classes.

## Proposed fixed comparison

Use a two-by-two design with two fresh random seeds, eight fits in total:

| Training boards | Original 362 inputs | Relative 387 inputs |
| --- | --- | --- |
| 512 existing fit boards plus 512 fresh random boards | Two seeds | Two seeds |
| Same 512 existing boards plus 512 fresh structured boards | Two seeds | Two seeds |

Both training sets contain exactly 1,024 boards. The structured draw balances
feasible cells of board rank multiplicity and maximum suit count, using only
visible cards. Keep all legal hero holdings on every board. Enumerate and check
the feasible cells and deterministic allocation before freezing a registration;
do not choose cells by consulting this experiment's labels or errors.

The structured arm intentionally changes the training distribution. It must not
be presented as an unbiased physical-deal sampler or plugged into the full-game
trainer without its own weighting analysis. Ordinary poker-distribution test
boards remain the primary evaluation. Report the cost of the changed curriculum
on every slice, including any losses in common situations.

Preserve the 64/64 networks, targets, optimizer, 8,192 updates, batch size 4,096,
checkpoints and original action conversion. No architecture or optimizer search.
Match initialization and context draws within each seed. For the two input widths
on the same board set, retain exact initial-output and common-example pairing.
Across different board sets, identify the intentionally different examples;
do not claim identical training data.

## Selection, independent tests and decision rule

- Use 128 fresh random validation boards, shared by all arms. Select the minimum
  stack-normalized validation loss, with the original earliest-checkpoint tie
  rule. Increasing validation coverage is common to all arms, not an extra
  candidate advantage.
- Freeze all eight selected model identities before producing final-test labels.
- Test on 128 fresh random boards as the primary population and 64 independently
  structured boards as a separately reported stress test. Never average the
  stress test into the primary result as if it had natural board frequencies.
- Exclude every previously used final/probe group from new fitting and selection.
  Keep the two new fit extensions, validation, primary test and stress test
  mutually disjoint under suit equivalence. Reuse only the named original 512
  fitting boards. Derive and hash the exclusion union from retained manifests.
- Fit at 20/40/100/200/400bb; keep 60/150bb out of fitting and selection. These
  depths are previously studied geometries, not globally unseen stack settings.
- Primary treatment comparison: structured versus random training boards with
  387 inputs. Require at least 20% reduction in the equally weighted 60/150bb
  normalized mean in BOTH seeds, and mean loss at most 0.001 starting stacks at
  EACH of those depths. The 362-input arms diagnose the interaction; they cannot
  be substituted after the test to manufacture a successful primary outcome.
- Retain per-board, depth, actor, price, hand-group and tail results, including
  unsupported cells. Show validation/test disagreements and both seeds. Treat
  the engineering gate as a finite-test criterion, not a population guarantee.
- Independently reconstruct selected predictions, cash losses, gate outcomes,
  board separation and file identities on CPU. Extend verification to reported
  subgroup means and tail quantiles, which the last readback did not recompute.

No final-test tuning, checkpoint reselection, extra updates or silent retry.
Preserve interrupted and unfavorable outcomes. Two seeds still provide limited
evidence; even a pass would support a subsequent reference comparison, not deploy
a strategy or prove whole-game accuracy.

## Resource and implementation boundary

Planning estimate: about 35-60 minutes of scientific work and verification once
resources are available, extrapolated from the completed four-fit comparison.
This is not a measured runtime for the proposed design. Cap the main attempt at
60 minutes and independent CPU verification at 30 minutes; preserve a timeout.

Keep research CUDA at 4GB with 2GB external headroom. A 1,024-board 387-column
float32 feature cache is about 1.71GB before validation, public features, other
arrays and allocator overhead; verify the complete estimate before admission.
Use at most eight hidden CPU preparation workers, single-threaded BLAS per
worker, and four CPU verification workers. Retain the existing RAM, CPU, disk
headroom and 800GB global allocated-storage guards. Proposed new evidence cap:
512MB plus 128MB reserve, with no historical deletion. Share with light desktop
use and yield to active production solves and heavy workloads.

Before any launch, qualify deterministic board selection, allocation, exclusion,
checkpoint identities and original-column parity; then freeze exact source
hashes, seeds, order, board lists, gates and resource limits in a new registration.
Do not alter the completed comparison or reuse its expired admission helper.

Production56708, GitHub and the paused heartbeat remain unchanged. No new
experiment is authorized by this document. The broader goal still requires
realistic action-conditioned opponent ranges, multiple decisions, all legal
betting actions and independent end-to-end preflop evaluation.
