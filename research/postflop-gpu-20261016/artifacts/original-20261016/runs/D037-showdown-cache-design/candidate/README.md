# D037 prepared candidate, outside checkout

Exact two-file candidate from accepted E015. `kernels.cu` adds an immutable u32 per-CTA card-position cache after the existing prefix region, loads it before the existing first barrier, and changes only the integer position lookup. All original float statements and barriers are preserved. `mod.rs` changes exactly both show_shared multipliers8 to16. No other launch, constructor, global admission, plan, evaluator or workload changes.

`base/` preserves E015, `candidate.patch` uses repository-relative paths, and `source-checks.json` records mechanical identity checks. The parent design manifest remains unchanged. This source is prepared only; root owns any reviewed integration/build/measurement decision. No production edits, builds or GPU calls occurred.
