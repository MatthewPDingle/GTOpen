# Conditional plans now reach the native action-value calculation

The separately planned prediction diagnostic can now join the verified history,
opponent-hand posterior and future-board sampler to the existing native payoff
code. The adapter receives an explicit chance plan and teacher manifest. It
does not select a teacher, draw a scientific dataset, train a network or admit
an experiment.

For each information state, it verifies the original teacher's history policy
against the posterior, exports visible-only native queries for every planned
physical deal, and infers all future policies before forcing any actions.
Matching original history and target rows must agree. The adapter forces both
players' chronological past and each target action across the shared plan,
leaving every future policy row unchanged. Shared interventions must be
consistent across hidden hands. A separate native profile mixes the target's
actions with its original probabilities to check the action-value baseline.

The native evaluator returns payoffs with actual sunk investments and exact
preflop all-in counts from the complete, immutable cache. Other postflop
outcomes use the supplied sampled board. Each action's conditional payoff is
an arithmetic mean over the same draws; repeated draws retain multiplicity.
Subtract the original teacher's action mix and divide by the starting stack
to obtain the common advantage label. No second entry, posterior or arrival
weight is applied. Existing attempt folders are refused rather than replaced.

## Qualification results

The bounded CPU check passed in 156.859 seconds. It used an old 362-input,
two-generation fixture teacher with weights 1 and 2, inherited entry ranges,
and retained own-hand/public-board anchors. It tested 16 information states:
both players on all four streets at 20bb and 60bb. The 60bb geometry is held
out in the registry, but this control is not an accuracy evaluation.

Each state had two independently seeded qualification plans of eight draws:
32 plans, 256 physical qualification draws and 64 native invocations, including
query exports. These are explicitly bounded implementation controls, not the
future scientific sample or noise budgets. No fitting or CUDA work occurred.

- Every tested fold lost exactly the actor's invested chips: maximum error 0.
- Native action values reproduced the original teacher's target mixture
  within 1.78e-15. Original history policy inference agreed within 1.12e-16.
- Shared profiles matched an independent union of individual qualified path
  interventions, with future policy rows preserved exactly.
- All ten corruption/refusal cases passed, covering attempt replacement,
  illegal actions, profile/deal order, estimator changes, incomplete draws,
  nonfinite values and cashflow or conservation failures.
- Independent readback authenticated all 77 input identities and 448 native
  artifacts, replayed chance plans, checked legal profile routing, and
  independently recomputed the label means, baseline and paired differences.

The two short plans sometimes differed substantially: the largest action-value
difference was 0.240469 of the starting stack. This is descriptive sampling
noise in the control cases, not a representation score or a population
estimate. Eight draws are sufficient for these transport checks; this result
does not establish an adequate scientific label budget. A real diagnostic
needs prospectively declared repeated labels and uncertainty calculations
that separate sampling noise from prediction error.

Sources are `stack_context_teacher_native_plan_v1.py`, its check, independent
readback and archive helper. Attempt/result/readback receipts bind all consumed
sources. The 62,163,063 bytes of original native evidence remain locally under
`stack-context-teacher-native-plan-check-v1/`. A verified 7,386,683-byte archive
and member SHA256 receipt preserve all 448 artifacts for the local Git evidence
checkpoint; no original evidence was deleted or altered.

## Remaining scientific work

The prospective teacher remains complete A-baseline played generations 0..63,
excluding unplayed fit 64, chosen before final comparison results. This fixture
does not qualify inference with that complete teacher. Authenticate its bank
after the main training finishes, then qualify resource use and inference.

The separate prediction experiment still needs actual public-flop splits and
a distinct preflop holdout, unsupported-state handling, sampling/source weights,
seeds, data/fit/noise budgets, paired initialization, stopping/model selection,
prediction-to-policy conversion and cluster-aware statistical registration.
No diagnostic has been admitted or completed. Relative-hand features remain
river-only, and source entry ranges remain inherited from 200bb at every depth.

The live four-arm comparison and its registered inputs are unchanged. It still
requires 64 cycles per arm, the actual complete-bank throughput gate, fresh
4096x7 evaluation, independent readback and plain-English analysis. These
controls provide label-generation plumbing; they do not establish equilibrium,
GTO Wizard agreement, arbitrary-position or multiway accuracy, or readiness
for production.
