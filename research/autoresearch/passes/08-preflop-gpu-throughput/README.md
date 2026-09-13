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
