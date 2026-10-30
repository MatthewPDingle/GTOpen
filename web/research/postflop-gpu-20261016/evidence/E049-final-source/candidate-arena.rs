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
        // Both inputs must prove positive-zero decoded bits: a negative q
        // with +0 scale, or a zero q with -0 scale, can decode to -0.0.
        // Check scales first so a warm arena can reject this path cheaply.
        let zero = match store {
            Store::I16 { q, scale } => {
                scale.as_slice().iter().all(|v| v.to_bits() == 0)
                    && (q.is_unexposed_default() || q.as_slice().iter().fold(0u16, |bits, &v| bits | v as u16) == 0)
            }
            Store::U16 { q, scale } => {
                scale.as_slice().iter().all(|v| v.to_bits() == 0)
                    && (q.is_unexposed_default() || q.as_slice().iter().fold(0u16, |bits, &v| bits | v) == 0)
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
}

#[cfg(test)]
mod provenance_predicate_tests {
    use super::*;

    fn original(layout: &ArenaLayout, store: &Store, which: usize) -> bool {
        let zero = match store {
            Store::I16 { q, scale } => scale.as_slice().iter().all(|v| v.to_bits() == 0)
                && q.as_slice().iter().fold(0u16, |bits, &v| bits | v as u16) == 0,
            Store::U16 { q, scale } => scale.as_slice().iter().all(|v| v.to_bits() == 0)
                && q.as_slice().iter().fold(0u16, |bits, &v| bits | v) == 0,
            Store::F32(_) => false,
        };
        zero && layout.initial[which].is_empty()
            && layout.inactive.iter().all(|b| b.initial[which] == usize::MAX)
    }

    #[test]
    fn untouched_and_exposed_predicates_match_original_scan() {
        let scales = [0, 0x80000000, 1, 0x80000001, 0x3f800000, 0xbf800000,
            0x7f800000, 0xff800000, 0x7fc00123, 0xffc00123];
        let mut cases = 0;
        let mut no_scan_witnesses = 0;
        for len in [0u64, 1, 3, 64, 4097] {
            for signed in [false, true] {
                for access in 0..7 {
                    for &scale_bits in &scales {
                        for snapshot in 0..4 {
                            let mut store = if signed { Store::i16(len, 2) } else { Store::u16(len, 2) };
                            macro_rules! prepare {
                                ($q:expr, $s:expr) => {{
                                    $s.as_mut_slice()[1] = f32::from_bits(scale_bits);
                                    match access {
                                        0 => {},
                                        1 => { let _ = $q.as_slice().as_ptr(); },
                                        2 => { $q.as_mut_slice().fill(0); },
                                        3 => { unsafe { $q.slice(0, len as usize).fill(0); } },
                                        4 if len > 0 => { unsafe { $q.write_at(len as usize - 1, 1); } },
                                        5 if len > 0 => { unsafe { $q.write_at(0, 1); $q.write_at(0, 0); } },
                                        6 if len > 0 => { unsafe { let _ = $q.read_at(0); } },
                                        _ => {},
                                    }
                                }};
                            }
                            match &mut store {
                                Store::I16 { q, scale } => prepare!(q, scale),
                                Store::U16 { q, scale } => prepare!(q, scale),
                                _ => unreachable!(),
                            }
                            let mut layout = ArenaLayout {
                                compact: true, len: len as usize, active: Vec::new(), copies: Vec::new(),
                                inactive: vec![InactiveBlock { node: 0, host: 0, len: 0, initial: [usize::MAX; 2] }],
                                initial: [Vec::new(), Vec::new()], zeros: Vec::new(),
                            };
                            if snapshot & 1 != 0 { layout.initial[0].push(-0.0); }
                            if snapshot & 2 != 0 { layout.inactive[0].initial[0] = 0; }
                            // Candidate must run first: the reference scan exposes q.
                            let pristine = match &store {
                                Store::I16 { q, .. } => q.is_unexposed_default(),
                                Store::U16 { q, .. } => q.is_unexposed_default(), _ => false,
                            };
                            for which in 0..2 {
                                let got = layout.can_upload_zeros(&store, which);
                                let still_pristine = match &store {
                                    Store::I16 { q, .. } => q.is_unexposed_default(),
                                    Store::U16 { q, .. } => q.is_unexposed_default(), _ => false,
                                };
                                if which == 0 && pristine && scale_bits == 0 {
                                    assert!(still_pristine, "fast-path must not expose q");
                                    no_scan_witnesses += 1;
                                }
                                assert_eq!(got, original(&layout, &store, which));
                                cases += 1;
                            }
                        }
                    }
                }
            }
        }
        assert_eq!(cases, 5600);
        assert!(no_scan_witnesses > 0);
        println!("E049_PREDICATE cases={cases} no_scan_witnesses={no_scan_witnesses}");
    }
}
