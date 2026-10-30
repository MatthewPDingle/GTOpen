#![allow(dead_code,unused_imports,unused_mut,hidden_glob_reexports)]
pub use solver::*;
#[path="baseline/mod.rs"]mod baseline;
#[path="candidate/mod.rs"]mod candidate;
fn main(){let b=(std::mem::size_of::<baseline::GpuSolver>(),std::mem::align_of::<baseline::GpuSolver>());let c=(std::mem::size_of::<candidate::GpuSolver>(),std::mem::align_of::<candidate::GpuSolver>());println!("D249_HOST {}",serde_json::json!({"baseline_size":b.0,"baseline_align":b.1,"candidate_size":c.0,"candidate_align":c.1,"constructors_called":0,"CUDA_APIs_or_kernels":0}));assert_eq!(b,(4448,8));assert_eq!(b,c);}
