# Next experiment: optimization budget on broad board coverage

Status: prospective design, not yet implemented or executed. The completed
24-versus512-board study remains unchanged. Its broad-coverage validation curves
were still improving at the final8192-update checkpoint, while its fresh test
missed the absolute accuracy gate. Test a larger fixed learning budget rather
than extend a completed trial or change multiple ingredients at once.

Reuse ONLY the512 fitting boards from stack-board-coverage-v1. No preceding
validation or test boards become fitting data. Keep their exact factors/counts,
fitting depths20/40/100/200/400 and the362-input64/64 model unchanged.

Before execution freeze a fresh board seed and two fresh initialization/batch
seeds. Select32 new validation and64 new final-test board groups, excluding all
earlier probe/learning/coverage groups. These sample counts are fixed; use the
existing grouped physical-hand weighting and exact uniform-opponent labels.

For each seed, fit one32768-update chain from the usual fresh initialization.
The short-budget baseline may select only checkpoints at0/1024/4096/8192.
The long-budget candidate may additionally select16384/32768. The shared prefix
makes the comparison paired without duplicating its work. Use unchanged Adam
0.001, batch4096 and policy conversion. No architecture, loss, learning-rate,
feature or reference changes. Both budgets select minimum context-balanced
normalized validation regret, tie earlier step.

Freeze all four selected identities before preparing final-test labels. Evaluate
them once on fresh final boards at fitting depths and60/150bb. Those two depths
are excluded from fitting/selection but their geometry is already familiar from
earlier studies. Report that limitation. Primary gate remains>=20% improvement
in both seeds and<=0.001 starting stacks at each excluded depth. Preserve all
requested tails and adverse slices; small average errors do not hide large
individual mistakes. No extension or redefinition after viewing the result.

Proposed execution cap3600s including admission/preparation/two chains/final
tests; new evidence256MB plus128MB reserve; research CUDA4GB plus2GB external
headroom, RAM28GB admission/24GB during, Sfree40GB, global allocation800GB.
Use eight hidden preparation workers and GPU row assembly; prioritize active
production/heavy work while sharing with light desktop use. Independently replay
the frozen result on CPU before interpreting it. No deployment or new push.

Implementation must create a new fitter/runner rather than editing executed
versions. Record precise seeds and checkpoint rules in a machine registration
before fitting. Qualification already established for unchanged data features
and native prices need not be redone wholesale. Old models are not production
checkpoints. A pass is permission to advance the scientific reference, not to
claim full preflop or multiway accuracy.
