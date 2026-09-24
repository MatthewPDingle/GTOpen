# Proposed matched training experiment: integrate root action paths

Prepared after ROOT-ACTION-NOISE-FINDINGS.md. No candidate training has started.
This document states the experiment to implement and admit; it is not evidence
that the controls below have passed or that any run is active.

## Change one root estimator

Start from fresh uniform policies in the same fixed BB-versus-BTN 2 bb open,
200 bb, 5%-rake/cap-2 scenario. Keep the exact initial BTN response, exact initial
BB jam target, all-sampled root accumulation, network architecture, reservoirs,
fitting schedule, feature representation, tree, inference precision, physical
chance law and output averaging of the preceding root-retention trials.

Change only the BB root accumulator's call/raise targets: use conditional
expectations over the existing complete current-policy action table on each
sampled physical deal. Do not perform new network inference or draw action RNG
values for this deterministic root integration. Keep original external-sampling
records and reservoir insertions unchanged, including their root rows, to isolate
the direct root-policy change from a shared-network training change. Retain
original and newly derived root targets for audit under different formats.

Introduce an explicit new model/checkpoint type. Never reinterpret or overwrite
old root-retained checkpoints. Keep complete source, input, policy, raw-target,
derived-target and checkpoint identities. Checkpoint publication must occur only
after both player fits and all root/BTN updates are complete.

## Controls before a full run

- Complete the separately typed accumulator, policy composition and checkpoint
  reader/writer; reject old or mismatched estimator metadata.
- Two updates on separate control seeds, with CPU/CUDA policy agreement, native
  forward/reverse accounting, independently reconstructed integrated root values,
  unchanged exact-jam replacement and centered advantages.
- Reconstruct original reservoir insertion order and state from unmodified raw
  external-sampling records. No integrated targets may silently enter that stream.
- Verify uninterrupted versus checkpoint-resumed next update: physical deals,
  action RNG, reservoirs, fit seeds, weights, root sums and checkpoint identities.
- Measure actual additional time and compressed allocation, including serialization
  and full files. Preserve failures; do not extend control budgets or retry silently.

Control limit: two updates, 30 minutes, 3 GB allocated / 10 GB logical outputs.
Use the shared exclusive research lock and production-idle guard. Freeze the
controller, reviewer, seeds and hashes before executing the control.

## Matched trial, conditional on admission

Run two fresh trials in the original predeclared seed order. Reuse the original
first-run training seeds (sampler 121301, action 121302, reservoirs 121303/121304,
fit base 121305), then replication seeds 357301 through 357305. These are
deliberately matched training comparisons, not new unseen validation seeds.
No model, fit hyperparameter or seed is selected using the already inspected
holdouts or chart appearance.

Each trial remains 78 updates of 8 x 64 physical deals; 512 fit steps/player/update,
262,144-row reservoirs, 302/64/64/4 architecture, chunk 4,096, learning rate .003,
float64 inference and float32 fitting. Use all played generations 0-77 with
linear weights 1-78 for the primary comparison; exclude generation 78. Report
all four equal/linear endpoint pairings without selecting the most favorable.

Prospective per-trial maximum: 6 hours training, 2 hours full readback,
12 GB allocated / 40 GB logical files. Before each trial, remeasure all research
roots and require the complete new-store allowance plus 2 GB reserve to fit the
800 GB combined limit. Require 40 GB free on T:, 20 GB available RAM and 3 GB
available GPU memory. Only one research GPU job at a time; never disrupt 56708.
These caps are not admission until the short control establishes feasibility.

## Interpretation

After each full training audit, run and independently reconstruct the complete
restricted endpoint evaluation. After both trials, compare every class and the
incoming-mass-weighted total variation with the preceding pair (46.32 points).
Report aggregate frequencies and unfavorable or conflicting results. Also report
resource cost. Smaller cross-seed variation alone is not range accuracy, and
restricted all-in gains do not validate call/raise choices.

If justified, a later broader root-response test needs a separate prospective
protocol with fresh, uninspected physical training/test deals and its own resource
admission. There is no automatic wider evaluation or production promotion here.
No inference is made about other positions, stack depths, sizing menus, multiway
play, or GTO Wizard agreement from this single context.
