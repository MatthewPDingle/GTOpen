# Matched board-root prefixes: complete

Both preselected arms completed their first two full-budget generations and
deterministic restart checks. These generations count toward the fixed 78 per
arm; they are not a pilot that can be discarded after inspecting the ranges.

The independent prefix audit passed in 336.078 seconds. Across both arms it
checked 16 public boards, 2,048 physical roots and 45,587 postflop training
targets. Maximum root-state discrepancy was 1.71e-13; maximum policy discrepancy
was 5.07e-13. The original tolerances were retained. The audit shares the native
poker engine, feature encoder, sampler and reservoir implementation; it is not
an independent poker-engine implementation or evidence of playing strength.

Evidence:

- `board-root-matched-prefix-v1-result.json`:
  `fe96f8f6fdea7333aa086284187c80b3b38b4a991b769e1b9a574f69f62d6042`
- `board-matched-prefix-readback-v1-result.json`:
  `3d0b10271c5433f5eb4bdcb8a3acc43c20a228932b7404fa74ac550e5ecf4e36`
- `board-prefix-followup-recovery-v3-result.json` links all prerequisite checks
  and records terminal completion of the prefix queue.

Next: measured full-study storage admission, then continuation to 78 generations
per arm if admitted, followed by independent full readback. The final fixed
65,536-deal comparison remains unstarted. No range-quality conclusion or
production deployment follows from these mechanical checks.

## Subsequent evaluation launcher

`board_evaluation_resource_wrapper_v1.py` uses the previously qualified
two-thread numerical context and closed-port-aware global storage inventory
for the frozen full-bank control and final evaluator. Its default invocation
only checks readiness. Both readiness paths were checked and correctly report
missing full training, full readback and (for final evaluation) complete-bank
qualification. No new evaluation deals were drawn.

After the required stages finish, invoke the control with `--stage control
--run`, perform `board_complete_control_readback_v1.py`, then invoke evaluation
with `--stage evaluation --run`. Explicit evaluation restarts use `--resume`
and a distinct `--attempt` name. Each attempt retains its own registration and
result or failure. The wrapper changes only the inventory dependency and
restores it on exit; all scientific drivers, seeds, qualifications, storage
bounds, statistical rules and source bindings remain unchanged. The qualified
runtime context is reused; there is no new numerical algorithm in the wrapper.
