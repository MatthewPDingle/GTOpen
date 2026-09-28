# Actual-current-policy river target cost pilot

Prepared before execution, 2026-09-28. Code inspection found that the existing
trainer already replaces all positive postflop targets with complete future-
action expectations at the sampled private cards. The native sampled-walker
control is therefore insufficient as the performance or ingestion baseline.

This pilot uses the first four old TRAIN selection deals, 000-003, in original
order. No final/evaluation deals or labels select this test. Use generation 77
from each of the two previously registered played-policy arms. Preserve all
preflop table, exact BTN, board-root overrides, original source identities and
the complete private-pair all-in cache. Policy inference is CPU float64 widened
from the unchanged float32 weights; the GPU is occupied by another workload.
Report these as CPU measurements, not estimates of GPU speed or a solver win.

For each deal/model, rebuild the format-3 native queries, infer the current
policy, verify the unchanged native sampler, and generate the current trainer's
full-action trace. Validate its targets with the existing postflop replacement
reader. Keep all original visits and all preflop/initial targets. Use action
seeds 9282901+deal index, paired between the two policies.

Discover all positive-tag river visits, in native visit order. For every unique
visible key, export the complete conditional river tree over all 990 legal
opponent pairs. Export up to four independent targets concurrently; CPU workers
yield to production solves and low free RAM. Cap this pilot at 128 unique
target exports and 512 MB retained evidence; exceeding either is a reported
feasibility failure, not silent target truncation.

Group query work by visible key and remap each real own-history reference.
For every union slice, require the complete prepared features/arrays and action
probabilities to match independently prepared original documents and unchanged
single-model CPU inference (probability tolerance 1e-10, identical legal support).
No table, policy smoothing, rank representation or input visibility changes.

Compute exact full action vectors under that same policy for histories and
future decisions. The actual sampled opponent's physical hand is mapped into
the target's canonical suit labeling; its pair-conditional values must match
the existing native full-action trace within 1e-8 bb. This ensures the comparator
is the trainer actually in use. Zero-opponent-support targets are explicit;
a positive-source-weight sampled visit with zero support is a failure.

Derive an overlay for the original visited river training rows only, retaining
the existing future-action integration for every flop/turn target. No ancestor
targets are replaced in this pilot: selecting private-hand-integrated targets
using sampled visits and then inserting those into an all-action trace would
require a separate unbiased-selection proof. Do not quietly replace the current
trainer by the older sampled-target baseline. This is an incremental experiment
in removing private-hand noise, not a narrower definition of the research goal.

Check all new regrets use one common current-policy baseline; preserve visit
keys, action arities and insertion order. Source-deal weights must remain
outside the target values and are not fitted or changed in this pilot.
Measure baseline queries/inference/sampling/trace and extra export, union,
preparation/inference and value calculation separately. Retain per-case counts,
unsupported states, all timing observations, source/binary/model hashes and
probability/target evidence. No quality gate or hyperparameter is chosen from
these reused cases. A lower-noise label alone does not prove faster training.

Maximum 900 seconds, each native process <=60 seconds; own memory <16 GB and
free RAM >=24 GB. Up to four native CPU export workers, one BLAS thread per
process. No GPU, model fitting, production changes, archive deletion, GitHub
push or edits to executed sources. Register before execution and preserve any
failure. The preceding 717.79 GB allocation plus all recent bounded artifacts
and this 512 MB allowance remains below the global 800 GB research cap.
