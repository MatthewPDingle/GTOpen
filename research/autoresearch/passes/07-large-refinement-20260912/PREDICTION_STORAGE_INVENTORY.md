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

This first inventory did not allocate or train a predictive solver. The subsequent
exact-tree inventory and small numerical tests are now complete:

| Validated compressed representation | Bytes |
| --- | ---: |
| Terminal history | 1,827,007,264 |
| Selected policy | 1,059,801,028 |
| Terminal/traverser offsets | 25,780,480 |
| Total persistent extra storage | 2,912,588,772 |

Of 6,445,120 terminal/traverser entries, 3,764,723 are scalar and 2,680,397
require all 169 hands. Compression saves 2,504,113,376 bytes (46.23%) compared
with the dense terminal-plus-policy representation, and fits the 4 GiB cap.
The plan checks masks, terminal types, offsets and arithmetic overflow.
Small native GPU terminal values round-trip bit-exactly through this layout.
Large GPU allocation remains untested: convergence screening failed first.
See raw/predictive-storage-exact-v1.json, raw/predictive-storage-verified.json,
PREDICTIVE_NUMERICAL_PLAN.md and PREDICTIVE_RESULTS.md.
