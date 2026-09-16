# Ten-hour research closeout

Research window: 16 September 2026, 10:49:02–20:49:02 UTC.
Finalized: 2026-09-16T20:49:36.870033+00:00.

The timeboxed research effort is complete. **No candidate qualified for deployment.**
The best full predictor improved fresh-board hand-value estimates, but failed
practical settling and end-to-end performance requirements. The unchanged quarter
blend improved with extra iterations, yet still missed the 0.005 bb target at1500.
This completes the research window, not the broader ambition of a better solver.

## Verification and boundaries

- N38:53 frozen inputs,2 snapshots and cumulative learning work audited; all5 separate repair-provenance hashes verified. Final gap0.00791807 bb.
- N35:46 frozen inputs,4 snapshots and10,309 hand/action oracle values audited; practical screens failed. N36's conditional80-reference workload was correctly skipped.
- N37:2 tests and8 scans passed after an archived syntax repair;21 inputs and8 output hashes verified. Its deeper-range difference is a diagnostic lead, not proof of cause.
- Earlier CPU and21 GPU equivalence suites passed for the research binary; no solver-library changes followed those checks. Later changes added research examples, experiments and reporting.
- Production audit: port56708 remains PID2564, executable timestamp15 September05:11:57 UTC; realization-fit SHA256 remains3f3040ca917930fafa0c9ab8982c44d31513321f3e63d44f39b3d2157673bf18. GET health check succeeded; no research processes remain. See production-final-audit.json.
- Original failed attempts and separately frozen repairs are retained. N14/N16 standalone GPU runs were not performed; their status is explicit in the ledger. No hidden pending experiments remain.
- Raw experimental saves and compiled kernels stay local and out of Git. Experimental saves must not be loaded in the app.

The short [findings](SUMMARY.md), [detailed results](RESULTS.md), [graph](accuracy-and-settling.png)
and [proposed next investigation](NEXT-STEPS.md) provide the handoff. The overnight
monitor is being removed as part of closing this timebox. No deployment or fresh
research run is scheduled by this closeout.
