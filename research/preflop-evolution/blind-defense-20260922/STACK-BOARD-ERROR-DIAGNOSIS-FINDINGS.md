# Remaining errors are mainly generalization of ordinary hand values

The CPU-only error decomposition completed and reproduced the original selected
GPU validation means within3.97e-7bb, below the unchanged1e-4bb tolerance. It used
the two long-budget selections,32 existing validation boards and a fixed random
subset of32 fitting boards, at fitting depths only. No final-test labels, new
boards, additional training or new model selection were used.

| Seed | Fitting-subset mean loss / stack | Validation mean loss / stack | Ratio |
| --- | ---: | ---: | ---: |
| 9296701 | 0.02749% | 0.17809% | 6.48x |
| 9296702 | 0.01389% | 0.24214% | 17.43x |

These descriptive comparisons support poor generalization to unfamiliar boards.
The fitting subset is not the entire training corpus and the validation set has
already selected checkpoints; these are exploratory findings, not an independent
population accuracy test. The completed training-budget final-test failure is
unchanged.

## Changing action conversion barely helps

Choosing the largest predicted legal value instead of positive-score mixing
reduces validation regret by0.269%/0.014% in the two seeds. Setting the fold value
to its exact zero before choosing an action reduces it by0.285%/0.013%.
This rules out action conversion as the main immediate repair under these data.
It does not justify adding cosmetic mixed frequencies to the model.

## Hand strength relative to the board is a useful next hypothesis

| Validation group | Share of evaluated rows | Seed1 share of total loss | Seed2 share of total loss |
| --- | ---: | ---: | ---: |
| Same category as board, better kickers | 37.06% | 63.03% | 53.78% |
| Improves the board's category | 60.40% | 31.50% | 44.37% |
| Plays the board exactly | 2.54% | 5.47% | 1.84% |

High-card and one-pair full hands account for81.27%/85.30% of validation losses,
on66.12% of the rows. Losses are not confined to rare made monsters. The existing
network already receives full hand rank and individual card identities; the
proposed change supplies explicit redundant board-only ranks and what the hole
cards add to them. The grouping is suggestive, not proof that this change works.

Separately, a metadata audit found training-board counts247 high-card,215 pair,
32 two-pair,14 trips,1 straight,2 full-house and1 quads among512; no board-only
flush or straight flush. The32 validation boards have22 high-card,8 pair,1 trips
and1 two-pair. A later stratified-coverage study should address that gap; it is
not a demonstrated explanation for losses in this validation set.

## Cost, evidence and next action

The analysis took344.969 seconds including accounting and used no GPU allocation.
Four BLAS threads were configured, with bounded CPU/RAM checks to respect other
applications. Retained new study evidence is0.85MB logical/0.32MB allocated.
GPU diagnostic v1 never started because heavier GPU work took priority; its
waiting helper was stopped before admission. The separate v2 CPU implementation
and amendment preserve that history.

Evidence: stack-board-error-diagnosis-v2-registration.json,
stack-board-error-diagnosis-v2-result.json and
stack-board-error-diagnosis-v2-analysis.json. The aggregation independently
checks that each partition's row shares and loss contributions sum to the whole.
Executed sources and all inputs remain hashed and unchanged.

Proceed with STACK-BOARD-RELATIVE-FEATURES-PLAN.md: qualify25 visible-only
features, then compare the original362-input network against387 inputs using
matched initial models, identical fitting boards/budgets and fresh validation
and final-test boards. First qualify feature correctness and initial-output
parity. Train only when the normal GPU resource checks admit it. No production
deployment or full preflop accuracy claim follows from these diagnostics.
