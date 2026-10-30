//! Research-only lossless paging of fully enumerated continuation games.
//! Each caller retains F32 CPU state. One exclusively borrowed workspace is
//! reused across boards; production solvers and captured graphs never use it.
use super::{e, GpuSolver, PinnedBuf};
use crate::{Algorithm, Solver, Spot, store::Store};
use cudarc::driver::CudaSlice;
use std::sync::Arc;

#[derive(Default)]
pub struct ContinuationWorkspace {
    buffers: Option<[CudaSlice<f32>; 7]>,
}

impl ContinuationWorkspace {
    pub fn bytes(&self) -> u64 {
        self.buffers.as_ref().map_or(0, |v| v.iter().map(|x| x.len() as u64 * 4).sum())
    }

    fn absorb(&mut self, buffers: [CudaSlice<f32>; 7]) {
        if let Some(current) = &mut self.buffers {
            for (old, new) in current.iter_mut().zip(buffers) {
                if new.len() > old.len() { *old = new; }
            }
        } else { self.buffers = Some(buffers); }
    }
}

pub struct PagedContinuationGpu {
    gpu: GpuSolver,
    spot: Arc<Spot>,
    lengths: [usize; 7],
    poisoned: bool,
    pub transferred_bytes: u64,
}

// Move all large mutable device allocations while leaving valid small dummies.
fn take(g: &mut GpuSolver) -> Result<[CudaSlice<f32>; 7], String> {
    let mut small = Vec::new();
    for _ in 0..7 { small.push(g.stream.alloc_zeros::<f32>(1).map_err(e)?); }
    let mut small = small.into_iter();
    Ok([
        std::mem::replace(&mut g.d_regrets[0], small.next().unwrap()),
        std::mem::replace(&mut g.d_regrets[1], small.next().unwrap()),
        std::mem::replace(&mut g.d_strat[0], small.next().unwrap()),
        std::mem::replace(&mut g.d_strat[1], small.next().unwrap()),
        std::mem::replace(&mut g.d_reach[0], small.next().unwrap()),
        std::mem::replace(&mut g.d_reach[1], small.next().unwrap()),
        std::mem::replace(&mut g.d_cfv, small.next().unwrap()),
    ])
}

fn swap(g: &mut GpuSolver, buffers: &mut [CudaSlice<f32>; 7]) {
    for (a, b) in g.d_regrets.iter_mut().chain(&mut g.d_strat)
        .chain(&mut g.d_reach).chain(std::iter::once(&mut g.d_cfv)).zip(buffers) {
        std::mem::swap(a, b);
    }
}

impl PagedContinuationGpu {
    fn validate(host: &Solver) -> Result<(), String> {
        if host.use_isomorphism || host.algo != Algorithm::CfrPlus
            || !host.locks.is_empty() || host.preds.is_some()
            || host.regrets.iter().chain(&host.strat).any(|a| !matches!(a, Store::F32(_))) {
            return Err("paged continuation requires unlocked F32 CFR+ and explicit chance".into());
        }
        Ok(())
    }

    pub fn new(host: &Solver, workspace: &mut ContinuationWorkspace) -> Result<Self, String> {
        Self::validate(host)?;
        // Force full action layouts, so host arenas are the sole parked copy.
        // The caller must preflight individual and total resident metadata.
        let mut gpu = GpuSolver::new(host)?;
        gpu.stream.synchronize().map_err(e)?;
        let buffers = take(&mut gpu)?;
        let lengths = std::array::from_fn(|i| buffers[i].len());
        if lengths[0] != host.spot.tree.data_size[0] as usize
            || lengths[1] != host.spot.tree.data_size[1] as usize {
            return Err("paging requires full host/device arena layouts".into());
        }
        // No per-board pinned arena image. Transfers below use the retained
        // F32 host stores and synchronize before their borrow is released.
        gpu.h_staging = PinnedBuf::new(&gpu._ctx, 1)?;
        workspace.absorb(buffers);
        Ok(Self { gpu, spot: host.spot.clone(), lengths, poisoned: false, transferred_bytes: 0 })
    }

    pub fn sweep(&mut self, host: &mut Solver, workspace: &mut ContinuationWorkspace,
                 p: usize, t: u32, own: &[f32], opponent: &[f32]) -> Result<Vec<f32>, String> {
        Self::validate(host)?;
        if self.poisoned || !Arc::ptr_eq(&self.spot, &host.spot) || p > 1 || t == 0 {
            return Err("invalid paged continuation state/player/iteration".into());
        }
        if own.len() != host.spot.hands[p].len() || opponent.len() != host.spot.hands[1-p].len()
            || own.iter().chain(opponent).any(|x| !x.is_finite() || *x < 0.) {
            return Err("invalid paged continuation reaches".into());
        }
        let buffers = workspace.buffers.as_mut().ok_or("missing continuation workspace")?;
        if buffers.iter().zip(self.lengths).any(|(b, len)| b.len() < len) {
            return Err("continuation workspace too small".into());
        }
        swap(&mut self.gpu, buffers);
        let result = (|| {
            for q in 0..2 {
                let Store::F32(r) = &host.regrets[q] else { unreachable!() };
                let Store::F32(s) = &host.strat[q] else { unreachable!() };
                self.gpu.stream.memcpy_htod(r.as_slice(), &mut self.gpu.d_regrets[q].slice_mut(0..self.lengths[q])).map_err(e)?;
                self.gpu.stream.memcpy_htod(s.as_slice(), &mut self.gpu.d_strat[q].slice_mut(0..self.lengths[q+2])).map_err(e)?;
                self.transferred_bytes += (self.lengths[q] + self.lengths[q+2]) as u64 * 4;
            }
            let values = self.gpu.research_continuation_sweep(p, t, own, opponent)?;
            // The traverser alone updates regrets and average sums.
            let Store::F32(r) = &mut host.regrets[p] else { unreachable!() };
            let Store::F32(s) = &mut host.strat[p] else { unreachable!() };
            self.gpu.stream.memcpy_dtoh(&self.gpu.d_regrets[p].slice(0..self.lengths[p]), r.as_mut_slice()).map_err(e)?;
            self.gpu.stream.memcpy_dtoh(&self.gpu.d_strat[p].slice(0..self.lengths[p+2]), s.as_mut_slice()).map_err(e)?;
            self.transferred_bytes += (self.lengths[p] + self.lengths[p+2]) as u64 * 4;
            self.gpu.stream.synchronize().map_err(e)?;
            host.iteration = t;
            Ok(values)
        })();
        // Cross-stream event tracking is disabled in GpuSolver. Never return
        // this workspace to another board while this stream still uses it.
        let sync = self.gpu.stream.synchronize().map_err(e);
        swap(&mut self.gpu, buffers);
        if result.is_err() || sync.is_err() { self.poisoned = true; }
        sync?;
        result
    }
}
