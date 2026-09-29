# Candidate: learn equity and calculate terminal calling value

Status: implementation controls passed; no scientific learning comparison has
started. Production, saved studies and their numerical tolerances are unchanged.

## Why this follows the evidence

The boundary diagnostic found two nearly equal negative learned action values
whose ordering changed between CPU and CUDA. A hard fallback amplified those
differences into opposite pure actions. Their predicted call values were also
wrong in economically meaningful ways.

The earlier STACK-BOARD-ERROR-DIAGNOSIS-FINDINGS.md already found that changing
action conversion alone reduced validation loss by only 0.014–0.285% across its
variants and seeds. That was an earlier pair of models, so it is context rather
than a new measurement on the current weights. It supports addressing the value
prediction problem rather than spending another trial on conversion alone.

BOARD-RIVER-STRENGTH-FIT-PLAN.md also documents why uniform-opponent equity cannot
replace equity against betting-conditioned ranges in the broader model. The
candidate below is deliberately restricted to the existing uniform-opponent
terminal river learning reference. It is not a replacement for GTOpen's preflop
or all-street continuation model.

## Representation

Use a shared 191-input, 64/64-hidden-unit, one-output network with a sigmoid
equity estimate between zero and one. Its inputs are the existing 133 card
indicators, 33 hand summaries and 25 relative-hand/board features. Exclude actor,
history and prices from this equity head because the diagnostic's opponent is
held uniform over legal hands. Equity must become range-conditioned before this
architecture could address actual betting-conditioned opponents.

The model starts at 50% predicted equity. Its final layer starts at zero; the
card encoder has seeded initialization. There are 16,513 learned parameters,
versus 58,504 across the current pair of 387-input player networks. This is a
comparison of modeling approaches, not an equal-parameter or equal-initial-
function experiment. No faster training claim follows from parameter count.

For each qualified terminal call, compute:

```
fold value = 0
call value = estimated equity × net pot after calling and rake − call cost
normalized call value = call value / starting stack
```

Retain every legal hand and decision. The greedy policy calls when the calculated
call value is positive and folds on ties. It has no learned negative fold score
and no fallback comparing two negative learned scores. It can still be wrong if
equity is wrong, and any hard action boundary remains sensitive sufficiently
close to zero. No cosmetic mixtures or discarded uncertain rows are introduced.

The original cash-flow reference is already qualified. This implementation
reuses its economics rather than changing rake, payoff conventions or labels.

## Keep the fitting objective comparable

Use the same normalized two-action mean squared value loss as the baseline. With
fold exactly zero and equity estimate q, its algebraic form is:

```
0.5 × (net pot / starting stack)^2 × (q − reference equity)^2
```

This preserves the reference's context/state/card weighting when the two models
receive identical batches. Do not silently replace it with unweighted equity
MSE and then describe the result as an isolated representation change.

## Implementation evidence

Eight CPU controls passed: feature selection/neutral initialization, exclusion
of public context from uniform equity, independent dense readback, normalized
values and loss gradients, physical bounds and unit scaling, explicit assumed
error bounds without dropping uncertain rows, always-unprofitable call prices,
and rejection of malformed inputs or the wrong opponent scope.

A separately recorded synthetic GPU control passed 12 cases: two seeds, batches
of 31/257/8,192 rows, and both float32 and float64. It compared equity, normalized
values, losses and gradients between CPU and CUDA, plus independent NumPy
inference. Maximum CPU/CUDA normalized value difference was 2.39e-7 in float32
and 4.45e-16 in float64. The fixed limits were 2e-6 and 2e-12 respectively.

The control computation took 0.813 seconds after admission and imports; the
whole invocation took about five seconds. Peak CUDA reservation was 155.2 MB.
These are implementation-control timings, not scientific training benchmarks.
No poker samples were fitted and no fresh-test model predictions were made.

The optional stability report assumes a supplied equity-error bound; it does
not estimate confidence. If equity error is at most epsilon, the induced call-
value error is at most net pot × epsilon. The greedy terminal decision's loss
is also bounded by that amount, ignoring additional floating-point rounding.
All rows still receive a predicted action and count in accuracy measurements.
A calibrated learned error bound would require separate evidence.

## Next controlled comparison

Prepare a new registration before training; this document is a proposal, not
an executed or frozen scientific protocol.

- Baseline: current 387-input, two-player value networks and action conversion.
  Candidate: this equity-pricing model. Two fresh fitting seeds, 9297601/9297602.
- Reuse the same 1,024 random-arm fitting boards from the balanced study, with
  their exact files and counts. Retain all five fitting stack depths and their
  admitted decisions. Use identical batches, Adam settings, 8,192 updates and
  checkpoint steps 0/1,024/4,096/8,192. No budget extension after outcomes.
- Select 128 fresh validation boards and 128 fresh random test boards with
  board seed 9297600, excluding all prior fitting, validation, test, stress and
  qualification groups. An additional 64 fresh structured stress boards remain
  separate from the primary population result.
- Select each model using validation normalized decision loss, tie to earliest
  step. Freeze all four model identities before preparing final/stress labels.
- Primary target: at least 20% lower mean normalized loss in both seeds, and
  mean loss no greater than 0.001 starting stacks at each of 60bb and 150bb.
  Those depths are excluded from fitting/selection but are not globally unseen.
- Preserve absolute loss, tails, hand groups, board groups, actors and price
  slices. Report adverse results and every numerical failure. The old failed
  comparison stays failed, regardless of this new comparison's outcome.
- Use float32 fitting and separately qualify widened-float64 final inference
  for BOTH arms before evaluating scientific test data. The new candidate's
  implementation control is done; baseline/evaluator integration remains.
  Keep the existing metric tolerances. Precision changes do not retroactively
  repair old recorded results.
- CPU readback should record all numeric discrepancies within its fixed budget,
  then report qualification failure if any required check fails. It must not
  retry or relax the checks. This avoids stopping with only the first discrepancy
  available for analysis; unexpected corruption/resource failures still stop.
- Register at most one hour of main work and 30 minutes of readback, 4 GB CUDA
  plus 2 GB external headroom, and 256 MB of new evidence plus 128 MB reserve.
  Respect active production, heavier workloads and the existing storage cap.

These are requirements for the next implementation/registration, not claims
that its dataset, runner or fairness controls already exist. Passing a learning
comparison would support moving to a range-conditioned, multi-decision reference;
it would not qualify deployment or establish accurate preflop ranges.

## Files

- `tools/research/stack_equity_priced_model_v1.py`
- `tools/research/test_stack_equity_priced_model_v1.py`
- `tools/research/stack_equity_priced_control_v1.py`
- `stack-equity-priced-control-v1-{registration,attempt,result}.json`

The original study artifacts and production on port 56708 remain untouched.
