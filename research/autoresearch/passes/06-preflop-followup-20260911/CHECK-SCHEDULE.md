# Full-check scheduling screen

The existing GPU evaluation already shares terminal calculations between best
response and average EV. There is no duplicate terminal pass to remove there.
Full 1,024-particle checks consume roughly a quarter of the sampled eight-player
run. Test scheduling overhead independently from learning changes.

Register `coarse_then_fine`: check every 100 iterations initially. Once a full
check finds total learning gap <= 0.02 bb (four times the 0.005 target), check
every 50 for the remainder. Still require two consecutive full checks <= 0.005,
never claim convergence from sampled checks, always check at the iteration cap.

After Phase C and conditional-refinement validation finish, rebuild the benchmark
and run eight-player gamma15 / 64 samples / seed42 with this schedule. Compare
to the fixed-50 trial with exactly that seed, sampling and averaging schedule.
Also run a fixed-50 small-fixture control with the rebuilt executable to verify
the default scheduling behavior retains identical learned arenas. Audit the
resulting candidate with the same six-path local evaluator. Record actual
end-to-end time rather than subtracting hypothetical skipped-check time.
