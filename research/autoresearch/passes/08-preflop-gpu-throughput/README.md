# GPU preflop throughput research

The loop changes one GPU mechanism at a time, checks solver equivalence, then
keeps only repeatable complete-work speed gains. Production stays unchanged.

- [Experiment rules](program.md)
- [Live dashboard and progress graph](DASHBOARD.md): http://127.0.0.1:56709
- [D01: duplicate-work inventory](D01_RESULTS.md)
- [C01: exact CDF reuse results](C01_RESULTS.md): retained; 4.0% less complete
  large-game runtime, 10.2% less warm-iteration time, exact paired outputs.

Raw records include failed trials, hashes, timings and regression output.
The broader quality/convergence requirements from pass 07 still apply; these
throughput results do not establish full convergence or a tenfold gain.

- [D02: sparse distribution screen](D02_RESULTS.md): rejected; only 5.63%
  of remaining large-game current distributions qualify.

- [C02: active terminal queue](C02_RESULTS.md): rejected, 16.6% slower than C01.

- [C03: no-tie product reuse](C03_RESULTS.md): rejected, 1.87% large gain below
  the 3% retention threshold.
- [C04: lossless CDF compression](C04_RESULTS.md): rejected; 96.1% slower
  on the first large pair despite exact numerical agreement.
- [D03: GPU time breakdown](D03_RESULTS.md): CDF construction is about43%
  of large iteration time; terminal evaluation is about54%. Exact outputs verified.
- [C05 proposal](C05_PROPOSAL.md): align first-prefix stores while preserving
  direct reads, numerical output and sample grouping. Not implemented yet.
