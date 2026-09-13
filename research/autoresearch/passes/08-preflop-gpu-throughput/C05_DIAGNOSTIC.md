# C05 follow-up diagnosis

The first large pair failed admission: complete runtime was9.49% slower.
C05 is rejected; there will be no extended retention pairs or full regression
qualification for this candidate.

One bounded eager control/candidate phase comparison will answer a different
question: did aligned stores help CDF construction but harm terminal reads, or
did both regress? This selects whether a lower-footprint aligned alternative
is worth testing. It cannot overturn the rejection or establish a speed gain.

Use the exact prefix/full-solver-tested executable and sources, the same frozen
large input, six learning/check rounds, two warmups, and the existing D03 event
hooks. Compare all checkpoint results and final arena fingerprints, account for
phase counts, and label these outputs diagnostic so they do not enter the graph.
No source changes/builds during the two serial runs. Cap180s each; run07 guard.
