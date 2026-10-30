# Next diagnostic: exact hand values at different prices

Status: design only. No data construction, fitting or accuracy test has started.
This follows the earlier decision to use a tractable poker reference when the
large study's evaluation cannot resolve useful improvements at reasonable cost.

## Question

Can the research network learn correct hand-dependent call/fold choices as the
public price and remaining stack change, when its target values are exact?
An answer separates representation/optimization failure from noisy targets and
weak evaluation. It does not certify full-game equilibrium or preflop ranges.

## A small, checkable reference

Use real 52-card Hold'em river holdings and registered equal-stack native public
states whose legal actions are exactly fold/call and whose call ends at showdown.
Do not drop legal raises from an otherwise three-action state. Check native
action meanings, costs and terminal behavior before admitting each state.

The opponent is a deliberately fixed uniform distribution over legal two-card
holdings, conditional on the visible board and the acting player's cards.
This is a uniform-jammer diagnostic, not a claim about an actual player's range
after betting. No inference from action history is attributed to this reference.

For pot P before calling, call cost C and rake R on the final pot, exact
call-minus-fold value is E*(P+C-R)-C, where E is win probability plus half the
tie probability. Enumerate every legal opponent holding to calculate E. The
best response is call if this value is positive and fold if negative; either
action is optimal at zero. Regret of a mixed prediction can then be calculated
exactly without a fitted responder or sampled hidden cards. Existing exact-river
payoff audits are useful dependencies, but do not replace this new reference.

## Qualification before training

1. Select native two-action terminal-call states by a fixed public rule, covering
   different prices where the existing geometry supplies them. Inspect geometry
   only; do not select states because a learner succeeds or fails on them.
   Report actual price coverage. Stack variation alone does not guarantee varied
   pot odds; a degenerate price grid must be fixed before fitting.
2. Use deterministic public boards with canonical suit-isomorphism grouping.
   Define separate training, validation and final-test board groups before model
   fitting. Select seeds and counts in a new immutable registration after a small
   cost/geometry probe. The probe is excluded from final testing.
3. Use a native evaluator for all legal hero/opponent combinations and an
   independent five-card-combination evaluator for a fixed qualification subset,
   plus tie/board-only/nut/loss cases. Reject card overlap and duplicated holdings.
4. Independently recompute call/fold cash flows and compare with native terminal
   values. Check complement symmetry and probability mass. Reference uncertainty
   is numerical tolerance only within this finite game, not a population claim.
5. Confirm visible features contain only hero cards and public information.
   The exact opponent enumeration supplies labels, never network inputs.

## Bounded learning experiment, only after reference qualification

Fit the new 362-input shared model at the five fitting depths. Keep 60/150 bb
out of fitting, hyperparameter selection and target inspection until the final
test. A comparable 302-input baseline deliberately lacks public numeric prices.
Its inability to separate otherwise identical observations is a diagnostic
limitation, not an estimate of production model quality.

Use no preflop lookup overrides in this river-only diagnostic. Normalize the
exact call advantage by starting stack as recorded in the model contract.
Specify context/state/hand weights explicitly; report both normalized loss and
unscaled bb decision regret. Constant stack normalization preserves the optimal
action, but changes relative regression emphasis unless weights compensate.
Freeze that choice before training. Do not select solely on averaged MSE.

Freeze initialization seeds, optimizer, step/elapsed budgets, sample counts,
validation selection rule and failure threshold before executing the fitting
comparison. Model outputs used as policies must retain legal-action masking and
the registered regret-matching rule. Include an analytic oracle and a constant
policy as checks, not as learned competitors. Record errors by stack, price,
hand-strength band and seat, including near-indifferent decisions.

If the shared model cannot learn this clean target under the fixed budget,
investigate representation/optimization on the diagnostic training/validation
data. Do not start broad expensive self-play. If it succeeds, move to a small
multi-decision game with independent best-response calculation before claiming
the complete learned continuation improves preflop choices.

## Resources and limits

First qualify the reference without another large solve. Reserve at most 250 MB
of new evidence and one hour for that qualification; decide the subsequent fit
budget prospectively from actual throughput. Retain global allocated research
storage <=800 GB and >=40 GB free on S:. Use bounded CPU parallelism where it
helps enumeration; never multiply numerical-library threads inside workers.
Use the GPU for fitting when admitted, sharing with light desktop use while
yielding to production/heavier work. Keep combined research CUDA <=4 GB and
external headroom >=2 GB. No production changes follow automatically.

Do not repeat the earlier three-card exact-CFR controls or the fixed-200bb
uniform-opponent audit as if they answered this cross-price learning question.
