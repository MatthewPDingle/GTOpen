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
- [C05: aligned writes](C05_RESULTS.md): rejected;9.49% slower on the first
  large pair. Both CDF construction and terminal evaluation regressed.
- [D04 proposal](D04_PROPOSAL.md): measure cross-player distribution reuse
  during accuracy checks before implementing shared evaluation.
- [D04 pair inventory](D04_RESULTS.md): rejected; about 21% check-table reuse
  falls short of the registered 25% admission threshold.
- [D05 wider-group inventory](D05_RESULTS.md): admitted a prototype based on
  exact reuse and complete allocation accounting.
- [C06 larger shared groups](C06_RESULTS.md): rejected; 41.1% slower despite
  identical results. Its memory footprint was much larger.
- [C07 bounded shared groups](C07_RESULTS.md): retained; 7.7% less complete
  large-game time versus C01, with 13.4% faster checks. All paired results and
  required regressions match. The dashboard shows about 11.4% cumulative less
  time from C01 and C07; neither is deployed to port 56708.
- [D06 retained-version profile](D06_RESULTS.md): terminal evaluation consumes
  about 64% of large checks and 54% of learning; scratch restoration is negligible.
- [C08 cooperative terminal reads](C08_RESULTS.md): rejected; 22.6% slower
  despite exact numerical results and unchanged global allocations.
- [C09 proposal](C09_PROPOSAL.md): test partial sample-loop unrolling, retaining
  the same sequential arithmetic and validating odd/partial sample counts.

- [C09 partial sample-loop unrolling](C09_RESULTS.md): retained; another 4.2%
  less large complete time versus C07, identical outputs and full regressions.
  Small complete median +1.8%; no deployment.
- [C10 proposal](C10_PROPOSAL.md): compare factor-four unrolling against C09,
  with all remainder classes tested before timing. Not implemented or measured.

- [C10 factor-four unrolling](C10_RESULTS.md): rejected; median 1.47% large
  gain below the 3% gate. Exact outputs; C09 restored.
- [C11 proposal](C11_PROPOSAL.md): test terminal L1-cache preference alone,
  keeping C09 PTX, samples and allocations. Not implemented or measured.
