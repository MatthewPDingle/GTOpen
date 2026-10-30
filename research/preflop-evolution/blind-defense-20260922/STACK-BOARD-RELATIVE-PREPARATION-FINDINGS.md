# Relative-hand experiment: implemented and prepared, accuracy not yet measured

The candidate now supplies 25 additional visible facts about how the private
cards improve the board. This is a controlled representation comparison, not a
production model or evidence of better preflop ranges yet.

## What passed

The CPU model control checked 960 retained probe rows for each of two seeds.
Both model widths produce exactly the same initial scores and share the same
original parameters. The extra inputs receive nonzero gradients, checkpoint
round trips are exact, and changed hashes or incorrect dimensions are rejected.
The control took 42.359 seconds including storage accounting and retained
184,673 allocated bytes. It used synthetic gradient probes, not policy training.

The independent NumPy evaluator was separately qualified against PyTorch CPU
inference on 5,760 rows, including synthetic nonzero extension weights for both
players. Its maximum score difference was 3.73e-8, below the prospectively fixed
1e-6 control tolerance. Six action-conversion edge cases passed and two nonfinite
cases were rejected. This control did not initialize CUDA or inspect new labels.
The final CPU/GPU context-mean replay tolerance remains 1e-4bb.

CPU preparation completed in 56.047 seconds, of which 41.593 seconds were storage
accounting and 10.562 seconds were the eight-worker preparation. It prepared 512
fitting-board extensions and 32 new validation boards. All workers and their
descendants exited. New allocated storage is 1,677,796 bytes. Original feature
prefixes, legal holdings, opponent counts, public padding and actors were checked.
No GPU training or final-test label generation has occurred at this checkpoint.

## Frozen comparison

- Original 362 inputs versus 387 inputs; hidden layers remain 64/64.
- Two paired seeds, identical initial predictions and sampling; 8,192 updates
  per model. The candidate adds 3,200 weights across its two player networks.
- Same 512 fitting boards; 32 fresh validation and 64 fresh final-test board
  groups exclude all 692 earlier groups.
- Fit at 20/40/100/200/400bb. Depths 60/150bb are excluded from fitting and
  selection, but are not globally unseen geometry.
- Freeze all four validation-selected identities before generating test labels.
- Both seeds must reduce normalized mean decision loss by at least 20%, while
  each excluded depth must have mean loss at most 0.1% of starting stack.
- Retain tails and seat/price/hand-category slices even if the mean improves.

The original first-layer matrix operation is retained, with a separate 25-column
term initialized to zero. This preserves exact initial computation. It is not a
speed optimization; both model costs will be reported separately.

## Current execution boundary

An initial GPU admission check deferred because external GPU utilization was
100%. The bounded admission helper can wait up to four hours, checking every
30 seconds. It starts a hidden owned child only after the existing production,
CPU, RAM, storage and GPU checks pass. The child rechecks admission and all
registered hashes. An already started scientific attempt is never retried by
the helper. A completed result still requires the independent CPU readback.

The scientific work cap remains 3,600 seconds including the completed CPU
preparation. Waiting before admission is separate. CUDA is capped at 4 GB with
2 GB external headroom; heavy foreground work and production solves take
priority. New evidence is capped at 256 MB plus 128 MB reserve under the global
800 GB allocated research budget.

All tests remain terminal river fold/call against uniform legal opponent hands.
Even a successful result must be tested in richer, range-conditioned sequential
decisions before it supports any claim about complete preflop ranges.

Evidence: stack-board-relative-model-control-v1-result.json,
stack-board-relative-readback-control-v1-result.json and
stack-board-relative-learning-v1-prepared.json, each linked to its immutable
registration and hashed inputs. Follow the live admission and learning status
files for state after this preparation checkpoint.
