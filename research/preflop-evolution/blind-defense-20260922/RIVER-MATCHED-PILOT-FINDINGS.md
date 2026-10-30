# Matched river-training pilot: verified findings

Completed and independently read back on 28 September 2026. This is a small
integration and cost study in the existing 200 bb BB–BTN research context.
It does not establish improved preflop ranges or qualify a production model.

## What completed

Two independent training seeds each forked the same complete state at update 78
into baseline and candidate arms. Every arm completed updates 79 and 80. The
candidate changes only visited river training targets, averaging over 64 draws
from the modeled opponent's conditional hand distribution. Earlier street
targets, sampling, fitting settings and board-root updates remain matched.

The final evaluation used 1,024 fresh common physical deals, all eight fixed
player-replacement comparisons and the complete played-model banks 0–79.
The fitted but unplayed model 80 was excluded. No test outcomes were used to
change this run's training, sample count or registered statistical analysis.

Independent readback passed all 32 evaluation batches (465,149 observations),
complete checkpoint recovery, source-deal replay, archive identity, crossings
and payoff checks. Independently recomputed statistics differed by at most
2.78e-17. This is a separate readback using the qualified native protocol,
not a second poker engine or independent neural implementation.

## Result: no demonstrated playing-strength improvement

All eight prospectively registered confidence intervals include zero. Point
estimates are small and mixed across seeds: approximately -0.0028 to +0.0067 bb
per entry. Neither seat improves consistently in both independent runs.
The result supports no promotion, deployment or broad accuracy claim.

The registered conservative intervals are approximately +/-11.8 bb per entry,
far wider than the observed effects. This short study is not a sensitive test
of a small edge. It retains those intervals without substituting a favorable
post-hoc analysis. The shared-policy bound described in PAIRED-MIXTURE-BOUND.md
is prospective only and was not used to reinterpret these results.

## Learning propagation is working, but needs more rounds

Model 79's postflop networks change under the candidate treatment while both
initial preflop components remain identical. In model 80, the initial BB policy
changes by 1.27% and 1.02% entry-weighted total variation in seeds A and B; the
largest individual action-probability changes are 14.37 and 13.07 percentage
points. The exact BTN first-shove response remains identical at this boundary.
These are changes, not evidence that the new decisions are better.

Model 80 has not played and is excluded from evaluation. Only model 79 differs
in the evaluated bank, contributing 2.469% of its unconditional mixture weight.
Every evaluated initial BB policy and exact BTN first-shove response is still
paired-identical. At least four new updates from boundary 78 are needed for
both changed initial preflop components to enter the played bank, if their
numerical policies change. A substantive comparison needs longer training.

## Measured learning cost

| Seed | Baseline: two updates | Candidate: two updates | Candidate / baseline |
| --- | ---: | ---: | ---: |
| A | 122.532 s | 482.250 s | 3.94x |
| B | 112.422 s | 535.578 s | 4.76x |

The baseline averages roughly 56–61 seconds per update; the candidate takes
235–282 seconds. Candidate physical-target generation is the dominant stage.
These are single sequential continuations, not a statistically established
runtime benchmark. Across the resumed pilot invocation, reported competing-GPU
wait totaled only 4.67 seconds. Light desktop sharing is no longer causing
substantial idle waits in this run.

Restart qualification was kept outside learning cost. The successful recovery
replay/readback took 297.546 seconds; the earlier completed qualification update
took 366.141 seconds. Total earlier incomplete-attempt cost was not retained
precisely and is not reconstructed. The completed study occupies 1.989 GB of
allocated storage (4.873 GB logical), preserving its partial attempts.

## Next work

1. Finish the now-started complete-update four/eight-worker check. Its prior
   32-task fixture check passed exactly, but full-update speed and checkpoint
   equality are still pending. Every case replays existing source state 78;
   none extends the scientific training bank or consumes fresh test deals.
2. Use actual runtime and storage evidence to register a longer matched
   continuation, provisionally 16–32 updates from source boundary 78. The
   current mixed result does not select a favorable seed, seat or test subset.
   Choose evaluation sensitivity and cost explicitly before fresh test draws.
3. Reuse the previously qualified shared-input evaluator in that future run.
   Its current core-source hashes match the original GPU control and board-bank
   control registrations, with successful independent readbacks. This avoids
   rebuilding identical inputs for all four banks. Do not use the still
   unqualified JSON-snapshot evaluator merely because it is prepared.
4. Assess equal-time quality, then additional stack/rake/sizing contexts before
   claiming robust preflop improvement. A candidate that learns more slowly
   must earn its extra computational cost.

Production and the active application were not changed. No additional GitHub
push or historical evidence deletion was performed.

## Evidence

- river-matched-training-pilot-v1-result.json
- river-matched-training-pilot-v1-independent-review-v2.json
- river-matched-training-pilot-v1-review-v2-registration.json
- river-matched-training-pilot-v1-execution-v2-registration.json
- RIVER-PILOT-INTERPRETATION.md and RIVER-PILOT-WAIT-RECOVERY.md
- EIGHT-WORKER-FULL-UPDATE-PLAN.md
- shared-query-gpu-control-v1-result.json and independent-review.json
- board-complete-evaluation-control-v1-result.json and independent-review.json

The broader research goal remains active and incomplete.
