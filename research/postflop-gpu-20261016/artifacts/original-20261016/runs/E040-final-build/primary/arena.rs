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

#[derive(Clone, Debug)]
pub(super) struct ReadbackChunk {
    pub(super) first: usize,
    pub(super) past: usize,
    pub(super) start: usize,
    pub(super) len: usize,
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
        // Both inputs must prove positive-zero decoded bits: a negative q
        // with +0 scale, or a zero q with -0 scale, can decode to -0.0.
        // Check scales first so a warm arena can reject this path cheaply.
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

    /// Complete-node groups, validated before any asynchronous transfer.
    pub(super) fn readback_chunks(
        &self, solver: &Solver, p: usize, window: usize, pieces: usize, min_words: usize,
    ) -> Option<Vec<ReadbackChunk>> {
        const MAX_CHUNKS: usize = 16;
        if pieces < 2 || pieces > 14 || self.len == 0 { return None; }
        let target = self.len.checked_add(pieces - 1)? / pieces;
        if target < min_words || target > window || window == 0 { return None; }
        let mut chunks = Vec::with_capacity(MAX_CHUNKS);
        let (mut first, mut past, mut start, mut len, mut covered) = (0, 0, 0, 0usize, 0usize);
        let mut append = |index: usize, device: usize, words: usize| -> Option<()> {
            if words == 0 || words > window || device != covered { return None; }
            let next = covered.checked_add(words)?;
            if next > self.len { return None; }
            if len != 0 && len.checked_add(words)? > target {
                if chunks.len() >= MAX_CHUNKS - 1 { return None; }
                chunks.push(ReadbackChunk { first, past, start, len });
                len = 0;
            }
            if len == 0 { first = index; start = device; }
            past = index.checked_add(1)?;
            len = len.checked_add(words)?;
            covered = next;
            Some(())
        };
        if self.compact {
            for (i, block) in self.active.iter().enumerate() {
                append(i, block.device, block.len)?;
            }
        } else {
            let nh = solver.spot.hands[p].len();
            for (i, node) in solver.spot.tree.nodes.iter().enumerate() {
                if node.kind == KIND_ACTION && node.player as usize == p {
                    append(i, usize::try_from(node.data_offset).ok()?,
                        (node.num_children as usize).checked_mul(nh)?)?;
                }
            }
        }
        drop(append);
        if covered != self.len || len == 0 { return None; }
        chunks.push(ReadbackChunk { first, past, start, len });
        if chunks.len() < 2 { return None; }
        Some(chunks)
    }

    /// Encode only complete nodes whose device words are in this chunk.
    pub(super) fn write_readback_chunk(
        &self, solver: &Solver, p: usize, which: usize, chunk: &ReadbackChunk, data: &[f32],
    ) {
        debug_assert_eq!(chunk.len, data.len());
        let store = if which == 0 { &solver.regrets[p] } else { &solver.strat[p] };
        if self.compact {
            self.active[chunk.first..chunk.past].par_iter().for_each(|block| {
                let off = block.device - chunk.start;
                unsafe { store.write_f32(block.node, block.host, block.len,
                    &data[off..off + block.len]); }
            });
        } else {
            let nh = solver.spot.hands[p].len();
            solver.spot.tree.nodes[chunk.first..chunk.past].par_iter().enumerate()
                .for_each(|(local, node)| {
                    if node.kind == KIND_ACTION && node.player as usize == p {
                        let count = node.num_children as usize * nh;
                        let off = node.data_offset as usize - chunk.start;
                        unsafe { store.write_f32((chunk.first + local) as u32,
                            node.data_offset, count, &data[off..off + count]); }
                    }
                });
        }
    }

    pub(super) fn write_readback_inactive(&self, solver: &Solver, p: usize, which: usize) {
        if !self.compact { return; }
        let store = if which == 0 { &solver.regrets[p] } else { &solver.strat[p] };
        self.inactive.par_iter().for_each(|block| {
            let start = block.initial[which];
            let values = if start == usize::MAX { &self.zeros[..block.len] }
                else { &self.initial[which][start..start + block.len] };
            unsafe { store.write_f32(block.node, block.host, block.len, values); }
        });
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
    fn readback_spot() -> Arc<crate::game::Spot> {
        use crate::{Spot, SpotConfig, StreetSizing, TreeConfig, parse_sizes};
        let sizing = || StreetSizing { bet: parse_sizes("50").unwrap(), raise: vec![], donk: vec![] };
        Arc::new(Spot::new_with_limit(SpotConfig {
            board: "KsQs2dJd".into(),
            range_oop: "AA,KK,QQ,JJ,AKs,AQs,AKo".into(),
            range_ip: "AA,QQ,TT,77,AQs,KQs,AQo".into(),
            tree: TreeConfig { starting_pot: 10.0, effective_stack: 20.0,
                oop: [sizing(), sizing(), sizing()], ip: [sizing(), sizing(), sizing()],
                ..Default::default() },
        }, Some(20_000)).unwrap())
    }

    fn assert_raw_stores_equal(a: &Solver, b: &Solver) {
        for (left, right) in a.regrets.iter().chain(&a.strat).zip(b.regrets.iter().chain(&b.strat)) {
            match (left, right) {
                (Store::I16 { q: lq, scale: ls }, Store::I16 { q: rq, scale: rs }) => {
                    assert_eq!(lq.as_slice(), rq.as_slice());
                    assert_eq!(ls.as_slice().iter().map(|x| x.to_bits()).collect::<Vec<_>>(),
                        rs.as_slice().iter().map(|x| x.to_bits()).collect::<Vec<_>>());
                }
                (Store::U16 { q: lq, scale: ls }, Store::U16 { q: rq, scale: rs }) => {
                    assert_eq!(lq.as_slice(), rq.as_slice());
                    assert_eq!(ls.as_slice().iter().map(|x| x.to_bits()).collect::<Vec<_>>(),
                        rs.as_slice().iter().map(|x| x.to_bits()).collect::<Vec<_>>());
                }
                _ => panic!("compressed stores required"),
            }
        }
    }

    #[test]
    fn readback_chunks_match_full_encoding_and_inactive_restore() {
        let spot = readback_spot();
        for iso in [false, true] {
            let mut original = Solver::with_storage(spot.clone(), crate::store::Storage::Compressed);
            let mut chunked = Solver::with_storage(spot.clone(), crate::store::Storage::Compressed);
            original.use_isomorphism = iso; chunked.use_isomorphism = iso;
            let plan = GpuPlan::build(&spot, iso);
            for p in 0..2 {
                let mut layout = ArenaLayout::new(&original, &plan, p);
                assert_eq!(layout.compact, iso);
                for block in &mut layout.inactive {
                    for which in 0..2 {
                        block.initial[which] = layout.initial[which].len();
                        layout.initial[which].extend((0..block.len).map(|i|
                            if i % 7 == 0 { -0.0 } else { (i as f32 - 13.0) * 0.125 }));
                    }
                }
                let window = layout.len / 2;
                let chunks = layout.readback_chunks(&original, p, window, 8, 1).unwrap();
                assert!(chunks.len() >= 2 && chunks.len() <= 16);
                assert_eq!(chunks[0].start, 0);
                assert_eq!(chunks.last().unwrap().start + chunks.last().unwrap().len, layout.len);
                for pair in chunks.windows(2) { assert_eq!(pair[0].start + pair[0].len, pair[1].start); }
                for chunk in &chunks { assert!(chunk.len <= window && chunk.first < chunk.past); }
                let values: Vec<f32> = (0..layout.len).map(|i|
                    if i % 23 == 0 { -0.0 } else { ((i % 97) as f32 - 45.0) * 0.125 }).collect();
                for which in 0..2 {
                    layout.write(&original, p, which, &values);
                    for chunk in &chunks {
                        layout.write_readback_chunk(&chunked, p, which, chunk,
                            &values[chunk.start..chunk.start + chunk.len]);
                    }
                    layout.write_readback_inactive(&chunked, p, which);
                    assert_raw_stores_equal(&original, &chunked);
                }
            }
        }
    }

    #[test]
    fn readback_chunks_decline_small_or_invalid_geometry() {
        let spot = readback_spot();
        let solver = Solver::with_storage(spot.clone(), crate::store::Storage::Compressed);
        for iso in [false, true] {
            let plan = GpuPlan::build(&spot, iso);
            let mut layout = ArenaLayout::new(&solver, &plan, 0);
            let window = layout.len / 2;
            assert!(layout.readback_chunks(&solver, 0, window, 0, 1).is_none());
            assert!(layout.readback_chunks(&solver, 0, window, usize::MAX, 1).is_none());
            assert!(layout.readback_chunks(&solver, 0, 1, 8, 1).is_none());
            assert!(layout.readback_chunks(&solver, 0, window, 8, layout.len).is_none());
            assert!(layout.readback_chunks(&solver, 0, window, 8, 1).is_some());
            if layout.compact { layout.active[0].device += 1; } else { layout.len += 1; }
            assert!(layout.readback_chunks(&solver, 0, window, 8, 1).is_none());
        }
    }

}

// Test-only differential and queued-copy lifetime control for E040.
#[cfg(test)]
mod e040_readback_control {
    use super::*;
    use super::super::{GpuSolver, ReadbackPolicy, READBACK_DRAIN_CALLS};
    use crate::{Spot, SpotConfig, StreetSizing, TreeConfig, parse_sizes};
    use crate::store::Storage;
    use cudarc::driver::sys;
    use serde_json::{json, Value};
    use std::io::{BufWriter, Write};
    use std::path::{Path, PathBuf};
    use std::sync::atomic::Ordering;
    type R<T> = Result<T, String>;

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
                let _ = writeln!(std::io::stderr().lock(), "E040_CONTROL_CLEANUP_ERROR {error}");
            }
        }
    }

    // The exact accepted serial method is inserted here by preparation.py.
    fn legacy_sync(gpu: &mut GpuSolver, solver: &mut Solver) -> Result<(), String> {
        gpu.stream.synchronize().map_err(e)?;
        for p in 0..2 {
            let len = gpu.d_regrets[p].len();
            gpu.stream
                .memcpy_dtoh(&gpu.d_regrets[p], &mut gpu.h_staging.as_mut_slice()[..len])
                .map_err(e)?;
            gpu.stream.synchronize().map_err(e)?;
            gpu.arena_layout[p].write(solver, p, 0, &gpu.h_staging.as_slice()[..len]);
            gpu.stream
                .memcpy_dtoh(&gpu.d_strat[p], &mut gpu.h_staging.as_mut_slice()[..len])
                .map_err(e)?;
            gpu.stream.synchronize().map_err(e)?;
            gpu.arena_layout[p].write(solver, p, 1, &gpu.h_staging.as_slice()[..len]);
        }
        solver.iteration = gpu.iteration;
        if gpu.iso_active {
            // only representative branches hold fresh data; queries/saves
            // re-materialize siblings via Solver::ensure_symmetric
            solver.mark_sym_dirty();
        }
        Ok(())
    }


    fn u32_word(out: &mut Vec<u8>, v: u32) { out.extend(v.to_le_bytes()); }
    fn u64_word(out: &mut Vec<u8>, v: u64) { out.extend(v.to_le_bytes()); }
    fn host_image(s: &Solver) -> Vec<u8> {
        let mut out = b"E040HOST1".to_vec();
        u64_word(&mut out, s.iteration as u64);
        out.push(u8::from(s.use_isomorphism));
        for store in [&s.regrets[0], &s.regrets[1], &s.strat[0], &s.strat[1]] {
            match store {
                Store::F32(b) => {
                    u32_word(&mut out, 0); u64_word(&mut out, b.len() as u64);
                    for v in b.as_slice() { u32_word(&mut out, v.to_bits()); }
                }
                Store::I16 { q, scale } => {
                    u32_word(&mut out, 1); u64_word(&mut out, q.len() as u64);
                    for v in q.as_slice() { out.extend(v.to_le_bytes()); }
                    u64_word(&mut out, scale.len() as u64);
                    for v in scale.as_slice() { u32_word(&mut out, v.to_bits()); }
                }
                Store::U16 { q, scale } => {
                    u32_word(&mut out, 2); u64_word(&mut out, q.len() as u64);
                    for v in q.as_slice() { out.extend(v.to_le_bytes()); }
                    u64_word(&mut out, scale.len() as u64);
                    for v in scale.as_slice() { u32_word(&mut out, v.to_bits()); }
                }
            }
        }
        out
    }
    fn seed(s: &mut Solver, salt: usize) {
        for (which, store) in s.regrets.iter_mut().chain(&mut s.strat).enumerate() {
            match store {
                Store::F32(b) => {
                    for (i,v) in b.as_mut_slice().iter_mut().enumerate() {
                        *v = ((i * 73 + which * 997 + salt) % 1009 + 1) as f32 / 32.0;
                        if which < 2 && i % 3 == 0 { *v = -*v; }
                    }
                }
                Store::I16 { q, scale } => {
                    for (i,v) in q.as_mut_slice().iter_mut().enumerate() {
                        *v = ((i * 73 + which * 997 + salt) % 60001) as i32 as i16;
                    }
                    for (i,v) in scale.as_mut_slice().iter_mut().enumerate() {
                        *v = ((i + which * 7 + salt) % 127 + 1) as f32 / 32.0;
                    }
                }
                Store::U16 { q, scale } => {
                    for (i,v) in q.as_mut_slice().iter_mut().enumerate() {
                        *v = ((i * 71 + which * 991 + salt) % 65535 + 1) as u16;
                    }
                    for (i,v) in scale.as_mut_slice().iter_mut().enumerate() {
                        *v = ((i + which * 11 + salt) % 131 + 1) as f32 / 128.0;
                    }
                }
            }
        }
        s.iteration = if salt == 1 { 0 } else { 999 };
    }
    fn target(spot: &Arc<Spot>, storage: Storage, iso: bool) -> Solver {
        let mut s = Solver::with_storage(spot.clone(), storage);
        s.use_isomorphism = iso;
        seed(&mut s, 37);
        s
    }
    fn query_image(s: &Solver) -> Vec<u8> {
        let mut out = b"E040QUERY1".to_vec();
        let mut nonuniform = false;
        for (id,node) in s.spot.tree.nodes.iter().enumerate() {
            if node.kind != KIND_ACTION { continue; }
            let nh = s.spot.hands[node.player as usize].len();
            let mut sigma = vec![f32::NAN; nh * node.num_children as usize];
            s.solved_strategy_into(node, &mut sigma);
            u32_word(&mut out, id as u32);
            u64_word(&mut out, sigma.len() as u64);
            if node.num_children > 1 {
                nonuniform |= (0..nh).any(|i| sigma[i].to_bits() != sigma[nh+i].to_bits());
            }
            assert!(sigma.iter().all(|x| x.is_finite()));
            for v in sigma { u32_word(&mut out, v.to_bits()); }
        }
        assert!(nonuniform, "query must exercise nonuniform strategy");
        out
    }
    fn device_image(gpu: &GpuSolver) -> R<Vec<u8>> {
        gpu.synchronize()?;
        let mut out = b"E040GPU1".to_vec();
        for d in [&gpu.d_regrets[0],&gpu.d_regrets[1],&gpu.d_strat[0],&gpu.d_strat[1]] {
            let v = gpu.stream.clone_dtoh(d).map_err(e)?;
            assert!(v.iter().all(|x| x.is_finite()));
            assert!(v.windows(2).any(|x| x[0].to_bits() != x[1].to_bits()));
            u64_word(&mut out, v.len() as u64);
            for x in v { u32_word(&mut out, x.to_bits()); }
        }
        Ok(out)
    }
    fn retain(dir: &Path, name: &str, bytes: &[u8], files: &mut Vec<Value>) -> R<()> {
        let file = std::fs::OpenOptions::new().write(true).create_new(true).open(dir.join(name)).map_err(e)?;
        let mut w = BufWriter::new(file);
        w.write_all(bytes).map_err(e)?; w.flush().map_err(e)?; w.get_ref().sync_all().map_err(e)?;
        files.push(json!({"file":name,"bytes":bytes.len()})); Ok(())
    }
    fn pair(dir: &Path, label: &str, a: Vec<u8>, b: Vec<u8>, files: &mut Vec<Value>) -> R<()> {
        retain(dir,&format!("{label}.reference.bin"),&a,files)?;
        retain(dir,&format!("{label}.candidate.bin"),&b,files)?;
        assert_eq!(a,b,"{label}"); Ok(())
    }
    fn saves(dir: &Path, label: &str, a: &Solver, b: &Solver, files: &mut Vec<Value>) -> R<()> {
        let mut bytes = Vec::new();
        for (arm,s) in [("reference",a),("candidate",b)] {
            let name = format!("{label}.{arm}.save");
            let path = dir.join(&name);
            assert!(!path.exists() && !path.with_extension("save.tmp").exists());
            s.save(path.to_str().ok_or("output encoding")?)?;
            let raw = std::fs::read(path).map_err(e)?;
            files.push(json!({"file":name,"bytes":raw.len()})); bytes.push(raw);
        }
        assert_eq!(bytes[0],bytes[1]); Ok(())
    }
    fn geometry(g: &GpuSolver) -> (usize,usize,[usize;4]) {
        (g.h_staging.ptr as usize,g.h_staging.len,
         [g.d_regrets[0].len(),g.d_regrets[1].len(),g.d_strat[0].len(),g.d_strat[1].len()])
    }
    fn run_case(dir: &Path, storage: Storage, iso: bool) -> R<Value> {
        let size = StreetSizing { bet:parse_sizes("50")?,raise:vec![],donk:vec![] };
        let spot = Arc::new(Spot::new_with_limit(SpotConfig {
            board:"KsQs2dJd".into(),range_oop:"AA,KK,QQ,JJ,AKs,AQs,AKo".into(),
            range_ip:"AA,QQ,TT,77,AQs,KQs,AQo".into(),
            tree:TreeConfig { starting_pot:10.0,effective_stack:20.0,
                oop:[size.clone(),size.clone(),size.clone()],ip:[size.clone(),size.clone(),size],
                ..Default::default() },
        },Some(20_000))?);
        assert!(spot.tree.data_size.iter().sum::<u64>() <= 250_000);
        let mut input = Solver::with_storage(spot.clone(),storage);
        input.use_isomorphism = iso; seed(&mut input,1);
        let plan = GpuPlan::build(&spot,iso);
        if iso {
            let mut inactive_ordinal = [0usize;2];
            for (i,node) in spot.tree.nodes.iter().enumerate() {
                if node.kind == KIND_ACTION && plan.node_data_off[i] == u64::MAX {
                    let p = node.player as usize;
                    inactive_ordinal[p] += 1;
                    if inactive_ordinal[p] % 2 != 0 { continue; }
                    let count = node.num_children as usize * spot.hands[p].len();
                    for store in [&input.regrets[p],&input.strat[p]] {
                        unsafe { store.write_f32(i as u32,node.data_offset,count,&vec![0.0;count]); }
                    }
                    if let Store::F32(b) = &input.regrets[p] {
                        unsafe { b.write_at(node.data_offset as usize,-0.0); }
                    }
                }
            }
        }
        let budget = if storage == Storage::F32 && iso {
            plan.staging_bytes() + (plan.arena_elements[0]+plan.arena_elements[1]) as u64 * 8 + 512*1024*1024
        } else { u64::MAX };
        let mut gpu = DrainOnDrop(GpuSolver::new_with_budget(&input,budget)?);
        let owner = gpu._ctx.clone();
        for p in 0..2 {
            assert_eq!(gpu.arena_layout[p].compact,iso);
            if iso {
                assert!(!gpu.arena_layout[p].inactive.is_empty());
                assert!(!gpu.arena_layout[p].initial[0].is_empty());
                assert!(!gpu.arena_layout[p].initial[1].is_empty());
                assert!(gpu.arena_layout[p].inactive.iter().any(|b| b.initial[1] == usize::MAX));
            }
        }
        let shape = geometry(&gpu);
        let mut files = Vec::new();
        retain(dir,"input.host.bin",&host_image(&input),&mut files)?;
        for _ in 0..4 { gpu.iterate()?; }
        let before = device_image(&gpu)?;
        retain(dir,"trained.gpu.bin",&before,&mut files)?;
        let mut reference = target(&spot,storage,iso);
        let mut candidate = target(&spot,storage,iso);
        let poisoned = host_image(&candidate);
        retain(dir,"poisoned.host.bin",&poisoned,&mut files)?;
        assert_eq!(poisoned,host_image(&reference));
        legacy_sync(&mut gpu,&mut reference)?;
        let forced = ReadbackPolicy { pieces:8,min_words:1,fault:None };
        let count = gpu.sync_to_cpu_policy(&mut candidate,forced)?;
        assert_eq!(count,if storage == Storage::Compressed {4} else {0});
        let first = host_image(&reference);
        pair(dir,"first.host",first.clone(),host_image(&candidate),&mut files)?;
        pair(dir,"first.query",query_image(&reference),query_image(&candidate),&mut files)?;
        saves(dir,"first",&reference,&candidate,&mut files)?;
        assert_eq!(host_image(&reference),first); assert_eq!(host_image(&candidate),first);
        reference.ensure_symmetric(); candidate.ensure_symmetric();
        let materialized = host_image(&reference);
        pair(dir,"materialized.host",materialized.clone(),host_image(&candidate),&mut files)?;
        if iso { assert_ne!(materialized,first); }
        pair(dir,"materialized.query",query_image(&reference),query_image(&candidate),&mut files)?;
        saves(dir,"materialized",&reference,&candidate,&mut files)?;
        legacy_sync(&mut gpu,&mut reference)?;
        assert_eq!(gpu.sync_to_cpu_policy(&mut candidate,forced)?,count);
        pair(dir,"repeat.host",host_image(&reference),host_image(&candidate),&mut files)?;
        assert_eq!(host_image(&candidate),first);
        // A normal tiny production workload must retain the serial fallback.
        let mut default_target = target(&spot,storage,iso);
        assert_eq!(gpu.sync_to_cpu_policy(&mut default_target,ReadbackPolicy::default())?,0);
        pair(dir,"default.host",first.clone(),host_image(&default_target),&mut files)?;
        let mut mixed_count = None;
        if storage == Storage::Compressed {
            let targets = [gpu.d_regrets[0].len().div_ceil(8),gpu.d_regrets[1].len().div_ceil(8)];
            assert_ne!(targets[0],targets[1]);
            let gate = targets[0].min(targets[1])+1;
            let mut mixed = target(&spot,storage,iso);
            let n = gpu.sync_to_cpu_policy(&mut mixed,ReadbackPolicy { min_words:gate,..forced })?;
            assert_eq!(n,2); mixed_count = Some(n);
            pair(dir,"mixed.host",first.clone(),host_image(&mixed),&mut files)?;
        }
        let mut faults = Vec::new();
        if storage == Storage::Compressed {
            for (ordinal,panic) in [(1,false),(2,true)] {
                let mut fault_target = target(&spot,storage,iso);
                let untouched = host_image(&fault_target);
                let drain_before = READBACK_DRAIN_CALLS.load(Ordering::SeqCst);
                let result = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
                    gpu.sync_to_cpu_policy(&mut fault_target,ReadbackPolicy {fault:Some((ordinal,panic)),..forced})
                }));
                if panic { assert!(result.is_err()); }
                else { assert_eq!(result.unwrap().unwrap_err(),"injected readback error after first queue"); }
                assert_eq!(READBACK_DRAIN_CALLS.load(Ordering::SeqCst),drain_before+1);
                // Query completion before any other synchronize/device inspection.
                owner.bind_to_thread().map_err(e)?;
                let ready = unsafe { sys::cuStreamQuery(gpu.stream.cu_stream()) };
                assert_eq!(ready,sys::CUresult::CUDA_SUCCESS);
                pair(dir,&format!("fault{ordinal}.host"),untouched,host_image(&fault_target),&mut files)?;
                let after_fault = device_image(&gpu)?;
                retain(dir,&format!("fault{ordinal}.gpu.bin"),&after_fault,&mut files)?;
                assert_eq!(after_fault,before);
                assert_eq!(gpu.sync_to_cpu_policy(&mut fault_target,forced)?,4);
                pair(dir,&format!("fault{ordinal}.reused.host"),first.clone(),host_image(&fault_target),&mut files)?;
                faults.push(json!({"ordinal":ordinal,"panic":panic,"drain_calls":1,"stream_ready_before_extra_sync":true,
                    "cpu_untouched":true,"gpu_unchanged":true,"reused_exact":true}));
            }
        }
        let after = device_image(&gpu)?;
        retain(dir,"final.gpu.bin",&after,&mut files)?; assert_eq!(before,after);
        assert_eq!(geometry(&gpu),shape);
        gpu.synchronize()?; drop(gpu); owner.check_err().map_err(e)?;
        let bytes: u64 = files.iter().map(|v| v["bytes"].as_u64().unwrap()).sum();
        assert!(bytes <= 32*1024*1024);
        Ok(json!({"storage":format!("{storage:?}"),"compact":iso,"nodes":spot.tree.nodes.len(),
            "host_elements":spot.tree.data_size,"device_elements":shape.2,"staging_words":shape.1,
            "forced_pipelined_arenas":count,"default_pipelined_arenas":0,"mixed_pipelined_arenas":mixed_count,
            "training_iterations":4,"full_raw_equality":true,"query_save_exact":true,
            "materialization_changed_host":materialized!=first,"repeat_restores_first":true,
            "staging_identity_and_device_lengths_unchanged":true,"faults":faults,
            "cleanup_complete":true,"output_bytes":bytes,"files":files}))
    }

    #[test]
    #[ignore = "root-only E040 async readback differential and drain control; CUDA and fresh E040_CONTROL_DIR required"]
    fn exact_readback_overlap_and_drain() -> R<()> {
        let dir = PathBuf::from(std::env::var_os("E040_CONTROL_DIR").ok_or("E040_CONTROL_DIR missing")?);
        std::fs::create_dir(&dir).map_err(e)?;
        let mut cases = Vec::new();
        for (name,storage,iso) in [("compressed-full",Storage::Compressed,false),
            ("compressed-compact",Storage::Compressed,true),("f32-full",Storage::F32,false),
            ("f32-compact",Storage::F32,true)] {
            let path = dir.join(name); std::fs::create_dir(&path).map_err(e)?;
            let result = run_case(&path,storage,iso)?;
            println!("E040_READBACK_CONTROL {}",json!({"stage":"case_complete","name":name,"result":result}));
            cases.push(result);
        }
        let summary = json!({"id":"E040-control","stage":"complete","cases":cases,
            "performance_measured":false,"candidate_accepted":false});
        retain(&dir,"evidence.json",&serde_json::to_vec_pretty(&summary).map_err(e)?,&mut Vec::new())?;
        println!("E040_READBACK_CONTROL {summary}"); Ok(())
    }
}
