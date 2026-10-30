# Independent source-only critique received

Reviewer: `/root/model_evidence_review`, collaborating agent. These messages were received during the D027 audit. No edits, builds or GPU jobs were performed by that reviewer for this critique.

Initial proposal:

> D027 proposed actor-only down list is source-feasible with no evident dependency/lock blocker: down_action writes only actor reach and nh_actor==0 skips every write in locked and unlocked branches (kernels.cu:47–91). Nodes at a level already execute as unordered independent CTAs, so stable per-actor filtering changes no per-node hand/action arithmetic; keep original aggregate list byte-identical for full-down/eval/up. Reuse0 must select actor1 and reuse1 actor0; chance edges still run with current zero-hand gating. New device list must be immutable and allocated/uploaded before capture, owned per GpuSolver and never workspace-swapped. Main obligations: verify partition union/disjointness, level membership/order, canonical visitation under iso/full layouts; preserve 3 graph variant selection/invalidation; include added payload in continuation_capacity metadata+observed_metadata and host spans, plus admission accounting. This is real extra allocation/upload/init cost, so assess full cycle. No unacceptable mathematical proof gap identified; runtime exact raw reach/arena tests remain required. I have not edited or executed anything.

All-uniform conditional allocation refinement:

> That conditional allocation is sensible: require proof that every nonempty original action span is single-actor before using its starts in the fallback, then give the other actor an empty span. Mixed-plan spans must all index the separate list consistently; do not mix original and partitioned starts for one pointer. Empty levels/no-action trees need valid zero spans without indexing a missing first node. Capacity observed/estimated accounting should handle Option None exactly. This avoids river's added device allocation but retains host planning/branch overhead, so retain river as a regression control. No additional blocker from this refinement.
