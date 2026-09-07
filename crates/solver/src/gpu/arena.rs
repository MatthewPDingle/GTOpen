//! Exact host mapping for GPU arenas containing only visited action nodes.
use super::{e, plan::GpuPlan, write_arena};
use crate::{cfr::Solver, store::Store, tree::KIND_ACTION};
use cudarc::driver::{CudaSlice, CudaStream};
use std::sync::Arc;

struct ActiveBlock {
    node: u32,
    host: u64,
    device: usize,
    len: usize,
}

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
            compact, len, active: Vec::new(), inactive: Vec::new(),
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
        }
        layout
    }

    pub(super) fn upload(
        &mut self, stream: &Arc<CudaStream>, solver: &Solver, p: usize, which: usize,
    ) -> Result<CudaSlice<f32>, String> {
        let store = if which == 0 { &solver.regrets[p] } else { &solver.strat[p] };
        if !self.compact {
            return match store {
                Store::F32(b) => stream.clone_htod(b.as_slice()).map_err(e),
                _ => stream.clone_htod(&solver.arena_to_f32(store, p)).map_err(e),
            };
        }
        let mut packed = vec![0.0; self.len];
        for block in &self.active {
            unsafe {
                store.read_f32(block.node, block.host, block.len,
                    &mut packed[block.device..block.device + block.len]);
            }
        }
        let mut scratch = vec![0.0; self.zeros.len()];
        for block in &mut self.inactive {
            let values = &mut scratch[..block.len];
            unsafe { store.read_f32(block.node, block.host, block.len, values); }
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
        stream.clone_htod(&packed).map_err(e)
    }

    pub(super) fn write(&self, solver: &Solver, p: usize, which: usize, data: &[f32]) {
        if !self.compact {
            write_arena(solver, which != 0, p, data);
            return;
        }
        let store = if which == 0 { &solver.regrets[p] } else { &solver.strat[p] };
        for block in &self.active {
            unsafe {
                store.write_f32(block.node, block.host, block.len,
                    &data[block.device..block.device + block.len]);
            }
        }
        for block in &self.inactive {
            let start = block.initial[which];
            let values = if start == usize::MAX { &self.zeros[..block.len] }
                else { &self.initial[which][start..start + block.len] };
            unsafe { store.write_f32(block.node, block.host, block.len, values); }
        }
    }
}
