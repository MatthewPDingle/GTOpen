//! Bounded exact packet readback. Main CUDA kernels/runtime compiler unchanged.
use super::{e, GpuSolver, PinnedBuf};
use crate::{cfr::Solver, store::Store};
use cudarc::{driver::{CudaFunction,CudaSlice,CudaStream,LaunchConfig,PushKernelArg},nvrtc::Ptx};
use std::sync::Arc;

pub(super) const PACKET_WORDS: usize = 65544;
const MAX_DESCRIPTORS: usize = 31;
pub(super) const MIN_SOURCE_BYTES: usize = 16 * 1024 * 1024;

#[derive(Clone, Copy, Debug)]
pub(super) struct Block { pub node:usize, pub host:u64, pub source:usize, pub len:usize }
pub(super) struct Functions { signed:CudaFunction, unsigned:CudaFunction }

fn store_bounds(store:&Store, signed:bool) -> Option<(usize,usize)> {
    match (signed,store) {
        (true,Store::I16{q,scale}) => Some((q.len(),scale.len())),
        (false,Store::U16{q,scale}) => Some((q.len(),scale.len())),
        _ => None,
    }
}

pub(super) fn validate(blocks:&[Block], source_len:usize, bounds:(usize,usize)) -> Option<()> {
    let (host_len,scale_len)=bounds;
    if source_len > isize::MAX as usize/4 || host_len > isize::MAX as usize/2 {return None;}
    let (mut host_end,mut source_end,mut previous_node)=(0u64,0usize,None);
    for b in blocks {
        if b.node>=scale_len || b.len>u32::MAX as usize || previous_node.is_some_and(|n|b.node<=n) {return None;}
        if b.source<source_end || b.host<host_end {return None;}
        source_end=b.source.checked_add(b.len)?;host_end=b.host.checked_add(b.len as u64)?;
        if source_end>source_len || host_end>host_len as u64 || 5usize.checked_add(b.len.checked_add(1)?/2)?>PACKET_WORDS {return None;}
        previous_node=Some(b.node);
    }
    Some(())
}

// The checked prefix is initialized with raw writes before any typed reference.
// Its exclusive mutable borrow covers uploads, downloads and both joined waits.
fn staging(buffer:&mut PinnedBuf) -> Option<&mut [f32]> {
    if buffer.len<PACKET_WORDS || buffer.ptr.is_null() || (buffer.ptr as usize)%4!=0 {return None;}
    let bytes=PACKET_WORDS.checked_mul(4)?;
    if bytes>isize::MAX as usize || (buffer.ptr as usize).checked_add(bytes).is_none() {return None;}
    unsafe {
        buffer.ptr.cast::<u8>().write_bytes(0,bytes);
        Some(std::slice::from_raw_parts_mut(buffer.ptr,PACKET_WORDS))
    }
}

fn scatter(store:&Store, blocks:&[Block], stage:&[f32], qwords:usize) {
    let n=blocks.len();assert_eq!(stage.len(),n+qwords);
    let mut offset=0;
    for (i,b) in blocks.iter().enumerate() {
        match store {
            Store::I16{q,scale} => unsafe {
                scale.write_at(b.node,stage[i]);
                for (j,dst) in q.slice(b.host,b.len).chunks_mut(2).enumerate() {
                    let word=stage[n+offset+j].to_bits();dst[0]=word as u16 as i16;
                    if dst.len()==2 {dst[1]=(word>>16) as u16 as i16;}
                }
            },
            Store::U16{q,scale} => unsafe {
                scale.write_at(b.node,stage[i]);
                for (j,dst) in q.slice(b.host,b.len).chunks_mut(2).enumerate() {
                    let word=stage[n+offset+j].to_bits();dst[0]=word as u16;
                    if dst.len()==2 {dst[1]=(word>>16) as u16;}
                }
            },
            Store::F32(_) => unreachable!("preflight rejects F32 before optional work"),
        }
        offset+=(b.len+1)/2;
    }
    assert_eq!(offset,qwords);
}

fn download(stream:&Arc<CudaStream>, function:&CudaFunction, source:&CudaSlice<f32>,
    scratch:&mut CudaSlice<f32>, stage:&mut [f32], blocks:&[Block], store:&Store) -> Result<(),String> {
    let mut first=0;
    while first<blocks.len() {
        let mut n=0;let mut qwords=0;
        while first+n<blocks.len() && n<MAX_DESCRIPTORS {
            let next=(blocks[first+n].len+1)/2;
            if 5*(n+1)+qwords+next>PACKET_WORDS {break;}
            n+=1;qwords+=next;
        }
        assert!(n>0);let batch=&blocks[first..first+n];let total=5*n+qwords;
        let mut offset=0;
        for (i,b) in batch.iter().enumerate() {
            for (j,word) in [b.source as u32,((b.source as u64)>>32)as u32,b.len as u32,offset as u32].into_iter().enumerate() {
                stage[4*i+j]=f32::from_bits(word);
            }
            offset+=(b.len+1)/2;
        }
        let copied=stream.memcpy_htod(&stage[..4*n],&mut scratch.slice_mut(..4*n));
        let waited=stream.synchronize();copied.map_err(e)?;waited.map_err(e)?;
        let copied=(|| {
            // f32 CudaSlice ownership is unchanged; the device pointer addresses
            // u32 packet bits in this private completed scratch phase only.
            unsafe {stream.launch_builder(function).arg(source).arg(&mut *scratch).arg(&(n as u32))
                .launch(LaunchConfig{grid_dim:(n as u32,1,1),block_dim:(128,1,1),shared_mem_bytes:0})?;}
            stream.memcpy_dtoh(&scratch.slice(4*n..total),&mut stage[..n+qwords])
        })();
        let waited=stream.synchronize();copied.map_err(e)?;waited.map_err(e)?;
        scatter(store,batch,&stage[..n+qwords],qwords);
        first+=n;
    }
    Ok(())
}

impl GpuSolver {
    // Caller has performed the original readback entry fence. min_source_bytes
    // is fixed at16MiB in application entry points; isolated controls may pass0.
    pub(super) fn try_packet_sync(&mut self, solver:&mut Solver, strategy_only:bool,
        min_source_bytes:usize) -> Result<bool,String> {
        let mut bytes=0usize;
        for p in 0..2 {
            if store_bounds(&solver.strat[p],false).is_none() || (!strategy_only && store_bounds(&solver.regrets[p],true).is_none()) {return Ok(false);}
            let Some(add)=self.d_strat[p].len().checked_add(if strategy_only {0}else{self.d_regrets[p].len()}).and_then(|n|n.checked_mul(4)) else {return Ok(false);};
            let Some(total)=bytes.checked_add(add) else {return Ok(false);};bytes=total;
        }
        if bytes<min_source_bytes || self.d_cfv.len()<PACKET_WORDS || self.h_staging.len<PACKET_WORDS {return Ok(false);}
        if self._ctx.compute_capability().map_err(e)?!=(12,0) {return Ok(false);}
        let plans=[self.arena_layout[0].packet_blocks(solver,0),self.arena_layout[1].packet_blocks(solver,1)];
        let [Some(a),Some(b)]=plans else {return Ok(false);};let plans=[a,b];
        crate::d157_emit(serde_json::json!({"kind":"packet_plan","capacity_bytes":plans.iter().map(|p|p.capacity()*std::mem::size_of::<Block>()).sum::<usize>(),"lengths":[plans[0].len(),plans[1].len()],"capacities":[plans[0].capacity(),plans[1].capacity()],"block_bytes":std::mem::size_of::<Block>(),"source_bytes":bytes}));
        for p in 0..2 {
            if validate(&plans[p],self.d_strat[p].len(),store_bounds(&solver.strat[p],false).unwrap()).is_none()
                || (!strategy_only && validate(&plans[p],self.d_regrets[p].len(),store_bounds(&solver.regrets[p],true).unwrap()).is_none()) {return Ok(false);}
        }
        // Validate pointer geometry before module loading or changing CPU/GPU data.
        let ptr=self.h_staging.ptr as usize;
        if ptr==0 || ptr%4!=0 || ptr.checked_add(PACKET_WORDS*4).is_none() {return Ok(false);}
        if self.packet_functions.is_none() {
            crate::d157_emit(self.d157_resources("module_before"));
            let prepared=(|| {
                let module=self._ctx.load_module(Ptx::from_src(include_str!("packet-sm120.ptx")))?;
                let signed=module.load_function("packet_quantize_i16")?;
                let unsigned=module.load_function("packet_quantize_u16")?;
                Ok::<_,cudarc::driver::result::DriverError>(Functions{signed,unsigned})
            })();
            match prepared {
                Ok(functions)=>self.packet_functions=Some(functions),
                Err(_)=>{self.stream.synchronize().map_err(e)?;return Ok(false);},
            }
        }
        crate::d157_emit(self.d157_resources("module_after"));
        let stage=staging(&mut self.h_staging).expect("preflight checked prefix geometry");
        let functions=self.packet_functions.as_ref().unwrap();
        for p in 0..2 {
            if !strategy_only {
                download(&self.stream,&functions.signed,&self.d_regrets[p],&mut self.d_cfv,stage,&plans[p],&solver.regrets[p])?;
                self.arena_layout[p].packet_restore_inactive(solver,p,0);
            }
            download(&self.stream,&functions.unsigned,&self.d_strat[p],&mut self.d_cfv,stage,&plans[p],&solver.strat[p])?;
            self.arena_layout[p].packet_restore_inactive(solver,p,1);
        }
        solver.iteration=self.iteration;
        if self.iso_active {solver.mark_sym_dirty();}
        Ok(true)
    }
}
