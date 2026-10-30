# E026: physical256 showdown work with the accepted logical128 scan

Prospective candidate only, from accepted E020. The CUDA file is the exact frozen D050 candidate. Only the two existing up_show host launches, evaluation and training, override block_dim to(256,1,1); Self::cfg supplies the unchanged grid and dynamic shared bytes. No other launch, allocation, host behavior, evaluator, arithmetic expression, logical hand count, graph/profile ordering or save format changes.

The CUDA candidate retains128 logical scan lanes when the physical width is256. It preserves all128 chunk-total writes, +0 accumulation, the full128-step left-to-right recurrence including empty tails, original per-chunk base addition and all unconditional barriers. The additional physical threads participate only in the existing disjoint staging/gather/CFV-zero/output loops. This is neither E008's recurrence rewrite nor E022's prefix-tail deletion.

D050 resource metadata alone does not authorize activation. Root must pin the independent D050 terminal/source/PTX PASS and the separately planned actual baseline128/candidate256 complete-up_show numerical comparison evidence, plus independent E026 source/script review. Any direct numerical mismatch blocks this candidate. This archive contains no activation script or executed native test.

The unchanged primary is84/4 unit inventory, then three alternating pairs against the immutable accepted E020 binary. Complete-cycle aggregate improvement must be at least2 percent; reject a fixture with more than3 percent median slowdown AND more than3 percent slowdown in at least2 of3 pairs. All18 non-timing results and138 convergence records remain exact. No exclusion or outcome-triggered extension is allowed.

Primary qualification is provisional. Existing original160 state/menu/resume records, three F32 cases, six GPU integration controls, relevant three continuation/paging/stored controls, the unchanged broad-range turn holdout and fresh-original cumulative three pairs remain conditional on primary passing. Numerical comparison and qualification must cover evaluation as well as training, both players and relevant locks/resume; the direct diagnostic is not a full-cycle performance claim.

Eight other kernels, CUDA ABI, memory layout and shared reservation remain accepted E020. Source checks are mechanical only; generated PTX and native exactness retain their own evidence boundaries. No production/status edits, compiler execution, GPU job or deployment occurred during preparation.
