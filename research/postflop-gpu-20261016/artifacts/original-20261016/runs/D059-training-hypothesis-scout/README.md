# D059: fixed showdown card-offset cache

One source-feasible, previously proposed but untested idea: cache all53absolute opponent card offsets in per-CTA static shared memory. Accepted E020 caches positions but retains four global offset loads per valid own hand. D037 explicitly deferred the smaller offset cache; the bounded E001-E030 review found no identical closed experiment.

Archived E020 PTX confirms those loads. D045 selected up_show medians are1.0034/1.0255ms at141120CTAs, but perturbed intervals and scalar counts reveal neither offset-load latency nor complete-cycle headroom. The extra53loads/stores perCTA and nominal212Bstatic shared storage can lose through initialization, cache behavior, bank access or occupancy. No gain is predicted.

A block-stride preload through53 before the existing first barrier preserves all reads, including nonzero/empty slots. Retain global card_base, absolute offsets, every floating expression/card-loop/scan/output and all5barriers. No host reservation/ABI/global metadata/workspace change is needed; evaluation also uses this entry.

GO only to the separately authorized one-file source preparation and compiler/resource feasibility review. report.json contains exact source/PTX/evidence pins and limits. The mutable ledger bytes are archived rather than pinned at a changing path. No compiler, native/GPU execution or production/status change occurred.
