# E038 original-versus-candidate upload control

This frozen source-only package attaches one identical ignored Rust test to the accepted E020 arena and the sealed E038 arena. The fixed base is authorized by `runs/E038-root-decisions/baseline.json`. Nothing has been compiled or executed. The original E038 archive is unchanged.

`original-control-arena.rs` is byte-for-byte `E038-design/base/arena.rs` followed by `attachment.rs`; `candidate-control-arena.rs` uses the corresponding candidate prefix and exactly the same attachment. Root may temporarily attach the matching complete file at `crates/solver/src/gpu/arena.rs` in separately controlled original and candidate unit builds. All other 161 accepted source identities and kernels remain unchanged. Restore the accepted source after each build, keep separate fresh targets and artifacts, and finish all compiler work before either native control invocation. These control-only builds must not become timing binaries.

Prospective compile shape, not an executed command: `cargo test -p solver --features gpu --lib --no-run --message-format=json`, using root-selected distinct fresh target directories. Confirm the actual test artifact and GPU-only feature identity from Cargo output. Then root runs each frozen solver test executable with the full qualified filter and arguments below (the established runner omits --exact and validates one selected test):

```
gpu::arena::e038_upload_control::exact_u16_zero_upload_lifecycle --ignored --nocapture --test-threads=1
```

Set `E038_CONTROL_DIR` to a fresh nonexistent absolute directory with an existing parent. Set `E038_CONTROL_EXPECT_FAST_PATH=0` for original and `=1` for candidate. The exact selected summaries are one pass/88 filtered and one pass/89 filtered respectively. Runtime, lock, timeout, child cleanup, binary/source custody and final authorization remain root-owned. Any failed run is retained; no rerun or scope change is implied.

The single existing small turn fixture runs full then compact. Each layout writes five complete host-store images, four complete device-arena images, two actual CPU-strategy query images and two existing-format saves: 13 files per layout, 26 total plus `evidence.json`. Three `E038_UPLOAD_CONTROL` JSON records appear in fixed order. Reject any `E038_CONTROL_CLEANUP_ERROR`. `schema.json` specifies all framing, fields and comparison rules.

U16 words are deterministic and nonzero at exact +0 scales. Finite, node-distinct I16 blocks make inactive sibling materialization and subsequent restoration observable. Both actual constructors, both full `sync_to_cpu` readbacks, actual `ensure_symmetric`, CPU query and save methods run unchanged. No solver iteration or exploitability call is added. Device outputs are full raw f32 bits; host images contain every raw q and scale word. Saved format is separately observed, not mistaken for raw-q preservation.

All 26 corresponding evidence files must be byte-identical between independent original and candidate processes. JSON permits only the asserted `u16_zero_fast_path` false-to-true distinction. The test proves host data remain unchanged through upload, then checks the same real re-encoding/materialization lifecycle in both arms. It does not require readback to preserve the deliberately noncanonical initial U16 representation.

Static inspection confirms APIs and byte attachment only; compilation, CUDA availability, actual compact geometry, all runtime assertions and cross-arm equality remain unvalidated. No performance, no-tradeoff or acceptance conclusion follows from preparation.
