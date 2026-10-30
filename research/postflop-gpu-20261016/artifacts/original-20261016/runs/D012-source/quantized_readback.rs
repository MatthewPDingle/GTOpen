//! Exact compressed download scratch. Solver f32 arenas are read-only inputs.
use super::{arena::ArenaLayout, e, PinnedBuf};
use crate::{cfr::Solver, store::Store};
use cudarc::driver::{
    result::DriverError, sys, CudaFunction, CudaModule, CudaSlice,
    CudaStream, LaunchConfig, PushKernelArg,
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

enum SetupError { Allocation(DriverError), Cuda(DriverError) }
impl SetupError {
    fn fallback(&self) -> bool {
        matches!(self, Self::Allocation(DriverError(sys::CUresult::CUDA_ERROR_OUT_OF_MEMORY)))
    }
    fn message(self) -> String {
        match self { Self::Allocation(err) | Self::Cuda(err) => e(err) }
    }
}

// Byte layout only: the existing PinnedBuf remains the sole allocation owner.
// No pointer or typed borrow survives a completed download.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
struct StagingLayout { words: usize, scales: usize, scale_offset: usize, bytes: usize }
impl StagingLayout {
    fn new(address: usize, capacity: usize, words: usize, scales: usize) -> Option<Self> {
        let align = std::mem::align_of::<f32>();
        if address == 0 || address % align != 0 || address % std::mem::align_of::<u16>() != 0 {
            return None;
        }
        let word_bytes = words.checked_mul(std::mem::size_of::<u16>())?;
        let scale_offset = word_bytes.checked_add(align - 1)? & !(align - 1);
        let bytes = scale_offset.checked_add(scales.checked_mul(std::mem::size_of::<f32>())?)?;
        if bytes > capacity || bytes > isize::MAX as usize { return None; }
        address.checked_add(bytes)?;
        Some(Self { words, scales, scale_offset, bytes })
    }

    fn for_buffer(buffer: &PinnedBuf, words: usize, scales: usize) -> Option<Self> {
        Self::new(buffer.ptr as usize, buffer.len.checked_mul(std::mem::size_of::<f32>())?, words, scales)
    }

    /// The caller must drain all GPU accesses to this buffer before entering,
    /// and finish both DTOH copies before accessing or ending the returned views.
    unsafe fn views<'a>(&self, buffer: &'a mut PinnedBuf) -> Result<(&'a mut [u16], &'a mut [f32]), String> {
        if Self::for_buffer(buffer, self.words, self.scales).as_ref() != Some(self)
            || buffer.initialized_prefix_bytes > buffer.len.checked_mul(4).ok_or("staging capacity overflow")? {
            return Err("quantized staging layout no longer fits".into());
        }
        let ptr = buffer.ptr.cast::<u8>();
        if buffer.initialized_prefix_bytes < self.bytes {
            // Zero-upload may never have touched h_staging. Initialize the entire
            // used prefix, including padding/tails, before creating typed slices.
            ptr.add(buffer.initialized_prefix_bytes).write_bytes(0, self.bytes - buffer.initialized_prefix_bytes);
            buffer.initialized_prefix_bytes = self.bytes;
        }
        // Checked aligned regions do not overlap; their lifetime exclusively
        // borrows the owner, so its f32 view cannot coexist with these views.
        Ok((std::slice::from_raw_parts_mut(ptr.cast::<u16>(), self.words),
            std::slice::from_raw_parts_mut(ptr.add(self.scale_offset).cast::<f32>(), self.scales)))
    }
}

struct DevicePlan { source: CudaSlice<u64>, output: CudaSlice<u64>, lengths: CudaSlice<u32> }

pub(super) struct QuantizedReadback {
    plans: [ArenaPlan; 2],
    metadata: [DevicePlan; 2],
    words: CudaSlice<u16>,
    scales: CudaSlice<f32>,
    host_layout: StagingLayout,
    signed: CudaFunction,
    unsigned: CudaFunction,
}

impl QuantizedReadback {
    pub(super) fn try_new(
        solver: &Solver, layouts: &[ArenaLayout; 2], staging: &PinnedBuf,
        stream: &Arc<CudaStream>, module: &Arc<CudaModule>, base_bytes: u64, budget: u64,
    ) -> Result<Option<Self>, String> {
        if !(0..2).all(|p| matches!(solver.regrets[p], Store::I16 { .. })
            && matches!(solver.strat[p], Store::U16 { .. })) { return Ok(None); }
        let plans = [layouts[0].quantized_plan(solver, 0)?, layouts[1].quantized_plan(solver, 1)?];
        if plans.iter().all(|p| p.blocks.is_empty()) { return Ok(None); }
        let Some(host_layout) = StagingLayout::for_buffer(staging,
            plans.iter().map(|p| p.words).max().unwrap(),
            plans.iter().map(|p| p.blocks.len()).max().unwrap()) else { return Ok(None); };
        if !extra_bytes(&plans).and_then(|extra| base_bytes.checked_add(extra))
            .is_some_and(|needed| needed <= budget) { return Ok(None); }
        // Base solver is fully allocated first. OOM here cannot evict its buffers.
        // Clear any prior asynchronous error before classifying allocation errors.
        stream.synchronize().map_err(e)?;
        match Self::prepare(plans, host_layout, stream, module) {
            Ok(value) => Ok(Some(value)),
            Err(err) if err.fallback() => { stream.synchronize().map_err(e)?; Ok(None) }
            Err(err) => Err(err.message()),
        }
    }

    fn prepare(plans: [ArenaPlan; 2], host_layout: StagingLayout, stream: &Arc<CudaStream>, module: &Arc<CudaModule>) -> Result<Self, SetupError> {
        let signed = module.load_function("quantize_i16_readback").map_err(SetupError::Cuda)?;
        let unsigned = module.load_function("quantize_u16_readback").map_err(SetupError::Cuda)?;
        let words_len = plans.iter().map(|p| p.words).max().unwrap().max(1);
        let scales_len = plans.iter().map(|p| p.blocks.len()).max().unwrap().max(1);
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
        Ok(Self { plans, metadata, words, scales, host_layout, signed, unsigned })
    }

    pub(super) fn download(&mut self, stream: &Arc<CudaStream>, source: &CudaSlice<f32>,
        staging: &mut PinnedBuf, solver: &Solver, layout: &ArenaLayout, p: usize, which: usize) -> Result<(), String> {
        // Complete any earlier upload/strategy download before reinterpreting or
        // initializing the shared allocation. This wait is inside readback timing.
        stream.synchronize().map_err(e)?;
        let (host_words, host_scales) = unsafe { self.host_layout.views(staging)? };
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
                    stream.memcpy_dtoh(&self.words.slice(..plan.words), &mut host_words[..plan.words])?;
                }
                stream.memcpy_dtoh(&self.scales.slice(..count), &mut host_scales[..count])
            })();
            let waited = stream.synchronize();
            copied.map_err(e)?;
            waited.map_err(e)?;
        }
        layout.write_quantized(solver, p, which, &plan.blocks,
            &host_words[..plan.words], &host_scales[..count]);
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn staging_layout_checks_padding_capacity_and_alignment() {
        let layout = StagingLayout::new(0x1000, 16, 3, 2).unwrap();
        assert_eq!(layout.scale_offset, 8);
        assert_eq!(layout.bytes, 16);
        assert!(StagingLayout::new(0x1000, 15, 3, 2).is_none());
        assert!(StagingLayout::new(0x1002, 16, 3, 2).is_none());
        assert!(StagingLayout::new(0, 16, 3, 2).is_none());
        let scales_only = StagingLayout::new(0x1000, 8, 0, 2).unwrap();
        assert_eq!(scales_only.scale_offset, 0);
        assert_eq!(scales_only.bytes, 8);
        // One-element blocks need six bytes each, exceeding f32 staging.
        assert!(StagingLayout::new(0x1000, 4 * 4, 4, 4).is_none());
    }
    #[test]
    fn staging_layout_rejects_checked_overflows() {
        assert!(StagingLayout::new(0x1000, usize::MAX, usize::MAX, 1).is_none());
        assert!(StagingLayout::new(0x1000, usize::MAX, 0, usize::MAX).is_none());
        assert!(StagingLayout::new(usize::MAX - 3, 8, 0, 2).is_none());
        assert!(StagingLayout::new(0x1000, usize::MAX, isize::MAX as usize / 2 + 1, 0).is_none());
    }
    #[test]
    fn staging_views_initialize_once_preserve_padding_and_allow_later_f32_reuse() {
        use std::mem::{ManuallyDrop, MaybeUninit};
        let mut storage = [MaybeUninit::<f32>::uninit(); 4];
        // This host-only test borrows stack storage; suppress the CUDA-owner Drop.
        let mut buffer = ManuallyDrop::new(PinnedBuf {
            ptr: storage.as_mut_ptr().cast(), len: storage.len(), initialized_prefix_bytes: 0,
        });
        let layout = StagingLayout::for_buffer(&buffer, 3, 2).unwrap();
        {
            let (words, scales) = unsafe { layout.views(&mut buffer).unwrap() };
            assert_eq!(words, [0; 3]);
            assert!(scales.iter().all(|v| v.to_bits() == 0));
            words.fill(0xa55a);
            scales[0] = f32::from_bits(0x7fc0_1234);
        }
        assert_eq!(buffer.initialized_prefix_bytes, 16);
        let padding = unsafe { std::slice::from_raw_parts(buffer.ptr.cast::<u8>().add(6), 2) };
        assert_eq!(padding, [0; 2]);
        {
            let (words, scales) = unsafe { layout.views(&mut buffer).unwrap() };
            assert_eq!(words, [0xa55a; 3]);
            assert_eq!(scales[0].to_bits(), 0x7fc0_1234);
        }
        // Models a completed strategy-only download after quantized borrows end.
        buffer.as_mut_slice().fill(-0.0);
        {
            let (_, scales) = unsafe { layout.views(&mut buffer).unwrap() };
            assert!(scales.iter().all(|v| v.to_bits() == (-0.0f32).to_bits()));
        }
        buffer.initialized_prefix_bytes = 17;
        assert!(unsafe { layout.views(&mut buffer) }.is_err());
    }

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
