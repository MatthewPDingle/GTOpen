//! Exact host mapping for GPU arenas containing only visited action nodes.
use super::{e, plan::GpuPlan, write_arena};
use crate::{cfr::Solver, store::Store, tree::KIND_ACTION};
use cudarc::driver::{CudaSlice, CudaStream};
use std::sync::Arc;
use rayon::prelude::*;

#[derive(Clone, Copy)]
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
        if self.len > staging.len()
            && (self.compact || !matches!(store, Store::F32(_))) {
            return self.upload_bounded(stream, solver, p, which, staging);
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

pub(super) const PINNED_WORD_LIMIT: usize = 64 * 1024 * 1024 / 4;

#[derive(Clone, Copy, Debug)]
struct TransferGroup { first: usize, end: usize, device: usize, len: usize }

fn next_transfer_group(blocks:&[ActiveBlock],first:usize,capacity:usize)->Result<Option<TransferGroup>,String>{
 if first==blocks.len(){return Ok(None)}
 if first>blocks.len(){return Err("first beyond blocks".into())}
 let base=blocks[first].device;let mut len=0usize;let mut end=first;
 while end<blocks.len(){
  let b=blocks[end];
  if b.device!=base.checked_add(len).ok_or("device overflow")?{return Err("device gap/overlap".into())}
  if b.len>capacity{return Err("row exceeds capacity".into())}
  let combined=len.checked_add(b.len).ok_or("length overflow")?;
  if combined>capacity{break}
  len=combined;end+=1;
 }
 if end==first{return Err("no progress".into())}
 Ok(Some(TransferGroup{first,end,device:base,len}))
}

fn finish_bounded_copy(
    stream: &Arc<CudaStream>,
    copy: Result<(), cudarc::driver::DriverError>,
) -> Result<(), String> {
    // Always retire a possibly submitted copy before staging reuse or an
    // error return. Preserve the original copy error when both calls fail.
    let ready = stream.synchronize().map_err(e);
    copy.map_err(e)?;
    ready
}

impl ArenaLayout {
    pub(super) fn prepare_bounded(
        &mut self, solver: &Solver, p: usize, limit: usize,
    ) -> Result<usize, String> {
        if self.len <= limit { return Ok(self.len); }
        if !self.compact {
            self.active.clear();
            let nh = solver.spot.hands[p].len();
            for (i, node) in solver.spot.tree.nodes.iter().enumerate() {
                if node.kind != KIND_ACTION || node.player as usize != p { continue; }
                self.active.push(ActiveBlock {
                    node: i as u32, host: node.data_offset,
                    device: node.data_offset as usize,
                    len: node.num_children as usize * nh,
                });
            }
        }
        self.check_bounded(usize::MAX)?;
        let largest = self.active.iter().map(|b| b.len).max().unwrap_or(0);
        Ok(self.len.min(limit).max(largest))
    }

    pub(super) fn discard_bounded(&mut self) {
        if !self.compact { self.active = Vec::new(); }
    }

    fn check_bounded(&self, capacity: usize) -> Result<(), String> {
        let mut cursor = 0usize;
        for block in &self.active {
            if block.device != cursor { return Err("bounded arena has a gap or overlap".into()); }
            if block.len > capacity { return Err("bounded staging cannot hold a node".into()); }
            cursor = cursor.checked_add(block.len).ok_or("bounded arena length overflow")?;
        }
        if cursor != self.len { return Err("bounded arena has incomplete coverage".into()); }
        Ok(())
    }

    fn copy_spans_in(&self, start: usize, end: usize) -> &[CopySpan] {
        if start == end { return &self.copies[..0]; }
        let first = self.copies.partition_point(|s| s.device + s.len <= start);
        let last = self.copies.partition_point(|s| s.device < end);
        &self.copies[first..last]
    }

    fn read_bounded_group(&self, store: &Store, group: TransferGroup, data: &mut [f32]) {
        if let Store::F32(buf) = store {
            if !self.compact {
                data[..group.len].copy_from_slice(
                    &buf.as_slice()[group.device..group.device + group.len]);
            } else {
                for span in self.copy_spans_in(group.device, group.device + group.len) {
                    let first = span.device.max(group.device);
                    let last = (span.device + span.len).min(group.device + group.len);
                    let host = span.host as usize + first - span.device;
                    data[first - group.device..last - group.device]
                        .copy_from_slice(&buf.as_slice()[host..host + last - first]);
                }
            }
        } else {
            for block in &self.active[group.first..group.end] {
                let off = block.device - group.device;
                unsafe {
                    store.read_f32(block.node, block.host, block.len,
                        &mut data[off..off + block.len]);
                }
            }
        }
    }

    fn write_bounded_group(&self, store: &Store, group: TransferGroup, data: &[f32]) {
        if let Store::F32(buf) = store {
            if !self.compact {
                unsafe { buf.slice(group.device as u64, group.len) }
                    .copy_from_slice(&data[..group.len]);
            } else {
                self.copy_spans_in(group.device, group.device + group.len)
                    .par_iter().for_each(|span| {
                        let first = span.device.max(group.device);
                        let last = (span.device + span.len).min(group.device + group.len);
                        let host = span.host + (first - span.device) as u64;
                        unsafe { buf.slice(host, last - first) }
                            .copy_from_slice(&data[first - group.device..last - group.device]);
                    });
            }
        } else {
            self.active[group.first..group.end].par_iter().for_each(|block| {
                let off = block.device - group.device;
                unsafe {
                    store.write_f32(block.node, block.host, block.len,
                        &data[off..off + block.len]);
                }
            });
        }
    }

    fn capture_bounded_inactive(&mut self, store: &Store, which: usize) {
        if !self.compact { return; }
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
    }

    fn restore_bounded_inactive(&self, store: &Store, which: usize) {
        if !self.compact { return; }
        if let Store::F32(buf) = store {
            self.inactive.par_iter().for_each(|block| {
                let dst = unsafe { buf.slice(block.host, block.len) };
                let start = block.initial[which];
                if start == usize::MAX { dst.fill(0.0); }
                else { dst.copy_from_slice(&self.initial[which][start..start + block.len]); }
            });
            return;
        }
        self.inactive.par_iter().for_each(|block| {
            let start = block.initial[which];
            let values = if start == usize::MAX { &self.zeros[..block.len] }
                else { &self.initial[which][start..start + block.len] };
            unsafe { store.write_f32(block.node, block.host, block.len, values); }
        });
    }

    fn upload_bounded(
        &mut self, stream: &Arc<CudaStream>, solver: &Solver, p: usize,
        which: usize, staging: &mut [f32],
    ) -> Result<CudaSlice<f32>, String> {
        self.check_bounded(staging.len())?;
        let store = if which == 0 { &solver.regrets[p] } else { &solver.strat[p] };
        self.capture_bounded_inactive(store, which);
        // Coverage is validated before allocation. Every device word is
        // written and drained before this array can reach a solver kernel.
        let mut device = unsafe { stream.alloc::<f32>(self.len) }.map_err(e)?;
        let mut first = 0;
        while let Some(group) = next_transfer_group(&self.active, first, staging.len())? {
            self.read_bounded_group(store, group, staging);
            let copy = stream.memcpy_htod(&staging[..group.len],
                &mut device.slice_mut(group.device..group.device + group.len));
            finish_bounded_copy(stream, copy)?;
            first = group.end;
        }
        Ok(device)
    }

    pub(super) fn download(
        &self, stream: &Arc<CudaStream>, solver: &Solver, p: usize,
        which: usize, device: &CudaSlice<f32>, staging: &mut [f32],
    ) -> Result<(), String> {
        let len = device.len();
        if len <= staging.len() {
            let copy = stream.memcpy_dtoh(device, &mut staging[..len]);
            finish_bounded_copy(stream, copy)?;
            self.write(solver, p, which, &staging[..len]);
            return Ok(());
        }
        if len != self.len { return Err("bounded device arena length mismatch".into()); }
        self.check_bounded(staging.len())?;
        let store = if which == 0 { &solver.regrets[p] } else { &solver.strat[p] };
        let mut first = 0;
        while let Some(group) = next_transfer_group(&self.active, first, staging.len())? {
            let copy = stream.memcpy_dtoh(
                &device.slice(group.device..group.device + group.len),
                &mut staging[..group.len]);
            finish_bounded_copy(stream, copy)?;
            self.write_bounded_group(store, group, &staging[..group.len]);
            first = group.end;
        }
        self.restore_bounded_inactive(store, which);
        Ok(())
    }
}

#[cfg(test)]
mod bounded_tests {
    use super::*;
    #[test]
    fn transfer_groups_keep_whole_nodes_and_reject_invalid_spans() {
        let mut device = 0;
        let blocks: Vec<_> = [0,1,3,0,5,2].into_iter().enumerate().map(|(node,len)| {
            let b=ActiveBlock{node:node as u32,host:device as u64,device,len};
            device+=len;b
        }).collect();
        let mut got=Vec::new();let mut first=0;
        while let Some(g)=next_transfer_group(&blocks,first,5).unwrap() {
            got.push((g.first,g.end,g.device,g.len));first=g.end;
        }
        assert_eq!(got,vec![(0,4,0,4),(4,5,4,5),(5,6,9,2)]);
        assert!(next_transfer_group(&blocks,4,4).is_err());
        let bad=[ActiveBlock{node:0,host:0,device:0,len:1},
            ActiveBlock{node:1,host:1,device:2,len:1}];
        assert!(next_transfer_group(&bad,0,5).is_err());
        assert!(next_transfer_group(&[],0,0).unwrap().is_none());
    }
    #[test]
    fn compact_copy_spans_cover_exact_window_intersections() {
        let l=ArenaLayout{
            compact:true,len:12,active:Vec::new(),inactive:Vec::new(),
            initial:[Vec::new(),Vec::new()],zeros:Vec::new(),
            copies:vec![CopySpan{host:3,device:0,len:5},
                CopySpan{host:20,device:5,len:3},CopySpan{host:30,device:8,len:4}],
        };
        let ranges=[(0,4),(4,9),(9,12)];
        let mut seen=Vec::new();
        for (first,last) in ranges {
            for s in l.copy_spans_in(first,last) {
                for d in s.device.max(first)..(s.device+s.len).min(last) {
                    seen.push((d,s.host+(d-s.device)as u64));
                }
            }
        }
        let expected:Vec<_>=(0..12).map(|d|(d,if d<5{3+d as u64}
            else if d<8{20+(d-5)as u64}else{30+(d-8)as u64})).collect();
        assert_eq!(seen,expected);
        assert!(l.copy_spans_in(5,5).is_empty());
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
