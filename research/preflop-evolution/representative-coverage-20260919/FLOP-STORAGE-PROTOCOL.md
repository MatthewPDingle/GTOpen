# Bounded full-flop storage screen

19 September 2026. Separate CPU-only feasibility work. The running reference,
frozen inputs, held-out panels and production app remain untouched.

Generate fixed-range full-flop CFR+ F32 states on 5c2h2d (pot39.5, stack182)
and AcQd9d (pot93.5, stack155). Both are existing development boards. The
first is the largest full-arena case in the 50/75 menu plan; the second
adds a high two-tone board and the other pot. Selection uses no solved
strategies or held-out outcomes. Use the registered supported entry hands,
uniform weights on that support, 50/75 bets and donks, pot raises, one raise
per street, 4% rake capped at6, no future-card isomorphism.

Save raw states at iterations1,100,1000, retaining incomplete checkpoints if
the run stops. Apply the unchanged fast codec screen only after all six
states exist. Verify all decoded bytes and preserve original arena hashes.
Measure LZ4 and Zstandard, with and without byte shuffle, and raw baseline,
using 1MiB blocks and raw fallback. Record times as concurrent single-pass
observations, not isolated performance rankings.

Limits: two CPU threads; one hour total including codec screen; node cap2M;
individual arena bytes below2GB; retain20GB free host RAM and50GB free disk.
Stop only this owned child if production becomes active, any probe fails,
or a limit is reached. Use a separate build target and output directory.
No CUDA work, app writes, overwrites of earlier evidence or user saves.

This is storage characterization, not a convergence or strategy evaluation.
It does not test evolving externally supplied ranges or native compressed
paging. No result here alone clears the larger47-flop betting menu to run.
