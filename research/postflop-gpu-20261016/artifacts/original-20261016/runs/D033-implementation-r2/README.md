# D033 implementation revision2: CUDA12.6 binding name

The first build failed with E0425 before any GPU/test execution. Its raw build.jsonl, build.stderr.log and exit.json remain unchanged in runs/D033-build; exact hashes are recorded here. The original D033-implementation archive is preserved and all its checksums reverified.

The sole source change from revision1 is replacing cuGraphKernelNodeGetParams with cuGraphKernelNodeGetParams_v2 at the descriptor query. The former is exposed by cudarc0.19.7 only for CUDA11 features. The project's cuda-12060 feature exposes the latter and maps CUDA_KERNEL_NODE_PARAMS to repr(C) CUDA_KERNEL_NODE_PARAMS_v2_st. Both the call signature and existing local parameter variable therefore use the same v2 ABI, including trailing kern and ctx fields. No cast, type/layout change or kernel argument mutation was introduced. binding-evidence.txt preserves the exact installed declaration/feature excerpts and manifest.json its full source hash.

The protocol, fixed configuration, anchors, schedule, graph edges, timings, comparisons and ownership/cleanup code are unchanged. The two unrelated preflop-import warnings were left untouched. candidate.patch includes the complete authorized two-file change from accepted E015; r1-to-r2.patch shows the one-identifier repair. Production mod.rs remains the identical cfg(test) append from revision1.

Rustfmt parse-only and git diff --check passed. The builder performed no Cargo build, test or GPU call. Root owns the second build and execution after the independent revision review. Ignored filter remains gpu::graph_device_events::captured_graph_device_event_diagnostic.
