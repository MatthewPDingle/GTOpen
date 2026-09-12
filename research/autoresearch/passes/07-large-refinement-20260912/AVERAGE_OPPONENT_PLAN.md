# Research-only learning against accumulated opponent strategies

Drafted while the forced-age large averaging discriminator is running. Do not
interrupt that run or execute concurrent hardware work. This is a different
learning algorithm, not a reinterpretation of its results or a proven
multiplayer convergence method.

Motivation: earlier large-game diagnostics found zero current opponent reach
at several branches whose average-policy response still fails. Changing only
average-output weighting cannot by itself restore updates to a zero-current-
reach branch. Test whether learning against accumulated opponent strategies
provides a more stable and better-covered target. The new final reach diagnostic
must first document coverage in both corrected large saved states.

In learning traverser p's down sweep, use accumulated strategy sums at learning
opponent nodes. Continue using regret-matched policy at p's learning nodes.
Frozen and forced/locked/profiled behavior remains exact. All average sums,
regret updates, discounts, payoffs, rake, canonical particles and terminal
estimators otherwise stay unchanged. Enable only as an explicit research
extension of the tested normalized-pair mode on a fresh engine. All native
evaluation and best-response passes bypass the extension. No production flag
or live-server entry point.

First require numerical tests, before admitting learning experiments:

1. For each learning traverser on a small raw/calibrated fixture, compare every
   reach block and its one-sweep learning increments to a separate native engine
   with the other learning seats temporarily frozen at their saved averages.
   Preserve existing locks and frozen seats. Require exact reach and matching
   values/updates within explicit float tolerance, plus unchanged fixed histories.
2. Verify eager/captured multi-iteration identity, native final CPU/GPU evaluation,
   invalid admission, and no mutation from read-only evaluation.
3. Run existing normalized-pair, exploration and production GPU equivalence tests
   with the new option disabled. CPU use remains a correctness reference only.

Do not run a large experiment solely because these numerical tests pass.
After the current averaging result and its reach diagnostic are verified,
register a separate small-game matched convergence screen with unchanged global
and conditional accuracy gates, complete wall time, fixed caps and seeds.
This plan admits implementation/numerical validation only. Port 56708 remains
untouched and all evidence is retained and pushed to GitHub.
