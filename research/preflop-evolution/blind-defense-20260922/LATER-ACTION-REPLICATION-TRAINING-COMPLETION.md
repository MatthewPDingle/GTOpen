# Second later-action training run completed

The second matched trial completed all 78 planned updates on September 25.
This is a training-completion milestone, not a range-quality finding. Its
full independent numerical audit and the complete-policy comparison remain
outstanding at this record's creation.

The storage interruption preserved 52 durable updates on T:. The unchanged
trial resumed from that checkpoint on S: and completed updates 53 through 78,
for 39,936 training deals in total. All 78 ordered metric references and the
final checkpoint hash were authenticated at completion. The configuration
matches the continuation registration; its two explicit history segments
retain the original evidence and the resumed evidence separately.

The independent reconstruction of the original 52-update prefix passed:
26,624 roots and 653,654 postflop targets were reconstructed. Maximum errors
were 3.64e-12 for root state, 5.69e-14 for targets, and 2.71e-12 for policy.
This prefix result is explicitly incomplete with respect to the planned
78-update training history. It is not a substitute for the full audit.

The continuation worker completed successfully in 3,811.594 seconds. Its
controller completed in 3,920.578 seconds, including waiting for the prefix
audit and final checks. These times cover the recovery execution, not the
original interrupted work or the entire study. The new S: store contains
8,812,174,344 logical bytes and 2,933,123,256 allocated bytes across 2,638
compressed files, including the imported checkpoint closure.

The recovered pipeline then launched the full 78-update independent audit
across T: and S:. The first trial's independent audit was still running.
Both full audits must pass before the unchanged full-bank control and fresh
65,536-deal comparison. No production deployment or accuracy claim follows
from this completion.

Evidence identities:

- Continuation registration: `53218960ebf31c91247466a15ff10a3437f42ea223d6cc35c4e96384fa13ff8e`.
- Continuation result: `65fcd4f69c6e7db21994b40c1db6e18d6f1a233d58da385e318fc7e182eabbad`.
- Continuation status: `740fc6ecd0712455abeecdfd012c98e48cb00606de9eaffad467852dc583c446`.
- Prefix independent review: `3b8f341287bfd2e3fd76790caedea72284ff220c804b18007c317c0653e8b523`.
- Prefix-audit admission: `c188264e152bbccbf53917923852bdbd34c6ef489bf42d2544d45b6245aeafcd`.
- Final checkpoint: `1ddc7936e7e08919e9991abf7d63a48c199a510865fc1a9c4ac779f8c89aac0f`.

The associated metadata uses the prefixes
`later-action-replication-volume-continuation-v1` and
`later-action-replication-storage-prefix-v1`. The original interrupted trial
and failed attempt remain preserved under their original identities.
