//! Research-only canonical host storage and optional SSD spill; explicit GPU calculation.
use super::SymmetricContinuationGpu;
use crate::{gpu::{GpuSolver, PinnedBuf, plan::GpuPlan}, store::Store, Algorithm, Solver, Spot};
use cudarc::driver::{CudaSlice,CudaFunction,CudaModule,PushKernelArg};
use std::{sync::Arc, path::Path};
#[path = "continuation_disk_state_tests.rs"]
mod disk_state;
use disk_state::DiskState;

// Keep only the canonical storage mapping; drop duplicate CPU river/planning tables.
struct StoragePlan {
    iso_active:bool, action_nodes:Vec<u32>, node_data_off:Vec<u64>, arena_elements:[usize;2],
}
impl From<GpuPlan> for StoragePlan {
    fn from(p:GpuPlan)->Self {Self{iso_active:p.iso_active,action_nodes:p.action_nodes,
        node_data_off:p.node_data_off,arena_elements:p.arena_elements}}
}
#[cfg(test)]
#[path="continuation_stored_device_tests.rs"]
mod device_tests;


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
fn packed(source: &Solver, plan: &StoragePlan) -> [Vec<f32>; 4] {
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

fn restore(spot: &Arc<Spot>, iteration: u32, plan: &StoragePlan, packed: &[Vec<f32>; 4]) -> Solver {
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
    compact: Option<[CudaSlice<f32>;4]>,
}
impl StoredWorkspace {
    pub fn bytes(&self) -> u64 { self.buffers.as_ref().map_or(0, |b| b.iter().map(|a| a.len() as u64 * 4).sum::<u64>()) + self.compact.as_ref().map_or(0, |b| b.iter().map(|a| a.len() as u64 * 4).sum::<u64>()) }
    fn absorb_compact(&mut self, buffers:[CudaSlice<f32>;4]) {
        if let Some(current)=&mut self.compact {
            for (old,new) in current.iter_mut().zip(buffers) {if new.len()>old.len() {*old=new;}}
        } else {self.compact=Some(buffers);}
    }
    fn absorb(&mut self, buffers: [CudaSlice<f32>; 7]) {
        if let Some(current) = &mut self.buffers {
            for (old,new) in current.iter_mut().zip(buffers) { if new.len()>old.len() { *old=new; } }
        } else { self.buffers=Some(buffers); }
    }
}
enum State { Memory([Vec<f32>;4]), Disk(DiskState) }

pub struct StoredContinuationGpu {
    spot: Arc<Spot>,
    plan: StoragePlan,
    gpu: SymmetricContinuationGpu,
    lengths: [usize;7],
    pack_nodes:CudaSlice<u32>,
    pack_offsets:CudaSlice<u64>,
    copy_kernel:CudaFunction,
    _copy_module:Arc<CudaModule>,
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
        let plan=StoragePlan::from(GpuPlan::build(&host.spot,true));
        let g=&mut gpu.gpu;
        let pack_nodes=g.stream.clone_htod(&plan.action_nodes).map_err(crate::gpu::e)?;
        let offsets:Vec<u64>=plan.action_nodes.iter().map(|&i|plan.node_data_off[i as usize]).collect();
        let pack_offsets=g.stream.clone_htod(&offsets).map_err(crate::gpu::e)?;
        if plan.iso_active {
            let sources=g.stream.clone_dtoh(&gpu.public_orbits.as_ref().ok_or("missing transport map")?.0).map_err(crate::gpu::e)?;
            let mut canonical=vec![false;host.spot.tree.nodes.len()];
            for &n in &plan.action_nodes {canonical[n as usize]=true;}
            let active_nodes=g.stream.clone_dtoh(&g.d_action_nodes).map_err(crate::gpu::e)?;
            let rejected_all=host.spot.tree.nodes.iter().enumerate().filter(|(i,n)|
                n.kind==crate::tree::KIND_ACTION && !canonical[sources[*i] as usize]).count();
            let missing:Vec<_>=active_nodes.iter().copied().filter(|&i|!canonical[sources[i as usize] as usize]).collect();
            println!("GPU_STORAGE_MAP active={} missing_active={} all_tree_missing={}",active_nodes.len(),missing.len(),rejected_all);
            if let Some(&i)=missing.first() {
                return Err(format!("active GPU transport source absent from parked plan: node={i} source={}",sources[i as usize]));
            }
            let mut device=Vec::new();
            for k in 0..4 {device.push(g.stream.alloc_zeros::<f32>(plan.arena_elements[k%2].max(1)).map_err(crate::gpu::e)?);}
            workspace.absorb_compact(device.try_into().unwrap());
        }
        static PTX:std::sync::OnceLock<Result<cudarc::nvrtc::Ptx,String>>=std::sync::OnceLock::new();
        let (major,minor)=g._ctx.compute_capability().map_err(crate::gpu::e)?;
        let ptx=PTX.get_or_init(|| {
            let arch=Box::leak(format!("compute_{major}{minor}").into_boxed_str());
            cudarc::nvrtc::compile_ptx_with_opts(include_str!("continuation_storage_copy.cu"),
                cudarc::nvrtc::CompileOptions{arch:Some(arch),..Default::default()}).map_err(crate::gpu::e)
        }).clone()?;
        let copy_module=g._ctx.load_module(ptx).map_err(crate::gpu::e)?;
        let copy_kernel=copy_module.load_function("continuation_storage_copy").map_err(crate::gpu::e)?;
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
        Ok(Self {spot:host.spot.clone(),plan,gpu,lengths,pack_nodes,pack_offsets,copy_kernel,_copy_module:copy_module,state,iteration:0,poisoned:false,
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
    fn copy_canonical(&mut self, compact:&mut [CudaSlice<f32>;4], p:usize, gather:bool)->Result<(),String> {
        let g=&mut self.gpu.gpu;
        let count=self.pack_nodes.len() as i32;
        if count==0 {return Ok(());}
        let [r0,r1,s0,s1]=compact;
        let (r,s)=if p==0 {(r0,s0)}else{(r1,s1)};
        unsafe {
            g.stream.launch_builder(&self.copy_kernel)
                .arg(&self.pack_nodes).arg(&count).arg(&g.d_node_player).arg(&g.d_node_na)
                .arg(&g.d_node_data_off).arg(&self.pack_offsets)
                .arg(&mut g.d_regrets[p]).arg(&mut g.d_strat[p]).arg(r).arg(s)
                .arg(&g.nh[p]).arg(&(p as i32)).arg(&(gather as i32))
                .launch(GpuSolver::cfg(count as u32,0)).map_err(crate::gpu::e)?;
        }
        Ok(())
    }
    pub fn sweep(&mut self, workspace: &mut StoredWorkspace, p:usize, t:u32,
                 own:&[f32], opponent:&[f32]) -> Result<Vec<f32>,String> {
        if self.poisoned || workspace.poisoned || p>1 || t==0 {return Err("invalid or poisoned stored continuation".into());}
        // Keep pageable upload owners alive until synchronization, including on errors.
        let disk_arrays=match &self.state {State::Disk(d)=>Some(d.load().map_err(|e|e.to_string())?),_=>None};
        if self.disk_backed {self.disk_read_bytes+=self.storage_bytes;}
        let arrays=match &self.state {State::Memory(a)=>a,State::Disk(_)=>disk_arrays.as_ref().unwrap()};
        let buffers=workspace.buffers.as_mut().ok_or("missing workspace")?;
        if buffers.iter().zip(self.lengths).any(|(b,n)|b.len()<n) {return Err("workspace too small".into());}
        if self.plan.iso_active {
            let compact=workspace.compact.as_ref().ok_or("missing canonical workspace")?;
            if compact.iter().zip(arrays).any(|(b,a)|b.len()<a.len()) {return Err("canonical workspace too small".into());}
        }
        swap(&mut self.gpu.gpu,buffers);
        // Upload before borrowing the whole wrapper for copy/transport operations.
        let upload=(|| {
            let g=&mut self.gpu.gpu;
            if self.plan.iso_active {
                let compact=workspace.compact.as_mut().unwrap();
                for k in 0..4 {g.stream.memcpy_htod(&arrays[k],&mut compact[k].slice_mut(0..arrays[k].len())).map_err(crate::gpu::e)?;}
                for q in 0..2 {
                    g.stream.memset_zeros(&mut g.d_regrets[q].slice_mut(0..self.lengths[q])).map_err(crate::gpu::e)?;
                    g.stream.memset_zeros(&mut g.d_strat[q].slice_mut(0..self.lengths[q+2])).map_err(crate::gpu::e)?;
                }
            } else {
                for q in 0..2 {
                    g.stream.memcpy_htod(&arrays[q], &mut g.d_regrets[q].slice_mut(0..arrays[q].len())).map_err(crate::gpu::e)?;
                    g.stream.memcpy_htod(&arrays[q+2], &mut g.d_strat[q].slice_mut(0..arrays[q+2].len())).map_err(crate::gpu::e)?;
                }
            }
            Ok::<(),String>(())
        })();
        let mut next: [Vec<f32>;4]=std::array::from_fn(|k|vec![0.;arrays[k].len()]);
        let result=(|| {
            upload?;
            if self.plan.iso_active {
                let compact=workspace.compact.as_mut().unwrap();
                for q in 0..2 {self.copy_canonical(compact,q,false)?;self.gpu.transport_player(q)?;}
            }
            let values=self.gpu.sweep(p,t,own,opponent)?;
            if self.plan.iso_active {
                let compact=workspace.compact.as_mut().unwrap();
                for q in 0..2 {self.copy_canonical(compact,q,true)?;}
                let g=&mut self.gpu.gpu;
                for k in 0..4 {g.stream.memcpy_dtoh(&compact[k].slice(0..next[k].len()),&mut next[k]).map_err(crate::gpu::e)?;}
            } else {
                let g=&mut self.gpu.gpu;
                for q in 0..2 {
                    g.stream.memcpy_dtoh(&g.d_regrets[q].slice(0..next[q].len()),&mut next[q]).map_err(crate::gpu::e)?;
                    g.stream.memcpy_dtoh(&g.d_strat[q].slice(0..next[q+2].len()),&mut next[q+2]).map_err(crate::gpu::e)?;
                }
            }
            Ok::<_,String>(values)
        })();
        let sync=self.gpu.gpu.stream.synchronize().map_err(crate::gpu::e);
        swap(&mut self.gpu.gpu,buffers);
        if result.is_err() || sync.is_err() {self.poisoned=true;workspace.poisoned=true;}
        sync?;
        let values=result?;
        match &mut self.state {
            State::Memory(a)=>*a=next,
            State::Disk(d)=> {
                if let Err(error)=d.replace(&next,t) {self.poisoned=true;return Err(error.to_string());}
                self.disk_write_bytes+=self.storage_bytes;
            }
        }
        self.iteration=t;
        self.transferred_bytes+=self.storage_bytes*2;
        Ok(values)
    }
}
