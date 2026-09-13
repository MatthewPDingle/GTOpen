# Predictive RM+ implementation and storage prerequisites

Registered before execution. No learning performance acceptance or deployment.
GPU preflop only; independent host arithmetic and read-only geometry are
correctness work. Serial run07 busy guard protects port 56708.

Reference: https://arxiv.org/html/2007.14358 Algorithm 5 and Appendix F.
Payoff sign convention: theta = max(0, z + predicted_Q - dot(old_policy,
predicted_Q)); normalize theta (native 1e-12 floor/uniform fallback). Prediction
uses each traverser's previous observed counterfactual terminal values, rolled
up bottom-up through newly selected descendant policies. Other-actor nodes
sum children because opponent reach is already included in terminal values.
After selecting p's whole policy: native down/terminal evaluation using all
players' most recently selected policies; save p's terminal history; then
z = max(0, z + observed_Q - dot(selected_policy, observed_Q)). No reach division
or regret discount. Average accumulation uses selected policy and native own
reach; end-of-iteration discount (t/(t+1))^2 gives quadratic averaging. Prediction
initially zero. A zero-prediction switch is a separate arithmetic control.

History compression: KIND_POT_SHARE with traverser live stores 169 floats;
fold-win terminals and folded traversers store one. Separate offsets for every
terminal/traverser. Dedicated policy array; no reliance on reused action value
scratch. Preserve constrained policies. Native average/BR evaluation bypasses
all prediction storage and does not modify it. Fresh zero learning histories
only; no reinterpretation of resumed saves or combination with other update
experiments. Sampling and optional pair correction configured before admission.

Storage prerequisite: inspect the exact large saved fixture without learning or
GPU allocation (180-second cap). Count all offsets, scalar/vector entries,
policy and mapping arrays. Entire persistent extra allocation must fit 4 GiB;
reject before allocation if it does not. Geometry map must reject overflow.

Numerical prerequisites, 600 seconds per test process: compare compressed
store/load to dense observed terminal values for every hand and traverser;
independent full-node host recursion must match prediction, observed regret and
average updates across four alternating iterations. Include raw/calibrated HU,
full 1024 and pair-corrected 64 samples, a frozen seat, a nonzero forced policy,
zero prediction, changing descendants, and zero-mass branches. Tolerances:
2e-5*(1+abs(reference)) for values/history/regrets, 2e-4 for probabilities.
Check eager/captured equality, admission refusals, and read-only native GPU/CPU
evaluation (0.005 bb). No model/terminal payoff changes or learned range model.

Run default solver and native GPU equivalence suites before publication.
Any convergence screen requires its own registered seeds, caps and unchanged
global-plus-conditional gates after these prerequisites pass.
