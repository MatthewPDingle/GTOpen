# Prediction storage: first bounds

Derived from the verified 1,567,754-node save comparison and its engine log;
input hashes and exact arithmetic are in raw/prediction-storage-inventory-v1.json.
These are allocation bounds, not measured predictive-engine memory use.

| Candidate persistent representation | Bytes |
| --- | ---: |
| One f32 per action/hand entry | 1,059,801,028 |
| Two such arrays | 2,119,602,056 |
| Every terminal, every hand, all eight traversers | 4,356,901,120 |
| Dense terminals plus an action-policy array | 5,416,702,148 |

The fixture has 805,640 terminals, 169 hand classes and 264,950,257 action
entries. Dense per-traverser terminal predictions alone exceed the earlier
4 GiB extra-storage screening budget. A full allocation must not be assumed
cheap just because the previous regret-matching+ baseline added no arrays.

ValuePlan::build in gpu.rs preserves terminal slots within a traversal but
reuses action slots across alternating depths. Subsequent traversers overwrite
the terminal values too. Retaining last iteration's predictions requires
dedicated storage or an explicitly validated reconstruction.

Before a predictive implementation, inventory hand-dependent live-player
terminal entries separately from terminal values that can be represented by
one scalar. Any compression must match all per-hand predicted values. Then
register prediction timing and the complete device budget, including policy,
terminal history, maps and scratch. The paper's descendant-strategy prediction
order must be tested independently; an action-array byte count does not prove
that simply retaining the previous regret increment implements that method.

No predictive training run or allocation has been started by this inventory.
