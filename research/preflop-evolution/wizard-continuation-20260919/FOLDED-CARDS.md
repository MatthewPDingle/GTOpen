# Folded cards and opponent response: reviewed diagnostic

The complete physical-deal check leaves the main conclusion intact: omitted folded-card information is a small contribution in this one AA decision, while the opponent response policy has a much larger effect. This is not a new solved strategy.

32 million deals, 40 independent batches, frozen saved policies, actual seven-card showdowns, and no equity cache. Hero holds AcAd; suit symmetry applies before the flop. Four CPU threads; production untouched.

| Condition | Opponent calls jam | AA equity when called | AA jam EV |
|---|---:|---:|---:|
| two_live_hands | 18.07% | 79.04% | 44.244bb |
| including_six_folds | 18.24% | 79.02% | 44.389bb |

Accounting for the six folds changes jam EV by +0.145bb; approximate paired Monte Carlo 95% interval [+0.119, +0.171]bb. Effective sample sizes are about 1,400,985 and 1,302,904. These intervals exclude model uncertainty and policy adaptation.

The no-fold-conditioning arm reproduces the analytic two-hand-compatible call probability within its sampling error. Its jam EV is also close to the prior cached-equity estimate of 44.20bb. The earlier, cheaper range-conditioning calculation retained cached equity and found +0.246bb; this extension samples the actual board as well. Do not treat the two estimates as the same experiment.

## Response-policy sensitivity

Holding GTOpen's LJ entering range fixed but replacing only the six inspected jam-response hand frequencies with Wizard's changes AA jam EV from 44.20bb to 60.27bb. This +16.07bb is a deliberately artificial intervention, not an improvement claim or a prediction of Wizard's EV.

Wizard and GTOpen put different hands into the preceding jam. An opponent defending against one jam range cannot be transplanted into the other and called an equilibrium. This supports testing jointly adapting ranges and responses rather than fitting a premium bonus or copying a visible chart.

Scope: one 200bb NL25 decision, saved GTOpen strategies, configured rake, and no new preflop solve. The original Wizard tree and GTOpen tree still have documented differences. Reserved 100bb references remain untouched.
