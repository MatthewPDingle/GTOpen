# Next: qualify river bounds in the complete played policy banks

## Evidence motivating this step

The fixed four-fit diagnostic reduced equal-dataset mean river Call-minus-Fold
validation error by 6.350%, under-50-bb contrast error by 12.185%, and full
postflop action error by 0.715%. The per-row non-increase controls passed across
694,032 training/validation rows, including 180,260 eligible river decisions.
No final-test inference, new deals, training or production modification occurred.

About 22.28% of eligible validation source weight violated the bounds, but only
3.11% had changed regret-matched policies; mean policy TV was 0.002993. These
fractions average the four datasets equally. Their source weights are not
game-reach frequencies. This is a real prediction defect, but its strategic
importance is unproved. Do not describe it as the main cause of bad ranges.

The diagnostic fits used 70% training partitions of saved reservoirs. The
actual played policies average complete historical banks fitted during the
original training runs. Neither applying the correction to one diagnostic
network nor averaging raw advantages reproduces that played policy.

## Adapter requirements

Create separate versioned research adapters; leave all frozen runtimes intact.
Use the two audited completed board-root arms, 9266201 and 9266301. Each bank
must contain played generations 0-77, with weights 1-78 and its exact original
preflop overrides. Exclude the unplayed next model. Admit models through the
board-root checkpoint validators, not the older format-3 visible-bank reader.

For every model and acting player:

1. Validate its positive finite saved advantage scale and exactly widen its
   float32 parameters and float32 input features to float64.
2. Join the query to the verified native public geometry and legal menu.
   Apply the frozen bounds projection only at river Fold/terminal-Call nodes.
   Use that model/player's own scale to convert predictions to bb and back.
3. Apply the existing positive-score normalization and first-legal-argmax
   fallback, then the original direct preflop overrides.
4. Compute that model's own-action reach with the resulting probabilities,
   including any earlier corrected river decision. Accumulate model weights
   in their original order and preserve the zero-support fallback.

The projection is per model before regret matching, not after averaging scores
or policies. Correcting one river decision can alter a later river node's
model weights through own-action reach. An unchanged node's averaged policy
can consequently change even though its raw scores were not projected. Treat
that as an explicit part of the candidate, not an accidental discrepancy.
Preflop/flop/turn scores, probabilities and averaged policies must remain
unchanged because no earlier projected river action can precede them.

## Qualification before any large run

Bind source, catalog, complete model references/scales, query provenance,
controls and this plan in a separate registration. Make the candidate optional
in the new adapter solely for baseline equivalence controls; do not add a
production setting or alter existing checkpoint metadata.

Use small hand-calculated synthetic histories to exercise unequal model/player
scales, both upper and lower violations, negative fallbacks and ties, exact
preflop overrides, nonuniform generation weights, zero reach and a later river
decision whose averaging changes only through an earlier action. CPU NumPy
and CUDA implementations should independently reproduce those calculations.
Reject reordered/missing banks, wrong game/menu/actor/history, invalid scales,
and observations missing their required own-action ancestors.

For real observations, select the first 32 already archived physical deals in
registered order from the existing complete board-root evaluation. Include
all their query batches with required own-action ancestors, without selecting
on predictions or results. Register the exact source routes and row counts
before inference. If that archive cannot provide the necessary query records,
record the limitation and register a replacement control source before use;
do not silently borrow a held-out result or generate new scored deals.

Required checks:

- Projection disabled reproduces the original typed CPU and CUDA board-root
  bank, including denominators and direct table overrides.
- Projection enabled CPU/CUDA probabilities agree within 1e-9; denominators
  within 1e-10 absolute plus 1e-10 relative tolerance. Record maxima.
- Float64 synthetic fixtures agree within 1e-12. Bounds and per-model
  probability normalization hold; no illegal action gets probability mass.
- Complete chunked and unchunked results agree under the original model order.
- Preflop, flop and turn remain identical within each backend. Report river
  changes separately for directly projected and reach-affected observations.
- Generation zero and verified in-bounds rows are unchanged. Saved files and
  complete bank memberships remain byte-identical.
- Report warmed baseline/candidate time and memory on the same fixed queries;
  do not omit a slow or discrepant batch. Time initialization separately.

This qualification uses no target-label loss and makes no EV claim. Query
coverage is descriptive; do not label it an independent accuracy test.

## Subsequent decision and resources

If qualification passes, register a fixed complete-policy comparison on fresh
physical deals, including source weighting, paired uncertainty, both roles,
baseline/candidate combinations and unchanged preflop entry ranges. An
inference-only comparison tests this correction, not a retrained equilibrium.
Do not retune projection strength or select a policy from those test outcomes.
A separate coadaptation/training experiment may follow if strategically useful.

Use available CPU parallelism for preparation and one GPU for batched inference,
sharing with light browser/video use while yielding to production solves or
heavier GPU work. Retain shared locks, fresh resource checks and the global
800 GB allocated-storage cap. Bound qualification to 30 minutes and 250 MB of
new artifacts; source archives remain immutable. Save any failing controls.
The broad preflop research goal remains active; these river-only results do
not qualify new positions, stack depths, action menus or multiway games.
