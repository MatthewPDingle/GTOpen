//! Exact host mapping for GPU arenas containing only visited action nodes.
use super::{e, plan::GpuPlan, write_arena};
use crate::{cfr::Solver, store::Store, tree::KIND_ACTION};
use cudarc::driver::{CudaSlice, CudaStream};
use std::sync::Arc;
use rayon::prelude::*;

struct ActiveBlock {
    node: u32,
    host: u64,
    device: usize,
    len: usize,
}

struct CopySpan { host: u64, device: usize, len: usize }

struct InactiveBlock {
    node: u32,
    host: u64,
    len: usize,
    // usize::MAX represents a block of positive-zero bits. Signed zero and
    // every other initial bit pattern have an explicit snapshot.
    initial: [usize; 2],
}

pub(super) struct ArenaLayout {
    compact: bool,
    len: usize,
    active: Vec<ActiveBlock>,
    copies: Vec<CopySpan>,
    inactive: Vec<InactiveBlock>,
    initial: [Vec<f32>; 2],
    zeros: Vec<f32>,
}

impl ArenaLayout {
    pub(super) fn new(solver: &Solver, plan: &GpuPlan, p: usize) -> Self {
        let len = plan.arena_elements[p];
        let compact = len != solver.spot.tree.data_size[p] as usize
            || solver.spot.tree.nodes.iter().enumerate().any(|(i, n)|
                n.kind == KIND_ACTION && n.player as usize == p
                    && plan.node_data_off[i] != n.data_offset);
        let mut layout = Self {
            compact, len, active: Vec::new(), copies: Vec::new(), inactive: Vec::new(),
            initial: [Vec::new(), Vec::new()], zeros: Vec::new(),
        };
        if compact {
            let nh = solver.spot.hands[p].len();
            let mut max_inactive = 0;
            for (i, node) in solver.spot.tree.nodes.iter().enumerate() {
                if node.kind != KIND_ACTION || node.player as usize != p { continue; }
                let count = node.num_children as usize * nh;
                let off = plan.node_data_off[i];
                if off == u64::MAX {
                    max_inactive = max_inactive.max(count);
                    layout.inactive.push(InactiveBlock {
                        node: i as u32, host: node.data_offset, len: count,
                        initial: [usize::MAX; 2],
                    });
                } else {
                    layout.active.push(ActiveBlock {
                        node: i as u32, host: node.data_offset, device: off as usize, len: count,
                    });
                }
            }
            layout.zeros.resize(max_inactive, 0.0);
            for block in &layout.active {
                if let Some(last) = layout.copies.last_mut() {
                    if last.host + last.len as u64 == block.host
                        && last.device + last.len == block.device {
                        last.len += block.len;
                        continue;
                    }
                }
                layout.copies.push(CopySpan { host: block.host, device: block.device, len: block.len });
            }
        }
        layout
    }

    fn can_upload_zeros(&self, store: &Store, which: usize) -> bool {
        // Prove positive-zero decoded bits. Signed q still needs its guard;
        // every unsigned q decodes to +0 with a +0 scale. Keep host q untouched:
        // CPU strategy queries can normalize those words without the scale.
        // Check scales first so a warm arena can reject this path cheaply.
        let zero = match store {
            Store::I16 { q, scale } => {
                scale.as_slice().iter().all(|v| v.to_bits() == 0)
                    && q.as_slice().iter().fold(0u16, |bits, &v| bits | v as u16) == 0
            }
            Store::U16 { scale, .. } => {
                scale.as_slice().iter().all(|v| v.to_bits() == 0)
            }
            Store::F32(_) => false,
        };
        // Keep previously captured inactive state on the existing path if a
        // layout is reused. Fresh layouts already have the zero sentinels.
        zero && self.initial[which].is_empty()
            && self.inactive.iter().all(|block| block.initial[which] == usize::MAX)
    }

    pub(super) fn upload(
        &mut self, stream: &Arc<CudaStream>, solver: &Solver, p: usize, which: usize,
        staging: &mut [f32],
    ) -> Result<CudaSlice<f32>, String> {
        let store = if which == 0 { &solver.regrets[p] } else { &solver.strat[p] };
        if self.can_upload_zeros(store, which) {
            // Fresh compressed arenas need neither f32 host decoding nor a
            // host-to-device copy. Inactive positive-zero sentinels stay intact.
            let device = stream.alloc_zeros::<f32>(self.len).map_err(e)?;
            stream.synchronize().map_err(e)?;
            return Ok(device);
        }
        if !self.compact {
            if let Store::F32(b) = store {
                return stream.clone_htod(b.as_slice()).map_err(e);
            }
            // Decode directly into the reusable pinned allocation. A full
            // temporary f32 image would duplicate this buffer for each upload.
            let data = &mut staging[..self.len];
            let nh = solver.spot.hands[p].len();
            for (i, node) in solver.spot.tree.nodes.iter().enumerate() {
                if node.kind == KIND_ACTION && node.player as usize == p {
                    let len = node.num_children as usize * nh;
                    let off = node.data_offset as usize;
                    unsafe { store.read_f32(i as u32, node.data_offset, len, &mut data[off..off + len]); }
                }
            }
            let device = stream.clone_htod(&data[..]).map_err(e)?;
            stream.synchronize().map_err(e)?;
            return Ok(device);
        }
        let packed = &mut staging[..self.len];
        if let Store::F32(buf) = store {
            for span in &self.copies {
                let host = span.host as usize;
                packed[span.device..span.device + span.len]
                    .copy_from_slice(&buf.as_slice()[host..host + span.len]);
            }
        } else {
            for block in &self.active {
                unsafe {
                    store.read_f32(block.node, block.host, block.len,
                        &mut packed[block.device..block.device + block.len]);
                }
            }
        }
        let mut scratch = vec![0.0; self.zeros.len()];
        for block in &mut self.inactive {
            let values = if let Store::F32(buf) = store {
                let host = block.host as usize;
                &buf.as_slice()[host..host + block.len]
            } else {
                let values = &mut scratch[..block.len];
                unsafe { store.read_f32(block.node, block.host, block.len, values); }
                &values[..]
            };
            // A bitwise OR reduction can vectorize the cold zero-block scan;
            // comparison by bits still preserves -0.0 and non-finite payloads.
            if values.iter().fold(0u32, |bits, v| bits | v.to_bits()) != 0 {
                block.initial[which] = self.initial[which].len();
                self.initial[which].extend_from_slice(values);
            }
        }
        // These snapshots are immutable for the engine's lifetime. CPU
        // queries can materialize suit siblings between downloads; a later
        // sync must restore exactly what the former full GPU arena held.
        self.initial[which].shrink_to_fit();
        let device = stream.clone_htod(&packed[..]).map_err(e)?;
        // The same pinned allocation stages the next upload and all downloads.
        stream.synchronize().map_err(e)?;
        Ok(device)
    }

    pub(super) fn write(&self, solver: &Solver, p: usize, which: usize, data: &[f32]) {
        if !self.compact {
            write_arena(solver, which != 0, p, data);
            return;
        }
        let store = if which == 0 { &solver.regrets[p] } else { &solver.strat[p] };
        if let Store::F32(buf) = store {
            // Host spans are disjoint, just like parallel CPU CFR arenas.
            self.copies.par_iter().for_each(|span| {
                unsafe { buf.slice(span.host, span.len) }
                    .copy_from_slice(&data[span.device..span.device + span.len]);
            });
            self.inactive.par_iter().for_each(|block| {
                let dst = unsafe { buf.slice(block.host, block.len) };
                let start = block.initial[which];
                if start == usize::MAX { dst.fill(0.0); }
                else { dst.copy_from_slice(&self.initial[which][start..start + block.len]); }
            });
            return;
        }
        self.active.par_iter().for_each(|block| {
            unsafe {
                store.write_f32(block.node, block.host, block.len,
                    &data[block.device..block.device + block.len]);
            }
        });
        self.inactive.par_iter().for_each(|block| {
            let start = block.initial[which];
            let values = if start == usize::MAX { &self.zeros[..block.len] }
                else { &self.initial[which][start..start + block.len] };
            unsafe { store.write_f32(block.node, block.host, block.len, values); }
        });
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn layout(compact: bool) -> ArenaLayout {
        ArenaLayout {
            compact, len: 4, active: Vec::new(), copies: Vec::new(),
            inactive: if compact {
                vec![InactiveBlock { node: 1, host: 2, len: 2, initial: [usize::MAX; 2] }]
            } else { Vec::new() },
            initial: [Vec::new(), Vec::new()], zeros: vec![0.0; 2],
        }
    }

    #[test]
    fn zero_upload_accepts_only_positive_zero_compressed_sources() {
        for compact in [false, true] {
            let layout = layout(compact);
            for store in [Store::i16(4, 2), Store::u16(4, 2)] {
                for which in 0..2 {
                    assert!(layout.can_upload_zeros(&store, which));
                }
                let mut decoded = [f32::NAN; 4];
                unsafe { store.read_f32(0, 0, decoded.len(), &mut decoded); }
                assert!(decoded.iter().all(|v| v.to_bits() == 0));
                assert!(layout.inactive.iter().all(|block| block.initial == [usize::MAX; 2]));
                assert!(layout.initial.iter().all(Vec::is_empty));
            }
            assert!(!layout.can_upload_zeros(&Store::f32(4), 0));
        }
    }

    #[test]
    fn zero_upload_rejects_nonzero_signed_quants_with_zero_scale() {
        let layout = layout(true);
        let mut signed = Store::i16(4, 2);
        for value in [1, -1, i16::MIN, i16::MAX] {
            if let Store::I16 { q, .. } = &mut signed {
                q.as_mut_slice()[3] = value;
            }
            assert!(!layout.can_upload_zeros(&signed, 0));
        }
    }

    #[test]
    fn zero_upload_accepts_all_u16_quants_with_positive_zero_scale() {
        let quants: Vec<u16> = (0..=u16::MAX).collect();
        let mut decoded = vec![f32::NAN; quants.len()];
        crate::store::decode_u16(&quants, 0.0, &mut decoded);
        for (&q, value) in quants.iter().zip(&decoded) {
            assert_eq!(value.to_bits(), 0, "unsigned quant {q}");
        }
        let mut store = Store::u16(quants.len() as u64, 2);
        if let Store::U16 { q, .. } = &mut store {
            q.as_mut_slice().copy_from_slice(&quants);
        }
        for compact in [false, true] {
            let layout = layout(compact);
            for which in 0..2 {
                assert!(layout.can_upload_zeros(&store, which));
            }
        }
        if let Store::U16 { q, scale } = &store {
            assert_eq!(q.as_slice(), quants.as_slice(), "host quants stay intact");
            assert!(scale.as_slice().iter().all(|value| value.to_bits() == 0));
        }
    }

    #[test]
    fn zero_upload_rejects_signed_zero_nonzero_and_nonfinite_scales() {
        let layout = layout(true);
        let values = [
            -0.0, 1.0, -1.0, f32::from_bits(1), -f32::from_bits(1),
            f32::INFINITY, f32::NEG_INFINITY, f32::from_bits(0x7fc0_0123),
        ];
        for mut store in [Store::i16(4, 2), Store::u16(4, 2)] {
            for value in values {
                match &mut store {
                    Store::I16 { scale, .. } | Store::U16 { scale, .. } => {
                        scale.as_mut_slice()[1] = value;
                    }
                    Store::F32(_) => unreachable!(),
                }
                assert!(!layout.can_upload_zeros(&store, 0), "scale bits {:08x}", value.to_bits());
            }
        }
    }

    #[test]
    fn zero_upload_preserves_existing_inactive_snapshot_metadata() {
        for store in [Store::i16(4, 2), Store::u16(4, 2)] {
            let mut layout = layout(true);
            layout.initial[0].push(-0.0);
            assert!(!layout.can_upload_zeros(&store, 0));
            layout.inactive[0].initial[0] = 0;
            assert!(!layout.can_upload_zeros(&store, 0));
            assert!(layout.can_upload_zeros(&store, 1));
            assert_eq!(layout.initial[0][0].to_bits(), (-0.0f32).to_bits());
            assert_eq!(layout.inactive[0].initial, [0, usize::MAX]);
            layout.initial[0].clear();
            assert!(!layout.can_upload_zeros(&store, 0));
        }
    }
}

// Identical test-only attachment for the pinned original and E038 arena.rs.
#[cfg(test)]
mod e038_upload_control {
    use super::*;
    use super::super::GpuSolver;
    use crate::game::{Spot, SpotConfig};
    use crate::store::Storage;
    use crate::tree::{parse_sizes, StreetSizing, TreeConfig};
    use serde_json::{json, Value};
    use std::io::{BufWriter, Write};
    use std::path::{Path, PathBuf};

    type ControlResult<T> = Result<T, String>;

    struct DrainOnDrop(GpuSolver);
    impl std::ops::Deref for DrainOnDrop {
        type Target = GpuSolver;
        fn deref(&self) -> &GpuSolver { &self.0 }
    }
    impl std::ops::DerefMut for DrainOnDrop {
        fn deref_mut(&mut self) -> &mut GpuSolver { &mut self.0 }
    }
    impl Drop for DrainOnDrop {
        fn drop(&mut self) {
            if let Err(error) = self.0.synchronize() {
                let _ = writeln!(std::io::stderr().lock(), "E038_CONTROL_CLEANUP_ERROR {error}");
            }
        }
    }

    fn u32_word(out: &mut Vec<u8>, value: u32) { out.extend(value.to_le_bytes()); }
    fn u64_word(out: &mut Vec<u8>, value: u64) { out.extend(value.to_le_bytes()); }

    // Complete raw compressed storage, including all non-action scale words.
    fn host_image(s: &Solver) -> Vec<u8> {
        let mut out = b"E038HOST1".to_vec();
        u64_word(&mut out, s.iteration as u64);
        out.push(u8::from(s.use_isomorphism));
        for store in [&s.regrets[0], &s.regrets[1], &s.strat[0], &s.strat[1]] {
            match store {
                Store::I16 { q, scale } => {
                    u32_word(&mut out, 1);
                    u64_word(&mut out, q.len() as u64);
                    for value in q.as_slice() { out.extend(value.to_le_bytes()); }
                    u64_word(&mut out, scale.len() as u64);
                    for value in scale.as_slice() { u32_word(&mut out, value.to_bits()); }
                }
                Store::U16 { q, scale } => {
                    u32_word(&mut out, 2);
                    u64_word(&mut out, q.len() as u64);
                    for value in q.as_slice() { out.extend(value.to_le_bytes()); }
                    u64_word(&mut out, scale.len() as u64);
                    for value in scale.as_slice() { u32_word(&mut out, value.to_bits()); }
                }
                Store::F32(_) => panic!("control requires compressed stores"),
            }
        }
        out
    }

    fn query_image(s: &Solver) -> Vec<u8> {
        let mut out = b"E038QUERY1".to_vec();
        let mut nonuniform = false;
        for (id, node) in s.spot.tree.nodes.iter().enumerate() {
            if node.kind != KIND_ACTION { continue; }
            let p = node.player as usize;
            let nh = s.spot.hands[p].len();
            let na = node.num_children as usize;
            let mut sigma = vec![f32::NAN; nh * na];
            s.solved_strategy_into(node, &mut sigma);
            u32_word(&mut out, id as u32);
            u32_word(&mut out, p as u32);
            u32_word(&mut out, nh as u32);
            u32_word(&mut out, na as u32);
            if na > 1 {
                nonuniform |= (0..nh).any(|i| sigma[i].to_bits() != sigma[nh + i].to_bits());
            }
            for value in sigma { u32_word(&mut out, value.to_bits()); }
        }
        assert!(nonuniform, "raw nonzero U16 quants must affect an actual CPU query");
        out
    }

    fn device_image(gpu: &GpuSolver) -> ControlResult<Vec<u8>> {
        gpu.synchronize()?;
        let mut out = b"E038GPU1".to_vec();
        for (index, data) in [&gpu.d_regrets[0], &gpu.d_regrets[1], &gpu.d_strat[0], &gpu.d_strat[1]].into_iter().enumerate() {
            let host = gpu.stream.clone_dtoh(data).map_err(e)?;
            if index >= 2 { assert!(host.iter().all(|value| value.to_bits() == 0)); }
            u64_word(&mut out, host.len() as u64);
            for value in host { u32_word(&mut out, value.to_bits()); }
        }
        Ok(out)
    }

    fn save_image(s: &Solver, path: &Path) -> ControlResult<Vec<u8>> {
        let name = path.to_str().ok_or("non-UTF8 output path")?;
        assert!(!path.exists() && !PathBuf::from(format!("{name}.tmp")).exists());
        s.save(name)?;
        std::fs::read(path).map_err(e)
    }

    fn retain(dir: &Path, name: &str, bytes: &[u8], files: &mut Vec<Value>) -> ControlResult<()> {
        let file = std::fs::OpenOptions::new().write(true).create_new(true)
            .open(dir.join(name)).map_err(e)?;
        let mut out = BufWriter::new(file);
        out.write_all(bytes).map_err(e)?;
        out.flush().map_err(e)?;
        out.get_ref().sync_all().map_err(e)?;
        files.push(json!({"file":name,"bytes":bytes.len()}));
        Ok(())
    }

    fn run_layout(dir: &Path, iso: bool, expected_fast_path: bool) -> ControlResult<Value> {
        let sizing = || StreetSizing { bet: parse_sizes("50").unwrap(), raise: vec![], donk: vec![] };
        let spot = Arc::new(Spot::new_with_limit(SpotConfig {
            board: "KsQs2dJd".into(),
            range_oop: "AA,KK,QQ,JJ,AKs,AQs,AKo".into(),
            range_ip: "AA,QQ,TT,77,AQs,KQs,AQo".into(),
            tree: TreeConfig { starting_pot:10.0, effective_stack:20.0,
                oop:[sizing(),sizing(),sizing()], ip:[sizing(),sizing(),sizing()],
                ..Default::default() },
        }, Some(20_000))?);
        // Keep this proof small; do not silently substitute another fixture.
        assert!(spot.tree.data_size.iter().sum::<u64>() <= 250_000);
        let mut s = Solver::with_storage(spot.clone(), Storage::Compressed);
        s.use_isomorphism = iso;
        let plan = GpuPlan::build(&spot, iso);
        for p in 0..2 {
            if let Store::U16 { q, scale } = &mut s.strat[p] {
                for (i, word) in q.as_mut_slice().iter_mut().enumerate() {
                    *word = ((i as u64 * 73 + p as u64 * 997) % 65535 + 1) as u16;
                }
                assert!(scale.as_slice().iter().all(|value| value.to_bits() == 0));
            }
        }
        // Distinct finite regret blocks make materialization/restoration observable.
        // These are seeded host inputs, not a synthetic solver iteration.
        for (id, node) in spot.tree.nodes.iter().enumerate() {
            if node.kind != KIND_ACTION { continue; }
            let p = node.player as usize;
            if let Store::I16 { q, scale } = &mut s.regrets[p] {
                let value = (id + 1) as i16 * if id % 2 == 0 { 1 } else { -1 };
                let start = node.data_offset as usize;
                let len = node.num_children as usize * spot.hands[p].len();
                q.as_mut_slice()[start..start + len].fill(value);
                scale.as_mut_slice()[id] = 1.0;
            }
        }
        let layouts = [ArenaLayout::new(&s, &plan, 0), ArenaLayout::new(&s, &plan, 1)];
        for p in 0..2 {
            assert_eq!(layouts[p].compact, iso);
            assert_eq!(layouts[p].can_upload_zeros(&s.strat[p], 1), expected_fast_path);
            if iso {
                assert!(!layouts[p].inactive.is_empty());
                assert!(plan.arena_elements[p] < spot.tree.data_size[p] as usize);
            } else {
                assert!(layouts[p].inactive.is_empty());
                assert_eq!(plan.arena_elements[p], spot.tree.data_size[p] as usize);
            }
        }
        let mut files = Vec::new();
        let initial = host_image(&s);
        let query_before = query_image(&s);
        retain(dir, "pre_upload.host.bin", &initial, &mut files)?;
        retain(dir, "pre_upload.query.bin", &query_before, &mut files)?;
        let save_before = save_image(&s, &dir.join("pre_upload.save"))?;
        files.push(json!({"file":"pre_upload.save","bytes":save_before.len()}));
        assert_eq!(host_image(&s), initial, "query/save must not rewrite seeded host input");

        let budget = plan.staging_bytes()
            + (plan.arena_elements[0] + plan.arena_elements[1]) as u64 * 8
            + 512 * 1024 * 1024;
        let mut gpu = DrainOnDrop(GpuSolver::new_with_budget(&s, budget)?);
        let owner = gpu._ctx.clone();
        for p in 0..2 {
            assert_eq!(gpu.arena_layout[p].compact, iso);
            assert_eq!(gpu.d_strat[p].len(), plan.arena_elements[p]);
            assert_eq!(gpu.d_regrets[p].len(), plan.arena_elements[p]);
            assert_eq!(gpu.arena_layout[p].inactive.len(), layouts[p].inactive.len());
            assert!(gpu.arena_layout[p].initial[1].is_empty());
            assert!(gpu.arena_layout[p].inactive.iter().all(|block| block.initial[1] == usize::MAX));
            if iso { assert!(!gpu.arena_layout[p].initial[0].is_empty()); }
        }
        assert_eq!(host_image(&s), initial, "constructor/upload changed raw host stores");
        let query_after = query_image(&s);
        let save_after = save_image(&s, &dir.join("post_upload.save"))?;
        assert_eq!(query_after, query_before);
        assert_eq!(save_after, save_before);
        assert_eq!(host_image(&s), initial, "post-upload query/save changed raw stores");
        files.push(json!({"file":"post_upload.save","bytes":save_after.len()}));
        retain(dir, "post_upload.query.bin", &query_after, &mut files)?;
        retain(dir, "post_upload.host.bin", &host_image(&s), &mut files)?;
        let gpu_initial = device_image(&gpu)?;
        retain(dir, "post_upload.gpu.bin", &gpu_initial, &mut files)?;

        gpu.sync_to_cpu(&mut s)?;
        let first_readback = host_image(&s);
        retain(dir, "first_readback.host.bin", &first_readback, &mut files)?;
        let device = device_image(&gpu)?;
        assert_eq!(device, gpu_initial);
        retain(dir, "first_readback.gpu.bin", &device, &mut files)?;
        s.ensure_symmetric();
        let materialized = host_image(&s);
        if iso { assert_ne!(materialized, first_readback, "inactive materialization witness"); }
        retain(dir, "materialized.host.bin", &materialized, &mut files)?;
        let device = device_image(&gpu)?;
        assert_eq!(device, gpu_initial);
        retain(dir, "materialized.gpu.bin", &device, &mut files)?;
        gpu.sync_to_cpu(&mut s)?;
        let repeated = host_image(&s);
        assert_eq!(repeated, first_readback, "readback must restore inactive initial state");
        retain(dir, "repeat_readback.host.bin", &repeated, &mut files)?;
        let device = device_image(&gpu)?;
        assert_eq!(device, gpu_initial);
        retain(dir, "repeat_readback.gpu.bin", &device, &mut files)?;

        gpu.synchronize()?;
        drop(gpu);
        owner.check_err().map_err(e)?;
        let bytes: u64 = files.iter().map(|f| f["bytes"].as_u64().unwrap()).sum();
        assert!(bytes <= 32 * 1024 * 1024, "per-layout output bound");
        Ok(json!({"layout":if iso {"compact"} else {"full"},
            "nodes":spot.tree.nodes.len(),"nh":plan.nh,"host_elements":spot.tree.data_size,
            "device_elements":plan.arena_elements,
            "inactive_blocks":[layouts[0].inactive.len(),layouts[1].inactive.len()],
            "u16_zero_fast_path":expected_fast_path,"host_query_save_preserved":true,
            "device_unchanged_after_readbacks":true,"repeat_restores_first_readback":true,
            "materialization_changed_host":materialized != first_readback,
            "cleanup_complete":true,"files":files,"output_bytes":bytes}))
    }

    #[test]
    #[ignore = "root-only original/candidate upload control; requires CUDA and fresh output directory"]
    fn exact_u16_zero_upload_lifecycle() -> ControlResult<()> {
        let dir = PathBuf::from(std::env::var_os("E038_CONTROL_DIR").ok_or("E038_CONTROL_DIR missing")?);
        let expected_fast_path = match std::env::var("E038_CONTROL_EXPECT_FAST_PATH").as_deref() {
            Ok("0") => false, Ok("1") => true, _ => return Err("expected fast path must be0 or1".into()),
        };
        std::fs::create_dir(&dir).map_err(e)?;
        let mut cases = Vec::new();
        for (label, iso) in [("full", false), ("compact", true)] {
            let path = dir.join(label);
            std::fs::create_dir(&path).map_err(e)?;
            let result = run_layout(&path, iso, expected_fast_path)?;
            println!("E038_UPLOAD_CONTROL {}", json!({"stage":"layout_complete","result":result}));
            cases.push(result);
        }
        let summary = json!({"id":"E038-control","stage":"complete","layouts":cases,
            "solve_iterations":0,"performance_measurement":false,"candidate_accepted":false});
        retain(&dir, "evidence.json", &serde_json::to_vec_pretty(&summary).map_err(e)?, &mut Vec::new())?;
        println!("E038_UPLOAD_CONTROL {summary}");
        Ok(())
    }
}
