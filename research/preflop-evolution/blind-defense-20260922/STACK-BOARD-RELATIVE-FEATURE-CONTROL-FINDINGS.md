# Visible board-relative features pass exact mathematical checks

The25 appended features matched an independent five-card-subset calculation
exactly for12,972 legal private holdings across12 retained qualification boards.
The control performed285,384 independent five-card evaluations and27,648 suit,
hole-order and flop-order variants. All direct/canonical comparisons matched,
and all8 malformed or incomplete input cases were rejected. Maximum feature
error was exactly0.

The minimum-private-card feature is checked independently by enumerating every
best five-card subset and counting the private cards it contains. Production
feature code instead compares the board-only, board-plus-one and full ranks.
No opponent hands, equity labels, unseen cards or GTO Wizard data enter features.
Qualification boards remain excluded from future fitting and fresh tests.

The CPU-only control used four owned hidden workers and completed in41.578s
including the storage inventory. No worker descendants remain active. Retained
evidence is16,980 bytes across17 files. GPU use, training and production changes
were all absent.

This qualifies feature mathematics and invariance only. It has not established
improved model predictions or better preflop ranges. The next required work is
the paired362/387-input model implementation, initial-output parity control,
extended feature preparation and the separately registered learning experiment
defined in STACK-BOARD-RELATIVE-FEATURES-PLAN.md. Do not skip initial-output and
checkpoint controls merely because this feature test passes.

Evidence: stack-board-relative-feature-control-v1-registration.json and
stack-board-relative-feature-control-v1-result.json. Registration SHA256:
631ee2aa0b2ded13b98305b0e29a9174331913e7bc015b4e847a4db23bb01d7e.
Executed sources and all inputs remain immutable.
