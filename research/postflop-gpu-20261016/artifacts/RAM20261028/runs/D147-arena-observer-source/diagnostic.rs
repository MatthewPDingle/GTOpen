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

// A constructor-local proof, tied to an immutable borrow of this exact Store.
// It does not survive initialization or permit a later mutation/traversal.
pub(super) struct ZeroCheck<'a> {
    store: &'a Store,
    positive: bool,
}

impl<'a> ZeroCheck<'a> {
    pub(super) fn new(store: &'a Store) -> Self {
        let zero = match store {
            Store::I16 { q, scale } => {
                scale.as_slice().iter().all(|v| v.to_bits() == 0)
                    && q.as_slice().iter().fold(0u16, |bits, &v| bits | v as u16) == 0
            }
            Store::U16 { q, scale } => {
                scale.as_slice().iter().all(|v| v.to_bits() == 0)
                    && q.as_slice().iter().fold(0u16, |bits, &v| bits | v) == 0
            }
            Store::F32(_) => false,
        };
        Self { store, positive: zero }
    }

    fn positive_for(&self, store: &Store) -> Option<bool> {
        std::ptr::eq(self.store, store).then_some(self.positive)
    }
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
        // Both inputs must prove positive-zero decoded bits: a negative q
        // with +0 scale, or a zero q with -0 scale, can decode to -0.0.
        // Check scales first so a warm arena can reject this path cheaply.
        self.can_upload_prechecked(store, which, &ZeroCheck::new(store))
    }

    fn can_upload_prechecked(&self, store: &Store, which: usize, check: &ZeroCheck<'_>) -> bool {
        let zero = check.positive_for(store) == Some(true);
        // Keep previously captured inactive state on the existing path if a
        // layout is reused. Fresh layouts already have the zero sentinels.
        zero && self.initial[which].is_empty()
            && self.inactive.iter().all(|block| block.initial[which] == usize::MAX)
    }

    pub(super) fn upload(
        &mut self, stream: &Arc<CudaStream>, solver: &Solver, p: usize, which: usize,
        staging: &mut [f32],
    ) -> Result<CudaSlice<f32>, String> {
        self.upload_prechecked(stream, solver, p, which, staging, None)
    }

    pub(super) fn upload_prechecked(
        &mut self, stream: &Arc<CudaStream>, solver: &Solver, p: usize, which: usize,
        staging: &mut [f32], check: Option<&ZeroCheck<'_>>,
    ) -> Result<CudaSlice<f32>, String> {
        let store = if which == 0 { &solver.regrets[p] } else { &solver.strat[p] };
        let zero = match check {
            Some(check) => self.can_upload_prechecked(store, which, check),
            None => self.can_upload_zeros(store, which),
        };
        if zero {
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

    // Diagnostic host wall clocks only; all original writes and joins remain.
    fn d147_emit_profile(&self, started: Option<std::time::Instant>,
        split: Option<std::time::Instant>, player: usize, which: usize, mode: &str) {
        if let Some(started) = started {
            let ended = std::time::Instant::now();
            let full_ms = ended.duration_since(started).as_secs_f64() * 1e3;
            let active_ms = split.map(|s| s.duration_since(started).as_secs_f64() * 1e3);
            let inactive_ms = split.map(|s| ended.duration_since(s).as_secs_f64() * 1e3);
            use std::io::Write;
            let mut stderr = std::io::stderr().lock();
            let _ = writeln!(stderr, "CPU_ARENA_PROFILE {}", serde_json::json!({
                "schema_version": 1, "player": player, "which": which,
                "mode": mode, "full_wall_ms_before_logging": full_ms,
                "active_wall_ms": active_ms, "inactive_wall_ms": inactive_ms,
                "active_blocks": self.active.len(), "inactive_blocks": self.inactive.len(),
                "copy_spans": self.copies.len(), "device_f32_elements": self.len,
                "diagnostic_only": true, "extra_gpu_operations": 0,
                "scope": "Host wall around unchanged CPU write stages; includes Rayon scheduling. Logging perturbs enclosing readback. No isolated encoder, removed-work or speed claim."
            }));
        }
    }

    pub(super) fn write(&self, solver: &Solver, p: usize, which: usize, data: &[f32]) {
        let d147_started = (std::env::var_os("POSTFLOP_AUTORESEARCH_LIFECYCLE_PROFILE")
            .as_deref() == Some(std::ffi::OsStr::new("1")))
            .then(std::time::Instant::now);

        if !self.compact {
            write_arena(solver, which != 0, p, data);
            self.d147_emit_profile(d147_started, None, p, which, "full");
            return;
        }
        let store = if which == 0 { &solver.regrets[p] } else { &solver.strat[p] };
        if let Store::F32(buf) = store {
            // Host spans are disjoint, just like parallel CPU CFR arenas.
            self.copies.par_iter().for_each(|span| {
                unsafe { buf.slice(span.host, span.len) }
                    .copy_from_slice(&data[span.device..span.device + span.len]);
            });
            let d147_split = d147_started.map(|_| std::time::Instant::now());
            self.inactive.par_iter().for_each(|block| {
                let dst = unsafe { buf.slice(block.host, block.len) };
                let start = block.initial[which];
                if start == usize::MAX { dst.fill(0.0); }
                else { dst.copy_from_slice(&self.initial[which][start..start + block.len]); }
            });
            self.d147_emit_profile(d147_started, d147_split, p, which, "compact_f32");
            return;
        }
        self.active.par_iter().for_each(|block| {
            unsafe {
                store.write_f32(block.node, block.host, block.len,
                    &data[block.device..block.device + block.len]);
            }
        });
        let d147_split = d147_started.map(|_| std::time::Instant::now());
        self.inactive.par_iter().for_each(|block| {
            let start = block.initial[which];
            let values = if start == usize::MAX { &self.zeros[..block.len] }
                else { &self.initial[which][start..start + block.len] };
            unsafe { store.write_f32(block.node, block.host, block.len, values); }
        });
        self.d147_emit_profile(d147_started, d147_split, p, which, "compact_compressed");
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
    fn zero_upload_rejects_nonzero_quantized_values_with_zero_scale() {
        let layout = layout(true);
        let mut signed = Store::i16(4, 2);
        for value in [1, -1, i16::MIN, i16::MAX] {
            if let Store::I16 { q, .. } = &mut signed {
                q.as_mut_slice()[3] = value;
            }
            assert!(!layout.can_upload_zeros(&signed, 0));
        }
        let mut unsigned = Store::u16(4, 2);
        for value in [1, u16::MAX] {
            if let Store::U16 { q, .. } = &mut unsigned {
                q.as_mut_slice()[3] = value;
            }
            assert!(!layout.can_upload_zeros(&unsigned, 1));
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
        let mut layout = layout(true);
        let store = Store::i16(4, 2);
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
    #[test]
    fn scoped_zero_checks_reject_other_stores_and_preserve_all_guards_and_bits() {
        fn image(s: &Store) -> Vec<u32> {
            match s {
                Store::I16 { q, scale } => q.as_slice().iter().map(|&x| x as u16 as u32)
                    .chain(scale.as_slice().iter().map(|x| x.to_bits())).collect(),
                Store::U16 { q, scale } => q.as_slice().iter().map(|&x| x as u32)
                    .chain(scale.as_slice().iter().map(|x| x.to_bits())).collect(),
                Store::F32(b) => b.as_slice().iter().map(|x| x.to_bits()).collect(),
            }
        }
        let mut cases = 0;
        for signed in [false, true] {
            let mut store = if signed { Store::i16(257, 4) } else { Store::u16(257, 4) };
            for step in 0..7 {
                if step == 1 {
                    match &mut store {
                        Store::I16 { q, .. } => q.as_mut_slice()[256] = -1,
                        Store::U16 { q, .. } => q.as_mut_slice()[256] = 1,
                        _ => unreachable!(),
                    }
                } else if step >= 2 {
                    let scale_bits = [0x8000_0000, 0x7f80_0000, 0xff80_0000, 0x7fc0_1234, 1][step - 2];
                    match &mut store {
                        Store::I16 { q, scale } => { q.as_mut_slice()[256] = 0; scale.as_mut_slice()[3] = f32::from_bits(scale_bits); }
                        Store::U16 { q, scale } => { q.as_mut_slice()[256] = 0; scale.as_mut_slice()[3] = f32::from_bits(scale_bits); }
                        _ => unreachable!(),
                    }
                }
                let before = image(&store);
                let check = ZeroCheck::new(&store);
                let other = Store::u16(257, 4);
                assert_eq!(check.positive_for(&other), None);
                for compact in [false, true] {
                    let mut arena = layout(compact);
                    for which in 0..2 {
                        assert_eq!(arena.can_upload_prechecked(&store, which, &check), step == 0);
                        assert!(!arena.can_upload_prechecked(&other, which, &check));
                    }
                    arena.initial[0].push(-0.0);
                    assert!(!arena.can_upload_prechecked(&store, 0, &check));
                    assert_eq!(arena.initial[0][0].to_bits(), 0x8000_0000);
                    arena.initial[0].clear();
                    if compact {
                        arena.inactive[0].initial[0] = 0;
                        assert!(!arena.can_upload_prechecked(&store, 0, &check));
                        assert_eq!(arena.inactive[0].initial, [0, usize::MAX]);
                    }
                }
                drop(check);
                assert_eq!(before, image(&store));
                cases += 1;
            }
        }
        let store = Store::f32(257);
        assert_eq!(ZeroCheck::new(&store).positive_for(&store), Some(false));
        assert_eq!(cases + 1, 15);
    }

}
