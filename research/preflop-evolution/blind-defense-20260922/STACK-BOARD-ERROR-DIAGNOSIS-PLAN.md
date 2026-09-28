# Diagnose remaining board errors without another training run

After independent verification of the fixed training-budget trial, inspect its
two long-budget selections using only their original 32 validation boards and
a fixed random subset of 32 out of the 512 fitting boards (seed 9296800).
Use only fitting depths 20/40/100/200/400. No final-test board, excluded-depth
label, new board, training update or new model selection enters this diagnosis.
This is exploratory evidence for the next design, not fresh confirmation.

Reconstruct original validation means before interpreting the decomposition.
For every context, retain the original mixed-policy loss and compare it with
choosing the largest predicted legal value, and with an exact zero fold value.
Measure fold/call prediction error and implied equity error. Decompose by board,
seat, price, made-hand category and the relationship of the private hand to the
board: plays the board exactly; improves kickers within the same category;
improves the category. Board category is evaluated from five public cards only.
These descriptive labels are not added to model inputs in this diagnosis.

Use fixed weighted rows (all 1081 legal private holdings on each selected board),
report counts and normalized losses, and preserve all adverse groups. Sparse
groups cannot justify population claims. Compare fitting-subset and validation
errors to distinguish memorization from a general inability to learn the target.

Bound this GPU/CPU analysis to 1800 seconds, 32 MB new evidence plus 32 MB reserve,
4 GB research CUDA, 2 GB external VRAM headroom, 28 GB available RAM at admission
and 24 GB during execution, 40 GB free S: storage and 800 GB global allocated
research storage. Respect production and heavier work; share with light desktop
activity as authorized. Reuse the qualified faster storage inventory and retain
source/input hashes. There is no deployment, new GitHub push or deletion.

If correct value-to-action conversion barely changes the losses, do not pursue
cosmetic range mixing. Use the error distribution to decide whether better
board-relative features, separation of known cashflow from learned card value,
or additional coverage is the appropriate next controlled experiment. Passing
this diagnostic is not a preflop quality gate; the full goal remains trustworthy
ranges across positions, stacks, sizes, rake and multiple players.
