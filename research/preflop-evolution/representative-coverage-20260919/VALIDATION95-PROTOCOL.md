# Independent larger validation panel

Registered before any strategic result on the original ten reserved boards,
the 47-board reference, or this new panel. Keep the original reserved panel
unchanged as a stress test. Its board identities contain no aces or nines;
that known chance-coverage limitation makes it inadequate as the sole test.

Freeze one 95-board panel using randomized systematic probability-proportional-
to-isomorphism-mass sampling, with equal sampled-board weights. Use the
existing canonical list order. Exclude the complete suit orbits of the
47-board training candidate, the old two development boards, panels A/B,
and the original ten reserved boards. Report the excluded physical flop
mass: the sampling population is the remaining canonical flops, not the
entire deck. Do not silently claim full-deck unbiasedness after exclusion.

Set the one systematic offset to the first eight SHA256 bytes (big-endian,
divided by 2^64) of `independent-systematic-95-20260919-v1`. For total eligible
physical mass M, select the boards containing positions (i+offset)*M/95,
i=0..94, in cumulative isomorphism mass. Keep all suit relabelings and the
same 50% bet / pot raise menu. No retry with different seeds, board swapping,
weight fitting or strategy-based selection is permitted.

Record exact structural metadata and pocket-pair opportunity comparisons
against both the full and eligible populations. Those are chance diagnostics,
not strategy outcomes or a reason to choose a more favorable sample.

Evaluate the same frozen source policies as in HOLDOUT-PROTOCOL.md after
implementation controls and runtime preflight. The one randomized systematic
panel has correlated selections; do not present naive independent-board
standard errors or a single-panel precise full-deck exploitability claim.
Keep its strategic results reserved until the candidate policies are frozen.
