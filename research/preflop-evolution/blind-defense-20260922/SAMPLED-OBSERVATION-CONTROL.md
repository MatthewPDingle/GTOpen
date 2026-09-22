# Physical-poker inputs for a future learned continuation

Status: observable-input and legal-action checks passed. No network has been
trained on these inputs yet. This does not qualify a BB strategy or change the
production application or experimental range viewer.

The sampled poker traversal already retained exact private cards and public
history. A learned model needs those observations as numbers, without seeing
the opponent's private cards or future board cards. This encoder supplies 269
binary features for the registered BB/BTN subtree:

- Both private cards and each visible board card, with explicit unknown slots.
- Acting player, street, and preflop decision or postflop continuation branch.
- The complete public action history, including street changes.

Ranks and suits remain separate, flop listing order is irrelevant, and turn
and river retain their order. The encoding has an exact inverse to its
canonical observation key. It does not place strategically different hands in
strength buckets or discard low-frequency starting hands. Pot, remaining
stacks and legal action amounts are recoverable from the fixed context and
history; they are not additional learned or guessed inputs.

Global suit names are canonicalized by considering all 24 relabelings. This is
appropriate for this fixed experiment's class-only incoming ranges and uniformly
permuted suit law. It is not automatically valid for suit-specific locked
ranges. Model artifacts must bind the context hash: node IDs and history tokens
cannot be reused under a different tree without a new qualification.

## Completed checks

- 455 public decision templates, sampled with 16 physical deals each: 7,280
  observations round-trip exactly and reconstruct the correct legal-action count.
- 174,720 global suit relabelings preserve the features exactly.
- Changing opponents' cards and hidden runouts preserves every tested input.
- Private-card order and flop listing order preserve inputs; swapping distinct
  turn/river ranks changes river inputs.
- All 1,326 physical starting hands are represented, with 169 distinct canonical
  starting classes before public cards are dealt.
- 604 malformed/illegal-input controls reject invalid cards, duplicates,
  premature board information, invalid action histories, actor mismatches,
  bad feature padding and terminal policy queries.
- A separately written Python encoder agrees on all 40 exported golden
  observations. Eight frozen input hashes remained unchanged.

Evidence uses `sampled-observation-v1`. The CPU check took 0.22 seconds including
launch and independent checks; it is a correctness control, not an inference
throughput benchmark. The next integration step is to connect these observable
features and legal masks to learned policy inference, then verify complete
sampled updates against a scalar reference. Actual poker training still waits
on an acceptable learning method and a registered evaluation plan.
