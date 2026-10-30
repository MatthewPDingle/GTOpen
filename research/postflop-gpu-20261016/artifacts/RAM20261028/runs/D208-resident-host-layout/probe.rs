#![allow(dead_code,unused_imports,unused_mut,hidden_glob_reexports)]
pub use solver::*;
#[path="gpu/mod.rs"]mod observed;
fn main(){
 let layout=observed::d208_layout();let baseline=std::mem::size_of::<solver::gpu::GpuSolver>();assert_eq!(baseline,4448);let actual=layout["actual_wrapper_bytes"].as_u64().unwrap() as usize;assert!(actual>=baseline&&actual-baseline<=32);assert_eq!(layout["actual_state_bytes"],24);assert_eq!(layout["parameter_bytes"],3008);assert_eq!(layout["parameter_alignment"],8);assert_eq!(layout["span_offset"],444);assert_eq!(layout["reserved_offset"],3004);
 let _=std::hint::black_box(observed::GpuSolver::new as fn(&solver::Solver)->Result<observed::GpuSolver,String>);let _=std::hint::black_box(observed::GpuSolver::iterate as fn(&mut observed::GpuSolver)->Result<(),String>);
 println!("D208_LAYOUT {}",serde_json::json!({"candidate":layout,"baseline_wrapper_bytes":baseline,"wrapper_delta_bytes":actual-baseline,"actual_constructor_CUDA_kernel_or_solver_calls":0}));
}
