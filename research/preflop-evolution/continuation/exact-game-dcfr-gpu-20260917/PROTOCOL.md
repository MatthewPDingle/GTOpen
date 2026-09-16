# Production CUDA update diagnostic

Continue the independently solved three-card game from exact-game-extension-20260917.
This is a diagnostic, not a Hold'em model or a deployment candidate.

## Registered comparison

Run full-tree DCFR, exact continuation cutoff, zero-own-support-completed exact
cutoff, and the unchanged prior RBF prediction cutoff. Reuse the frozen 1,024
training contexts and model settings; no new samples or target fitting.
Checkpoints: 100, 500, 2,000, 5,000, 10,000, 20,000 alternating iterations.
An iteration updates player 0, then player 1 using the updated regrets, then
discounts positive regrets by t^1.5/(t^1.5+1), negative regrets by 0.5, and strategy
sums by (t/(t+1))^2, matching GTOpen. Uniform fallback threshold is 1e-12.

Compile the complete, unmodified production kernels.cu with NVRTC. Execute its
pf_down, pf_up, and pf_discount_nodes, with original NC=169 and float32 arenas.
Only the first three lanes carry probability, 1/3 each. Assert the other lanes
retain zero regrets and strategy sums. This does not exercise production host
tree construction, value-slot aliasing, forced models, multiplayer leaves,
CUDA graphs, batching, Hold'em hand encoding, or the N15 network.

The separate fixture transfer kernel implements the full-precision learned
interface expression: opponent reach mass times compatible conditional mass /
entry legal mass, times (pot times predicted share minus investment). For this
game the entry legal mass is 2/3. Encode toy net values as (value+c)/(2c), with
pot=2c and investment=c. Shares may exceed [0,1]; no such clipping is valid.
Toy compatibility means unequal cards, not Hold'em combo counts.

## Checks and decision rules

Before registered end-to-end runs, check 24 random arena states for each layout,
including uniform/tiny regrets, and a 100-iteration serial full-tree run, against
an independent float32 alternating CPU reference. Absolute tolerance 1e-5 plus
relative tolerance 2e-6, including reaches, values, regrets and strategy sums.
For each leaf compare the transfer kernel to direct explicit-deal values.
Common leaf inputs isolate arithmetic from equilibrium-selection ties. Keep any
failed screen rather than silently weakening it. Smoke compilation may precede
registration; frozen source and protocol hashes establish the actual run.

Evaluate every checkpoint in the complete game using all 512 pure best responses
per player, cross-check against a separate recursive best response. Cutoff arms
receive fresh exact continuation policies at the averaged upper ranges; they
are not fully learned agents. Record predicted fixed-leaf internal gap separately.
Record elapsed time for audit only: Python launches and CPU LP calls make this
unsuitable for production performance comparisons.

Exact integration passes only if all three control arms have final full-game
NashConv <=0.005 chips. Prediction passes only if that gate passes, its own
NashConv <=0.005, and no more than 0.002 above plain exact cutoff. If controls
fail, retain results and run the declared prediction diagnostic, but do not
attribute its failure solely to prediction. No automatic extension or tuning.

Port 56708 and production code remain unchanged. Publish scripts, source hashes,
logs and results to GitHub; exclude compiled PTX and unrelated research artifacts.
