# What the neural-CFR papers do and do not establish here

Reviewed September 22, 2026. This review does not change any registered trial.

The original Deep CFR experiments used a seven-layer, 98,948-parameter network
with card embeddings and separate card/betting branches. They allocated up to
40 million examples per advantage memory. Flop hold'em used 4,000 minibatch
updates of 10,000 examples; full limit hold'em used 32,000 updates of 20,000.
Its convergence analysis retains an approximation-error term; more CFR iterations
alone do not eliminate that term. These are different games and budgets, not a
recipe that establishes accuracy in our raked no-limit subtree.
[Deep CFR, sections 4-5](https://proceedings.mlr.press/v97/brown19b/brown19b.pdf).

Single Deep CFR stores the iteration policies and reconstructs their average
using the player's own action reach. This avoids learning a second network to
approximate the average, but does not fix errors already in the value networks.
Its reported Leduc setting used 1,500 traversals per iteration; that six-card
game is not a realistic benchmark budget for full-deck no-limit poker.
[Single Deep CFR, section 5 and the Leduc appendix](https://arxiv.org/html/1901.07621).

Our fixed dense trial uses two 64-unit hidden layers (21,700 parameters per
player), at most 262,144 retained visits per player, and 512 fresh deals per
update. It makes 512 full-data optimizer updates, so the step count cannot be
compared directly with the papers' minibatch update counts. Our all-generation
average uses ordinary rather than linear iteration weights. We freeze both
players for an update rather than updating them alternately. The game includes
rake; the two-player zero-sum equilibrium guarantee does not transfer directly.

## Consequences for the research

The retained-data diagnosis found substantial preflop fitting error. Testing a
direct table there is a focused way to remove that source of error while leaving
the postflop network and training objective alone. It cannot repair noisy targets
or inaccurate postflop continuation play. The larger fresh-data trial separately
tests coverage with all other training settings fixed.

If both remain weak, investigate postflop representation and fitting capacity
with controlled comparisons, rather than treating small training loss or plausible
preflop charts as success. More samples, richer card features, architecture, and
iteration weighting are distinct hypotheses. Change one at a time and retain a
fresh accuracy test. This prototype is inspired by neural CFR; it is not a
reproduction of the published experimental configurations.
