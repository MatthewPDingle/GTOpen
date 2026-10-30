# Resumable sampling beyond the fixed flop panel

The resumable sampler now supports both the qualified 112-board panel and a
separately identified **full-deck** mode. Its sampling-law and checkpoint controls
passed. This enables a broader training population; no new policy has been trained
or evaluated with it yet.

## Two explicit chance populations

Panel mode reproduces the earlier law: choose a representative board in proportion
to its nominal weight times compatible private-pair mass, draw the private hands
conditionally, apply one uniform global suit permutation, then draw ordered turn
and river cards without replacement. All 8,192 saved fixture deals were reproduced
exactly. Every board's mass and probability agree with the independent dense oracle.

Full-deck mode draws compatible physical private hands in proportion to the same
supplied entry weights, then draws five public cards uniformly without replacement
from the remaining 48 cards. The first three become a sorted flop; turn and river
retain their order. There is no selected flop panel and no additional suit
permutation is needed: private cards already span the physical deck.

Both modes preserve the frozen context's existing per-combo scaling and 1e-5
entry cutoff. BB retains all 169 supported classes and BTN all 96 inherited
supported classes. Full-deck mode does not learn new incoming opening ranges,
restore classes excluded by the original prior, or model earlier folded cards.
It also does not expand the fixed postflop action menus.

The populations must remain explicitly distinguished in comparisons. The selected
panel's weighted card removal changes the effective private-hand marginal: its
player-0 marginal differs from the full-deck marginal by **0.0336784 total variation**
in this context. That is a property of conditioning on different board populations,
not evidence of a new range improvement or a sampler error. Supplied entry weights
are the same; selected-board and full-deck strategy metrics are not interchangeable.

## Evidence

The full-deck private-pair distribution was independently enumerated over all
1,326-by-1,326 pair combinations. Maximum first-hand marginal error was 7.59e-19;
maximum joint probability error was 1.91e-21. A separate generator using that dense
distribution reproduced all 512 full physical draws, including ordered runouts.

Those 512 draws contained 505 distinct physical flops and observed 149 BB and 82
BTN classes. Finite samples need not visit every supported class. These counts
are a sampling sanity check, not a coverage guarantee or strength result.

Splitting the full-deck draws at 173, serializing state, restoring and drawing
339 more exactly matches one uninterrupted 512-deal run. Panel continuation also
replays exactly. Checkpoints bind the mode, source-context hash, optional manifest
hash, NumPy version, deal counter and PCG64 state. Seven invalid inputs were
rejected without changing the live sampler state. Eight registered inputs and
the checkpoint/fixture artifacts were hash-verified. The control took 1.06 seconds,
used no GPU and left production unchanged.

## Next use

The full-deck fixture is implementation evidence, not a reserved strategic test
set. A physical training pilot must register its own fresh seed, budget, model
settings and stopping rules. Independent evaluation needs separate random draws
and the fixed-deviation uncertainty rules already documented. To diagnose board
coverage specifically, compare the same learning method with panel and full-deck
training, reporting each policy on the same independent evaluation population.
Do not attribute any difference solely to training coverage if incoming weights,
bet menus or fitting settings also change.

This is sampler checkpointing only. Complete self-play resume also needs the
action RNG, reservoirs, iteration and actually played model bank. The broader
physical self-play and strategic-method gates remain pending.

Evidence prefix: `sampled-physical-deals-v1`.
