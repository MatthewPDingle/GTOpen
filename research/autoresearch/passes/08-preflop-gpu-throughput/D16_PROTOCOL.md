# D16: learning-only empty scan dispatch

Registered before computing the lower bound. GPU preflop only; retained
C14/R03 control, port 56708 read-only, one run07-guarded workload at a time.

D15 rejected an unconditional shortcut: the large averaged policies have no
empty scan tiles. This proposal instead selects a separate writer for learning
evaluations only, before graph capture, and keeps the original check writer.
It does not reinterpret D15's failed gate or count a learning-only improvement
as solving the overall convergence problem.

A 169-class CDF scan uses six tiles (32,32,32,32,32,9). A distribution with K
strictly positive classes has at most min(K,6) nonempty tiles in any sample's
permutation, so at least max(0,6-K) tiles are empty. Sum this lower bound over
the preserved D10 distinct learning rows; reconcile counts with D11 and D15.
Independently enumerate all 64 tile masks for K=1..169, requiring at least one
positive class per selected tile and sufficient selected capacity. This proves
both the minimum and maximum empty counts without using sampled rank order.

Admission requires a guaranteed empty fraction >=20% on the large learning
fixture. If it fails, stop this distribution-independent screen; no automatic
budget extension. A pass admits a separately registered GPU prototype, not a
speed claim. Exact counts may exceed the lower bound, but must not be invented.
Both fixtures and all traversers are included. Hash source witnesses and the
protocol. Host screen cap180 seconds, no solve advancement or GPU allocation.

The possible implementation uses a warp-wide exact-zero vote to bypass the
five shuffle/add steps on an empty tile. Loads, votes, carry propagation and
output stores remain. No tiny-positive pruning, sample/order/precision changes,
shared staging, or changes to nonempty scan arithmetic. Signed zero,
subnormals, aliases, zero-mass recovery, partial batches and all output bits
require independent device qualification before complete-work timing. Dense
learning rows may lose time to the vote; checks must not pay that cost.

Any admitted runtime candidate still needs the established complete-work
first-pair screen, three alternating pairs per fixture, >=3% median large gain,
<=3% small regression, exact full state/roots/continuation/graph tests and full
default/native regressions. The overall tenfold target remains unachieved.
