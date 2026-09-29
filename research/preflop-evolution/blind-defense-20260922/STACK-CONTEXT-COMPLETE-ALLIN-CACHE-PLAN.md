# Complete the exact all-in inputs before cross-stack training

This prepares candidate-independent exact equity counts. It is not a new learning
comparison, does not fit/select models and changes no preflop action menus.

The reviewed old cache covers 47,478 suit-canonical private matchups for the old
BB/BTN incoming ranges (169 BB classes, 96 BTN classes). The new stack geometry
fixtures have all 169 classes in both incoming ranges. Their complete universe
contains 1,624,350 ordered compatible physical hand pairs, or 93,769 canonical
keys. The old cache cannot be silently applied to this wider population.

Reversing the roles in reviewed exact counts adds 23,722 keys: exchange wins and
losses, preserve ties, and canonicalize suits without losing role identity.
Every overlap must agree exactly. The remaining 22,569 keys form reversal pairs;
enumerate only one representative from each pair and reconstruct its reverse.
The count of native representatives is fixed in registration before enumeration.

Use the already qualified hu_allin_board_reference.exe, enumerating all
1,712,304 boards per selected private matchup. Retain native inputs/outputs and
check integer totals plus two boards with the independent Python scorer. Run
at most 12 single-thread native processes at below-normal priority, using the
5950X while leaving room for desktop work. No CUDA allocation is required by this
enumerator. Do not introduce a new GPU evaluator into this data qualification.

Pause new batch admissions during active production solves or heavy external CPU
work; let short admitted batches finish. Preserve the research lock, 24 GB free
RAM and 40 GB free disk floors. Cap new files at 1 GB, total allocated research
storage at 800 GB and the invocation at two hours. No batch retry or failed-file
deletion. A started failed attempt retains its evidence.

After completion, the separately defined readback verifies source identities,
full physical coverage by disjoint canonical suit-orbit sizes, reviewed-cache
reuse, role reversal, every saved native batch and independent sample-board
scores. This is not a second exhaustive board enumeration or strategy validation.
Require that readback before using the extended cache for stack-specific matrices.

Those matrices must still use each context's actual incoming range probabilities,
pot, contributions and rake. Equity-count reuse does not permit copying or
relabeling the old context's probability/payoff matrix. Preserve production 56708
and all failed scientific results. No training, deployment or GitHub push here.
