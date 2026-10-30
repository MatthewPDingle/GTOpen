# Richer betting-menu feasibility

This is CPU-only planning, not a new strategic experiment. The existing
`continuation_orbit_memory` executable was reused with the same entering
support, 47 boards, two called pots, stacks, rake, pot-sized raises and one
raise per street. Only the planning copy's bet/donk menu changes from 50% to
50% / 75% on all streets for both players. Tonight's registered solve is
unchanged.

The planner built all 94 continuations within its existing two-million-node
cap. It allocated no solver regret/strategy arenas and no CUDA buffers.
Planning finished in 39.4 seconds on two CPU threads while the reference
was running. That is not an isolated performance benchmark or a solve time.

| Storage quantity | 50% bets | 50% / 75% bets |
|---|---:|---:|
| Full F32 regret and average-strategy arrays, all 94 continuations | 35.26 GB | 97.39 GB |
| Largest individual continuation's unprojected buffer plan | 1.47 GB | 4.39 GB |
| Packed arena plan with future-card suit reuse | 26.50 GB | 73.20 GB |

Units are decimal GB. The first row is a lower bound on host storage for
the current paged implementation: it excludes trees, board evaluations,
metadata, scratch space and the production app. The individual-buffer row
is not the total GPU requirement: the shared workspace can combine maxima
from different boards, and per-board metadata also remains resident.

The current long run left approximately 64.9 GB host RAM free during this
check. Replacing its 35.26 GB action arrays with 97.39 GB would consume
another 62.13 GB, before growth in other structures. This cannot preserve
the registered 20 GB free-host reserve. **Do not launch the broader menu
with the current all-board host allocation.** Actual resources must be
checked again before any future run; these figures are not a permanent
machine-capacity guarantee.

Future-card suit reuse is a planning alternative, not a qualified remedy.
The current host solver still keeps full arrays even when GPU arenas are
packed, and the separate compact bridge retains a failed abrupt-range-change
stress test. Its lower planned storage does not authorize using it here.

The next implementation question is whether state can be stored more
compactly while preserving the connected game's updates and evaluation.
Lossless storage or a correctly validated compact representation would
address capacity; each needs its own parity, resource and timing checks.
Sampling fewer updates is another algorithmic research question, with
different convergence and variance requirements. Neither is implemented by
this planning check, and using fewer boards alone would not satisfy the
broader coverage objective.

Independent transfer of the current 47-board policy remains the next
strategic gate. If that fails, retain the outcome and investigate the
source of the failure before expanding the action menu. No current
threshold, reserved panel or production policy is changed.

Inputs and executable hashes: [planning freeze](menu50-75-planning-freeze.json).
Raw results: [memory plan](menu50-75-memory-plan.json) and
[completion status](menu50-75-planning-status.json).
