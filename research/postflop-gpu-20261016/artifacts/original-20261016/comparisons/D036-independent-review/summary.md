# D036 independent runtime review

PASS for the fixed standalone numerical/resource probe. This supports proceeding to a separately qualified solver experiment; it establishes no solver speedup or acceptance.

The frozen R3 manifest, binary, corpus, CUDA, dependencies, NVRTC DLLs and protected accepted-source hashes match the saved provenance. One compile and one native invocation returned zero. The recorded 4.547 s compiler and 2.891 s probe durations are operational metadata only.

All 180 full-kernel pairs matched across all saved output images: 1,771,280 active word pairs, including 126,520 mandatory finite-overflow output pairs. Those overflow outputs include 7,200 infinity and 118,560 NaN bit patterns, all identical between compiled baseline and candidate. All 1,644,760 finite-domain full outputs changed from the initial guard; 942,363 were nonzero. All 5,969,780 full guard checks and 4,520 raw guard checks passed. Ten zero-count and ten zero-own-hand pairs are retained.

All 1,120 raw-total case pairs matched. An independent Python reconstruction rounding every addition to f32 reproduced the saved CPU/GPU result for all 1,040 finite-domain raw cases. The remaining 80 overflow cases were still mandatory GPU bit comparisons; 70 produced infinity, all exact. Every fixed block shape (128, 16, 32, 64, 256), player and scenario appears in the prespecified order. No case was excluded or retried.

The frozen native source checks all 14 input buffers after each full-kernel variant and three buffers after each raw variant: 5,070 buffer comparisons in total. Successful marker flow proves those checks completed. Input readback images were not separately saved, so that part relies on the verified executable checks rather than an independent re-comparison of saved device input images.

Both full kernels report 39 registers, zero local bytes, 1,232 static shared bytes, 1,024 maximum threads, and 12 theoretical 128-thread blocks per SM for each of the four recorded dynamic shared sizes (0, 1,028, 1,276, 5,304 bytes). All eight other PTX entrypoints are byte-identical. Five shuffle sites appear in the candidate fold entry. Static PTX and occupancy do not establish dynamic timing or solver benefit.

The R2 compiler-only failure (62 E0277 errors) and all 28 R2 files remain intact. No R2 native case ran. R3 changes only explicit error conversion; it did not replace a numerical sample. One review script stopped after numerical checks because it omitted the single newline intentionally added to PTX excerpt files; the script/failure record are retained and the corrected check passed without rerunning the experiment.

Limits: the corpus is finite and constructed, with finite inputs. Matching overflow-generated nonfinite outputs does not establish a general NaN/Inf input-payload guarantee. The independent CPU oracle covers raw totals; compiled original full up_fold remains the full-CFV oracle. Solver lifecycle, graph integration, correctness controls and complete-cycle performance still require the separate native candidate protocol.
