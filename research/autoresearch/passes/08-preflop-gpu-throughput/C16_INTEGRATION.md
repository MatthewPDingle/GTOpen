# C16 integration qualification

Kernel source version 1 passes 672 exact prefix/terminal cases. The first cargo
filter selected zero tests; that invocation is not qualification evidence. The
corrected fully qualified filter ran the manual test successfully without source
changes. Both logs are preserved.

Version 2 adds research-only opt-in direct module construction, cache keys and
launch dispatch. The selected evaluator skips global CDF production and receives
normalized rows plus rank order. It keeps every device allocation, cohort plan,
normalization and duplicate-classification step. The global CDF is now unused
scratch on this path; the old scratch-prefix assertion is inapplicable there.
The new local-prefix device test checks the actual replacement prefix function.
All terminal, root, full-arena, gap/EV, graph and stop assertions remain enabled.
The mode assertion verifies the fused evaluator is actually selected.

Run all expanded cohort tests with PREFLOP_GPU_FUSED_CDF=1 and freeze the
executable. Validate both saved allocation plans, then the registered first
large pair. Keep independent compiler artifacts and source maps. A failed exact
or timing gate stops the candidate. No runtime source edits during workloads.
