# Next research after actual-policy river cost controls

Updated 2026-09-28. The actual-policy pilot and shared native batch comparison
are terminal. No live study process remains. The broader goal remains active.
Read RIVER-LEARNED-BATCH-FINDINGS.md first: it corrects the planned integration
against the actual trainer and records the unfavorable cost result.

## Evidence retained

- Broader exact training passed two fresh local gates: prediction error
  -16.28%, Fold/Call cost -36.28%. Mixed subgroups and a generalization gap
  remain. No full-preflop gain proven; BOARD-RIVER-DEAL-COVERAGE-REVIEW.md.
- Fixed-current-policy generation-77 pilot: 23/24 supported fixtures,
  including 18 supported zero-own-reach cases. CPU/GPU probability/value
  equivalence passed. Opponent private-hand variation dominated target noise
  in these reused fixtures; this is not a population-weighted estimate.
- Vector visible-summary preparation: 40,528 direct examples and 57,025 query
  rows byte-identical. Whole preparation 1.837x faster in that paired control.
- Native single-target substitution preserved visits and RNG in 24 engineering
  configurations. Ancestor value error <=3.56e-15 bb; finite-pair weight checks
  and seven malformed transports passed. Not learned-policy training.
- Actual-policy cost pilot: four old TRAIN deals x two last-played policies,
  67 river records supported, sampled-pair native values exactly matched.
  All 68 other postflop rows and 12 preflop rows retained. Measured generation
  stages cost 19.9819x baseline; this is not complete end-to-end training time.
- Shared native export: all eight paired cases passed with identical numeric
  values, plus five malformed request controls. 35.508 s -> 28.810 s, 1.2325x
  throughput gain. Whole experiment 101.80 s. Does not remove the large
  exhaustive-opponent cost. Both current controls were CPU-only; no fitting.

## Integration correction

The current board pipeline already replaces all positive postflop targets
with complete future-action expectations at the sampled private cards through
later_action_training_ingest_v1. Raw external-sampler targets are the wrong
baseline. A callback-walker result alone would be overwritten by that ingester.

Use a visited-river-only overlay; preserve its full-action flop/turn targets
and exact preflop/board-root overrides. Do not propagate replacements selected
by sampled visits into full-action ancestors without an unbiased-selection
proof. Source-deal weights attach once at original weighted ingestion and
fitting; they do not multiply the conditional target vector.

## Next bounded implementation

Avoid another large exhaustive run. Predeclare K=64 posterior opponent draws
per visited river target. Two stages: query all compatible pairs' actual
history probabilities, then expand future trees for only sampled pairs.
Posterior = entry weight times opponent history likelihood, normalized across
all compatible pairs. Include exact current-policy overrides. Draw with
replacement; share draws across hero actions and use the same strategy for
centering. No sparse self-normalized importance estimate or duplicate reach
factor. Preserve unsupported states explicitly.

Use retained complete exports to qualify exact posterior, visible query
closure, full legal actions and unbiased estimator moments before native
implementation. Measure demand first, then real elapsed cost; fewer rows alone
are not a speed claim. Existing exported trees provide independent references.
Then qualify the actual weighted-reservoir path and run bounded matched
training with fresh full-policy evaluation. Preserve insertion order/RNG and
all previous overrides. No broad quality claim from these reused TRAIN cases.

All executed/registered sources and existing results remain immutable. Version
corrections. Do not reuse spent final deals for tuning. Cross-stack/rake/sizing
coverage remains separate under STACK-CONTEXT-PLAN.md. Do not change production
or perform additional GitHub pushes, deletions, Jev work or app popups.

The 800 GB allocated research cap remains. Last inventory was 717.79 GB;
subsequent bounded evidence including these ~520 MB additions stays below
720 GB. Re-inventory before large admission. Light desktop/video GPU sharing
is authorized; qualified guard permits <65% utilization with 4 GB own budget,
2 GB external VRAM headroom and 24 GB free RAM. Heavy GPU workloads and active
production solves take priority. Latest probe was 100% GPU, so work remained
CPU-only. Always probe again before GPU work.
