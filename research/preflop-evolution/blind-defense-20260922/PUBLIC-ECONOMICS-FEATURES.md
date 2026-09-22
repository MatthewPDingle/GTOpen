# Public stack and price inputs: first checked prototype

The research encoder now has a separate 60-number public-state descriptor.
It is not connected to the running model and does not establish stack-general
poker accuracy. The current full training trial remains unchanged at 200 bb.

## What it exposes

From the acting player's perspective: starting/remaining stacks, committed
chips, pot, dead money, call cost, effective stack summaries, stack-to-pot ratios,
call price and rake. Each of four action slots includes a legality mask, action
type, all-in flag, additional chip cost and relative size. Monetary values and
SPR use a declared log transform; fractions retain their meaning. Cards, hidden
runouts, opponents' hole cards and value targets are not used by this descriptor.

The existing public-node/history inputs only identify prices within a frozen
game. A context hash remains mandatory: the same node ID in a different stack
configuration must not reuse a cached table or policy by accident.

## Checks completed

`public-economics-control-v1` extracted 455 distinct public states from 7,277
existing observations. Every public ledger was reconstructed along its action
history and checked against native state totals. Preflop incremental prices were
also checked independently against absolute raise-to amounts. The root facing
a 2 bb open has pot 3.5, call cost 1, raise-to-6 cost 5, and jam cost 199 bb.
After calling, the flop pot is 4.5 and both players have 198 bb remaining.

Changing private-card fields and hidden batch text left public output unchanged.
Ten negative controls rejected mismatched context, inconsistent chip totals,
wrong call price, oversized action, incorrect all-in flag, NaN, illegal check,
duplicate state and oversized action menu. Arithmetic fixtures at 20, 40, 60,
100, 150, 200 and 400 bb produced different stack/jam inputs.

Those seven depth fixtures are synthetic arithmetic tests, not newly generated
native game trees or training observations. Only the 200 bb native context was
checked. The ledger replay independently accumulates exported action increments;
it does not independently regenerate every postflop legal size. The existing
native state implementation supplies those actions.

## Still needed

Generate independently validated native contexts at multiple depths, including
short-stack changes to the legal tree. Add a genuinely independent legal-action
comparison and stricter context qualification. Integrate the descriptor with a
versioned cross-context observation/table/checkpoint scheme, then train and test
with held-out depths. Equal-stack heads-up is the current prototype scope;
unequal stacks, side pots and multiway generalization remain separate work.
See `STACK-CONTEXT-PLAN.md` for the broader experiment requirements.
