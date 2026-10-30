# Locate the source of the exact all-in mistakes

The complete averaged candidates have independently verified all-in errors.
This separate post-hoc diagnostic will attribute those errors to **every**
played generation, without choosing a winner or changing either candidate.

For each candidate, keep the opposing player at its complete 78-generation
average. Evaluate generations 0 through 77 of BB and BTN separately at the
two already qualified preflop decision points. Both are the player's first
own action in this context, so their own-reach weights are one and the saved
equal-weight mean is linear. The unused next generation 78 remains excluded.

Use the existing complete exact values and unchanged endpoint definitions:
BTN's class-based fold/call response gain, and BB's restricted fold/shove
reallocation gain with call/raise frequencies unchanged. Report every generation
and the fixed groups: initial 0, early 1–25, middle 26–51, late 52–77. Report both
within-group mean and contribution to the full average. Do not select or promote
an intermediate, final, tail-averaged or reweighted policy based on this trace.

The runner validates each complete model bank before creating read-only
individual in-memory model views. Stored checkpoint identities are unchanged.
It must reproduce all 265 audited averaged policy rows and both exact endpoint
gains by arithmetic averaging. The independent reviewer does not use individual
views: it reconstructs every ordered prefix with the original CPU bank
constructor, checks the cumulative means, and independently reconstructs gains
as inferior-action probability times the exact action disadvantage.

No training, new deals, GPU inference or production change occurs. The runner
has a ten-minute cap; the full-prefix review has a fifteen-minute cap. Both stop
on production activity, inadequate free memory or integrity/numeric failure.

The diagnosis can establish where these particular averaged errors originate.
It cannot establish full-game convergence, rank the candidates against a common
opponent, or prove that a later jointly changing policy is a good equilibrium.
