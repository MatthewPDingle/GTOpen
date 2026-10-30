#![allow(dead_code,unused_imports,unused_mut,hidden_glob_reexports)]
pub use solver::*;
#[path="baseline/mod.rs"]mod baseline;
#[path="candidate/mod.rs"]mod candidate;
use cudarc::{driver::{CudaContext,sys::CUdevice_attribute as Attr},nvrtc::{compile_ptx_with_opts,CompileOptions,Ptx}};
use std::{fs::OpenOptions,io::Write,path::PathBuf};
fn emit(v:serde_json::Value){println!("E106_RESOURCE {v}");std::io::stdout().flush().unwrap();}
fn main(){
 let b=std::mem::size_of::<baseline::GpuSolver>();let r=candidate::e106_layout();let c=r["wrapper_bytes"].as_u64().unwrap() as usize;assert_eq!(b,4448);assert!(c>=b&&c-b<=8);assert_eq!(r["argument_helper_bytes"],16);assert_eq!(r["static_zero_word_bytes"],8);
 let _=std::hint::black_box(candidate::GpuSolver::new as fn(&solver::Solver)->Result<candidate::GpuSolver,String>);let _=std::hint::black_box(candidate::GpuSolver::iterate as fn(&mut candidate::GpuSolver)->Result<(),String>);let _=std::hint::black_box(candidate::GpuSolver::iterate_profiled as fn(&mut candidate::GpuSolver)->Result<candidate::Profile,String>);let _=std::hint::black_box(candidate::GpuSolver::exploitability as fn(&mut candidate::GpuSolver,&solver::Solver)->Result<f64,String>);let _=std::hint::black_box(candidate::GpuSolver::update_locks as fn(&mut candidate::GpuSolver,&solver::Solver)->Result<(),String>);
 emit(serde_json::json!({"stage":"host_layout","baseline_wrapper_bytes":b,"candidate":r,"wrapper_delta_bytes":c-b,"GPU_solver_constructor_calls":0}));

 let out=PathBuf::from(std::env::args().nth(1).unwrap());let ctx=CudaContext::new(0).unwrap();assert_eq!(ctx.name().unwrap(),"NVIDIA GeForce RTX 5090");assert_eq!(ctx.compute_capability().unwrap(),(12,0));
 let names=["copy_root","down_action","down_chance","up_fold","up_show","up_chance","up_action","copy_span","up_action_eval"];
 for variant in ["baseline","candidate"]{
  let ptx=if variant=="baseline"{Ptx::from_src(include_str!("baseline-compute_120.ptx"))}else{let p=compile_ptx_with_opts(include_str!("candidate.cu"),CompileOptions{arch:Some("compute_120"),..Default::default()}).unwrap();let mut f=OpenOptions::new().create_new(true).write(true).open(out.join("candidate-compute_120.ptx")).unwrap();f.write_all(p.to_src().as_bytes()).unwrap();f.sync_all().unwrap();p};
  let before=ctx.get_limit(cudarc::driver::sys::CUlimit::CU_LIMIT_STACK_SIZE).unwrap();let m=ctx.load_module(ptx).unwrap();let after=ctx.get_limit(cudarc::driver::sys::CUlimit::CU_LIMIT_STACK_SIZE).unwrap();
  for name in names{let f=m.load_function(name).unwrap();let dynamic=match name{"up_fold"=>1326*4,"up_show"=>1326*20,_=>0};let occupancy:Vec<_>=[64u32,128,256].into_iter().map(|t|(t,f.occupancy_max_active_blocks_per_multiprocessor(t,dynamic,None).unwrap())).collect();emit(serde_json::json!({"stage":"resource","variant":variant,"kernel":name,"registers":f.num_regs().unwrap(),"local_bytes_per_thread":f.local_size_bytes().unwrap(),"static_shared_bytes":f.shared_size_bytes().unwrap(),"dynamic_shared_bytes":dynamic,"max_threads":f.max_threads_per_block().unwrap(),"occupancy_by_threads":occupancy,"device_shared_limit":ctx.attribute(Attr::CU_DEVICE_ATTRIBUTE_MAX_SHARED_MEMORY_PER_BLOCK).unwrap(),"device_thread_limit":ctx.attribute(Attr::CU_DEVICE_ATTRIBUTE_MAX_THREADS_PER_BLOCK).unwrap(),"context_stack_before":before,"context_stack_after":after,"application_kernels":0}));}drop(m);ctx.check_err().unwrap();
 }
 let p=compile_ptx_with_opts(include_str!("candidate.cu"),CompileOptions{arch:Some("compute_75"),..Default::default()}).unwrap();let mut f=OpenOptions::new().create_new(true).write(true).open(out.join("candidate-compute_75.ptx")).unwrap();f.write_all(p.to_src().as_bytes()).unwrap();f.sync_all().unwrap();drop(f);ctx.check_err().unwrap();drop(ctx);emit(serde_json::json!({"stage":"complete","candidate_NVRTC_compiles":2,"baseline_PTX_reused":true,"resource_rows":18,"application_kernels":0,"solver_or_speed_runs":0}));
}
