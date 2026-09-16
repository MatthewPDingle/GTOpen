# N15: reduce the nonlinear correction by one quarter

This proposal explicitly follows inspection of N06's **training-family**
scores. It is model selection using known training results, not an independent
discovery. No prospective evaluation outcomes select its settings.

N06's eight-unit, penalty-0.1 model improved mean error 6.77%, but its worst
family worsened 5.0442%, narrowly failing the unchanged 5% limit. Test one
conservative revision: retain the exact same fitted base and network, and
multiply only the learned nonlinear correction by 0.75. This shrinks its
changes toward the original predictor. Do not change the gate, round the
failure away, refit against a held-out family or search further blend weights.

Use the original 26 contexts, four whole-family folds, width eight, penalty
0.1, the same two seeds, CPU float64 and 500 steps. Reproduce both the N06
unshrunk and ordinary control errors case by case before accepting the new
screen. Require >=5% lower equal-family mean error and <=5% worsening in
every family. If eligible, fit all 26 and freeze scaled output weights.

Before any new outcomes exist, separately register on all 400 unused
expanded-validation queries (50 disjoint flops across eight historical
held-out contexts). Require >=15% lower mean error than Balanced in each
family and no case >10% worse than the original conditional model. Report
uncertainty and reference quality. No reuse of the N09 evaluation outcomes
for selecting or fitting this model.

The two-seed ensemble retains 16 hidden units. Shrinking does not make it
cheaper to run. A successful accuracy result still needs its own GPU
implementation, arithmetic oracle, matched timing (<=10% overhead target),
and changed-policy validation. No deployment is authorized by these tests.
Respect the existing fixed deadline and keep port 56708 unchanged.
