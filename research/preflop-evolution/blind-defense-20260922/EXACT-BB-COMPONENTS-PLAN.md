# Spend BB evaluation samples on the continuations that need them

The queued complete all-in table can also provide BB's shove value for every
starting-hand class. Unlike the BTN response calculation, this is a
counterfactual action value: do not multiply it by BB's current shove frequency.
Even a BB policy that never shoves still has a well-defined shove alternative.

For each compatible private pair, use BTN's fixed fold/call policy and the
complete all-board equity to calculate BB's shove payoff. Average over the
original incoming private-pair probabilities, conditional on BB's hand class.
BB's immediate fold payoff is already exact. Calls and non-all-in raises retain
their actual modeled continuations and still require evaluation.

## A decomposition that preserves the target

Let `pi` be BB's baseline class policy, `rho` a fixed candidate response, and
`Q_a(P,B)` the return for root action `a`, private pair `P` and board `B`.
The response gain can be split into:

```
exact term = E[(rho_fold - pi_fold) Q_fold
             + (rho_jam - pi_jam) Q_jam]
residual   = E[(rho_call - pi_call) Q_call
             + (rho_raise - pi_raise) Q_raise]
gain       = exact term + residual
```

With complete private-pair coverage and fixed policies, the first expectation
can be summed exactly. Only the second needs fresh population samples. This
removes root-fold/root-shove sampling error from the estimator, but does not
guarantee lower total variance: covariance with the remaining terms matters.
It also does not remove all-in terminals reached after the root raise; those
remain part of the raise continuation.

For response training, exact class-level fold/shove values can be compared with
sampled call/raise values from the correctly conditioned training stream. That
may prevent a few lucky sampled shove outcomes from choosing a bad responder.
The response must still be frozen before drawing a separate population test
stream. Class-balanced training samples must never be averaged unweighted as
the population evaluation.

## Admission and present limits

`finite_bb_root_components_v1.py` supplies the exact terms for an explicitly
supplied finite population; it does not establish that population is complete.
The separate control reconstructs native returns from the old four-model,
192-deal fixture, checks six fixed response policies, and verifies the identity
even when BB's actual policy never shoves. It uses no current candidate, fresh
deals, policy inference or GPU work. A fixture pass is arithmetic evidence only.

The control passed in 1.14 seconds. On its 192 deals covering 108 BB classes,
class-level shove values agreed with the saved native evaluator within 3.6e-14
bb; the six reconstructed total-gain identities agreed within 2.0e-15 bb.
The zero-own-shove-frequency check also passed. Evidence is recorded in
`bb-exact-components-control-v1-result.json`; the full 169-class population,
variance and strategic usefulness remain untested by this fixture.

Before any new strategic evaluation: audit the complete population and exact
equity table, admit the full policy bank, measure cost and variance on designated
planning data, freeze response-training/test counts and seeds, and derive valid
residual bounds and an explicit uncertainty rule. Add the exact term to the
residual interval without pretending the existing whole-return interval rule is
unchanged. No sample-count reduction or precision improvement is assumed yet.

This preparation does not modify the active visible-feature trial or the queued
BTN endpoint. Those evaluations retain their original contracts.

## Additional exact BB check before another sampled evaluation

Once the full tables and candidate policies pass their audits, a restricted BB
deviation can also be evaluated without postflop sampling. Keep each hand's
call and raise frequencies unchanged. Move only its existing combined fold/jam
frequency to whichever of folding and jamming has the higher exact conditional
value. For class `h`, with original entry mass `m_h` and
`alpha_h = pi_fold(h) + pi_jam(h)`, its improvement is:

```
m_h * [alpha_h * max(Q_fold(h), Q_jam(h))
       - pi_fold(h) * Q_fold(h) - pi_jam(h) * Q_jam(h)]
```

Summing gives a nonnegative profitable-deviation lower bound against the frozen
BTN policy. The unchanged call/raise paths cancel exactly. This does not test
whether more hands should call or raise, and cannot upper-bound the full best
response. A small value is therefore limited reassurance; a material positive
value is a concrete defect. Zero entry mass has no effect; ties may keep the
existing mix. Complete population evidence, native policy compatibility and an
independent scalar reconstruction are still prerequisites. Apply the same fixed
check to both completed candidates; do not select a checkpoint after seeing it.

The separate runner `hu_bb_fold_jam_response_20260923.py` and its reviewer are
prepared but unrun. Admission requires the queued exhaustive BTN endpoint and
its independent review, including complete equity coverage and the two complete
78-generation policy banks. The runner reuses those audited policy artifacts
without neural inference. The reviewer independently reclassifies private cards,
reconstructs outcome-wise payoffs and scalar class sums, and checks that call and
raise probabilities are exactly unchanged. Both stages have three-minute caps.
The existing running queue is not modified; this endpoint follows it separately.
