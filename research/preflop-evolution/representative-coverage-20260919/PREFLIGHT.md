# Representative-board feasibility preflight

Use the existing deterministic 47-flop report subset unchanged, with equal
board weights and all suit relabelings. The report sampler chooses systematic
midpoints of cumulative full-deck isomorphism mass; its output was checked
against the frozen 1,755 canonical list in the preceding coverage study.
Do not multiply these board weights by isomorphism counts a second time.

Before any connected strategy solve:

1. Verify no board overlaps the ten previously reserved development holdouts.
2. Preserve the frozen UTG/LJ subtree, entry support cutoff, rake, investments,
   stacks, and 50% bet / pot raise menu used by panel AB.
3. Use the read-only memory planner to measure per-board host-arena and GPU
   requirements. This does not enable any unvalidated symmetry bridge.
4. Record that pocket-pair flop-opportunity error is at most 4.284 percentage
   points in the preceding exact chance audit, versus 31.404 points for AB.
   This is not sufficient to establish strategy accuracy.
5. Preregister the eventual solve schedule, numerical accounting, convergence,
   and independent validation protocol after the engine's correctness and
   memory feasibility gates pass. No strategy result is produced by preflight.

This is a candidate larger reference set, not a production-model change.
