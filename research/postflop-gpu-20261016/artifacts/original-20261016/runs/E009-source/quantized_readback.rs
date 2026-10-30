//! Exact compressed download scratch. Solver f32 arenas are read-only inputs.
use super::{arena::ArenaLayout, e};
use crate::{cfr::Solver, store::Store};
use cudarc::driver::{
    result::{self, DriverError}, sys, CudaContext, CudaFunction, CudaModule, CudaSlice,
    CudaStream, DeviceRepr, LaunchConfig, PushKernelArg, ValidAsZeroBits,
};
use std::sync::Arc;

#[derive(Clone, Debug)]
pub(super) struct Block {
    pub node: u32,
    pub host: u64,
    pub source: u64,
    pub output: u64,
    pub len: u32,
}

pub(super) struct ArenaPlan {
    pub blocks: Vec<Block>,
    pub words: usize,
}

impl ArenaPlan {
    pub(super) fn new(mut blocks: Vec<Block>, source_len: usize, host_len: usize) -> Result<Self, String> {
        let mut words = 0usize;
        let mut host_end = 0u64;
        let mut last_node = None;
        for block in &mut blocks {
            // The 128-stride proof kernel uses u32 induction; prevent wraparound.
            if block.len > u32::MAX - 127 { return Err("quantized block too long".into()); }
            if last_node.is_some_and(|node| block.node <= node) || block.host < host_end {
                return Err("quantized blocks must have distinct ordered nodes and host ranges".into());
            }
            last_node = Some(block.node);
            host_end = block.host.checked_add(block.len as u64).ok_or("quantized host range overflow")?;
            let source_end = block.source.checked_add(block.len as u64).ok_or("quantized source range overflow")?;
            if host_end > host_len as u64 || source_end > source_len as u64 {
                return Err("quantized block exceeds arena".into());
            }
            block.output = words as u64;
            words = words.checked_add(block.len as usize).ok_or("quantized output overflow")?;
        }
        if blocks.len() > i32::MAX as usize { return Err("quantized grid too large".into()); }
        Ok(Self { blocks, words })
    }
}

fn extra_bytes(plans: &[ArenaPlan; 2]) -> Option<u64> {
    let words = plans.iter().map(|p| p.words).max()?.max(1) as u64;
    let blocks = plans.iter().map(|p| p.blocks.len()).max()?.max(1) as u64;
    let metadata = plans.iter().try_fold(0u64, |sum, p| {
        sum.checked_add((p.blocks.len().max(1) as u64).checked_mul(20)?)
    })?;
    words.checked_mul(2)?.checked_add(blocks.checked_mul(4)?)?.checked_add(metadata)
}

enum SetupError { Allocation(DriverError), Cuda(DriverError), Invalid(String) }
impl SetupError {
    fn fallback(&self) -> bool {
        matches!(self, Self::Allocation(DriverError(sys::CUresult::CUDA_ERROR_OUT_OF_MEMORY)))
    }
    fn message(self) -> String {
        match self { Self::Allocation(err) | Self::Cuda(err) => e(err), Self::Invalid(err) => err }
    }
}

// Cached pinned memory; cudarc's general pinned allocator is write-combined,
// which is unsuitable for the CPU scatter reads here. Only zero-valid types.
struct Pinned<T> { ptr: *mut T, len: usize }
unsafe impl<T: Send> Send for Pinned<T> {}
unsafe impl<T: Sync> Sync for Pinned<T> {}
impl<T: DeviceRepr + ValidAsZeroBits> Pinned<T> {
    fn new(ctx: &CudaContext, len: usize) -> Result<Self, SetupError> {
        let bytes = len.checked_mul(std::mem::size_of::<T>())
            .filter(|&n| n <= isize::MAX as usize)
            .ok_or_else(|| SetupError::Invalid("quantized pinned size overflow".into()))?;
        ctx.bind_to_thread().map_err(SetupError::Cuda)?;
        let ptr = unsafe { result::malloc_host(bytes, 0) }.map_err(SetupError::Allocation)? as *mut T;
        // Initialize before constructing Rust slices, including unused tails.
        unsafe { ptr.write_bytes(0, len); }
        Ok(Self { ptr, len })
    }
    fn as_slice(&self) -> &[T] { unsafe { std::slice::from_raw_parts(self.ptr, self.len) } }
    fn as_mut_slice(&mut self) -> &mut [T] { unsafe { std::slice::from_raw_parts_mut(self.ptr, self.len) } }
}
impl<T> Drop for Pinned<T> {
    fn drop(&mut self) { unsafe { result::free_host(self.ptr as _).ok(); } }
}

struct DevicePlan { source: CudaSlice<u64>, output: CudaSlice<u64>, lengths: CudaSlice<u32> }

pub(super) struct QuantizedReadback {
    plans: [ArenaPlan; 2],
    metadata: [DevicePlan; 2],
    words: CudaSlice<u16>,
    scales: CudaSlice<f32>,
    host_words: Pinned<u16>,
    host_scales: Pinned<f32>,
    signed: CudaFunction,
    unsigned: CudaFunction,
}

impl QuantizedReadback {
    pub(super) fn try_new(
        solver: &Solver, layouts: &[ArenaLayout; 2], ctx: &Arc<CudaContext>,
        stream: &Arc<CudaStream>, module: &Arc<CudaModule>, base_bytes: u64, budget: u64,
    ) -> Result<Option<Self>, String> {
        if !(0..2).all(|p| matches!(solver.regrets[p], Store::I16 { .. })
            && matches!(solver.strat[p], Store::U16 { .. })) { return Ok(None); }
        let plans = [layouts[0].quantized_plan(solver, 0)?, layouts[1].quantized_plan(solver, 1)?];
        if plans.iter().all(|p| p.blocks.is_empty()) { return Ok(None); }
        if !extra_bytes(&plans).and_then(|extra| base_bytes.checked_add(extra))
            .is_some_and(|needed| needed <= budget) { return Ok(None); }
        // Base solver is fully allocated first. OOM here cannot evict its buffers.
        // Clear any prior asynchronous error before classifying allocation errors.
        stream.synchronize().map_err(e)?;
        match Self::prepare(plans, ctx, stream, module) {
            Ok(value) => Ok(Some(value)),
            Err(err) if err.fallback() => { stream.synchronize().map_err(e)?; Ok(None) }
            Err(err) => Err(err.message()),
        }
    }

    fn prepare(plans: [ArenaPlan; 2], ctx: &Arc<CudaContext>, stream: &Arc<CudaStream>, module: &Arc<CudaModule>) -> Result<Self, SetupError> {
        let signed = module.load_function("quantize_i16_readback").map_err(SetupError::Cuda)?;
        let unsigned = module.load_function("quantize_u16_readback").map_err(SetupError::Cuda)?;
        let words_len = plans.iter().map(|p| p.words).max().unwrap().max(1);
        let scales_len = plans.iter().map(|p| p.blocks.len()).max().unwrap().max(1);
        let host_words = Pinned::new(ctx, words_len)?;
        let host_scales = Pinned::new(ctx, scales_len)?;
        // Every transferred element is written before readback; no device clear.
        let words = unsafe { stream.alloc::<u16>(words_len) }.map_err(SetupError::Allocation)?;
        let scales = unsafe { stream.alloc::<f32>(scales_len) }.map_err(SetupError::Allocation)?;
        let allocate = |len: usize| -> Result<DevicePlan, SetupError> {
            let len = len.max(1);
            Ok(DevicePlan {
                source: unsafe { stream.alloc::<u64>(len) }.map_err(SetupError::Allocation)?,
                output: unsafe { stream.alloc::<u64>(len) }.map_err(SetupError::Allocation)?,
                lengths: unsafe { stream.alloc::<u32>(len) }.map_err(SetupError::Allocation)?,
            })
        };
        let mut metadata = [allocate(plans[0].blocks.len())?, allocate(plans[1].blocks.len())?];
        // No asynchronous host transfers start until all optional allocations pass.
        for (plan, device) in plans.iter().zip(&mut metadata) {
            if plan.blocks.is_empty() { continue; }
            let source: Vec<_> = plan.blocks.iter().map(|b| b.source).collect();
            let output: Vec<_> = plan.blocks.iter().map(|b| b.output).collect();
            let lengths: Vec<_> = plan.blocks.iter().map(|b| b.len).collect();
            let copied = (|| {
                stream.memcpy_htod(&source, &mut device.source)?;
                stream.memcpy_htod(&output, &mut device.output)?;
                stream.memcpy_htod(&lengths, &mut device.lengths)
            })();
            // Keep host vectors alive through completion even on a submission error.
            let waited = stream.synchronize();
            copied.map_err(SetupError::Cuda)?;
            waited.map_err(SetupError::Cuda)?;
        }
        Ok(Self { plans, metadata, words, scales, host_words, host_scales, signed, unsigned })
    }

    pub(super) fn download(&mut self, stream: &Arc<CudaStream>, source: &CudaSlice<f32>,
        solver: &Solver, layout: &ArenaLayout, p: usize, which: usize) -> Result<(), String> {
        let plan = &self.plans[p];
        let count = plan.blocks.len();
        if count != 0 {
            let metadata = &self.metadata[p];
            let function = if which == 0 { &self.signed } else { &self.unsigned };
            let copied = (|| {
                unsafe {
                    stream.launch_builder(function).arg(source).arg(&metadata.source)
                        .arg(&metadata.output).arg(&metadata.lengths).arg(&mut self.words)
                        .arg(&mut self.scales)
                        .launch(LaunchConfig { grid_dim: (count as u32, 1, 1), block_dim: (128, 1, 1), shared_mem_bytes: 0 })?;
                }
                if plan.words != 0 {
                    stream.memcpy_dtoh(&self.words.slice(..plan.words), &mut self.host_words.as_mut_slice()[..plan.words])?;
                }
                stream.memcpy_dtoh(&self.scales.slice(..count), &mut self.host_scales.as_mut_slice()[..count])
            })();
            let waited = stream.synchronize();
            copied.map_err(e)?;
            waited.map_err(e)?;
        }
        layout.write_quantized(solver, p, which, &plan.blocks,
            &self.host_words.as_slice()[..plan.words], &self.host_scales.as_slice()[..count]);
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    fn block(node: u32, host: u64, source: u64, len: u32) -> Block {
        Block { node, host, source, output: 999, len }
    }
    #[test]
    fn descriptors_pack_holes_and_empty_blocks() {
        let plan = ArenaPlan::new(vec![block(1, 2, 7, 2), block(3, 6, 4, 0), block(4, 9, 0, 3)], 9, 12).unwrap();
        assert_eq!(plan.words, 5);
        assert_eq!(plan.blocks.iter().map(|b| b.output).collect::<Vec<_>>(), [0, 2, 2]);
        let plans = [plan, ArenaPlan::new(vec![], 0, 0).unwrap()];
        assert_eq!(extra_bytes(&plans), Some(10 + 12 + 20 * 4));
    }
    #[test]
    fn descriptors_reject_bad_ranges_ownership_and_stride_overflow() {
        for blocks in [vec![block(1, 9, 0, 2)], vec![block(1, 0, 9, 2)],
            vec![block(1, u64::MAX, 0, 2)], vec![block(1, 0, u64::MAX, 2)],
            vec![block(1, 0, 0, 3), block(2, 2, 3, 2)],
            vec![block(1, 0, 0, 1), block(1, 1, 1, 1)],
            vec![block(1, 0, 0, u32::MAX)]] {
            assert!(ArenaPlan::new(blocks, 10, 10).is_err());
        }
    }
    #[test]
    fn only_allocation_oom_can_fallback() {
        let oom = DriverError(sys::CUresult::CUDA_ERROR_OUT_OF_MEMORY);
        assert!(SetupError::Allocation(oom).fallback());
        assert!(!SetupError::Cuda(oom).fallback());
        assert!(!SetupError::Allocation(DriverError(sys::CUresult::CUDA_ERROR_INVALID_CONTEXT)).fallback());
    }
}
