# Particle-count discriminator with combined quality gates (v1)

Motivation: the fixed-unit branch continuation screen was rejected. Additional
read-only audits found that earlier sampled dynamic-normalization runs passed
4/6 and 5/6 conditional paths despite failing the global gap limit. Their
controls stopped on a global-only gate and passed 2/6, so those prior times
were not measured at equal conditional quality. This experiment tests whether
removing particle subsampling changes that outcome; it does not accept the
optimizer or extend its original 1,000-iteration ceiling.

Use the unchanged six-solver.json (23,038 nodes, all six seats learning),
canonical coupled_deck_v1 and gamma15 schedule/horizon 1,000. Fresh histories.
Cases, serially: 64 particles, seeds 42 and 314159, normalization off/on for
each seed; then 1,024 particles, seed 42, normalization off/on. Full-particle
learning is deterministic under the fixed deck, so another RNG seed would
not constitute an independent full-particle trial. No CV, exploration,
pruning change, warm start, branch refinement or altered payoffs.

At every 25 iterations, up to 1,000: full 1,024-particle native global check
and all six paths from exploration-diagnostic-paths.json, conditioned before
CPU reference evaluation. Copy current device histories for reference checks;
CPU work is correctness only. Record all per-hand action values/probabilities.
Require finite, nonnegative six-seat gaps summing to <=0.005 bb and all six
conditional gates (0.1-bb inferior action, <=0.1 bad-action probability, relevant
hand mass >=0.0025). Unreachable paths fail. Stop only after two consecutive
combined passes; otherwise finish at 1,000. Both controls and candidates obey
the same gate. No threshold or iteration-cap adaptation after seeing results.

Report end-to-end runtime including GPU setup, publication, checks and save
validation; distinguish learning time. Full sampling is a diagnostic reference,
not itself a promised speed improvement. Advance no large experiment unless
a mode actually qualifies on combined quality. If normalization with all
particles qualifies while its sampled counterpart does not, investigate
variance under the actual conditional nodes; if full normalization still
fails, report that subsampling removal was insufficient. Any future speed
ranking must compare qualified outputs at the same gate.

run07 records source/executable/input SHA-256 and guards live user work on
port 56708. One workload at a time, 900-second process cap per case. Final
saves get separate conditioned audits and exact arena roundtrip checks.
