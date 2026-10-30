# E011 inactive-zero readback design (not implemented)

Status: stopped before source edits, build, or GPU execution. This is a design record, not a measured candidate. No patch or binary was produced.

Proposed scope: arena.rs only. For a compact compressed inactive block whose initial[which] equals usize::MAX, bypass Store::write_f32's redundant positive-zero max scan; fill exactly its owned quantized range with zero and write positive-zero to its own node scale. Keep generic encoding for explicit snapshots, including signed-zero/nonfinite inputs; leave the F32 branch and layout/constructor/kernel behavior unchanged.

Exactness basis: the sentinel denotes positive-zero decoded bits. Both existing compressed encoders return positive-zero scale and all-zero q for an all-positive-zero input, including length zero. The fast path would retain the existing disjoint node/range contract. Explicit snapshots must not be reclassified.

Proposed oracle checks: compare whole I16 and U16 q arrays and bitwise scale arrays against the original Store::write_f32 path; seed nonzero destinations and disjoint guard ranges/scales; include empty and nonempty ranges, both which indices, explicit signed-zero/nonfinite/finite snapshots, and repeated restores. No checks were executed.

Stop reason: parent review found the affected-stage upper bound insufficient for the registered 2% complete-cycle gate: rainbow is noncompact and unaffected, while the entire measured two-tone CPU readback stage was reported as 204.4 ms (about 1.8% of aggregate). This note records the parent finding; it is not an independently recomputed performance estimate. A zero-scan-only change cannot recover more than that entire stage and would retain its other work.

Inspected source: X:\Dev\GTOpen-gpu-research-20261016\crates\solver\src\gpu\arena.rs
Source SHA256: 7e55bff7face4f5beeddd99119cfda0c4f2acf9a1930c900f198d52d07ec8ed9
