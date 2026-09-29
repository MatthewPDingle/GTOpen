# Complete private-hand all-in count coverage

The new cache covers every legal ordered pair of two-player starting hands:
1,624,350 physical pairs, represented by 93,769 suit-canonical keys. Player roles
are preserved. This removes a coverage limitation when deriving resources for
the retained stack-depth fixtures, whose declared incoming ranges are broader
than the original BB/BTN research context.

We reused 47,478 previously verified keys. Reversing the two players and swapping
wins/losses increased reusable coverage to 71,200 keys. Of the remaining 22,569
keys, 11,346 required new native exhaustive calculation; role reversal supplies
the remainder. Each calculation enumerates all 1,712,304 legal five-card boards.
No missing matchup receives an approximate or uniform-equity fallback.

The bounded run completed in 121.594 seconds using up to 12 single-thread native
workers. The summed native work time was 1,246.447 seconds; this is overlapping
work accounting, not a matched performance benchmark. Retained inputs, outputs
and counts occupy 19.7 MB logical and 8.33 MB allocated, all NTFS compressed.

The independent readback passed in 16.203 seconds. It checked full-universe
suit-orbit coverage, previously reviewed counts, every new native artifact,
explicit role reversal, and 22,692 sample-board winner checks. It did not repeat
the exhaustive enumeration. Main session 91955 and readback session 29115 both
exited successfully; neither may be retried or overwritten.

Registration SHA256:
`242663d663a66a530827efdf3e94fa1720228f6fbb05816d36023dce4658512b`

Cache SHA256:
`32c9225b3e500f72e5f670c8fd99a90eeeca104fb9178847c47d989e58553f87`

Files use prefix `stack-context-complete-allin-cache-v1`; the cache and retained
native outputs live in `S:\GTOpen-research\stack-context-complete-allin-cache-v1`.
The result is linked to `stack-context-complete-allin-cache-v1-readback.json` by
its exact hash. Use that successful proof, not merely the cache filename.

These are candidate-independent all-in counts. They are not a trained strategy,
postflop continuation values, multiway equities or evidence of better preflop
ranges. Context-specific ranges, pot, investments and rake still determine each
payoff matrix. Production 56708 was not modified.
