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

// Each output chunk owns a disjoint range. Splitting an encoded node is exact:
// read_f32 applies that node's unchanged scale independently to every entry.
fn decode_blocks(store: &Store, blocks: &[ActiveBlock], data: &mut [f32]) {
    if data.len() < 262_144 {
        for block in blocks {
            unsafe { store.read_f32(block.node, block.host, block.len,
                &mut data[block.device..block.device + block.len]); }
        }
        return;
    }
    const CHUNK: usize = 65_536;
    data.par_chunks_mut(CHUNK).enumerate().for_each(|(index, output)| {
        let begin = index * CHUNK;
        let mut block_index = blocks.partition_point(|b| b.device + b.len <= begin);
        let mut written = 0;
        while written < output.len() {
            let block = &blocks[block_index];
            let offset = begin + written - block.device;
            let len = (block.len - offset).min(output.len() - written);
            // Both encoded input entries and decoded output entries are disjoint
            // across chunks; scale reads are immutable, including split nodes.
            unsafe { store.read_f32(block.node, block.host + offset as u64, len,
                &mut output[written..written + len]); }
            written += len;
            block_index += 1;
        }
    });
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

    pub(super) fn upload(
        &mut self, stream: &Arc<CudaStream>, solver: &Solver, p: usize, which: usize,
        staging: &mut [f32],
    ) -> Result<CudaSlice<f32>, String> {
        let store = if which == 0 { &solver.regrets[p] } else { &solver.strat[p] };
        if !self.compact {
            if let Store::F32(b) = store {
                return stream.clone_htod(b.as_slice()).map_err(e);
            }
            // Decode directly into the reusable pinned allocation. A full
            // temporary f32 image would duplicate this buffer for each upload.
            let data = &mut staging[..self.len];
            let nh = solver.spot.hands[p].len();
            if data.len() < 262_144 {
                for (i, node) in solver.spot.tree.nodes.iter().enumerate() {
                    if node.kind == KIND_ACTION && node.player as usize == p {
                        let len = node.num_children as usize * nh;
                        let off = node.data_offset as usize;
                        unsafe { store.read_f32(i as u32, node.data_offset, len, &mut data[off..off + len]); }
                    }
                }
            } else {
                let blocks: Vec<_> = solver.spot.tree.nodes.iter().enumerate()
                    .filter(|(_, n)| n.kind == KIND_ACTION && n.player as usize == p)
                    .map(|(i, n)| ActiveBlock { node: i as u32, host: n.data_offset,
                        device: n.data_offset as usize, len: n.num_children as usize * nh })
                    .collect();
                decode_blocks(store, &blocks, data);
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
            decode_blocks(store, &self.active, packed);
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
    #[test]
    fn chunked_decode_preserves_node_scales_and_host_gaps() {
        let blocks = [
            ActiveBlock { node: 0, host: 37, device: 0, len: 101_003 },
            ActiveBlock { node: 1, host: 103_079, device: 101_003, len: 173_009 },
        ];
        for signed in [false, true] {
            let store = if signed { Store::i16(300_000, 2) } else { Store::u16(300_000, 2) };
            for block in &blocks {
                let values: Vec<_> = (0..block.len).map(|i| {
                    let magnitude = (i % 17) as f32 * if block.node == 0 { 0.1 } else { 137.0 };
                    if signed && i % 3 == 0 { -magnitude } else { magnitude }
                }).collect();
                unsafe { store.write_f32(block.node, block.host, block.len, &values); }
            }
            let mut expected = vec![0f32; 274_012];
            for block in &blocks {
                unsafe { store.read_f32(block.node, block.host, block.len,
                    &mut expected[block.device..block.device + block.len]); }
            }
            let mut actual = vec![0f32; expected.len()];
            decode_blocks(&store, &blocks, &mut actual);
            assert!(actual.iter().zip(&expected).all(|(a, b)| a.to_bits() == b.to_bits()));
            let mut small = vec![0f32; blocks[0].len];
            decode_blocks(&store, &blocks[..1], &mut small);
            assert!(small.iter().zip(&expected).all(|(a, b)| a.to_bits() == b.to_bits()));
        }
    }
}
