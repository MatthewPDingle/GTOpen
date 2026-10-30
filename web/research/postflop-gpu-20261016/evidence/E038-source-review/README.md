# E038 off-tree source review

PASS for the frozen arena-only draft, pending final baseline selection and runtime validation. The sole production predicate change is exact for unsigned quants with positive-zero scales, and host q remains untouched. Production reversal is exact; the new written CPU test invokes decode_u16 across all65536 values. Existing I16/F32/scale/snapshot guards remain.

The proposed bounded original-versus-candidate full/compact GPU control is appropriate but unimplemented. No measured gain or adoption claim; no compiler/native/GPU work or partial family timing reads occurred.
