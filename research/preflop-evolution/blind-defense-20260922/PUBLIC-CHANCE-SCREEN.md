# Public-card sampling: useful for work scheduling, not a storage solution alone

The CPU-only census passed for all 336 continuations in the unchanged 112-board
BB-defense panel. It independently traverses suit-canonical public branches and
reconciles allocation totals with the existing capacity planner. No GPU solver,
production service, strategy values or incoming ranges were changed.

## Where the state lives

| Stored component | Decimal GB |
|---|---:|
| Flop regret and average-strategy arrays | 0.033 |
| Turn arrays | 6.213 |
| River arrays | 1,087.676 |
| Allocated slots outside the representative traversal | 11.476 |
| Existing total canonical allocation | 1,105.398 |

River arrays account for **99.43% of the reachable state**, or 98.40% of the
existing total allocation. Even removing every unvisited allocation slot would
save only about 1.04%. It cannot remove the present capacity barrier.

The first census attempt incorrectly equated visited action storage with the
planner's entire allocation. It stopped on its first probe: 5,627,792,352 versus
5,744,549,552 bytes. The existing direct-DMA layout can retain unreachable slots.
The preserved v2 correction reports both quantities separately, verifies their
sum for every continuation, and checks all canonical action counts. The failed
attempt, source copies and logs remain preserved; it produced no strategic data.

## How much would lazy sampling allocate?

This calculation assumes independent public-card draws, all betting branches
visited for the selected cards, full hand support, and retention of every state
ever touched. A canonical public prefix with sampling probability p has an
expected visited fraction `1 - (1-p)^T` after T draws. The census supplies actual
byte counts and suit-orbit multiplicities; no hand or action pruning is assumed.

| Global rounds | One uniformly selected flop per round | One weighted flop per round | One runout on every flop per round |
|---|---:|---:|---:|
| 2,000 | 13.29 GB | 13.21 GB | 717.18 GB |
| 20,000 | 111.19 GB | 109.84 GB | 1,093.77 GB |
| 200,000 | 674.53 GB | 640.20 GB | 1,093.92 GB |
| 2,000,000 | 1,093.55 GB | 1,085.94 GB | 1,093.92 GB |

These are **expectations, not peak-memory admission bounds or convergence
estimates**. They exclude metadata, maps, temporary arrays and checkpoints.
One sampled round is not equivalent to one full-tree CFR iteration. A small
early allocation does not establish that sufficiently accurate play will be
learned before the memory budget is exhausted.

Public Chance Sampling was developed to reduce traversal work while retaining
private-hand enumeration. Its benefits do not imply that all previously learned
information sets can be discarded. The published convergence setting is
two-player zero-sum; our raked candidate requires separate empirical validation.
[Johanson et al., 2012](https://johanson.ca/publications/poker/2012-aamas-pcs/2012-aamas-pcs.pdf).

## Chance-value check

An independent finite-sum oracle exhausted all 2,352 ordered public turn/river
proposals for each of 384 fixed compatible private deals across three flops.
Each private deal has 1,980 legal runouts. Masking card collisions and multiplying
by `2352/1980` reconstructed the full legal-runout expectation to at most
2.23e-16 error. Without that correction, even a constant unit payoff averages
only 0.84184. That intentionally incorrect control was rejected.

This verifies a fixed-policy terminal-value estimator only. It does not validate
sampled regret updates, strategy averaging, public-prefix weighting for earlier
folds, suit transport, or convergence. Future cards must not be disclosed to an
earlier decision, and an earlier fold must not be conditioned on unused future
cards. Those require separate integration controls.

## Decision

Do not launch the full forest on the assumption that sampling alone fixes memory.
The actionable finding is the concentration of state on the river. Next qualify
a river decomposition design: keep earlier streets and the necessary boundary
values, and determine whether smaller river problems can be solved/reconstructed
within acceptable cost and error. Do not simply discard river strategies and
re-solve ordinary fixed-range games: previous continuation-transfer work already
identified that as an unresolved source of changed earlier incentives.

The relevant existing warning is
[`RESOLVING-INTERPRETATION.md`](../representative-coverage-20260919/RESOLVING-INTERPRETATION.md).
The next design must carry the correct counterfactual boundary values, handle
zero-reach hands, check the complete assembled policy, and explicitly distinguish
zero-rake controls from the actual raked BB experiment.

Evidence: `public-chance-screen-v2-registration.json`,
`public-chance-screen-v2-review.json`, the probe/panel results, and native logs.
The panel finished in 70.06 seconds without CUDA allocation; 114 source/input
hashes were verified unchanged. No strategy has been trained or deployed by
this screen.
