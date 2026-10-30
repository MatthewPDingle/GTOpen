# Exact updates for a rarely visited BTN response

23 September 2026. Pure CPU control while the registered broader evaluation
continues unchanged. No new training, model override or deployment occurred.

## Why this is worth testing

The old trace diagnosis found only 12-14 BTN responses to an initial shove in
some late 512-deal updates, spread across 96 supported hand classes. Merely
improving a visited hand's target leaves most classes unvisited. The completed
later-weighted study still showed clear errors at this response.

The exact physical-pair matrix can calculate both action values for every
supported BTN class on every iteration. This permits a separate exact regret
accumulator for this particular decision, without inventing sampled visits or
adding repeated synthetic records to the uniform reservoir.

## Reach must be included exactly once

For a class with incoming population mass m, let F and C be its fold and call
payoff contributions per game entry. These already include the probability of
the opponent choosing the shove. If BTN's current call probability is p, the
iteration adds these two regrets:

    [(F - ((1-p)F + pC)) / m, (C - ((1-p)F + pC)) / m]

Sum these contributions across played generations. Each iteration here has the
same deal budget, so its common count multiplier does not affect regret matching.
The source policies must be the current frozen played policies, not a final
average or a selected checkpoint. Unsupported incoming classes receive no update.
Zero shove reach contributes exactly zero; a positive payout at zero reach is
rejected. Classes with no accumulated reach retain their supplied fallback.

This differs from the previously controlled per-visited-record correction:
when the walker samples a visit, divide by that visit's shove reach and do not
multiply again. When integrating all classes deterministically, divide by fixed
incoming class mass and retain the shove reach already in F and C. Mixing these
two conventions would bias learning.

A two-iteration control makes the distinction concrete. Calling is worth +100
when the response occurs only 1% of the time, then -2 when it occurs every time.
Against the two fixed 50/50 played policies, the correctly weighted cumulative
regrets select fold. Treating both conditional observations equally selects call.

## Verification

`exact_btn_regret_accumulator_v1.py` uses an explicit new state identity. It adds
zero sampled observations, rejects duplicate/nonsequential updates, and supports
checked checkpoint round trips. It is not a format-1 sampled preflop table.

The control compares four old individual played policies (generations 0, 25,
51 and 77), a zero-shove policy and an all-shove policy. A separate scalar sum
enumerates all 47,478 canonical private pairs and their exact board outcomes,
weighting each potential sampled visit by its probability. Maximum increment
error was 2.14e-14 bb; cumulative error was 2.85e-14 bb. All six state round trips
passed. Absent classes retained fallback, zero-reach updates left regrets intact,
and six invalid-input cases were rejected without mutating the state.

This proves the tested expectation arithmetic, not end-to-end training quality.
Replacing finite sampled reservoir estimates with exact cumulative state changes
the realized learning trajectory and must be assessed in a new trial.

## Integration requirements before training

Use a distinct checkpoint/model/table identity that describes exact cumulative
regrets truthfully. Do not place a made-up observation count or these sums into
an artifact described as sampled retained-mean regrets.

At this BTN node the runtime table must consume only the exact accumulator;
do not combine its sums with sampled regrets for the same decision. If original
records remain in the postflop network's training reservoir to preserve that
objective, document that the exact runtime override takes precedence at this
node and test that those records cannot also enter the exact accumulator.
Alternatively, removing them is a separately declared training-objective change.

Verify complete visible-node mapping and CPU/CUDA probabilities, own-history
averaging, immutable played-generation progression and restart restoration.
Couple this with the already controlled BB shove-value correction, whose root
baseline changes every action's regret consistently. Preserve ordinary call,
raise and postflop traversal/RNG behavior. Pass a small integration/replay control
before registering any fresh training comparison. The current wider evaluation
has priority and its candidate and samples remain frozen.

This targets known all-in errors. It cannot replace the work on ordinary calling
ranges, postflop approximation, other positions or stack sizes.

Evidence: `exact-btn-accumulator-control-v1-registration.json` and its result.
