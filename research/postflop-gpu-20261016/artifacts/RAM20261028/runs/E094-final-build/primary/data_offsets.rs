//! Private device metadata width. CPU plans and all address arithmetic stay u64.
use cudarc::driver::{CudaSlice,CudaStream,LaunchArgs,PushKernelArg};
use std::sync::Arc;

pub(super) enum DeviceOffsets { Narrow(CudaSlice<u32>), Wide(CudaSlice<u64>) }

pub(super) fn narrow_fits(values:&[u64])->bool {
    values.iter().all(|&d|d==u64::MAX || d<u32::MAX as u64)
}

impl DeviceOffsets {
    pub(super) fn upload(stream:&Arc<CudaStream>,values:&[u64],narrow:bool)->Result<Self,String> {
        if !narrow {return stream.clone_htod(values).map(Self::Wide).map_err(super::e);}
        assert!(narrow_fits(values));
        let packed:Vec<u32>=values.iter().map(|&d|if d==u64::MAX {u32::MAX} else {d as u32}).collect();
        let uploaded=stream.clone_htod(&packed);
        // Keep the temporary owner through completion even when upload returns an error.
        // This synchronization and packing cost remain inside ordinary GPU construction.
        let synchronized=stream.synchronize();
        let device=uploaded.map_err(super::e)?;
        synchronized.map_err(super::e)?;
        Ok(Self::Narrow(device))
    }
    pub(super) fn bytes(&self)->u64 {
        match self {Self::Narrow(v)=>(v.len()*4) as u64,Self::Wide(v)=>(v.len()*8) as u64}
    }
}

// Delegate to cudarc's original typed-slice argument implementation. It retains
// the same slice owner/lifetime, pointer-to-argument storage and event tracking.
// The constructor pairs this immutable owner with the corresponding shader format.
unsafe impl<'a,'b:'a> PushKernelArg<&'b DeviceOffsets> for LaunchArgs<'a> {
    #[inline(always)]
    fn arg(&mut self,arg:&'b DeviceOffsets)->&mut Self {
        match arg {DeviceOffsets::Narrow(v)=>self.arg(v),DeviceOffsets::Wide(v)=>self.arg(v)}
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn offset_representation_preserves_reserved_boundary_and_wide_fallback() {
        assert!(narrow_fits(&[]));
        assert!(narrow_fits(&[0,1,u32::MAX as u64-1,u64::MAX]));
        assert!(!narrow_fits(&[u32::MAX as u64]));
        assert!(!narrow_fits(&[1u64<<32]));
        assert!(!narrow_fits(&[u64::MAX-1]));
        for base in [0,1,u32::MAX as u64-1] {
            for action in [0u64,1,3,16] {for hand in [0u64,1,1325] {
                assert_eq!(base+action*1326+hand,(base as u32) as u64+action*1326+hand);
            }}
        }
    }
}
