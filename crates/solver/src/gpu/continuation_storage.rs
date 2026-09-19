//! Research-only canonical host storage and optional SSD spill; explicit GPU calculation.
use super::SymmetricContinuationGpu;
use crate::{gpu::{GpuSolver, PinnedBuf, plan::GpuPlan}, store::Store, Algorithm, Solver, Spot};
use cudarc::driver::CudaSlice;
use std::{sync::Arc, path::Path};
#[path = "continuation_disk_state_tests.rs"]
mod disk_state;
use disk_state::DiskState;

fn data(s: &Store) -> &[f32] {
    let Store::F32(a) = s else {
        panic!("F32 required")
    };
    a.as_slice()
}
fn data_mut(s: &mut Store) -> &mut [f32] {
    let Store::F32(a) = s else {
        panic!("F32 required")
    };
    a.as_mut_slice()
}
fn packed(source: &Solver, plan: &GpuPlan) -> [Vec<f32>; 4] {
    if !plan.iso_active {
        return std::array::from_fn(|k| {
            data(if k < 2 {
                &source.regrets[k]
            } else {
                &source.strat[k - 2]
            })
            .to_vec()
        });
    }
    let mut result = std::array::from_fn(|k| vec![0.; plan.arena_elements[k % 2]]);
    let mut copied = [0usize; 2];
    for &i in &plan.action_nodes {
        let n = &source.spot.tree.nodes[i as usize];
        let p = n.player as usize;
        let len = n.num_children as usize * source.spot.hands[p].len();
        let src = n.data_offset as usize;
        let dst = plan.node_data_off[i as usize] as usize;
        for (k, s) in [(p, &source.regrets[p]), (p + 2, &source.strat[p])] {
            result[k][dst..dst + len].copy_from_slice(&data(s)[src..src + len]);
        }
        copied[p] += len;
    }
    assert_eq!(copied, plan.arena_elements);
    result
}

fn restore(spot: &Arc<Spot>, iteration: u32, plan: &GpuPlan, packed: &[Vec<f32>; 4]) -> Solver {
    let mut restored = Solver::new(spot.clone());
    restored.algo = Algorithm::CfrPlus;
    restored.iteration = iteration;
    restored.use_isomorphism = true;
    if !plan.iso_active {
        for p in 0..2 {
            data_mut(&mut restored.regrets[p]).copy_from_slice(&packed[p]);
            data_mut(&mut restored.strat[p]).copy_from_slice(&packed[p + 2]);
        }
        restored.use_isomorphism = false;
        return restored;
    }
    for &i in &plan.action_nodes {
        let n = &spot.tree.nodes[i as usize];
        let p = n.player as usize;
        let len = n.num_children as usize * spot.hands[p].len();
        let dst = n.data_offset as usize;
        let src = plan.node_data_off[i as usize] as usize;
        data_mut(&mut restored.regrets[p])[dst..dst + len]
            .copy_from_slice(&packed[p][src..src + len]);
        data_mut(&mut restored.strat[p])[dst..dst + len]
            .copy_from_slice(&packed[p + 2][src..src + len]);
    }
    restored.mark_sym_dirty();
    restored.ensure_symmetric();
    restored.use_isomorphism = false;
    restored
}

fn take(g: &mut GpuSolver) -> Result<[CudaSlice<f32>; 7], String> {
    g.stream.synchronize().map_err(crate::gpu::e)?;
    let mut small: Vec<_> = (0..7)
        .map(|_| g.stream.alloc_zeros::<f32>(1).map_err(crate::gpu::e))
        .collect::<Result<_, _>>()?;
    let mut result = Vec::new();
    for old in g
        .d_regrets
        .iter_mut()
        .chain(&mut g.d_strat)
        .chain(&mut g.d_reach)
        .chain(std::iter::once(&mut g.d_cfv))
    {
        result.push(std::mem::replace(old, small.pop().unwrap()));
    }
    Ok(result.try_into().unwrap())
}

fn swap(g: &mut GpuSolver, workspace: &mut [CudaSlice<f32>; 7]) {
    for (a, b) in g
        .d_regrets
        .iter_mut()
        .chain(&mut g.d_strat)
        .chain(&mut g.d_reach)
        .chain(std::iter::once(&mut g.d_cfv))
        .zip(workspace)
    {
        std::mem::swap(a, b);
    }
}

#[derive(Default)]
pub struct StoredWorkspace {
    buffers: Option<[CudaSlice<f32>; 7]>,
    poisoned: bool,
}
impl StoredWorkspace {
    pub fn bytes(&self) -> u64 { self.buffers.as_ref().map_or(0, |b| b.iter().map(|a| a.len() as u64 * 4).sum()) }
    fn absorb(&mut self, buffers: [CudaSlice<f32>; 7]) {
        if let Some(current) = &mut self.buffers {
            for (old,new) in current.iter_mut().zip(buffers) { if new.len()>old.len() { *old=new; } }
        } else { self.buffers=Some(buffers); }
    }
}
enum State { Memory([Vec<f32>;4]), Disk(DiskState) }

pub struct StoredContinuationGpu {
    spot: Arc<Spot>,
    plan: GpuPlan,
    gpu: SymmetricContinuationGpu,
    lengths: [usize;7],
    state: State,
    iteration: u32,
    poisoned: bool,
    pub storage_bytes: u64,
    pub disk_backed: bool,
    pub transferred_bytes: u64,
    pub disk_read_bytes: u64,
    pub disk_write_bytes: u64,
}
impl StoredContinuationGpu {
    pub fn new(host: &Solver, workspace: &mut StoredWorkspace, disk_root: &Path, key: u64,
               remaining_ram_bytes: &mut u64) -> Result<Self,String> {
        if workspace.poisoned { return Err("workspace is poisoned".into()); }
        // The constructor validates zero-initialized unlocked F32 CFR+ state.
        let mut gpu=SymmetricContinuationGpu::new_explicit_reference(host,u64::MAX)?;
        let buffers=take(&mut gpu.gpu)?;
        let lengths=std::array::from_fn(|i|buffers[i].len());
        gpu.gpu.h_staging=PinnedBuf::new(&gpu.gpu._ctx,1)?;
        let plan=GpuPlan::build(&host.spot,true);
        let arrays=packed(host,&plan);
        let storage_bytes=arrays.iter().map(|a|a.len() as u64*4).sum::<u64>();
        let disk_backed=storage_bytes>*remaining_ram_bytes;
        let state=if disk_backed {
            State::Disk(DiskState::create(disk_root,key,&arrays,0).map_err(|e|e.to_string())?)
        } else {
            *remaining_ram_bytes-=storage_bytes;
            State::Memory(arrays)
        };
        workspace.absorb(buffers);
        Ok(Self {spot:host.spot.clone(),plan,gpu,lengths,state,iteration:0,poisoned:false,
            storage_bytes,disk_backed,transferred_bytes:0,disk_read_bytes:0,
            disk_write_bytes:if disk_backed {storage_bytes} else {0}})
    }
    pub fn spot(&self) -> &Arc<Spot> { &self.spot }
    pub fn materialize(&self) -> Result<Solver,String> {
        if self.poisoned { return Err("stored continuation is poisoned".into()); }
        match &self.state {
            State::Memory(a)=>Ok(restore(&self.spot,self.iteration,&self.plan,a)),
            State::Disk(d)=>Ok(restore(&self.spot,self.iteration,&self.plan,&d.load().map_err(|e|e.to_string())?)),
        }
    }
    pub fn sweep(&mut self, workspace: &mut StoredWorkspace, p:usize, t:u32,
                 own:&[f32], opponent:&[f32]) -> Result<Vec<f32>,String> {
        if self.poisoned || workspace.poisoned || p>1 || t==0 {return Err("invalid or poisoned stored continuation".into());}
        let mut host=self.materialize()?;
        if self.disk_backed {self.disk_read_bytes+=self.storage_bytes;}
        let buffers=workspace.buffers.as_mut().ok_or("missing workspace")?;
        if buffers.iter().zip(self.lengths).any(|(b,n)|b.len()<n) {return Err("workspace too small".into());}
        swap(&mut self.gpu.gpu,buffers);
        let result=(|| {
            let g=&mut self.gpu.gpu;
            for q in 0..2 {
                g.stream.memcpy_htod(data(&host.regrets[q]), &mut g.d_regrets[q].slice_mut(0..self.lengths[q])).map_err(crate::gpu::e)?;
                g.stream.memcpy_htod(data(&host.strat[q]), &mut g.d_strat[q].slice_mut(0..self.lengths[q+2])).map_err(crate::gpu::e)?;
            }
            let values=self.gpu.sweep(p,t,own,opponent)?;
            let g=&mut self.gpu.gpu;
            for q in 0..2 {
                g.stream.memcpy_dtoh(&g.d_regrets[q].slice(0..self.lengths[q]), data_mut(&mut host.regrets[q])).map_err(crate::gpu::e)?;
                g.stream.memcpy_dtoh(&g.d_strat[q].slice(0..self.lengths[q+2]), data_mut(&mut host.strat[q])).map_err(crate::gpu::e)?;
            }
            Ok::<_,String>(values)
        })();
        // Workspace tracking is disabled: synchronize even on failed operations.
        let sync=self.gpu.gpu.stream.synchronize().map_err(crate::gpu::e);
        swap(&mut self.gpu.gpu,buffers);
        if result.is_err() || sync.is_err() {self.poisoned=true;workspace.poisoned=true;}
        sync?;
        let values=result?;
        let arrays=packed(&host,&self.plan);
        match &mut self.state {
            State::Memory(a)=>*a=arrays,
            State::Disk(d)=> {
                if let Err(error)=d.replace(&arrays,t) {self.poisoned=true;return Err(error.to_string());}
                self.disk_write_bytes+=self.storage_bytes;
            }
        }
        self.iteration=t;
        self.transferred_bytes+=self.lengths[..4].iter().sum::<usize>() as u64*8;
        Ok(values)
    }
}
