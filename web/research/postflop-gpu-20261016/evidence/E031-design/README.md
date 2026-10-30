# E031: static showdown card-offset cache

Off-tree source preparation from exact accepted E020. Only crates/solver/src/gpu/kernels.cu changes. Add `__shared__ u32 card_off_sh[53]`, cooperatively fill all53absolute offsets with a block-stride loop after the current position copy and before the existing first barrier, then replace the two textual c0/c1 reads (four logical reads per own hand). The earlier global card_base stays unchanged.

Every original floating expression/order, prefix recurrence, card loop, CFV zero/output, all5barriers, ABI and other8entries remain unchanged. All positive legal block widths cover53words; host-only coverage checked1..256. Empty slots still supply53valid equal offsets and card IDs0..51 keep c+1 in bounds. Nonzero absolute bases are preserved.

Nominal212Bstatic shared growth requires actual compiler allocation/occupancy review. Host dynamic reservations, both training/evaluation launch sites, persistent budget/continuation/workspace, constructors and the frozen evaluator are unchanged. No ownership/partial-move changes. No new unit declarations: existing GPU-only84normal/4ignored inventory remains.

Source checks establish byte/geometry facts only. No compiler, native/GPU execution, activation or performance claim. Root separately owns resource/exactness/full-cycle decisions; no primary package is prepared. D059 records evidence and scoped history, including D037's previously deferred offset-cache idea.
