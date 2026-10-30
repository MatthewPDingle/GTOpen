# D042 independent source and script review

PASS_SOURCE_AND_SCRIPT_REVIEW_ONLY. No actionable finding remains in the frozen source, protocol, build, cohort or assessment scripts.

The instrumentation invokes the byte-identical can_upload_zeros predicate exactly once, then times the original alloc_zeros call and existing stream wait in their original order. Source reversal exactly recovers accepted arena.rs; fallback, readback and existing tests are unchanged. It adds stack timing/metadata fields and best-effort locked stderr output, no host arena/device allocation, store mutation, CUDA copy or synchronization. All162 current sources still match accepted E020 before activation.

The fresh-target build pins all sources, evaluator, CUDA, dependencies and authorization, checks fresh compiler artifacts and both embedded CUDA/diagnostic marker, and freezes a distinct binary. Child cleanup stays under the build lock. The cohort runs exactly B1/P1,P2/B2,B3/P3 with all fixtures and the frozen environment; all outputs/IDs are unused at review. The assessment matches raw/result identities, all18 complete non-timing records and138 convergence checks, fixed200/200/60 stopping iterations, and all36 diagnostic records. Each fixture must have player/which order(0,0),(1,0),(0,1),(1,1) between build_complete and gpu_ready, correct q/scale byte counts, and finite nonnegative timings.

The absolute10percent change in sum of fixture medians is diagnostic usefulness only. U16 predicate time includes retained scale/metadata work. It is not a complete-cycle savings ceiling; allocation/submission and waited time are host spans, not device timings. Timer/logging perturbation remains included in the complete cycle, and logging is outside the three component timers. All repetitions remain, with no outcome extension or acceptance/deployment action.

This review did not compile or execute native/GPU work. Root retains execution and restoration responsibility.
