# Lossless board-state paging preflight

The 47-board plan exceeds 24 GB of device memory, even with future-card
symmetry. Its full F32 action arenas use 35.26 GB of system RAM, which fits
the observed 128 GB machine. Investigate lossless paging before a broad solve.

Keep this implementation research-only. Start with fully enumerated chance,
not the symmetry candidate whose abrupt-changing-range test remains failing.
Do not quantize, restart, renormalize or discard any regret/average state.
Each board retains its CPU solver and GPU metadata; one exclusive workspace
holds the current board's regrets, average sums, reaches and CFVs. Upload the
state, perform the existing eager continuation sweep, download changed state,
then release the workspace before switching boards. Synchronize explicitly
before buffers cross streams. Release per-board pinned transfer scratch.

Required gates before 47-board work:

1. Alternating two distinct tiny boards (different hand and arena dimensions)
   with changing reaches and zero-reach intervals reproduces each resident
   reference's returned CFVs and cumulative arenas bit for bit. Check both
   players, repeated switches, and an invalid-input rejection before mutation.
2. The two-board connected development game through 2,000 iterations agrees
   with its original fully enumerated unprojected reference: independently
   checked accounting, EV difference <0.0001 bb, root prior-weighted policy TV
   <0.0001. Require matching numerical updates, not merely a similar gap.
3. Record actual live RAM/VRAM, transfer volume and elapsed time on a short
   47-board allocation/iteration trial. Preserve at least 20 GB free host RAM
   and 3 GB free VRAM with the production app still resident. If this cannot
   fit, stop the owned trial and revisit metadata residency; never clear the
   user's production sessions.
4. Register the final iteration count/checkpoints only after estimating the
   duration from that trial. The existing report-47 manifest and reserved-board
   exclusion remain fixed. Report coverage limitations explicitly.

Only one GPU experiment may run at once. Preserve port 56708 and stop owned
research if production becomes active. Preserve each source/binary/input
freeze, including failed trials. No production deployment follows this work.
