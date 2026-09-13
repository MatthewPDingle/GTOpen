# GPU preflop throughput research

Latest: [C18 compact rank products](C18_RESULTS.md) was rejected: 43.67% slower
on complete large work despite exact outputs. Retained runtime restored.

[D13 exact rank reuse](D13_RESULTS.md) admits a compact-product GPU
prototype: about 56% less terminal source arithmetic before coordination costs.
[C18 protocol](C18_PROTOCOL.md) registers exactness and complete-timing gates.
No new runtime improvement is claimed.

[D12 partial-product inventory](D12_RESULTS.md) was rejected before a
GPU prototype: under 4% arithmetic and 2% logical traffic saved.
[D11 retained cost audit](D11_RESULTS.md) verifies that probability tables
and multiway evaluation consume 96-99% of large GPU work. No new speed point.

[C17 packed terminal warps](C17_RESULTS.md) was rejected after exact
qualification and a slower first pair. The retained runtime is restored.
[R03 normal-server qualification](R03_RESULTS.md) remains ready for a separate
56708 switch; no deployment occurred. [D09 writer screen](D09_RESULTS.md) was
rejected before timing. [C16 fused evaluator](C16_RESULTS.md) was rejected: 44.08% slower on the first
large timing pair. The retained runtime is restored.

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

- [C11 terminal L1-cache preference](C11_RESULTS.md): rejected; first large
  complete run 16.8% slower, with identical PTX, allocations and numerical outputs.
- [D07 proposal](D07_PROPOSAL.md): inventory whether a fixed terminal ordering
  improves probability-row locality before attempting another GPU change.
- [D07 locality inventory](D07_RESULTS.md): rejected before a GPU prototype;
  the large fixture had 2.80-2.82 times as many simulated misses. Independent
  witness verification matched; retained GPU runtime is unchanged.
- [C12 predicated probability scan](C12_RESULTS.md): rejected; exact outputs
  but only 0.16% less complete time, below the screening gate. C09 restored.

- [D08 compiler inspection](D08_RESULTS.md): hardware counters unavailable;
  independently audited linked assembly explains why the C12 PTX change was
  much smaller in native instructions. No new speed claim or deployment.

- [R01 rollout qualification](R01_RESULTS.md): automatic memory selection and
  normal-GPU fallback match both saved fixtures; 19 native GPU and 181 default
  regressions pass. Research-only; production integration remains.
- [C13 proposal](C13_PROPOSAL.md): bounded 32-bit CDF element indices to reduce
  terminal address arithmetic. Not implemented or measured.

- [C13 bounded element indices](C13_RESULTS.md): exact and 6.3% faster on large
  complete work, but rejected for 3.67% slower small complete work. C09 restored.
- [C14 protocol](C14_PROTOCOL.md): remove C13's duplicate module construction
  while preserving the same bounded arithmetic; not implemented or measured.

- [D10 bounded terminal tiles](D10_RESULTS.md): exact sharing inventory passes
  construction-work gates but exceeds the registered table-storage budget.
  Scheduling launch counts are also large; no GPU prototype admitted.

- [C17 packed terminal warps](C17_RESULTS.md): exact results but 167.39% slower
  on the first large timing pair. Candidate removed; retained runtime restored.

- [D14 warp-local rank sharing](D14_RESULTS.md): declined before GPU work.
  Removing duplicate lanes preserves every original warp arithmetic path and
  requested CDF sector in the fixed schedule. No measured speed improvement.

- [C19 interleaved CDF scans](C19_RESULTS.md): exactness passes, but the complete
  timing gain is only 0.27%, below the 1% screen. Integration removed.

- [D15 empty scan tiles](D15_RESULTS.md): the large averaged ranges have no
  zero tiles, rejecting a both-mode shortcut. Learning-only remains unqualified.

- [D16: conservative learning-only scan bound](D16_RESULTS.md): insufficient to admit a prototype.
- [D17: actual learning scan occupancy](D17_RESULTS.md): 33.64% empty large-learning tiles admits separate GPU qualification, not a speed claim.

- [C20: exact-zero scan bypass](C20_RESULTS.md): 1,008 exact GPU cases; rejected at compiler-cost gate before solver integration.

- [C21: sparse predicate scan](C21_RESULTS.md): fully exact, but first complete large timing is 0.89% slower; rejected and integration removed.
