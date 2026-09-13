# D08: compiler evidence, hardware counters unavailable

The bounded Nsight Compute smoke returned `ERR_NVGPUCTRPERM`. The selected
GPU prefix test itself passed and the profiler disconnected. No counters were
collected, no permission or driver setting was changed, and no denied request
was repeated. The portable tool also reported a section-directory warning and
a Python encoding error after disconnect; these do not turn the run into valid
profiling evidence.

The permitted alternative was to link archived PTX with the CUDA driver and
disassemble it, without launching kernels. The official CUDA 13.1.1 manifest,
published archive checksums, local executable hashes, input PTX, generated
cubins and assembly are preserved. Tools live only under the ignored local
`target/research-tools` directory. No installer or global PATH change was used.

| CDF kernel | Static instructions, excluding NOP | Shuffle-up | Float add | Select |
| --- | ---: | ---: | ---: | ---: |
| C12 reference | 187 | 30 | 41 | 1 |
| C12 candidate | 182 | 30 | 41 | 1 |

This provides a plausible explanation for C12's ineffective optimization:
although its PTX removed 30 selections, the linked reference already contained
only one native select. The difference is five predicate comparisons and some
NOP padding. Both versions use 26 registers and no local/shared storage.
This is an inference about compiler behavior, not a measured stall cause.

**Limits:** driver linking treats PTX as relocatable input; it does not prove
the exact instruction stream used by direct PTX module loading. In fact, C09's
terminal shared allocation differs (84 bytes direct versus 80 bytes linked).
Both report 54 registers and zero local storage. Static instruction counts are
not dynamic execution counts or hardware throughput measurements. No speed
point is added to the graph, and C09 remains the retained version.

The first native inspection incorrectly required identical direct/link resource
attributes and stopped after the first module. Its original script and failure
are archived. Version 2 records the difference explicitly and completed all
four modules. The counter protocol's original prefix was recovered byte for
byte against its recorded hash. Assembly text hashes in the producer precede
Windows newline expansion; the verifier checks normalized text and separately
records hashes of the actual archived bytes. No measurement files were edited.

Validation: `python check_d08.py` independently verifies published component
hashes, run input hashes, the Git source snapshot, failure/success outcomes,
PTX/cubin/assembly provenance, resources and per-kernel instruction counts.
See `raw/d08-verified.json`. The script does not invoke CUDA or modify 56708.

Next: qualify a memory-aware selection path for the retained optimizations,
preserving the configured solver's particle grouping and saved-state behavior.
Further kernel ideas need a complete-work benchmark; compiler instruction
counts alone are insufficient grounds to retain them.
