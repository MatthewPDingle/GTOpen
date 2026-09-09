# Contextual preflop modeling — experimental v1

The model library includes **Data · Ignition · NL10 regular · Contextual v1**.
It is a separate entry derived from the existing Ignition pool. Existing
profiles, hand-painted ranges and saved games are not converted.

Select the new entry for a modeled seat, then **Apply model** or **Re-solve**.
For joint adaptive solves, leave HERO off and your own seat on Solver. Opening,
vs-limp, vs-raise and squeeze policies retain the existing measured ranges.
The new model changes responses to a **3-bet or later raise**.

## What changes

Previously, the same hand at a position used one pooled response after entering,
regardless of how it entered, raise depth or call price. The new predictor uses:

- Whether the player has not entered voluntarily, has only limped/called, or
  has raised earlier in this hand.
- Facing a 3-bet versus a 4-bet or later raise.
- Incremental call, pot before calling, prior investment and remaining stack.
- Position, table size and the hand's ranks and suitedness.

The game records prior raises explicitly. Being the last aggressor is not the
same as having raised earlier. The nominal call price is
`min(faced total − already invested, remaining stack) / (pot + capped call)`.
It is not side-pot-adjusted pot odds. All amounts are in big blinds.

The model predicts fold/call/raise probabilities. Existing profile size rules
map raising mass onto the legal action menu; it does not learn a new re-raise
size distribution or a separate jam probability. If no further raise is legal,
the existing legal-action fallback applies.

## Inspecting a range

Open **Manage models → Edit → Vs 3-bet+**. For the contextual version, choose
the earlier action and raise depth, then adjust **Already in**, **Facing total**
and **Pot before call**. The starting stack and position come from the built
game. The price and source/fallback explanation appear immediately below.

This is a read-only preview of one hypothetical situation, not a static range
to paint over every re-raise node. Changing preview controls does not change
the model or either live solve. The action ribbon's actual node reports whether
the contextual prediction, a fallback, a point lock or an adaptive response
is in use. Frequencies are conditional on reaching that situation; the ribbon
grid also shows which hands actually arrive through the chosen history.

The existing **adaptive responses from % of stack** setting still takes
precedence. At the default 25% threshold, the solver learns the response to
large raises. The preview explains when its hypothetical amount reaches that
threshold; its predicted frequencies are not then forced in the game.

At a heads-up flop endpoint, expand **Preflop continuation estimate** below
the range grid to inspect the current approximation. The two values include
modeled future play, before subtracting preflop investments. **Unallocated
amount** is the pot minus both values; under the calibrated model it mixes
embedded training rake and approximation error, and must not be read as an
expected-rake estimate. The panel reports whether requested rake is applied.
All-in equity uses the requested rake even with a calibrated setup.

## Coverage and limitations

This version is enabled for **3–6 players, no ante, 0.5/1 bb blinds**. On other
formats, including 8-handed $2/2 and $2/5, the saved measured policies remain
the fallback and the UI says so. Transferring the predictor to those formats
needs separate evaluation. Within the source format, stacks, opponent positions,
individual hands and rare histories can still be sparse; supported format does
not mean every situation has strong direct evidence.

The [offline comparison](../research/ignition-reraise/README.md) found 9.3%
lower overall log loss on 2,351 later re-raise decisions, and 10.8% lower after
prior entry. Those periods had already been inspected during development:
this is retrospective evidence, not a fresh independent test. Lower log loss
does not imply the same increase in win rate. Cheap calls with rare weak hands
can still be overestimated. Other sites and stakes are not newly learned here.

Preflop continuation values remain a separate approximation. See the
[initial value audit](../research/preflop-evolution/continuation/README.md)
for the observed rake/accounting limitations. A small solver gap measures
convergence within the configured model, not complete poker accuracy.
The [192-reference continuation study](../research/preflop-evolution/continuation/pass2/README.md)
tests a joint value/rake candidate against disjoint evaluation boards. It lowers
mean value error relative to calibrated in the sampled fixtures, but its small
lead over static is uncertain. It is not installed as a production value model.

## Versioning and implementation

The immutable predictor is `ignition-nl10-reraise-v1`, embedded from
`cache/contextual/ignition-nl10-reraise-v1.json`. Its coefficients and baseline
probabilities match the frozen offline artifact. Profiles carry the version in
`response.contextual_reraise`; generation inputs use
`stats.dataset.contextual_reraise`. Missing fields retain legacy behavior;
unknown versions are rejected. A future fitted model must get a new version.

CPU and CUDA compile the same legal policy. CPU inference reuses identical
contexts in a bounded cache; CUDA uploads the compiled policies when the
solver is initialized. No model training occurs while solving.

Pass 2 precomputes baseline logs and hand terms once. Paired benchmarks show
3.20-times faster full-range inference, at a cost of 23.77 KiB of added numeric
storage. All observed f32 probabilities match the original dense implementation;
the artifact and version are unchanged. This measurement does not establish a
corresponding improvement in complete solve speed.

The [strategy sensitivity study](../research/preflop-evolution/behavior/README.md)
and [cross-source evaluation](../research/preflop-evolution/transfer/README.md)
extend the evidence without changing existing profiles. Transfer gains are
offline diagnostics; they do not enable the model on 0.4/1 or eight-player games.

`POST /api/preflop/contextual-preview` accepts `{version, cfg, seat, context}`.
The context contains `entry` (`cold`, `called`, `raised`), `raises` (2 for a
3-bet, 3+ for later raises), `pot`, `invested` and `to_call`. It returns the
policy, nominal price and explanation without accessing either live session.
Unsupported formats return `policy: null`, requesting the caller's existing
fallback. Invalid amounts or unknown versions return an error.

Tests, measured cost and progress charts are tracked in the
[development record](../research/preflop-evolution/README.md).
