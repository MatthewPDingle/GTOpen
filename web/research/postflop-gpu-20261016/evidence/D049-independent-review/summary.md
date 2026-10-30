# D049 independent terminal review

**Confirmed rejection at the fixed resource prerequisite.** Registers rose from 40 to 48; theoretical active 128-thread blocks per SM fell from 12 to 10 (48 to 40 warps). Local storage remained 32 bytes/thread. The non-worse-register and non-decreasing-occupancy requirements both fail.

The four raw markers contain exactly two resource rows, produced by one recorded successful compiler invocation followed by one successful standalone probe. Device/compiler identity is RTX 5090, compute_120, NVRTC 12.9. Frozen source, script, dependency, compiler, DLL, binary and output provenance were verified; all 162 current checkout source hashes still equal accepted E020. The eight unaffected PTX entry bodies are byte-identical, and the down_action ABI is unchanged.

The preserved static counts are 50→14 branch sites and 119→83 integer global-load sites. They are not executed counts, speed measurements or numerical proof. Detailed NA2/3/4 mechanism/floating-dependency assessment is **NOT ASSESSED**, because the prerequisite failure already stops qualification. No kernel was launched and no solver, accuracy screen or performance test ran. No native candidate or rescue variant is justified by this probe.

The pre-execution CRLF patch-format failure remains preserved in the original preparation artifacts. No reviewer or native rerun was performed for this audit. Resource inspection alone does not show that the changed code is numerically exact or slower in practice; rejection follows the fixed prospective gate.
