# Exact-response runtime and averaging control

23 September 2026. The separate version-4 policy can now be evaluated as an
individual model or an ordered played-model bank. It composes the exact BTN
response table with the existing base tables before policy use and own-history
averaging. The bank requires an explicit completed-iteration count; missing,
reordered or extra unplayed models are rejected.

The CPU control used the same historical base/synthetic exact-state fixtures
as the checkpoint control. In 7,276 real native query rows, individual model
probabilities matched their exact states at the 14 response rows and preserved
all other base probabilities. Generation zero preserved the entire uniform
base policy. Neural scores and base-table coverage were also unchanged.

Both equal weights and linear weights 1,2,3,4 matched the closed-form response
average exactly. This is a first-own-action decision: its own-history reach is
one, so average-policy weights do not include opponent shove reach. Opponent
reach belongs in the exact regret updates, as checked separately. All 7,262
nonresponse rows and their own-history averaging weights matched the base bank
exactly. An impossible own-action history at the initial response was rejected.

A CUDA wrapper is implemented but has not been executed or qualified. No GPU
work was launched alongside the fixed wider evaluation. It needs explicit
single-model/bank CPU-CUDA parity and native integration checks once the GPU is
available. The BB target correction, actual frozen-policy update wiring, and
a small complete training/restart/replay trial also remain. These fixtures are
not jointly trained candidate models and supply no new poker-strength result.

Evidence: `exact-initial-policy-cpu-control-v1-{registration,result}.json`.
